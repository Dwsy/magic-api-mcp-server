#!/usr/bin/env python3
"""Magic-API 搜索客户端 CLI。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

import requests


def _get_env(env: Mapping[str, str], key: str, default: str) -> str:
    return env.get(key, default)


def _str_to_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


DEFAULT_BASE_URL = "http://127.0.0.1:10712"
DEFAULT_WS_URL = "ws://127.0.0.1:10712/magic/web/console"
DEFAULT_TIMEOUT = 30.0


@dataclass(slots=True)
class MagicAPISettings:
    """封装 Magic-API 服务相关的环境配置。"""

    base_url: str = DEFAULT_BASE_URL
    ws_url: str = DEFAULT_WS_URL
    username: str | None = None
    password: str | None = None
    token: str | None = None
    auth_enabled: bool = False
    timeout_seconds: float = DEFAULT_TIMEOUT

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "MagicAPISettings":
        """从环境变量加载配置。"""
        env = env or os.environ
        base_url = _get_env(env, "MAGIC_API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        ws_url = _get_env(env, "MAGIC_API_WS_URL", DEFAULT_WS_URL)
        username = env.get("MAGIC_API_USERNAME") or None
        password = env.get("MAGIC_API_PASSWORD") or None
        token = env.get("MAGIC_API_TOKEN") or None
        auth_enabled = _str_to_bool(env.get("MAGIC_API_AUTH_ENABLED"))

        timeout_raw = env.get("MAGIC_API_TIMEOUT_SECONDS")
        try:
            timeout_seconds = float(timeout_raw) if timeout_raw else DEFAULT_TIMEOUT
        except (TypeError, ValueError):
            timeout_seconds = DEFAULT_TIMEOUT

        return cls(
            base_url=base_url,
            ws_url=ws_url,
            username=username,
            password=password,
            token=token,
            auth_enabled=auth_enabled,
            timeout_seconds=timeout_seconds,
        )

    def inject_auth(self, headers: MutableMapping[str, str]) -> MutableMapping[str, str]:
        """根据配置向请求头注入认证信息。"""
        if not self.auth_enabled:
            return headers

        if self.token:
            headers.setdefault("Authorization", f"Bearer {self.token}")
            headers.setdefault("Magic-Token", self.token)

        if self.username and self.password:
            headers.setdefault("Magic-Username", self.username)
            headers.setdefault("Magic-Password", self.password)

        return headers


class MagicAPISearchClient:
    """Magic-API 搜索客户端。"""

    def __init__(self, settings: MagicAPISettings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "magicapi-search-manager/1.0",
        })
        self.settings.inject_auth(self.session.headers)

        if self.settings.auth_enabled and self.settings.username and self.settings.password:
            self._login()

    def _login(self) -> bool:
        """登录获取认证。"""
        payload = {
            "username": self.settings.username,
            "password": self.settings.password,
        }
        try:
            response = self.session.post(
                f"{self.settings.base_url}/magic/web/login",
                data=payload,
                timeout=self.settings.timeout_seconds,
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                    return data.get("code") == 1
                except json.JSONDecodeError:
                    pass
        except requests.RequestException:
            pass
        return False

    def search(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """在所有 API 脚本中搜索关键词。

        Args:
            keyword: 搜索关键词

        Returns:
            搜索结果列表，每个结果包含 id、text、line 字段
        """
        if not keyword.strip():
            print("❌ 搜索关键词不能为空")
            return []

        url = f"{self.settings.base_url}/magic/web/search"
        data = {'keyword': keyword}

        try:
            response = self.session.post(url, data=data, timeout=self.settings.timeout_seconds)
            response.raise_for_status()
            result = response.json()
            if result.get("code") == 1:
                results = result.get("data", [])
                # 应用 limit 限制
                if limit > 0:
                    results = results[:limit]
                return results
            else:
                print(f"❌ API 返回错误: {result.get('message', '未知错误')}")
                return []
        except requests.RequestException as exc:
            print(f"❌ 请求异常: {exc}")
            return []

    def search_todo(self, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索所有 TODO 注释。

        Returns:
            TODO 注释列表，每个结果包含 id、text、line 字段
        """
        url = f"{self.settings.base_url}/magic/web/todo"

        try:
            response = self.session.get(url, timeout=self.settings.timeout_seconds)
            response.raise_for_status()
            result = response.json()
            if result.get("code") == 1:
                results = result.get("data", [])
                # 应用 limit 限制
                if limit > 0:
                    results = results[:limit]
                return results
            else:
                print(f"❌ API 返回错误: {result.get('message', '未知错误')}")
                return []
        except requests.RequestException as exc:
            print(f"❌ 请求异常: {exc}")
            return []


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="Magic-API 搜索客户端")
    parser.add_argument("--search", help="在所有API脚本中搜索关键词")
    parser.add_argument("--todo", action="store_true", help="搜索所有TODO注释")
    parser.add_argument("--limit", type=int, default=5, help="返回结果的最大数量（默认5条）")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出结果")
    return parser.parse_args()


def build_client(settings: MagicAPISettings) -> MagicAPISearchClient:
    """构建搜索客户端。"""
    return MagicAPISearchClient(settings)


def perform_search(client: MagicAPISearchClient, keyword: str, limit: int, json_output: bool) -> None:
    """执行关键词搜索。"""
    print(f"🔍 搜索关键词: '{keyword}' (限制 {limit} 条)")
    results = client.search(keyword, limit)

    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("📭 没有找到匹配的结果")
            return

        print(f"📋 找到 {len(results)} 个匹配结果:")
        for i, result in enumerate(results, 1):
            print(f"{i}. 文件ID: {result.get('id', 'N/A')}")
            print(f"   行号: {result.get('line', 'N/A')}")
            print(f"   内容: {result.get('text', 'N/A')}")
            print()


def perform_todo_search(client: MagicAPISearchClient, limit: int, json_output: bool) -> None:
    """执行TODO搜索。"""
    print(f"📝 搜索TODO注释... (限制 {limit} 条)")
    results = client.search_todo(limit)

    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("📭 没有找到TODO注释")
            return

        print(f"📋 找到 {len(results)} 个TODO注释:")
        for i, result in enumerate(results, 1):
            print(f"{i}. 文件ID: {result.get('id', 'N/A')}")
            print(f"   行号: {result.get('line', 'N/A')}")
            print(f"   内容: {result.get('text', 'N/A')}")
            print()


def main() -> None:
    """主函数。"""
    args = parse_args()

    # 验证参数组合
    operations = [bool(args.search), args.todo]
    if sum(operations) != 1:
        print("❌ 必须且只能指定一个操作: --search 或 --todo")
        sys.exit(1)

    settings = MagicAPISettings.from_env()
    client = build_client(settings)

    try:
        if args.search:
            perform_search(client, args.search, args.limit, args.json)
        elif args.todo:
            perform_todo_search(client, args.limit, args.json)
    except KeyboardInterrupt:
        print("\n⏹️ 操作已取消")
        sys.exit(1)


if __name__ == "__main__":
    main()
