#!/usr/bin/env python3
"""Validate an actual managed install and write its target-bound receipt."""

from __future__ import annotations

import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import sys

# Source checkouts and installed skills both keep core beside scripts/.
_CORE_PARENT = str(Path(__file__).resolve().parents[1])
if _CORE_PARENT not in sys.path:
    sys.path.insert(0, _CORE_PARENT)
from claude_ads_core.cli_support import LocaleArgumentParser, cli_locale
from claude_ads_core.i18n import locale_scope, t


EXPECTED_INVENTORY_SHA256 = "48ed1cdd3023bdb9781e7ffe9d987fb9425cc23e2dea053e2da5e8d461e588de"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: str) -> str:
    return value.lower().replace("_", "-").replace(".", "-")


def write_receipt(inventory_path: Path, lock_path: Path, evidence_path: Path, report_path: Path, target_id: str, output: Path) -> None:
    if digest(inventory_path) != EXPECTED_INVENTORY_SHA256:
        raise ValueError(t('maintenance.write_install_receipt.dependency_inventory_is_not_the_reviewed_document'))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    target = next((item for item in inventory["targets"] if item["id"] == target_id), None)
    if target is None or target["profile"] != "runtime":
        raise ValueError(t('maintenance.write_install_receipt.unknown_runtime_target'))
    if digest(evidence_path) != target["resolution_evidence_sha256"]:
        raise ValueError(t('maintenance.write_install_receipt.target_evidence_binding_mismatch'))
    expected = {item["name"]: item for item in target["components"]}
    report_data = report_path.read_bytes()
    report = json.loads(report_data)
    pip_version = metadata.version("pip")
    if report.get("pip_version") != pip_version:
        raise ValueError(t('maintenance.write_install_receipt.pip_report_resolver_version_mismatch'))
    selected = {}
    for item in report.get("install", []):
        name = canonical(item.get("metadata", {}).get("name", ""))
        component = expected.get(name)
        download = item.get("download_info", {})
        if component is None or name in selected:
            raise ValueError(t('maintenance.write_install_receipt.unexpected_or_duplicate_installed_component', v0=name))
        artifact = component["artifact"]
        if item["metadata"].get("version") != component["version"] or download.get("url") != artifact["url"] or download.get("archive_info", {}).get("hashes", {}).get("sha256") != artifact["sha256"]:
            raise ValueError(t('maintenance.write_install_receipt.installed_artifact_mismatch', v0=name))
        if metadata.version(name) != component["version"]:
            raise ValueError(t('maintenance.write_install_receipt.installed_version_mismatch', v0=name))
        selected[name] = {"name": name, "version": component["version"], "artifact": artifact}
    if set(selected) != set(expected):
        raise ValueError(t('maintenance.write_install_receipt.installed_closure_does_not_equal_the_target_inventory'))
    installed = {
        canonical(distribution.metadata.get("Name", "")): distribution.version
        for distribution in metadata.distributions()
        if distribution.metadata.get("Name")
    }
    bootstrap = {"pip", "setuptools", "wheel"}
    unexpected = sorted(set(installed) - set(expected) - bootstrap)
    missing = sorted(set(expected) - set(installed))
    if unexpected or missing:
        raise ValueError(
            t('maintenance.write_install_receipt.managed_environment_closure_mismatch_missing_unexpected', v0=missing, v1=unexpected)
        )
    for name, component in expected.items():
        if installed[name] != component["version"]:
            raise ValueError(t('maintenance.write_install_receipt.managed_environment_version_mismatch', v0=name))
    receipt = {
        "schema_version": "1.0.0", "receipt_class": "managed-python-runtime-install",
        "target_id": target_id, "target": {key: target[key] for key in ("python_version", "implementation", "os", "arch", "abi")},
        "resolver": "pip / PyPI", "python_full_version": platform.python_version(), "pip_version": pip_version,
        "requirements_lock_sha256": digest(lock_path), "dependency_inventory_sha256": digest(inventory_path),
        "target_evidence_sha256": digest(evidence_path), "pip_install_report_sha256": hashlib.sha256(report_data).hexdigest(),
        "components": [selected[name] for name in sorted(selected)],
    }
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(output)


def main(argv: list[str] | None = None) -> int:
    with locale_scope(cli_locale(argv)):
        return _main(argv)


def _main(argv: list[str] | None = None) -> int:
    parser = LocaleArgumentParser(description=t("maintenance.write_install_receipt.description"))
    parser.add_argument("--inventory", type=Path, required=True, help=t("maintenance.write_install_receipt.inventory_help"))
    parser.add_argument("--lock", type=Path, required=True, help=t("maintenance.write_install_receipt.lock_help"))
    parser.add_argument("--evidence", type=Path, required=True, help=t("maintenance.write_install_receipt.evidence_help"))
    parser.add_argument("--pip-report", type=Path, required=True, help=t("maintenance.common.pip_report_help"))
    parser.add_argument("--target-id", required=True, help=t("maintenance.write_install_receipt.target_help"))
    parser.add_argument("--output", type=Path, required=True, help=t("maintenance.common.output_help"))
    args = parser.parse_args(argv)
    try:
        write_receipt(
            args.inventory,
            args.lock,
            args.evidence,
            args.pip_report,
            args.target_id,
            args.output,
        )
    except Exception as exc:
        print(t('maintenance.write_install_receipt.install_receipt_validation_failed', v0=exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
