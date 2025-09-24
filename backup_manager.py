#!/usr/bin/env python3
"""Magic-API 备份管理客户端 CLI。"""

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


class MagicAPIBackupClient:
    """Magic-API 备份管理客户端。"""

    def __init__(self, settings: MagicAPISettings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "magicapi-backup-manager/1.0",
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
                json=payload,
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

    def get_backups(self, timestamp: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询备份列表。

        Args:
            timestamp: 时间戳，查询该时间戳之前的备份记录

        Returns:
            备份记录列表
        """
        url = f"{self.settings.base_url}/magic/web/backups"
        params = {}
        if timestamp:
            params['timestamp'] = timestamp

        try:
            response = self.session.get(url, params=params, timeout=self.settings.timeout_seconds)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 1:
                return data.get("data", [])
            else:
                print(f"❌ API 返回错误: {data.get('message', '未知错误')}")
                return []
        except requests.RequestException as exc:
            print(f"❌ 请求异常: {exc}")
            return []

    def get_backup_by_id(self, backup_id: str) -> List[Dict[str, Any]]:
        """根据 ID 查询备份历史。

        Args:
            backup_id: 备份对象 ID

        Returns:
            该对象的备份历史记录
        """
        if not backup_id:
            print("❌ 备份ID不能为空")
            return []

        url = f"{self.settings.base_url}/magic/web/backup/{backup_id}"

        try:
            response = self.session.get(url, timeout=self.settings.timeout_seconds)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 1:
                return data.get("data", [])
            else:
                print(f"❌ API 返回错误: {data.get('message', '未知错误')}")
                return []
        except requests.RequestException as exc:
            print(f"❌ 请求异常: {exc}")
            return []

    def rollback_backup(self, backup_id: str, timestamp: int) -> bool:
        """回滚到指定备份版本。

        Args:
            backup_id: 备份对象 ID
            timestamp: 备份时间戳

        Returns:
            回滚是否成功
        """
        url = f"{self.settings.base_url}/magic/web/backup/rollback"
        data = {
            'id': backup_id,
            'timestamp': timestamp
        }

        try:
            response = self.session.post(url, json=data, timeout=self.settings.timeout_seconds)
            response.raise_for_status()
            result = response.json()
            if result.get("code") == 1:
                return result.get("data", False)
            else:
                print(f"❌ API 返回错误: {result.get('message', '未知错误')}")
                return False
        except requests.RequestException as exc:
            print(f"❌ 请求异常: {exc}")
            return False

    def get_backup_content(self, backup_id: str, timestamp: int) -> Optional[str]:
        """获取备份的脚本内容。

        Args:
            backup_id: 备份对象 ID
            timestamp: 备份时间戳

        Returns:
            备份的脚本内容
        """
        url = f"{self.settings.base_url}/magic/web/backup"
        params = {
            'id': backup_id,
            'timestamp': timestamp
        }

        try:
            response = self.session.get(url, params=params, timeout=self.settings.timeout_seconds)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 1:
                return data.get("data")
            else:
                print(f"❌ API 返回错误: {data.get('message', '未知错误')}")
                return None
        except requests.RequestException as exc:
            print(f"❌ 请求异常: {exc}")
            return None

    def create_full_backup(self) -> bool:
        """执行手动全量备份。

        Returns:
            备份是否成功
        """
        url = f"{self.settings.base_url}/magic/web/backup/full"

        try:
            response = self.session.post(url, timeout=self.settings.timeout_seconds)
            response.raise_for_status()
            result = response.json()
            if result.get("code") == 1:
                return result.get("data", False)
            else:
                print(f"❌ API 返回错误: {result.get('message', '未知错误')}")
                return False
        except requests.RequestException as exc:
            print(f"❌ 请求异常: {exc}")
            return False


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="Magic-API 备份管理客户端")
    parser.add_argument("--list", action="store_true", help="查询备份列表")
    parser.add_argument("--filter", help="模糊过滤备份记录（支持名称、类型、创建者等字段）")
    parser.add_argument("--name-filter", help="按名称精确过滤备份记录")
    parser.add_argument("--limit", type=int, default=10, help="返回结果的最大数量（默认10条）")
    parser.add_argument("--timestamp", type=int, help="查询指定时间戳之前的备份")
    parser.add_argument("--id", help="指定备份对象ID")
    parser.add_argument("--history", action="store_true", help="查询指定ID的备份历史")
    parser.add_argument("--content", action="store_true", help="获取备份内容（需要 --id 和 --timestamp）")
    parser.add_argument("--rollback", action="store_true", help="回滚到指定备份版本（需要 --id 和 --timestamp）")
    parser.add_argument("--full-backup", action="store_true", help="执行手动全量备份")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出结果")
    return parser.parse_args()


def build_client(settings: MagicAPISettings) -> MagicAPIBackupClient:
    """构建备份管理客户端。"""
    return MagicAPIBackupClient(settings)


def filter_backups(backups: List[Dict[str, Any]], filter_text: Optional[str], name_filter: Optional[str]) -> List[Dict[str, Any]]:
    """根据过滤条件筛选备份记录。

    Args:
        backups: 备份记录列表
        filter_text: 通用过滤关键词（模糊匹配多个字段）
        name_filter: 名称过滤关键词（精确匹配名称字段）

    Returns:
        过滤后的备份记录列表
    """
    # 先应用通用过滤
    if filter_text:
        filter_lower = filter_text.lower()
        filtered = []
        for backup in backups:
            # 检查各个字段是否匹配过滤条件
            searchable_fields = [
                backup.get('id', ''),
                backup.get('type', ''),
                backup.get('name', ''),
                backup.get('createBy', ''),
                backup.get('tag', ''),
            ]

            # 将所有字段转换为字符串并检查是否包含过滤关键词
            if any(filter_lower in str(field).lower() for field in searchable_fields if field):
                filtered.append(backup)
        backups = filtered

    # 再应用名称过滤
    if name_filter:
        name_filter_lower = name_filter.lower()
        filtered = []
        for backup in backups:
            backup_name = backup.get('name', '')
            if backup_name and name_filter_lower in str(backup_name).lower():
                filtered.append(backup)
        backups = filtered

    return backups


def list_backups(client: MagicAPIBackupClient, timestamp: Optional[int], filter_text: Optional[str], name_filter: Optional[str], limit: int, json_output: bool) -> None:
    """列出备份记录。"""
    print("🔍 查询备份列表...")
    backups = client.get_backups(timestamp)

    # 应用过滤
    original_count = len(backups)
    backups = filter_backups(backups, filter_text, name_filter)
    filtered_count = len(backups)

    # 应用 limit 限制
    if limit > 0:
        backups = backups[:limit]

    # 显示过滤信息
    filter_conditions = []
    if filter_text:
        filter_conditions.append(f"通用过滤: '{filter_text}'")
    if name_filter:
        filter_conditions.append(f"名称过滤: '{name_filter}'")

    if filter_conditions or limit != 10:  # 默认 limit 为 10
        info_parts = []
        if filter_conditions:
            info_parts.append(f"过滤条件: {'; '.join(filter_conditions)}")
        if limit != 10:
            info_parts.append(f"限制条数: {limit}")
        print(f"🔍 {'; '.join(info_parts)}")

    if original_count != len(backups):
        print(f"📊 总数: {original_count} 条 → 过滤后: {filtered_count} 条 → 返回: {len(backups)} 条")

    if json_output:
        print(json.dumps(backups, ensure_ascii=False, indent=2))
    else:
        if not backups:
            if filter_conditions:
                print(f"📭 没有找到匹配的备份记录")
            else:
                print("📭 没有找到备份记录")
            return

        print(f"📋 找到 {len(backups)} 个备份记录:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. ID: {backup.get('id', 'N/A')}")
            print(f"   类型: {backup.get('type', 'N/A')}")
            print(f"   名称: {backup.get('name', 'N/A')}")
            print(f"   创建者: {backup.get('createBy', 'N/A')}")
            print(f"   创建时间: {backup.get('createDate', 'N/A')}")
            print()


def show_backup_history(client: MagicAPIBackupClient, backup_id: str, json_output: bool) -> None:
    """显示备份历史。"""
    print(f"🔍 查询备份历史 (ID: {backup_id})...")
    history = client.get_backup_by_id(backup_id)

    if json_output:
        print(json.dumps(history, ensure_ascii=False, indent=2))
    else:
        if not history:
            print("📭 没有找到备份历史")
            return

        print(f"📋 找到 {len(history)} 个历史记录:")
        for i, backup in enumerate(history, 1):
            print(f"{i}. 备份时间: {backup.get('createDate', 'N/A')}")
            print(f"   类型: {backup.get('type', 'N/A')}")
            print(f"   名称: {backup.get('name', 'N/A')}")
            print(f"   创建者: {backup.get('createBy', 'N/A')}")
            print()


def get_backup_content(client: MagicAPIBackupClient, backup_id: str, timestamp: int, json_output: bool) -> None:
    """获取备份内容。"""
    print(f"📄 获取备份内容 (ID: {backup_id}, 时间戳: {timestamp})...")
    content = client.get_backup_content(backup_id, timestamp)

    if content is None:
        print("❌ 获取备份内容失败")
        return

    if json_output:
        print(json.dumps({"content": content}, ensure_ascii=False, indent=2))
    else:
        print("📝 备份内容:")
        print(content)


def rollback_backup(client: MagicAPIBackupClient, backup_id: str, timestamp: int) -> None:
    """执行回滚操作。"""
    print(f"⚠️ 即将回滚到备份版本 (ID: {backup_id}, 时间戳: {timestamp})")
    confirm = input("确认要执行回滚操作吗？(输入 'yes' 确认): ")
    if confirm.lower() != 'yes':
        print("❌ 取消回滚操作")
        return

    print("🔄 执行回滚...")
    success = client.rollback_backup(backup_id, timestamp)

    if success:
        print("✅ 回滚成功")
    else:
        print("❌ 回滚失败")


def create_full_backup(client: MagicAPIBackupClient) -> None:
    """执行全量备份。"""
    print("💾 执行全量备份...")
    success = client.create_full_backup()

    if success:
        print("✅ 全量备份成功")
    else:
        print("❌ 全量备份失败")


def main() -> None:
    """主函数。"""
    args = parse_args()

    # 验证参数组合
    operations = [args.list, args.history, args.content, args.rollback, args.full_backup]
    if sum(operations) != 1:
        print("❌ 必须且只能指定一个操作: --list, --history, --content, --rollback, 或 --full-backup")
        sys.exit(1)

    # 验证必需参数
    if args.history and not args.id:
        print("❌ --history 操作需要指定 --id 参数")
        sys.exit(1)

    if args.content and (not args.id or not args.timestamp):
        print("❌ --content 操作需要指定 --id 和 --timestamp 参数")
        sys.exit(1)

    if args.rollback and (not args.id or not args.timestamp):
        print("❌ --rollback 操作需要指定 --id 和 --timestamp 参数")
        sys.exit(1)

    settings = MagicAPISettings.from_env()
    client = build_client(settings)

    try:
        if args.list:
            list_backups(client, args.timestamp, args.filter, args.name_filter, args.limit, args.json)
        elif args.history:
            show_backup_history(client, args.id, args.json)
        elif args.content:
            get_backup_content(client, args.id, args.timestamp, args.json)
        elif args.rollback:
            rollback_backup(client, args.id, args.timestamp)
        elif args.full_backup:
            create_full_backup(client)
    except KeyboardInterrupt:
        print("\n⏹️ 操作已取消")
        sys.exit(1)


if __name__ == "__main__":
    main()
