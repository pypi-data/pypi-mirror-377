from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict

import httpx

__all__ = ["Deflect", "DeflectClient", "DeflectError", "VerdictResponse"]


class VerdictObj(TypedDict, total=False):
    can_pass: bool


class DeviceObj(TypedDict, total=False):
    fingerprint: str
    user_agent: str
    languages: str
    timezone: str
    os: str
    is_mobile: bool


class IpObj(TypedDict, total=False):
    address: str
    type: str
    is_datacenter: bool
    is_proxy: bool
    is_tor: bool
    is_vpn: bool
    is_threat: bool
    is_bogon: bool
    asn: str
    asn_number: int


class LocationObj(TypedDict, total=False):
    city: str
    postal_code: str
    country: str
    continent: str
    latitude: float
    longitude: float


class SessionObj(TypedDict, total=False):
    started_at: str
    finished_at: str


class VerdictResponse(TypedDict, total=False):
    success: bool
    verdict: VerdictObj
    device: DeviceObj
    ip: IpObj
    location: LocationObj
    session: SessionObj


class DeflectError(Exception):
    def __init__(self, message: str, status: Optional[int] = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body

    def __repr__(self) -> str:  # pragma: no cover
        return f"DeflectError(status={self.status}, message={self.args[0]!r})"


@dataclass
class DeflectOptions:
    api_key: str
    action_id: str
    base_url: str = "https://api.deflect.bot"
    timeout: float = 4.0  # seconds
    max_retries: int = 2  # additional attempts on transient failures
    client: Optional[httpx.Client] = None
    async_client: Optional[httpx.AsyncClient] = None


class _BaseClient:
    def __init__(self, opts: DeflectOptions):
        if not opts.api_key:
            raise ValueError("api_key is required")
        if not opts.action_id:
            raise ValueError("action_id is required")
        self._opts = opts
        self._base_url = opts.base_url.rstrip("/")

    def _should_retry(self, attempt: int, status: Optional[int], is_timeout: bool, is_network: bool, max_retries: int) -> bool:
        if attempt >= max_retries:
            return False
        if is_timeout or is_network:
            return True
        if status and 500 <= status < 600:
            return True
        return False


class Deflect(_BaseClient):
    """Synchronous client for the Deflect API."""

    def __init__(self, opts: DeflectOptions):
        super().__init__(opts)
        self._client = opts.client or httpx.Client(timeout=opts.timeout)

    def get_verdict(self, token: str) -> VerdictResponse:
        if not token:
            raise ValueError("token is required")
        body = {"api_key": self._opts.api_key, "action_id": self._opts.action_id, "token": token}
        attempt = 0
        last_error: Optional[DeflectError] = None
        while attempt <= self._opts.max_retries:
            try:
                resp = self._client.post(f"{self._base_url}/verify", json=body)
            except httpx.TimeoutException:
                is_timeout = True
                is_network = False
                status = None
                if self._should_retry(attempt, status, is_timeout, is_network, self._opts.max_retries):
                    attempt += 1
                    continue
                raise DeflectError("Request timed out", 408)
            except httpx.HTTPError as e:  # network
                if self._should_retry(attempt, None, False, True, self._opts.max_retries):
                    attempt += 1
                    continue
                raise DeflectError(f"Network error: {e}") from e

            status = resp.status_code
            if status >= 500 and self._should_retry(attempt, status, False, False, self._opts.max_retries):
                attempt += 1
                continue
            # parse JSON (robust)
            try:
                data = resp.json()
            except json.JSONDecodeError:
                data = {}
            if status >= 400:
                raise DeflectError(f"Deflect API error {status}", status, data)
            return data  # type: ignore
        raise DeflectError("Request failed after retries", last_error.status if last_error else None)


class AsyncDeflect(_BaseClient):
    """Asynchronous client for the Deflect API."""

    def __init__(self, opts: DeflectOptions):
        super().__init__(opts)
        self._client = opts.async_client or httpx.AsyncClient(timeout=opts.timeout)

    async def get_verdict(self, token: str) -> VerdictResponse:
        if not token:
            raise ValueError("token is required")
        body = {"api_key": self._opts.api_key, "action_id": self._opts.action_id, "token": token}
        attempt = 0
        last_error: Optional[DeflectError] = None
        while attempt <= self._opts.max_retries:
            try:
                resp = await self._client.post(f"{self._base_url}/verify", json=body)
            except httpx.TimeoutException:
                is_timeout = True
                is_network = False
                status = None
                if self._should_retry(attempt, status, is_timeout, is_network, self._opts.max_retries):
                    attempt += 1
                    continue
                raise DeflectError("Request timed out", 408)
            except httpx.HTTPError as e:
                if self._should_retry(attempt, None, False, True, self._opts.max_retries):
                    attempt += 1
                    continue
                raise DeflectError(f"Network error: {e}") from e

            status = resp.status_code
            if status >= 500 and self._should_retry(attempt, status, False, False, self._opts.max_retries):
                attempt += 1
                continue
            try:
                data = resp.json()
            except json.JSONDecodeError:
                data = {}
            if status >= 400:
                raise DeflectError(f"Deflect API error {status}", status, data)
            return data  # type: ignore
        raise DeflectError("Request failed after retries", last_error.status if last_error else None)


