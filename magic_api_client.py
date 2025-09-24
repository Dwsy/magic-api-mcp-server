#!/usr/bin/env python3
"""Magic-API WebSocket 客户端 CLI。"""

from __future__ import annotations

import argparse
import asyncio
import sys

from magicapi_tools import MagicAPISettings
from magicapi_tools import MagicAPIWebSocketClient, parse_call_arg, run_custom_api_call


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Magic-API WebSocket 客户端")
    parser.add_argument("--call", help="执行 API 调用，格式 'METHOD PATH'")
    parser.add_argument("--params", help="查询参数字符串，例如 'a=1&b=2'")
    parser.add_argument("--data", help="请求体 JSON 字符串")
    parser.add_argument("--listen-only", action="store_true", help="仅连接 WebSocket 监听日志")
    return parser.parse_args()


def build_client(settings: MagicAPISettings) -> MagicAPIWebSocketClient:
    return MagicAPIWebSocketClient(
        settings.ws_url,
        settings.base_url,
        username=settings.username if settings.auth_enabled else None,
        password=settings.password if settings.auth_enabled else None,
    )


def listen_only(client: MagicAPIWebSocketClient) -> None:
    async def runner():
        try:
            await client.connect()
        except KeyboardInterrupt:
            print("\n⏹️ 监听已停止")
        finally:
            await client.close()

    asyncio.run(runner())


def execute_call(
    client: MagicAPIWebSocketClient,
    call_arg: str,
    params: str | None,
    data: str | None,
) -> None:
    try:
        method, path = parse_call_arg(call_arg)
    except ValueError as exc:
        print(f"❌ 参数错误: {exc}")
        sys.exit(1)

    run_custom_api_call(
        client,
        method,
        path,
        params=params,
        data=data,
        enable_websocket=False,
    )


def main() -> None:
    args = parse_args()
    if not args.listen_only and not args.call:
        print("❌ 必须指定 --call 或 --listen-only")
        sys.exit(1)

    settings = MagicAPISettings.from_env()
    client = build_client(settings)

    if args.listen_only:
        listen_only(client)
        return

    execute_call(client, args.call, args.params, args.data)


if __name__ == "__main__":
    main()
