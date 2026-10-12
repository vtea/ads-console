#!/usr/bin/env python3
"""
Analyze landing page quality for ad campaigns using Playwright.

Checks Core Web Vitals, mobile responsiveness, message match elements,
and conversion-readiness signals aligned with ad audit checks G59-G61.

Usage:
    python analyze_landing.py https://example.com/landing --egress-attestation attestation.json
    python analyze_landing.py https://example.com/landing --json --egress-attestation attestation.json
"""

import json
import sys
from pathlib import Path

# Source checkouts keep core beside scripts; installed layouts keep it inside scripts.
if not (Path(__file__).resolve().parent / "claude_ads_core").is_dir():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from claude_ads_core.cli_support import LocaleArgumentParser, cli_locale
from claude_ads_core.i18n import locale_scope, t

from url_utils import (
    EgressSandboxAttestation,
    create_guarded_browser_context,
    load_egress_sandbox_attestation,
    sanitize_error,
    sanitize_url,
    validate_browser_url,
)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    sync_playwright = None
    PlaywrightTimeout = TimeoutError


def analyze_landing(
    url: str,
    timeout: int = 30000,
    *,
    egress_attestation: EgressSandboxAttestation | None = None,
) -> dict:
    """
    Analyze landing page quality for ad campaign relevance.

    Checks:
        - Core Web Vitals (LCP, CLS) for G59 (mobile speed)
        - H1/title for G60 (landing page relevance)
        - Schema markup for G61 (structured data)
        - Mobile responsiveness
        - CTA visibility above fold
        - Form presence and field count
        - Trust signals (testimonials, badges, reviews)
    """
    if sync_playwright is None:
        print(t("tools.common.playwright_required"), file=sys.stderr)
        sys.exit(1)

    result = {
        "url": sanitize_url(url),
        "performance": {
            "lcp_ms": None,
            "cls": None,
            "ttfb_ms": None,
            "dom_content_loaded_ms": None,
        },
        "content": {
            "title": None,
            "h1": None,
            "meta_description": None,
            "word_count": 0,
        },
        "conversion": {
            "cta_above_fold": False,
            "form_present": False,
            "form_fields": 0,
            "phone_number": False,
            "chat_widget": False,
        },
        "trust": {
            "testimonials": False,
            "trust_badges": False,
            "reviews_schema": False,
        },
        "mobile": {
            "viewport_meta": False,
            "horizontal_scroll": False,
            "font_readable": True,
        },
        "schema": {
            "types_found": [],
            "product_schema": False,
            "faq_schema": False,
            "service_schema": False,
        },
        "error": None,
        "egress_attestation": None,
    }

    try:
        # Playwright cannot bind its eventual socket to a Python-validated DNS
        # answer. Default browser analysis is denied unless the caller attests
        # an independent OS/container egress enforcement boundary.
        url = validate_browser_url(
            url,
            egress_attestation=egress_attestation,
        )
        result["egress_attestation"] = egress_attestation.audit_reference()
    except ValueError as e:
        result["error"] = sanitize_error(e)
        return result

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # Desktop analysis
            desktop, desktop_blocks = create_guarded_browser_context(
                browser,
                viewport={"width": 1920, "height": 1080},
                egress_attestation=egress_attestation,
            )
            page = desktop.new_page()

            page.goto(url, wait_until="networkidle", timeout=timeout)
            # Playwright follows redirects silently. Re-validate the final URL
            # against the SSRF blocklist (initial URL was already checked).
            validate_browser_url(
                page.url,
                egress_attestation=egress_attestation,
            )
            if desktop_blocks:
                blocked = desktop_blocks[0]
                raise ValueError(t("tools.common.blocked_browser_request", url=blocked['url'], error=blocked['error']))

            # Performance metrics
            perf = page.evaluate("""
                () => {
                    const nav = performance.getEntriesByType('navigation')[0];
                    return {
                        ttfb: nav ? nav.responseStart : null,
                        domContentLoaded: nav ? nav.domContentLoadedEventEnd : null,
                    };
                }
            """)
            if perf.get("ttfb"):
                result["performance"]["ttfb_ms"] = round(perf["ttfb"])
            if perf.get("domContentLoaded"):
                result["performance"]["dom_content_loaded_ms"] = round(perf["domContentLoaded"])

            # CLS
            cls = page.evaluate("""
                () => new Promise(resolve => {
                    let clsValue = 0;
                    new PerformanceObserver(list => {
                        for (const entry of list.getEntries()) {
                            if (!entry.hadRecentInput) clsValue += entry.value;
                        }
                        resolve(clsValue);
                    }).observe({type: 'layout-shift', buffered: true});
                    setTimeout(() => resolve(clsValue), 3000);
                })
            """)
            result["performance"]["cls"] = round(cls, 4) if cls is not None else None

            # Content analysis
            result["content"]["title"] = page.title()

            h1 = page.query_selector("h1")
            if h1:
                result["content"]["h1"] = h1.text_content().strip()

            meta_desc = page.query_selector('meta[name="description"]')
            if meta_desc:
                result["content"]["meta_description"] = meta_desc.get_attribute("content")

            result["content"]["word_count"] = page.evaluate(
                "() => document.body.innerText.split(/\\s+/).filter(w => w.length > 0).length"
            )

            # CTA above fold
            cta_selectors = [
                "a[href*='signup']", "a[href*='register']", "a[href*='contact']",
                "a[href*='demo']", "a[href*='trial']", "a[href*='buy']",
                "button:has-text('Get Started')", "button:has-text('Sign Up')",
                "button:has-text('Buy Now')", "button:has-text('Contact')",
                "button:has-text('Free Trial')", "button:has-text('Book')",
                ".cta", "[class*='cta']",
            ]
            for selector in cta_selectors:
                try:
                    cta = page.query_selector(selector)
                    if cta:
                        box = cta.bounding_box()
                        if box and box["y"] < 1080:
                            result["conversion"]["cta_above_fold"] = True
                            break
                except Exception:
                    pass

            # Form analysis
            forms = page.query_selector_all("form")
            if forms:
                result["conversion"]["form_present"] = True
                inputs = page.query_selector_all("form input:not([type='hidden']):not([type='submit'])")
                result["conversion"]["form_fields"] = len(inputs)

            # Phone number
            result["conversion"]["phone_number"] = page.query_selector("a[href^='tel:']") is not None

            # Chat widget
            chat_selectors = [
                "[class*='chat']", "[id*='chat']", "[class*='intercom']",
                "[class*='drift']", "[class*='hubspot']", "[class*='zendesk']",
            ]
            for sel in chat_selectors:
                try:
                    if page.query_selector(sel):
                        result["conversion"]["chat_widget"] = True
                        break
                except Exception:
                    pass

            # Trust signals
            page_text = page.evaluate("() => document.body.innerText.toLowerCase()")
            result["trust"]["testimonials"] = any(k in page_text for k in ["testimonial", "customer said", "what our"])
            result["trust"]["trust_badges"] = any(k in page_text for k in ["trusted by", "as seen", "certified", "award"])

            # Schema markup
            schemas = page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                    const types = [];
                    scripts.forEach(s => {
                        try {
                            const data = JSON.parse(s.textContent);
                            if (data['@type']) types.push(data['@type']);
                            if (Array.isArray(data['@graph'])) {
                                data['@graph'].forEach(item => { if (item['@type']) types.push(item['@type']); });
                            }
                        } catch(e) {}
                    });
                    return types;
                }
            """)
            result["schema"]["types_found"] = schemas
            result["schema"]["product_schema"] = "Product" in schemas
            result["schema"]["faq_schema"] = "FAQPage" in schemas
            result["schema"]["service_schema"] = "Service" in schemas
            result["trust"]["reviews_schema"] = "Review" in schemas or "AggregateRating" in schemas

            desktop.close()

            # Mobile analysis
            mobile, mobile_blocks = create_guarded_browser_context(
                browser,
                viewport={"width": 375, "height": 812},
                egress_attestation=egress_attestation,
            )
            page = mobile.new_page()
            page.goto(url, wait_until="networkidle", timeout=timeout)
            validate_browser_url(
                page.url,
                egress_attestation=egress_attestation,
            )
            if mobile_blocks:
                blocked = mobile_blocks[0]
                raise ValueError(t("tools.common.blocked_browser_request", url=blocked['url'], error=blocked['error']))

            # LCP on mobile viewport (G59 = mobile speed)
            lcp = page.evaluate("""
                () => new Promise(resolve => {
                    new PerformanceObserver(list => {
                        const entries = list.getEntries();
                        resolve(entries.length > 0 ? entries[entries.length - 1].startTime : null);
                    }).observe({type: 'largest-contentful-paint', buffered: true});
                    setTimeout(() => resolve(null), 3000);
                })
            """)
            if lcp:
                result["performance"]["lcp_ms"] = round(lcp)

            result["mobile"]["viewport_meta"] = page.query_selector('meta[name="viewport"]') is not None

            scroll_width = page.evaluate("document.documentElement.scrollWidth")
            viewport_width = page.evaluate("window.innerWidth")
            result["mobile"]["horizontal_scroll"] = scroll_width > viewport_width

            base_font = page.evaluate(
                "() => parseFloat(window.getComputedStyle(document.body).fontSize)"
            )
            result["mobile"]["font_readable"] = base_font >= 16

            mobile.close()
            browser.close()

    except PlaywrightTimeout:
        result["error"] = t("tools.common.page_timeout", timeout=timeout)
    except Exception as e:
        result["error"] = t("tools.common.external_error", error=sanitize_error(e))

    return result


def grade_landing(result: dict) -> dict:
    """Grade landing page quality based on ad audit criteria."""
    if result.get("error"):
        raise ValueError(t("tools.landing.cannot_grade"))

    grades = {}

    # G59: Mobile speed (LCP)
    lcp = result["performance"].get("lcp_ms")
    if lcp:
        if lcp < 2500:
            grades["G59_mobile_speed"] = "PASS"
        elif lcp < 4000:
            grades["G59_mobile_speed"] = "WARNING"
        else:
            grades["G59_mobile_speed"] = "FAIL"

    # G60: Landing page relevance (H1 present)
    grades["G60_relevance"] = "PASS" if result["content"]["h1"] else "FAIL"

    # G61: Schema markup (Product/FAQ/Service per google-audit.md)
    has_relevant_schema = (
        result["schema"]["product_schema"]
        or result["schema"]["faq_schema"]
        or result["schema"]["service_schema"]
    )
    grades["G61_schema"] = "PASS" if has_relevant_schema else "FAIL"

    # CTA above fold
    grades["cta_above_fold"] = "PASS" if result["conversion"]["cta_above_fold"] else "FAIL"

    # Mobile responsive
    has_viewport = result["mobile"]["viewport_meta"]
    no_scroll = not result["mobile"]["horizontal_scroll"]
    grades["mobile_responsive"] = "PASS" if has_viewport and no_scroll else "FAIL"

    # Form friction (for lead gen)
    if result["conversion"]["form_present"]:
        fields = result["conversion"]["form_fields"]
        if fields <= 5:
            grades["form_friction"] = "PASS"
        elif fields <= 8:
            grades["form_friction"] = "WARNING"
        else:
            grades["form_friction"] = "FAIL"

    return grades


def _display_value(value):
    """Localize missing human-readable values, never page text or JSON data."""
    return t("tools.landing.null_value") if value is None else value


def main(argv: list[str] | None = None) -> int:
    with locale_scope(cli_locale(argv)):
        try:
            return _main(argv)
        except (OSError, ValueError, RuntimeError) as exc:
            print(t("tools.common.error", error=sanitize_error(exc)), file=sys.stderr)
            return 1


def _main(argv: list[str] | None) -> int:
    parser = LocaleArgumentParser(description=t("tools.landing.description"))
    parser.add_argument("url", help=t("tools.landing.url_help"))
    parser.add_argument("--timeout", "-t", type=int, default=30000, help=t("tools.common.timeout_ms_help"))
    parser.add_argument("--json", "-j", action="store_true", help=t("tools.landing.json_help"))
    parser.add_argument(
        "--egress-attestation",
        help=t("tools.common.egress_help"),
    )

    args = parser.parse_args(argv)
    try:
        egress_attestation = (
            load_egress_sandbox_attestation(args.egress_attestation)
            if args.egress_attestation
            else None
        )
    except ValueError as exc:
        print(t("tools.common.error", error=sanitize_error(exc)), file=sys.stderr)
        return 1
    result = analyze_landing(
        args.url,
        timeout=args.timeout,
        egress_attestation=egress_attestation,
    )
    if result.get("error"):
        error = sanitize_error(result["error"])
        if args.json:
            print(json.dumps({**result, "error": error}, indent=2, ensure_ascii=False))
        print(t("tools.common.error", error=error), file=sys.stderr)
        return 1

    grades = grade_landing(result)

    if args.json:
        output = {**result, "grades": grades}
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(t("tools.landing.title"))
        print("=" * 50)
        print(t("tools.landing.url", url=result['url']))

        print(t("tools.landing.performance"))
        lcp = result["performance"]["lcp_ms"]
        lcp_status = t("tools.landing.good") if lcp and lcp < 2500 else t("tools.landing.slow") if lcp else t("tools.landing.not_available")
        print(t("tools.landing.lcp", value=_display_value(lcp), status=lcp_status))
        cls = result["performance"]["cls"]
        cls_status = t("tools.landing.good") if cls is not None and cls < 0.1 else t("tools.landing.poor") if cls else t("tools.landing.not_available")
        print(t("tools.landing.cls", value=_display_value(cls), status=cls_status))
        print(t("tools.landing.ttfb", value=_display_value(result['performance']['ttfb_ms'])))

        print(t("tools.landing.content"))
        print(t("tools.landing.page_title", title=_display_value(result['content']['title'])))
        print(t("tools.landing.h1", heading=result['content']['h1'] or t("tools.landing.missing")))
        print(t("tools.landing.words", count=result['content']['word_count']))

        print(t("tools.landing.conversion"))
        print(t("tools.landing.cta", present=t("tools.landing.yes") if result['conversion']['cta_above_fold'] else t("tools.landing.no")))
        print(t("tools.landing.form", present=t("tools.landing.form_fields", count=result['conversion']['form_fields']) if result['conversion']['form_present'] else t("tools.landing.no")))
        print(t("tools.landing.phone", present=t("tools.landing.yes") if result['conversion']['phone_number'] else t("tools.landing.no")))
        print(t("tools.landing.chat", present=t("tools.landing.yes") if result['conversion']['chat_widget'] else t("tools.landing.no")))

        print(t("tools.landing.schema", types=', '.join(result['schema']['types_found']) or t("tools.landing.none")))

        print(t("tools.landing.grades"))
        for check, grade in grades.items():
            print(f"  [{t('tools.landing.grade.' + grade)}] {check}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
