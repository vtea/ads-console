#!/usr/bin/env python3
"""Verify a completed managed installer result on its native host."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

# Source checkouts and installed skills both keep core beside scripts/.
_CORE_PARENT = str(Path(__file__).resolve().parents[1])
if _CORE_PARENT not in sys.path:
    sys.path.insert(0, _CORE_PARENT)
from claude_ads_core.cli_support import LocaleArgumentParser, cli_locale
from claude_ads_core.i18n import locale_scope, t


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _target_id() -> str:
    if sys.implementation.name != "cpython" or sys.version_info[:2] not in {(3, 11), (3, 12)}:
        raise ValueError(t('maintenance.verify_managed_install.managed_install_verification_requires_cpython_3_11_or_3_12'))
    system = platform.system().lower()
    machine = platform.machine().lower()
    machine = {"amd64": "x86_64", "aarch64": "arm64"}.get(machine, machine)
    if system == "linux" and machine == "x86_64":
        platform_id = "linux"
    elif system == "darwin" and machine in {"x86_64", "arm64"}:
        platform_id = "macos-x86" if machine == "x86_64" else "macos-arm"
    elif system == "windows" and machine == "x86_64":
        platform_id = "windows"
    else:
        raise ValueError(t('maintenance.verify_managed_install.no_managed_install_target_for', v0=system, v1=machine))
    return f"runtime-{platform_id}-cp{sys.version_info.major}{sys.version_info.minor}"


def verify(repository: Path, skill_dir: Path) -> dict[str, object]:
    receipt_path = skill_dir / "managed-runtime-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    expected_fields = {
        "schema_version", "receipt_class", "target_id", "target", "resolver",
        "python_full_version", "pip_version", "requirements_lock_sha256",
        "dependency_inventory_sha256", "target_evidence_sha256",
        "pip_install_report_sha256", "components",
    }
    if not isinstance(receipt, dict) or set(receipt) != expected_fields:
        raise ValueError(t('maintenance.verify_managed_install.managed_runtime_receipt_fields_mismatch'))
    if receipt.get("schema_version") != "1.0.0" or receipt.get("receipt_class") != "managed-python-runtime-install":
        raise ValueError(t('maintenance.verify_managed_install.managed_runtime_receipt_identity_mismatch'))
    target_id = _target_id()
    if receipt.get("target_id") != target_id or receipt.get("resolver") != "pip / PyPI":
        raise ValueError(t('maintenance.verify_managed_install.managed_runtime_receipt_native_target_mismatch'))
    components = receipt.get("components")
    if not isinstance(components, list) or len(components) != 33:
        raise ValueError(t('maintenance.verify_managed_install.managed_runtime_receipt_closure_mismatch'))
    if receipt.get("requirements_lock_sha256") != _sha256(repository / "requirements.lock"):
        raise ValueError(t('maintenance.verify_managed_install.managed_runtime_receipt_lock_binding_mismatch'))
    inventory_path = repository / "control-plane/manifests/dependency-inventory.json"
    if receipt.get("dependency_inventory_sha256") != _sha256(inventory_path):
        raise ValueError(t('maintenance.verify_managed_install.managed_runtime_receipt_inventory_binding_mismatch'))
    evidence_path = repository / "control-plane/dependency-evidence" / f"{target_id}.json"
    if receipt.get("target_evidence_sha256") != _sha256(evidence_path):
        raise ValueError(t('maintenance.verify_managed_install.managed_runtime_receipt_target_evidence_binding_mismatch'))

    python = skill_dir / ".venv" / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
    if not python.is_file():
        raise ValueError(t('maintenance.verify_managed_install.managed_runtime_interpreter_is_missing'))
    checks = (
        [str(python), "-m", "pip", "check"],
        [str(python), "-c", "import claude_ads_core; print(claude_ads_core.__version__)"],
    )
    for command in checks:
        result = subprocess.run(command, check=False, text=True, capture_output=True)
        if result.returncode:
            raise ValueError(t('maintenance.verify_managed_install.managed_runtime_execution_check_failed', v0=result.stderr.strip()))
    return receipt


def main(argv: list[str] | None = None) -> int:
    with locale_scope(cli_locale(argv)):
        return _main(argv)


def _main(argv: list[str] | None = None) -> int:
    parser = LocaleArgumentParser(description=t("maintenance.verify_managed_install.description"))
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1], help=t("maintenance.common.root_help"))
    parser.add_argument("--skill-dir", type=Path, required=True, help=t("maintenance.verify_managed_install.skill_dir_help"))
    args = parser.parse_args(argv)
    try:
        receipt = verify(args.repository.resolve(), args.skill_dir.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(t('maintenance.verify_managed_install.managed_install_verification_failed', v0=exc), file=sys.stderr)
        return 1
    print(t('maintenance.verify_managed_install.verified_managed_install', v0=receipt['target_id']))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
