#!/usr/bin/env python3
"""环境状态管理单元测试."""

from __future__ import annotations

import json

from magicapi_tools.ws import EnvironmentState, MessageType, WSMessage, parse_ws_message


class DummyResolver:
    def __init__(self, details: dict[str, dict]):
        self._details = details

    def resolve_file(self, file_id: str):  # noqa: D401
        return self._details.get(file_id)


def _print_header(title: str) -> None:
    print("=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:
    dummy_detail = {
        "file123": {
            "id": "file123",
            "name": "示例接口",
            "method": "GET",
            "path": "/demo/example",
            "groupName": "演示组",
            "groupPath": "demo",
        }
    }

    state = EnvironmentState(resource_resolver=DummyResolver(dummy_detail))
    state.set_primary_client("client-1")

    _print_header("1. 处理登录响应，合并到IP环境")
    login_payload = json.dumps({"clientId": "client-1", "loginIp": "192.168.1.8", "nickname": "测试用户"})
    login_msg = parse_ws_message(f"login_response,1,{login_payload}")
    env_after_login = state.handle_message(login_msg, default_client_id="client-1")
    print("环境标识:", env_after_login.ide_key if env_after_login else None)
    print("客户端集合:", sorted(env_after_login.client_ids) if env_after_login else None)
    print("最新用户:", env_after_login.latest_user if env_after_login else None)

    _print_header("2. 处理文件切换，记录接口上下文")
    set_file_msg = parse_ws_message("set_file_id,file123,{\"clientId\":\"client-1\"}")
    env_after_file = state.handle_message(set_file_msg, default_client_id="client-1")
    opened = env_after_file.opened_files.get("client-1") if env_after_file else None
    if opened:
        print("打开的文件:", opened.file_id)
        print("接口路径:", opened.method, opened.path)
        print("接口名称:", opened.name)
        print("分组链:", opened.group_chain)
    else:
        print("未找到打开文件记录")

    _print_header("3. 处理断点消息，更新变量和行号")
    breakpoint_payload = json.dumps(
        {
            "variables": [
                {
                    "name": "header",
                    "type": "java.util.Map",
                    "value": json.dumps({
                        "magic-request-client-id": "client-1",
                        "magic-request-script-id": "file123",
                        "magic-request-breakpoints": "5,9",
                    }),
                },
                {"name": "db", "type": "Object", "value": "{}"},
            ],
            "range": [5, 1, 5, 20],
        }
    )
    breakpoint_msg = parse_ws_message(f"breakpoint,file123,{breakpoint_payload}")
    env_after_breakpoint = state.handle_message(breakpoint_msg, default_client_id="client-1")
    ctx = env_after_breakpoint.opened_files.get("client-1") if env_after_breakpoint else None
    if ctx:
        print("最后断点范围:", ctx.last_breakpoint_range)
        print("捕获变量数量:", len(ctx.last_variables or []))
        print("Headers: magic-request-client-id=", ctx.headers.get("magic-request-client-id") if ctx.headers else None)
    else:
        print("断点上下文缺失")

    _print_header("4. 总环境快照")
    for env in state.list_environments():
        print(
            "IDE环境:", env.ide_key,
            "| 客户端数量:", len(env.client_ids),
            "| 打开文件:", list(env.opened_files.keys()),
        )


if __name__ == "__main__":
    main()
