#!/usr/bin/env python3
"""Verify a native pip report and downloaded wheel closure against reviewed evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
from pathlib import Path
import subprocess
import sys

# Source checkouts and installed skills both keep core beside scripts/.
_CORE_PARENT = str(Path(__file__).resolve().parents[1])
if _CORE_PARENT not in sys.path:
    sys.path.insert(0, _CORE_PARENT)
from claude_ads_core.cli_support import LocaleArgumentParser, cli_locale
from claude_ads_core.i18n import locale_scope, t

_RELEASE_SPEC = importlib.util.spec_from_file_location("claude_ads_target_release", Path(__file__).with_name("release.py"))
if _RELEASE_SPEC is None or _RELEASE_SPEC.loader is None:  # pragma: no cover
    raise RuntimeError(t('maintenance.verify_target_lock.cannot_load_the_release_verifier'))
release = importlib.util.module_from_spec(_RELEASE_SPEC)
sys.modules[_RELEASE_SPEC.name] = release
_RELEASE_SPEC.loader.exec_module(release)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_target_id(profile: str) -> str:
    if sys.implementation.name != "cpython" or sys.version_info[:2] not in {(3, 11), (3, 12)}:
        raise release.ReleaseError(t('maintenance.verify_target_lock.native_lock_evidence_requires_cpython_3_11_or_3_12'))
    system = platform.system().lower()
    machine = platform.machine().lower()
    machine = {"amd64": "x86_64", "aarch64": "arm64"}.get(machine, machine)
    if system == "linux" and machine == "x86_64":
        libc_name, libc_version = platform.libc_ver()
        try:
            libc_ok = libc_name == "glibc" and tuple(map(int, libc_version.split(".")[:2])) >= (2, 17)
        except ValueError:
            libc_ok = False
        if not libc_ok:
            raise release.ReleaseError(t('maintenance.verify_target_lock.native_linux_lock_evidence_requires_glibc_2_17_musl_is_unsupported'))
        target = "linux"
    elif system == "darwin" and machine in {"arm64", "x86_64"}:
        target = "macos-arm" if machine == "arm64" else "macos-x86"
    elif system == "windows" and machine == "x86_64":
        target = "windows"
    else:
        raise release.ReleaseError(t('maintenance.verify_target_lock.no_reviewed_native_lock_target_for', v0=system, v1=machine))
    return f"{profile}-{target}-cp{sys.version_info.major}{sys.version_info.minor}"


def verify(root: Path, profile: str, pip_report: Path, wheel_dir: Path, output: Path) -> None:
    inventory = release._load_dependency_inventory(root)
    target_id = native_target_id(profile)
    target = next(item for item in inventory["targets"] if item["id"] == target_id)
    expected = {item["name"]: item for item in target["components"]}

    report_data = pip_report.read_bytes()
    report = json.loads(report_data)
    try:
        from pip import __version__ as executing_pip_version
    except ImportError as exc:
        raise release.ReleaseError(t('maintenance.verify_target_lock.pip_is_required_for_native_target_verification')) from exc
    if report.get("pip_version") != executing_pip_version:
        raise release.ReleaseError(t('maintenance.verify_target_lock.pip_report_version_does_not_equal_the_executing_resolver'))
    observed = {}
    for item in report.get("install", []):
        metadata = item.get("metadata", {})
        name = release._canonical_package_name(str(metadata.get("name", "")))
        download = item.get("download_info", {})
        hashes = download.get("archive_info", {}).get("hashes", {})
        record = expected.get(name)
        if record is None or name in observed:
            raise release.ReleaseError(t('maintenance.verify_target_lock.pip_report_contains_duplicate_or_unexpected_component', v0=name))
        artifact = record["artifact"]
        if (
            str(metadata.get("version")) != record["version"]
            or download.get("url") != artifact["url"]
            or hashes.get("sha256") != artifact["sha256"]
        ):
            raise release.ReleaseError(t('maintenance.verify_target_lock.pip_report_artifact_mismatch', v0=target_id, v1=name))
        observed[name] = {
            "name": name, "version": record["version"], "filename": artifact["filename"],
            "url": artifact["url"], "sha256": artifact["sha256"],
        }
    if set(observed) != set(expected):
        raise release.ReleaseError(t('maintenance.verify_target_lock.pip_report_closure_mismatch_missing', v0=sorted(set(expected) - set(observed))))

    wheels = {path.name: sha256(path) for path in wheel_dir.glob("*.whl") if path.is_file()}
    expected_wheels = {item["artifact"]["filename"]: item["artifact"]["sha256"] for item in expected.values()}
    if wheels != expected_wheels:
        raise release.ReleaseError(t('maintenance.verify_target_lock.downloaded_wheel_filenames_hashes_do_not_equal_the_target_inventory'))

    evidence_path = root / "control-plane/dependency-evidence" / f"{target_id}.json"
    inventory_path = root / "control-plane/manifests/dependency-inventory.json"
    lock_path = root / ("requirements.lock" if profile == "runtime" else "requirements-dev.lock")
    commit_result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=False, capture_output=True, text=True)
    if commit_result.returncode:
        raise release.ReleaseError(t('maintenance.verify_target_lock.cannot_bind_native_target_evidence_to_a_git_commit'))
    attestation = {
        "schema_version": "1.0.0",
        "evidence_class": "native-pip-report-and-downloaded-wheel-confirmation",
        "target_id": target_id,
        "environment": {
            "implementation": platform.python_implementation(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "platform": platform.platform(),
            "machine": platform.machine(),
            "libc": list(platform.libc_ver()),
            "runner": {name: os.environ[name] for name in ("ImageOS", "ImageVersion", "RUNNER_OS", "RUNNER_ARCH") if name in os.environ},
        },
        "source_commit": commit_result.stdout.strip(),
        "dependency_inventory_sha256": sha256(inventory_path),
        "requirements_lock_sha256": sha256(lock_path),
        "pip_version": executing_pip_version,
        "pip_report_sha256": hashlib.sha256(report_data).hexdigest(),
        "normalized_evidence_sha256": sha256(evidence_path),
        "components": [observed[name] for name in sorted(observed)],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(attestation, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    with locale_scope(cli_locale(argv)):
        return _main(argv)


def _main(argv: list[str] | None = None) -> int:
    parser = LocaleArgumentParser(description=t("maintenance.verify_target_lock.description"))
    parser.add_argument("--profile", choices=("runtime", "development"), required=True, help=t("maintenance.verify_target_lock.profile_help"))
    parser.add_argument("--pip-report", type=Path, required=True, help=t("maintenance.common.pip_report_help"))
    parser.add_argument("--wheel-dir", type=Path, required=True, help=t("maintenance.verify_target_lock.wheel_dir_help"))
    parser.add_argument("--output", type=Path, required=True, help=t("maintenance.common.output_help"))
    args = parser.parse_args(argv)
    try:
        verify(Path(__file__).resolve().parents[1], args.profile, args.pip_report, args.wheel_dir, args.output)
    except (OSError, ValueError, json.JSONDecodeError, release.ReleaseError) as exc:
        print(t('maintenance.verify_target_lock.target_lock_verification_failed', v0=exc), file=sys.stderr)
        return 1
    print(t('maintenance.verify_target_lock.verified_native_target_lock', v0=native_target_id(args.profile)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
