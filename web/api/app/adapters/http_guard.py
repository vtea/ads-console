"""Outbound HTTP guard: https-only, host allowlist, public-IP resolution, no redirects, redacted errors."""

from __future__ import annotations

import ipaddress
import socket
from typing import Any, Iterable
from urllib.parse import urlsplit

import httpx

from ..security.redact import sanitize_error


class EgressDenied(RuntimeError):
    pass


def _is_public_address(address: str) -> bool:
    ip = ipaddress.ip_address(address)
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified)


def resolve_public_host(host: str) -> tuple[str, ...]:
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise EgressDenied(f"DNS resolution failed for {host}") from exc
    addresses = tuple(sorted({info[4][0] for info in infos}))
    if not addresses or not all(_is_public_address(a) for a in addresses):
        raise EgressDenied(f"{host} resolves to a non-public address")
    return addresses


def validate_outbound_url(url: str, allowed_hosts: Iterable[str], *, resolve: bool = True) -> str:
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise EgressDenied("only https is allowed")
    host = (parts.hostname or "").lower()
    if host not in {h.lower() for h in allowed_hosts}:
        raise EgressDenied(f"host {host or '<empty>'} is not allowlisted")
    if parts.username or parts.password or parts.port not in (None, 443):
        raise EgressDenied("credentials or non-standard ports are not allowed in URLs")
    if resolve:
        resolve_public_host(host)
    return url


class GuardedClient:
    """httpx.Client wrapper that enforces the allowlist on every request and never follows redirects."""

    def __init__(self, allowed_hosts: Iterable[str], *, timeout: float = 20.0, transport: httpx.BaseTransport | None = None, resolve_dns: bool = True) -> None:
        self.allowed_hosts = tuple(allowed_hosts)
        self._resolve_dns = resolve_dns
        self._client = httpx.Client(timeout=timeout, follow_redirects=False, transport=transport)

    def get_json(self, url: str, *, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        validate_outbound_url(url, self.allowed_hosts, resolve=self._resolve_dns)
        try:
            response = self._client.get(url, params=params, headers=headers)
        except httpx.HTTPError as exc:
            raise EgressDenied(sanitize_error(exc)) from None
        if 300 <= response.status_code < 400:
            raise EgressDenied("redirects are not followed")
        if response.status_code >= 400:
            raise EgressDenied(sanitize_error(RuntimeError(f"upstream status {response.status_code}")))
        try:
            payload = response.json()
        except ValueError as exc:
            raise EgressDenied("upstream returned non-JSON") from exc
        if not isinstance(payload, dict):
            raise EgressDenied("upstream returned a non-object JSON payload")
        return payload

    def close(self) -> None:
        self._client.close()
