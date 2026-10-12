"""Command-line interface for deterministic Claude Ads core operations."""

from __future__ import annotations

import argparse
from datetime import date
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from . import __version__
from .adapters import AdapterError, GenericCSVExportAdapter
from .contracts import CONTRACT_NAMES, ContractError, load_contract, validate_contract
from .cli_support import LocaleArgumentParser, cli_locale
from .i18n import locale_scope, t
from .errors import safe_error_text
from .reporting import ReportRenderError, write_report_bundle
from .product_status import ProductStatusError, evaluate_product_status
from .scoring import ScoringError, score_account, score_portfolio


def _read_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("core.io.load", path=path, exc=exc) from exc


def _emit(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = LocaleArgumentParser(prog="claude-ads-core")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help=t("core.cli.validate_help"))
    validate.add_argument("contract", choices=CONTRACT_NAMES, help=t("core.cli.contract_help"))
    validate.add_argument("path", help=t("core.cli.json_path_help"))

    score = commands.add_parser("score", help=t("core.cli.score_help"))
    score.add_argument("--controls", required=True, help=t("core.cli.controls_help"))
    score.add_argument("--findings", required=True, help=t("core.cli.findings_help"))
    score.add_argument("--weights", required=True, help=t("core.cli.weights_help"))

    portfolio = commands.add_parser("portfolio", help=t("core.cli.portfolio_help"))
    portfolio.add_argument("path", help=t("core.cli.portfolio_path_help"))

    status = commands.add_parser("status", help=t("core.cli.status_help"))
    status.add_argument("path", nargs="?", help=t("core.cli.status_path_help"))
    status.add_argument("--root", default=".", help=t("core.cli.repository_root_help"))
    status.add_argument("--as-of", help=t("core.cli.as_of_help"))
    status.add_argument("--release-gate", help=t("core.cli.release_gate_help"))

    next_command = commands.add_parser("next", help=t("core.cli.next_help"))
    next_command.add_argument("--root", default=".", help=t("core.cli.repository_root_help"))
    next_command.add_argument("--as-of", required=True, help=t("core.cli.as_of_help"))
    next_command.add_argument("--release-gate", help=t("core.cli.release_gate_help"))

    render = commands.add_parser(
        "render", aliases=["report"], help=t("core.cli.render_help"),
    )
    render.add_argument("path", help=t("core.cli.report_path_help"))
    render.add_argument("--format", choices=("markdown", "html", "pdf"), default="markdown", help=t("core.cli.format_help"))
    render.add_argument("--root", default=".claude-ads/runs", help=t("core.cli.output_root_help"))
    render.add_argument("--output", help=t("core.cli.output_help"))
    render.add_argument("--font", help=t("legacy_report.cli_font"))

    ingest = commands.add_parser("ingest-export", help=t("core.cli.ingest_help"))
    ingest.add_argument("--platform", required=True, help=t("core.cli.platform_help"))
    ingest.add_argument("path", help=t("core.cli.csv_path_help"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    with locale_scope(cli_locale(argv)):
        return _main(argv)


def _main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            load_contract(args.contract, args.path)
            _emit({"contract": args.contract, "path": args.path, "status": "valid"})
        elif args.command == "score":
            controls = _read_json(args.controls)
            findings = _read_json(args.findings)
            weights = _read_json(args.weights)
            if not isinstance(controls, list) or not isinstance(findings, list) or not isinstance(weights, dict):
                raise ScoringError("core.cli.scoring_shape")
            _emit(score_account(controls, findings, weights).to_dict())
        elif args.command == "portfolio":
            accounts = _read_json(args.path)
            if not isinstance(accounts, list):
                raise ScoringError("core.cli.portfolio_shape")
            _emit(score_portfolio(accounts).to_dict())
        elif args.command == "status":
            if args.path:
                bundle = _read_json(args.path)
                validate_contract("report-bundle", bundle)
                scoring = bundle["scoring"]
                manifest = bundle["run_manifest"]
                _emit(
                    {
                        "run_id": manifest["run_id"],
                        "completeness": manifest["completeness"],
                        "health_score": scoring["health_score"],
                        "evidence_coverage": scoring["evidence_coverage"],
                        "status": scoring["status"],
                    }
                )
            else:
                if not args.as_of:
                    raise ProductStatusError("core.cli.as_of_required")
                try:
                    as_of = date.fromisoformat(args.as_of)
                except ValueError as exc:
                    raise ProductStatusError("core.cli.as_of_invalid") from exc
                _emit(
                    evaluate_product_status(
                        args.root, as_of=as_of, release_gate_path=args.release_gate
                    )
                )
        elif args.command == "next":
            try:
                as_of = date.fromisoformat(args.as_of)
            except ValueError as exc:
                raise ProductStatusError("core.cli.as_of_invalid") from exc
            status_payload = evaluate_product_status(
                args.root, as_of=as_of, release_gate_path=args.release_gate
            )
            _emit(
                {
                    "schema_version": status_payload["schema_version"],
                    "as_of": status_payload["as_of"],
                    "selection_policy": status_payload["selection_policy"],
                    "next_blocker": status_payload["next_blocker"],
                }
            )
        elif args.command in {"render", "report"}:
            bundle = load_contract("report-bundle", args.path)
            extension = {"markdown": "md", "html": "html", "pdf": "pdf"}[args.format]
            destination = args.output or f"{bundle['run_manifest']['run_id']}/report.{extension}"
            output_path = write_report_bundle(bundle, args.format, args.root, destination, font=args.font)
            _emit(
                {
                    "format": args.format,
                    "path": str(output_path),
                    "run_id": bundle["run_manifest"]["run_id"],
                    "status": "rendered",
                }
            )
        elif args.command == "ingest-export":
            _emit(GenericCSVExportAdapter(args.platform).read_snapshot(args.path))
    except (AdapterError, ContractError, ProductStatusError, ReportRenderError, ScoringError) as exc:
        print(json.dumps({"status": "invalid", "error": safe_error_text(exc)}, sort_keys=True, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
