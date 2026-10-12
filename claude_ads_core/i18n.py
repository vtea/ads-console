from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
from importlib import resources
import json
import os
from string import Formatter
from typing import Iterator


DEFAULT_LOCALE = "zh-CN"
SUPPORTED_LOCALES = ("zh-CN", "en")
_current_locale: ContextVar[str | None] = ContextVar("claude_ads_locale", default=None)


class LocaleError(ValueError):
    pass


def resolve_locale(locale: str | None = None) -> str:
    selected = locale if locale is not None else (_current_locale.get() or os.environ.get("CLAUDE_ADS_LOCALE") or DEFAULT_LOCALE)
    if selected not in SUPPORTED_LOCALES:
        raise LocaleError("不支持的语言；请选择 zh-CN 或 en。")
    return selected


@contextmanager
def locale_scope(locale: str | None = None) -> Iterator[str]:
    selected = resolve_locale(locale)
    token = _current_locale.set(selected)
    try:
        yield selected
    finally:
        _current_locale.reset(token)


def _message_object(pairs: list[tuple[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in pairs:
        if key in result:
            raise LocaleError(f"语言资源键重复：{key}")
        result[key] = value
    return result


@lru_cache(maxsize=2)
def catalog(locale: str) -> dict[str, str]:
    directory = resources.files("claude_ads_core").joinpath("locales", resolve_locale(locale))
    messages: dict[str, str] = {}
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if path.name.endswith(".json"):
            entries = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_message_object)
            if not isinstance(entries, dict) or any(not isinstance(value, str) for value in entries.values()):
                raise LocaleError(f"语言资源格式无效：{path.name}")
            overlap = messages.keys() & entries.keys()
            if overlap:
                raise LocaleError(f"语言资源键重复：{', '.join(sorted(overlap))}")
            messages.update(entries)
    return messages


def t(key: str, *, locale: str | None = None, **values: object) -> str:
    selected = resolve_locale(locale)
    try:
        template = catalog(selected)[key]
    except KeyError as exc:
        raise LocaleError(f"语言包缺少文案：{key}") from exc
    return template.format(**values) if values else template


def label(group: str, value: object, *, locale: str | None = None) -> str:
    key = f"label.{group}.{value}"
    return catalog(resolve_locale(locale)).get(key, str(value))


def guidance_text(value: str, document: str, *, locale: str | None = None) -> str:
    selected = resolve_locale(locale)
    if selected == "en":
        return value
    prefix = f"guidance.{document}#"
    english = catalog("en")
    matches = {catalog(selected)[key] for key, source in english.items() if key.startswith(prefix) and source == value and key in catalog(selected)}
    return matches.pop() if len(matches) == 1 else value


def validate_catalogs() -> list[str]:
    errors: list[str] = []
    source = catalog("en")
    translated = catalog("zh-CN")
    for key in sorted(source.keys() ^ translated.keys()):
        errors.append(f"中英文案键不一致：{key}")
    formatter = Formatter()
    for key in sorted(source.keys() & translated.keys()):
        try:
            expected = {(field, spec, conversion) for _, field, spec, conversion in formatter.parse(source[key]) if field is not None}
            actual = {(field, spec, conversion) for _, field, spec, conversion in formatter.parse(translated[key]) if field is not None}
            if expected != actual:
                errors.append(f"占位符不一致：{key}")
        except ValueError:
            errors.append(f"占位符格式无效：{key}")
    return errors
