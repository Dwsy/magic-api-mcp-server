"""Magic-API HTTP 客户端封装。"""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Mapping, MutableMapping, Optional

import requests

from magicapi_mcp.settings import MagicAPISettings, DEFAULT_SETTINGS
from magicapi_tools.logging_config import get_logger

# 获取HTTP客户端的logger
logger = get_logger('utils.http_client')


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

    def _build_full_paths(self, tree_data: Dict[str, Any]) -> Dict[str, Any]:
        """为资源树中的每个节点构建完整路径"""
        def build_path_recursive(node: Dict[str, Any], parent_path: str = "") -> Dict[str, Any]:
            """递归构建节点的全路径"""
            node_copy = dict(node)  # 复制节点避免修改原数据

            # 获取当前节点的路径信息
            node_info = node_copy.get("node", {})
            current_path = node_info.get("path", "")

            # 构建完整路径
            if parent_path and current_path:
                full_path = f"{parent_path}/{current_path}"
            elif current_path:
                full_path = current_path
            else:
                full_path = parent_path

            # 清理路径（去除多余的斜杠）
            full_path = full_path.strip("/")
            while "//" in full_path:
                full_path = full_path.replace("//", "/")

            # 为节点添加full_path信息
            if node_info:
                node_info["full_path"] = f"/{full_path}" if full_path else "/"
                node_copy["node"] = node_info

            # 递归处理子节点
            if "children" in node_copy and node_copy["children"]:
                new_children = []
                for child in node_copy["children"]:
                    new_child = build_path_recursive(child, full_path)
                    new_children.append(new_child)
                node_copy["children"] = new_children

            return node_copy

        # 处理整个树结构
        result = {}
        for key, subtree in tree_data.items():
            if isinstance(subtree, dict) and "children" in subtree:
                # 这是一个分组节点
                result[key] = build_path_recursive(subtree)
            else:
                # 直接复制非树形数据
                result[key] = subtree

        return result

    def resource_tree(self) -> tuple[bool, Any]:
        url = f"{self.settings.base_url}/magic/web/resource"
        logger.debug(f"HTTP请求: POST {url}")

        try:
            response = self.session.post(url, timeout=self.settings.timeout_seconds)
            logger.debug(f"HTTP响应: {response.status_code}, 耗时: {response.elapsed.total_seconds()}s")

            if response.status_code != 200:
                logger.error(f"获取资源树失败: HTTP {response.status_code}")
                logger.error(f"  请求URL: {url}")
                logger.error(f"  响应内容: {response.text[:500]}...")
                return False, {
                    "code": response.status_code,
                    "message": "获取资源树失败",
                    "detail": response.text,
                }

            payload = response.json()
            logger.debug(f"  响应数据: code={payload.get('code')}, message={payload.get('message')}")

            if payload.get("code") != 1:
                logger.error(f"获取资源树失败: {payload.get('message', '接口返回异常')}")
                logger.error(f"  响应数据: {payload}")
                return False, {
                    "code": payload.get("code", -1),
                    "message": payload.get("message", "接口返回异常"),
                }

            data = payload.get("data", {})

            # 为资源树添加完整路径信息
            data_with_paths = self._build_full_paths(data)


            return True, data_with_paths

        except requests.RequestException as exc:
            logger.error(f"获取资源树网络异常: {exc}")
            logger.error(f"  请求URL: {url}")
            import traceback
            logger.debug(f"  异常堆栈: {traceback.format_exc()}")
            return False, {
                "code": "network_error",
                "message": "请求资源树出现异常",
                "detail": str(exc),
            }

    def api_detail(self, file_id: str) -> tuple[bool, Any]:
        url = f"{self.settings.base_url}/magic/web/resource/file/{file_id}"
        logger.debug(f"HTTP请求: GET {url}")
        logger.debug(f"  文件ID: {file_id}")

        try:
            response = self.session.get(url, timeout=self.settings.timeout_seconds)
            logger.debug(f"HTTP响应: {response.status_code}, 耗时: {response.elapsed.total_seconds()}s")

            if response.status_code != 200:
                logger.error(f"获取API详情失败: HTTP {response.status_code}")
                logger.error(f"  请求URL: {url}")
                logger.error(f"  文件ID: {file_id}")
                logger.error(f"  响应内容: {response.text[:200]}...")
                logger.debug(f"  响应头: {dict(response.headers)}")

                return False, {
                    "code": response.status_code,
                    "message": "获取接口详情失败",
                    "detail": response.text,
                    "url": url,
                    "file_id": file_id,
                }

            payload = response.json()
            logger.debug(f"  响应数据: code={payload.get('code')}, message={payload.get('message')}")

            if payload.get("code") != 1:
                error_code = payload.get("code", -1)
                error_message = payload.get("message", "接口返回异常")
                error_data = payload.get("data")

                logger.error(f"获取API详情失败: {error_message}")
                logger.error(f"  请求URL: {url}")
                logger.error(f"  文件ID: {file_id}")
                logger.error(f"  错误代码: {error_code}")
                logger.error(f"  错误数据: {error_data}")
                logger.debug(f"  完整响应: {payload}")

                return False, {
                    "code": error_code,
                    "message": error_message,
                    "data": error_data,
                    "url": url,
                    "file_id": file_id,
                }

            data = payload.get("data")
            if data is None:
                logger.warning(f"API详情数据为空: {file_id}")
                logger.warning(f"  请求URL: {url}")
                logger.debug(f"  响应: {payload}")

            logger.info(f"获取API详情成功: {file_id}")
            return True, data

        except requests.RequestException as exc:
            logger.error(f"获取API详情网络异常: {exc}")
            logger.error(f"  文件ID: {file_id}")
            logger.error(f"  请求URL: {url}")
            import traceback
            logger.debug(f"  异常堆栈: {traceback.format_exc()}")

            return False, {
                "code": "network_error",
                "message": "请求接口详情异常",
                "detail": str(exc),
                "file_id": file_id,
                "url": url,
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

        logger.debug(f"HTTP请求: {method} {url}")
        if params:
            logger.debug(f"  查询参数: {params}")
        if data:
            if isinstance(data, (dict, list)):
                logger.debug(f"  请求体(JSON): {json.dumps(data, ensure_ascii=False)[:200]}...")
            elif isinstance(data, str) and len(data) < 200:
                logger.debug(f"  请求体: {data}")
            else:
                logger.debug(f"  请求体: ({len(str(data))} 字符)")

        request_headers: MutableMapping[str, str] = {
            "X-MAGIC-CLIENT-ID": self.client_id,
            "X-MAGIC-SCRIPT-ID": uuid.uuid4().hex,
        }
        if headers:
            request_headers.update(headers)
        self.settings.inject_auth(request_headers)

        logger.debug(f"  请求头: {dict(request_headers)}")

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
            logger.debug(f"HTTP响应: {response.status_code}, 耗时: {response.elapsed.total_seconds()}s")

            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    body = response.json()
                    logger.debug(f"  响应体(JSON): {json.dumps(body, ensure_ascii=False)[:200]}...")
                except json.JSONDecodeError:
                    body = response.text
                    logger.debug(f"  响应体(文本): {body[:200]}...")
            else:
                body = response.text
                logger.debug(f"  响应体: {body[:200]}...")

            if response.status_code >= 400:
                logger.error(f"API调用失败: HTTP {response.status_code}")
                logger.error(f"  响应体: {body}")

            return True, {
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": body,
            }
        except requests.RequestException as exc:
            logger.error(f"API调用网络异常: {exc}")
            logger.error(f"  请求: {method} {url}")
            import traceback
            logger.debug(f"  异常堆栈: {traceback.format_exc()}")

            return False, {
                "code": "network_error",
                "message": "调用 Magic-API 接口失败",
                "detail": str(exc),
            }


__all__ = ["MagicAPIHTTPClient"]
