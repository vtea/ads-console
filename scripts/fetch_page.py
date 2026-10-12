#!/usr/bin/env python3
"""
Fetch a landing page for ad campaign quality analysis.

Usage:
    python fetch_page.py https://example.com/landing
    python fetch_page.py https://example.com/landing --output page.html
"""

import sys
from pathlib import Path
from urllib.parse import urljoin

# Source checkouts keep core beside scripts; installed layouts keep it inside scripts.
if not (Path(__file__).resolve().parent / "claude_ads_core").is_dir():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from claude_ads_core.cli_support import LocaleArgumentParser, cli_locale
from claude_ads_core.i18n import locale_scope, t

from url_utils import (
    guarded_request,
    resolve_output_path,
    sanitize_error,
    sanitize_headers,
    sanitize_url,
    validate_url,
)

try:
    import requests
except ImportError:
    requests = None


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ClaudeAds/1.7; +https://github.com/AgriciDaniel/claude-ads)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


def fetch_page(
    url: str,
    timeout: int = 30,
    follow_redirects: bool = True,
    max_redirects: int = 5,
) -> dict:
    """
    Fetch a landing page and return response details relevant to ad quality checks.

    Returns:
        Dictionary with url, status_code, content, headers, redirect_chain, error
    """
    if requests is None:
        print(t("tools.common.requests_required"), file=sys.stderr)
        sys.exit(1)

    result = {
        "url": sanitize_url(url),
        "status_code": None,
        "content": None,
        "headers": {},
        "redirect_chain": [],
        "error": None,
    }

    try:
        url = validate_url(url)
    except ValueError as e:
        result["error"] = sanitize_error(e)
        return result

    try:
        session = requests.Session()
        # Ignore ambient HTTP(S)_PROXY settings. They can route validated
        # public URLs through an unexpected internal proxy and leak headers.
        session.trust_env = False
        current_url = url
        redirect_chain = []

        # Manual redirect loop with per-hop SSRF revalidation. The previous
        # `allow_redirects=True` path delegated to urllib3, which fetched
        # `Location` targets without re-checking them against the private-IP
        # blocklist. A public origin returning a 302 to e.g. 169.254.169.254
        # would have reached cloud metadata.
        for _ in range(max_redirects + 1):
            # Validate immediately before every network dispatch, not only at
            # input parsing time. Redirect targets are validated both when
            # parsed and here at the pre-request boundary.
            response = guarded_request(
                session,
                "GET",
                current_url,
                headers=DEFAULT_HEADERS,
                timeout=timeout,
            )

            if not follow_redirects or response.status_code not in (301, 302, 303, 307, 308):
                break

            location = response.headers.get("Location")
            if not location:
                break

            next_url = urljoin(current_url, location)
            try:
                next_url = validate_url(next_url)
            except ValueError as e:
                result["error"] = t("tools.fetch.blocked_redirect", error=sanitize_error(e))
                return result

            redirect_chain.append(current_url)
            current_url = next_url
        else:
            result["error"] = t("tools.fetch.too_many_redirects", maximum=max_redirects)
            return result

        result["url"] = sanitize_url(current_url)
        result["status_code"] = response.status_code
        result["content"] = response.text
        result["headers"] = sanitize_headers(response.headers)
        result["redirect_chain"] = [sanitize_url(item) for item in redirect_chain]

    except requests.exceptions.Timeout:
        result["error"] = t("tools.fetch.request_timeout", timeout=timeout)
    except requests.exceptions.SSLError as e:
        result["error"] = t("tools.fetch.ssl_error", error=sanitize_error(e))
    except requests.exceptions.ConnectionError as e:
        result["error"] = t("tools.fetch.connection_error", error=sanitize_error(e))
    except requests.exceptions.RequestException as e:
        result["error"] = t("tools.fetch.request_failed", error=sanitize_error(e))

    return result


def main(argv: list[str] | None = None):
    with locale_scope(cli_locale(argv)):
        try:
            return _main(argv)
        except (OSError, ValueError, RuntimeError) as exc:
            print(t("tools.common.error", error=sanitize_error(exc)), file=sys.stderr)
            sys.exit(1)


def _main(argv: list[str] | None):
    parser = LocaleArgumentParser(description=t("tools.fetch.description"))
    parser.add_argument("url", help=t("tools.fetch.url_help"))
    parser.add_argument("--output", "-o", help=t("tools.fetch.output_help"))
    parser.add_argument("--timeout", "-t", type=int, default=30, help=t("tools.fetch.timeout_help"))
    parser.add_argument("--no-redirects", action="store_true", help=t("tools.fetch.no_redirects_help"))

    args = parser.parse_args(argv)

    result = fetch_page(
        args.url,
        timeout=args.timeout,
        follow_redirects=not args.no_redirects,
    )

    if result["error"]:
        print(t("tools.common.error", error=sanitize_error(result["error"])), file=sys.stderr)
        sys.exit(1)

    if args.output:
        try:
            output_path = resolve_output_path(args.output, create_parent=True)
        except ValueError as exc:
            print(t("tools.common.error", error=sanitize_error(exc)), file=sys.stderr)
            sys.exit(1)
        with output_path.open("w", encoding="utf-8") as f:
            f.write(result["content"])
        print(t("tools.fetch.saved", path=sanitize_error(output_path)))
    else:
        print(result["content"])

    print(t("tools.fetch.url", url=sanitize_url(result["url"])), file=sys.stderr)
    print(t("tools.fetch.status", status=result["status_code"]), file=sys.stderr)
    if result["redirect_chain"]:
        sanitized_chain = [sanitize_url(u) for u in result["redirect_chain"]]
        print(t("tools.fetch.redirects", chain=' -> '.join(sanitized_chain)), file=sys.stderr)


if __name__ == "__main__":
    main()
