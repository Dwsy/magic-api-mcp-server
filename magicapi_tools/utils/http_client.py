"""Magic-API HTTP 客户端封装。"""

from __future__ import annotations

import json
import uuid
from typing import Any, Mapping, MutableMapping, Optional

import requests

from magicapi_mcp.settings import MagicAPISettings, DEFAULT_SETTINGS


def _default_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "magicapi-tools/1.0",
    }


class MagicAPIHTTPClient:
    """简化 Magic-API 调用的 HTTP 客户端。"""

    def __init__(self, settings: MagicAPISettings | None = None, client_id: str | None = None) -> None:
        self.settings = settings or DEFAULT_SETTINGS
        self.client_id = client_id or uuid.uuid4().hex
        self.session = requests.Session()
        self.session.headers.update(_default_headers())
        self.settings.inject_auth(self.session.headers)

        if self.settings.auth_enabled and self.settings.username and self.settings.password:
            self._login()

    def _login(self) -> bool:
        payload = {
            "username": self.settings.username,
            "password": self.settings.password,
        }
        try:
            response = self.session.post(
                f"{self.settings.base_url}/magic/web/login",
                json=payload,
                timeout=self.settings.timeout_seconds,
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return False
                return data.get("code") == 1
            return False
        except requests.RequestException:
            return False

    def resource_tree(self) -> tuple[bool, Any]:
        try:
            response = self.session.post(
                f"{self.settings.base_url}/magic/web/resource",
                timeout=self.settings.timeout_seconds,
            )
            if response.status_code != 200:
                return False, {
                    "code": response.status_code,
                    "message": "获取资源树失败",
                    "detail": response.text,
                }
            payload = response.json()
            if payload.get("code") != 1:
                return False, {
                    "code": payload.get("code", -1),
                    "message": payload.get("message", "接口返回异常"),
                }
            return True, payload.get("data", {})
        except requests.RequestException as exc:
            return False, {
                "code": "network_error",
                "message": "请求资源树出现异常",
                "detail": str(exc),
            }

    def api_detail(self, file_id: str) -> tuple[bool, Any]:
        try:
            response = self.session.get(
                f"{self.settings.base_url}/magic/web/resource/file/{file_id}",
                timeout=self.settings.timeout_seconds,
            )
            if response.status_code != 200:
                return False, {
                    "code": response.status_code,
                    "message": "获取接口详情失败",
                    "detail": response.text,
                }
            payload = response.json()
            if payload.get("code") != 1:
                return False, {
                    "code": payload.get("code", -1),
                    "message": payload.get("message", "接口返回异常"),
                }
            return True, payload.get("data")
        except requests.RequestException as exc:
            return False, {
                "code": "network_error",
                "message": "请求接口详情异常",
                "detail": str(exc),
            }

    def call_api(
        self,
        method: str,
        path: str,
        params: Optional[Mapping[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> tuple[bool, Any]:
        method = method.upper()
        if not path.startswith("/"):
            path = f"/{path}"

        url = f"{self.settings.base_url}{path}"

        request_headers: MutableMapping[str, str] = {
            "X-MAGIC-CLIENT-ID": self.client_id,
            "X-MAGIC-SCRIPT-ID": uuid.uuid4().hex,
        }
        if headers:
            request_headers.update(headers)
        self.settings.inject_auth(request_headers)

        request_kwargs: dict[str, Any] = {
            "params": params,
            "headers": request_headers,
            "timeout": self.settings.timeout_seconds,
        }

        if isinstance(data, (dict, list)):
            request_kwargs["json"] = data
        elif isinstance(data, str):
            request_kwargs["data"] = data
        elif data is not None:
            request_kwargs["data"] = json.dumps(data)

        try:
            response = self.session.request(method, url, **request_kwargs)
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    body = response.json()
                except json.JSONDecodeError:
                    body = response.text
            else:
                body = response.text

            return True, {
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": body,
            }
        except requests.RequestException as exc:
            return False, {
                "code": "network_error",
                "message": "调用 Magic-API 接口失败",
                "detail": str(exc),
            }


__all__ = ["MagicAPIHTTPClient"]
