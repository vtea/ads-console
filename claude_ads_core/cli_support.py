"""Scoped, dependency-free localization for command-line argument diagnostics."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Sequence

from .errors import safe_error_text
from .i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES, LocaleError, locale_scope, resolve_locale, t


def _diagnostic(message: str) -> str:
    """Translate only known argparse templates, never opaque user values."""
    if resolve_locale() == "en":
        return message
    argument = re.fullmatch(r"argument (.*?): (.*)", message, re.DOTALL)
    if argument:
        return t("core.cli.argument", argument=argument[1], message=_diagnostic(argument[2]))
    prefixes = (
        ("the following arguments are required: ", "core.cli.required"),
        ("unrecognized arguments: ", "core.cli.unrecognized"),
        ("not allowed with argument ", "core.cli.conflict"),
        ("ignored explicit argument ", "core.cli.ignored_explicit"),
    )
    for prefix, key in prefixes:
        if message.startswith(prefix):
            return t(key, arguments=message[len(prefix):])
    fixed = {
        "expected one argument": "core.cli.expected_one",
        "expected at most one argument": "core.cli.expected_at_most_one",
        "expected at least one argument": "core.cli.expected_at_least_one",
    }
    if message in fixed:
        return t(fixed[message])
    count = re.fullmatch(r"expected (\d+) arguments?", message)
    if count:
        return t("core.cli.expected_count", count=count[1])
    required_group = re.fullmatch(r"one of the arguments (.*) is required", message, re.DOTALL)
    if required_group:
        return t("core.cli.required_group", arguments=required_group[1])
    ambiguous = re.fullmatch(r"ambiguous option: (.*?) could match (.*)", message, re.DOTALL)
    if ambiguous:
        return t("core.cli.ambiguous", option=ambiguous[1], matches=ambiguous[2])
    # Custom argparse type errors may be external data. Preserve them verbatim;
    # error() supplies the localized diagnostic prefix.
    return message


class LocaleHelpFormatter(argparse.HelpFormatter):
    """Keep argparse's layout algorithm and localize its usage prefix only."""

    def _format_usage(self, usage, actions, groups, prefix):
        return super()._format_usage(
            usage, actions, groups, t("core.cli.usage") if prefix is None else prefix
        )


class LocaleRawDescriptionHelpFormatter(LocaleHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Localized usage with unchanged multiline descriptions."""


class LocaleArgumentParser(argparse.ArgumentParser):
    """ArgumentParser with local diagnostics; never mutates argparse or locale.

    Construct and parse inside ``locale_scope(cli_locale(argv))`` so translated
    help is built in the selected locale. The caller keeps that scope active
    while executing its command. Subparsers inherit this class and accept
    ``--locale`` without overwriting a locale supplied before the subcommand.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("formatter_class", LocaleHelpFormatter)
        super().__init__(*args, **kwargs)
        self._positionals.title = t("core.cli.positionals")
        self._optionals.title = t("core.cli.options")
        self.add_argument(
            "--locale", choices=SUPPORTED_LOCALES, default=argparse.SUPPRESS,
            help=t("core.cli.locale_help"),
        )

    def add_argument(self, *args, **kwargs):
        if kwargs.get("help") == "show this help message and exit":
            kwargs["help"] = t("core.cli.help")
        if kwargs.get("action") == "version" and kwargs.get("help") is None:
            kwargs["help"] = t("core.cli.version")
        return super().add_argument(*args, **kwargs)

    def _check_value(self, action, value):
        if action.choices is not None and value not in action.choices:
            if action.dest == "locale":
                raise argparse.ArgumentError(action, t("core.cli.unsupported_locale"))
            raise argparse.ArgumentError(
                action,
                t("core.cli.invalid_choice", value=value, choices=", ".join(map(repr, action.choices))),
            )

    def _get_value(self, action, arg_string):
        try:
            return super()._get_value(action, arg_string)
        except argparse.ArgumentError as exc:
            type_func = self._registry_get("type", action.type, action.type)
            type_name = getattr(type_func, "__name__", repr(type_func))
            expected = "invalid %s value: %r" % (type_name, arg_string)
            if exc.message == expected:
                raise argparse.ArgumentError(
                    action, t("core.cli.invalid_type", type=type_name, value=arg_string)
                ) from exc
            raise

    def _match_argument(self, action, arg_strings_pattern):
        try:
            return super()._match_argument(action, arg_strings_pattern)
        except argparse.ArgumentError as exc:
            raise argparse.ArgumentError(action, _diagnostic(exc.message)) from exc

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, t("core.cli.error", prog=self.prog, message=safe_error_text(_diagnostic(message))) + "\n")


def cli_locale(argv: Sequence[str] | None = None) -> str:
    """Resolve locale before help/validation, with ordinary argparse exit 2.

    A help-free preliminary parser recognizes only the locale option. It does
    not remove arguments from the real parser, and honors the ``--`` delimiter.
    Explicit flags take precedence over the environment, including when the
    environment contains an unsupported locale.
    """
    arguments = list(sys.argv[1:] if argv is None else argv)
    selected = None
    locale_arguments: list[str] = []
    for index, argument in enumerate(arguments):
        if argument == "--":
            break
        if argument.startswith("--locale="):
            selected = argument.partition("=")[2]
            locale_arguments.append(argument)
        elif argument == "--locale":
            locale_arguments.append(argument)
            if index + 1 < len(arguments) and not arguments[index + 1].startswith("-"):
                selected = arguments[index + 1]
                locale_arguments.append(selected)
    try:
        diagnostic_locale = resolve_locale(selected)
    except LocaleError:
        diagnostic_locale = DEFAULT_LOCALE
    with locale_scope(diagnostic_locale):
        parser = LocaleArgumentParser(add_help=False, allow_abbrev=False)
        parsed, _ = parser.parse_known_args(locale_arguments)
    try:
        return resolve_locale(getattr(parsed, "locale", None))
    except LocaleError as exc:
        with locale_scope(diagnostic_locale):
            parser.error(str(exc))
    raise AssertionError("unreachable")
