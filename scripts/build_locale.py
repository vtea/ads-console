#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from claude_ads_core.i18n import validate_catalogs


PROTECTED = {"THIRD_PARTY_NOTICES.md", "tests/fixtures/reports/sanitized-report.md"}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_path(root: Path, relative: str) -> Path:
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts or "\\" in relative:
        raise ValueError(f"语言包路径无效：{relative}")
    destination = root.joinpath(*path.parts)
    for parent in (destination, *destination.parents):
        if parent.is_symlink():
            raise ValueError(f"语言包路径不能为符号链接：{relative}")
        if parent == root:
            break
    if not destination.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"语言包路径越界：{relative}")
    return destination


def _document_path(root: Path, relative: str) -> Path:
    path = PurePosixPath(relative)
    if path.suffix != ".md" or (len(path.parts) > 1 and path.parts[0] not in {"ads", "skills", "agents", "control-plane", "tests", ".github"}):
        raise ValueError(f"语言清单包含非受管文档：{relative}")
    return _safe_path(root, relative)


def _fences(text: str) -> list[tuple[str, str]]:
    return re.findall(r"(?m)^(`{3,}|~{3,})[^\n]*\n([\s\S]*?)^\1\s*$", text)


def _links(text: str) -> set[str]:
    return set(re.findall(r"\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)", text))


def _anchors(text: str) -> set[str]:
    anchors = set(re.findall(r'<a\s+(?:name|id)=[\"\']([^\"\']+)[\"\']', text))
    seen: dict[str, int] = {}
    for heading in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", text):
        heading = re.sub(r"<[^>]*>", "", heading)
        base = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        suffix = seen.get(base, 0)
        seen[base] = suffix + 1
        anchors.add(base if not suffix else f"{base}-{suffix}")
    return anchors


def inspect_documents(root: Path, *, check_views: bool = True) -> tuple[list[str], list[tuple[Path, bytes]]]:
    package = root / "claude_ads_core" / "locales"
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    planned: list[tuple[Path, bytes]] = []
    paths: set[str] = set()
    translations: dict[str, str] = {}
    entries = manifest["documents"]
    current_paths = {path.name for path in root.glob("*.md") if path.is_file()}
    for directory in ("ads", "skills", "agents", "control-plane", "tests", ".github"):
        current_paths.update(path.relative_to(root).as_posix() for path in (root / directory).rglob("*.md") if path.is_file())
    declared = {entry["path"] for entry in entries}
    for relative in sorted(current_paths - declared):
        errors.append(f"新增文档尚未纳入语言包：{relative}")
    for relative in sorted(declared - current_paths):
        errors.append(f"文档被删除或改名，需更新语言清单：{relative}")
    for entry in entries:
        relative = entry["path"]
        if relative in paths:
            errors.append(f"文档重复：{relative}")
            continue
        paths.add(relative)
        source = _document_path(package / "en" / "documents", relative)
        target = _document_path(package / "zh-CN" / "documents", relative)
        view = _document_path(root, relative)
        if not source.is_file() or _digest(source) != entry["source_sha256"]:
            errors.append(f"英文源发生变更，需复核译文：{relative}")
            continue
        if not target.is_file():
            errors.append(f"缺少中文译文：{relative}")
            continue
        source_text = source.read_text(encoding="utf-8")
        text = target.read_text(encoding="utf-8")
        translations[relative] = text
        if not re.search(r"[㐀-鿿]", text):
            errors.append(f"译文没有中文：{relative}")
        for _, block in _fences(source_text):
            if block not in text:
                errors.append(f"原始代码块被改动：{relative}")
                break
        for identifier in re.findall(r"(?m)^(?:name|tools|model):.+$", source_text):
            if identifier not in text:
                errors.append(f"入口标识被改动：{relative} ({identifier.split(':')[0]})")
        if relative in PROTECTED:
            if view.exists() and _digest(view) != entry["source_sha256"]:
                errors.append(f"受保护的法律原文发生变更：{relative}")
            continue
        data = target.read_bytes()
        if check_views and (not view.is_file() or view.read_bytes() != data):
            errors.append(f"中文视图未同步：{relative}")
        if view.is_file() and view.read_bytes() not in (source.read_bytes(), data):
            if not check_views and _digest(view) != entry.get("generated_sha256"):
                errors.append(f"视图存在本地改动，请先合并到语言包：{relative}")
        planned.append((view, data))
    for relative, text in translations.items():
        for link in _links(text):
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or link.startswith("$"):
                continue
            logical = (root / relative).parent / unquote(parsed.path) if parsed.path else root / relative
            resolved = logical.resolve()
            if not resolved.is_relative_to(root.resolve()):
                errors.append(f"文档链接越界：{relative} -> {link}")
                continue
            target_relative = resolved.relative_to(root.resolve()).as_posix()
            if target_relative not in translations and not resolved.exists():
                errors.append(f"文档链接不存在：{relative} -> {link}")
            if parsed.fragment and target_relative in translations:
                if unquote(parsed.fragment) not in _anchors(translations[target_relative]):
                    errors.append(f"中文锚点不存在：{relative} -> {link}")
    return errors, planned


