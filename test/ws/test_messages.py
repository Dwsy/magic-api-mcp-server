#!/usr/bin/env python3
"""测试 WebSocket 消息解析功能。"""

import os
import sys
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from magicapi_tools.ws.messages import MessageType, parse_ws_message


def test_log_message():
    print("🧪 测试 LOG 消息解析")
    message = parse_ws_message("log,这是一条日志")
    assert message.type == MessageType.LOG
    assert message.text == "这是一条日志"
    assert message.data["logs"] == ["这是一条日志"]


def test_login_response():
    print("🧪 测试 LOGIN_RESPONSE 消息解析")
    raw = "login_response,1,{\"clientId\":\"abc123\",\"loginIp\":\"127.0.0.1\"}"
    message = parse_ws_message(raw)
    assert message.type == MessageType.LOGIN_RESPONSE
    assert message.data["status"] == 1
    assert message.data["user"]["clientId"] == "abc123"


def test_breakpoint_message():
    print("🧪 测试 BREAKPOINT 消息解析")
    raw = "breakpoint,script123,{\"range\":[5,1,5,10],\"variables\":[{\"name\":\"var\",\"type\":\"java.lang.String\",\"value\":\"demo\"}]}"
    message = parse_ws_message(raw)
    assert message.type == MessageType.BREAKPOINT
    assert message.data["script_id"] == "script123"
    assert message.data["payload"]["range"][0] == 5


if __name__ == "__main__":
    test_log_message()
    test_login_response()
    test_breakpoint_message()
    print("✅ WebSocket 消息解析测试完成")