def inspect_metadata(root: Path, *, check_views: bool = True) -> tuple[list[str], list[tuple[Path, bytes]]]:
    resources_root = root / "claude_ads_core" / "locales"
    english = json.loads((resources_root / "en/messages.json").read_text(encoding="utf-8"))
    chinese = json.loads((resources_root / "zh-CN/messages.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    planned: list[tuple[Path, bytes]] = []
    for relative, fields in (
        (".claude-plugin/plugin.json", [("description", "metadata.plugin_description")]),
        (".claude-plugin/marketplace.json", [("metadata.description", "metadata.marketplace_description"), ("plugins.0.description", "metadata.marketplace_plugin_description")]),
    ):
        path = _safe_path(root, relative)
        document = json.loads(path.read_text(encoding="utf-8"))
        for dotted, key in fields:
            parts = dotted.split(".")
            parent = document
            for part in parts[:-1]:
                parent = parent[int(part)] if isinstance(parent, list) else parent[part]
            if parent[parts[-1]] not in (english[key], chinese[key]):
                errors.append(f"发现元数据有未合并修改：{relative} {dotted}")
            parent[parts[-1]] = chinese[key]
        data = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if check_views and data != path.read_bytes():
            errors.append(f"中文元数据未同步：{relative}")
        planned.append((path, data))
    path = _safe_path(root, "ads/agents/openai.yaml")
    text = path.read_text(encoding="utf-8")
    for field, key in (("short_description", "metadata.short_description"), ("default_prompt", "metadata.default_prompt")):
        text = re.sub(rf"(?m)^  {field}:.*$", f"  {field}: " + json.dumps(chinese[key], ensure_ascii=False), text)
    data = text.encode("utf-8")
    if check_views and data != path.read_bytes():
        errors.append("中文元数据未同步：ads/agents/openai.yaml")
    planned.append((path, data))
    return errors, planned


def inspect_installer_messages(root: Path, *, check_views: bool = True) -> tuple[list[str], list[tuple[Path, bytes]]]:
    start = "# BEGIN GENERATED INSTALLER MESSAGES"
    end = "# END GENERATED INSTALLER MESSAGES"
    messages = {
        locale: json.loads((root / "claude_ads_core/locales" / locale / "installer.json").read_text(encoding="utf-8"))
        for locale in ("en", "zh-CN")
    }
    errors: list[str] = []
    if messages["en"].keys() != messages["zh-CN"].keys():
        return ["安装文案键不一致"], []
    shell = [start, "# Generated from claude_ads_core/locales/{en,zh-CN}/installer.json. Do not edit.",
             "locale_template() {", '    case "$CLAUDE_ADS_SELECTED_LOCALE:$1" in']
    powershell = [start, "# Generated from claude_ads_core/locales/{en,zh-CN}/installer.json. Do not edit.",
                  "function Get-LocaleTemplate([string]$Key) {", '    switch -CaseSensitive ("${script:SelectedLocale}:$Key") {']
    for locale, entries in messages.items():
        for key in sorted(entries):
            value = entries[key]
            if not re.fullmatch(r"installer\.[a-z_]+", key) or not isinstance(value, str):
                raise ValueError("安装语言资源格式无效")
            shell.append("        " + locale + ":" + key + ") LOCALE_TEMPLATE='" + value.replace("'", "'\"'\"'") + "' ;;")
            powershell.append("        '" + locale + ":" + key + "' { return '" + value.replace("'", "''") + "' }")
    shell.extend(["        *) return 1 ;;", "    esac", "}", end])
    powershell.extend(["        default { throw ('installer.unknown_key: ' + $Key) }", "    }", "}", end])
    planned: list[tuple[Path, bytes]] = []
    for filename in ("install.sh", "uninstall.sh", "install.ps1", "uninstall.ps1"):
        path = _safe_path(root, filename)
        text = path.read_text(encoding="utf-8-sig")
        if text.count(start) != 1 or text.count(end) != 1:
            errors.append(f"安装脚本文案边界缺失或重复：{filename}")
            continue
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        block = "\n".join(shell if filename.endswith(".sh") else powershell)
        data = (before + block + after).encode("utf-8-sig" if filename.endswith(".ps1") else "utf-8")
        if check_views and data != path.read_bytes():
            errors.append(f"安装文案未同步：{filename}")
        planned.append((path, data))
    return errors, planned


def inspect_guidance(root: Path) -> list[str]:
    path = root / "claude_ads_core/locales/en/guidance.json"
    entries = json.loads(path.read_text(encoding="utf-8"))
    documents: dict[str, object] = {}
    errors: list[str] = []
    for key, source in entries.items():
        relative, pointer = key.removeprefix("guidance.").split("#", 1)
        if relative not in documents:
            documents[relative] = json.loads(_safe_path(root, relative).read_text(encoding="utf-8"))
        value = documents[relative]
        try:
            for part in pointer.split("/")[1:]:
                part = part.replace("~1", "/").replace("~0", "~")
                value = value[int(part)] if isinstance(value, list) else value[part]
            if value != source:
                errors.append(f"说明原文已变更，需复核译文：{key}")
        except (KeyError, IndexError, TypeError, ValueError):
            errors.append(f"说明原文路径已变更：{key}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成或检查独立中文语言包及文档视图")
    parser.add_argument("--check", action="store_true", help="只检查，不写入文件")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="仓库根目录")
    args = parser.parse_args(argv)
    try:
        errors, planned = inspect_documents(args.root.resolve(), check_views=args.check)
        document_count = len(planned)
        metadata_errors, metadata_plan = inspect_metadata(args.root.resolve(), check_views=args.check)
        errors.extend(metadata_errors)
        planned.extend(metadata_plan)
        installer_errors, installer_plan = inspect_installer_messages(args.root.resolve(), check_views=args.check)
        errors.extend(installer_errors)
        planned.extend(installer_plan)
        errors.extend(validate_catalogs())
        errors.extend(inspect_guidance(args.root.resolve()))
    except (OSError, ValueError, KeyError) as exc:
        print(f"语言包检查失败：{exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    if not args.check:
        for destination, data in planned:
            destination.write_bytes(data)
        manifest_path = args.root / "claude_ads_core/locales/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["documents"]:
            if entry["path"] not in PROTECTED:
                entry["generated_sha256"] = _digest(args.root / entry["path"])
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "valid", "documents": document_count, "generated_files": len(planned), "locale": "zh-CN", "mode": "check" if args.check else "build"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
