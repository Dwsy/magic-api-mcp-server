"""Magic-API 搜索相关 MCP 工具。

此模块提供强大的搜索功能，支持：
- API脚本内容关键词搜索
- TODO注释搜索
- 代码片段定位
- 全文检索和过滤

主要工具：
- search_api_scripts: 在所有API脚本中搜索关键词
- search_todo_comments: 搜索API脚本中的TODO注释
"""

from __future__ import annotations

import json
import requests
from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional

from pydantic import Field

from magicapi_tools.logging_config import get_logger
from magicapi_tools.tools.common import error_response

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext

# 获取搜索工具的logger
logger = get_logger('tools.search')


class SearchTools:
    """搜索工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册搜索相关工具。"""

        @mcp_app.tool(
            name="search_api_scripts",
            description="在所有API脚本中搜索关键词。",
            tags={"search", "keyword", "api", "scripts"},
        )
        def search_api_scripts_tool(
            keyword: Annotated[
                str,
                Field(description="搜索关键词")
            ],
            limit: Annotated[
                int,
                Field(description="返回结果的最大数量，默认5条")
            ] = 5,
        ) -> Dict[str, Any]:
            """搜索API脚本中的关键词。"""
            try:
                if not keyword.strip():
                    return error_response("invalid_param", "搜索关键词不能为空")

                # 直接使用session发送表单数据（因为call_api会将dict转换为JSON）
                search_data = {'keyword': keyword}
                url = f"{context.settings.base_url}/magic/web/search"

                # 设置请求头
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": "magicapi-search-manager/1.0",
                }
                context.settings.inject_auth(headers)

                try:
                    http_response = context.http_client.session.post(
                        url,
                        data=search_data,
                        headers=headers,
                        timeout=context.settings.timeout_seconds
                    )
                    http_response.raise_for_status()

                    # 手动处理响应
                    content_type = http_response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        try:
                            data = http_response.json()
                        except json.JSONDecodeError:
                            data = http_response.text
                    else:
                        data = http_response.text

                    response = {
                        "status": http_response.status_code,
                        "headers": dict(http_response.headers),
                        "body": data,
                    }
                    ok = True

                except requests.RequestException as exc:
                    ok = False
                    response = {
                        "code": "network_error",
                        "message": "搜索API脚本失败",
                        "detail": str(exc),
                    }

                if not ok:
                    return error_response(
                        response.get("code", "network_error"),
                        response.get("message", "搜索API脚本失败"),
                        response.get("detail")
                    )

                data = response.get("body", {})
                if data.get("code") != 1:
                    return error_response(
                        data.get("code", -1),
                        data.get("message", "搜索API脚本失败"),
                        data.get("data")
                    )

                results = data.get("data", [])

                # 为搜索结果添加API名称
                if results:
                    # 收集所有API ID
                    api_ids = [result.get("id") for result in results if result.get("id")]

                    # 批量获取API详情来获取名称、方法和路径
                    api_info_map = {}
                    for api_id in api_ids:
                        try:
                            ok, payload = context.http_client.api_detail(api_id)
                            if ok and payload:
                                api_name = payload.get("name", "")
                                api_method = payload.get("method", "")
                                api_path = payload.get("path", "")
                                if api_name:
                                    # 构建完整路径：方法 + 路径
                                    full_path = ""
                                    if api_method and api_path:
                                        full_path = f"{api_method} {api_path}"
                                    elif api_method:
                                        full_path = api_method
                                    elif api_path:
                                        full_path = api_path
                                    else:
                                        full_path = "未知路径"

                                    api_info_map[api_id] = {
                                        "name": api_name,
                                        "full_path": full_path
                                    }
                        except Exception as exc:
                            logger.warning(f"获取API {api_id} 详情失败: {exc}")
                            continue

                    # 为每个搜索结果添加名称和完整路径
                    for result in results:
                        api_id = result.get("id")
                        if api_id and api_id in api_info_map:
                            result["name"] = api_info_map[api_id]["name"]
                            result["full_path"] = api_info_map[api_id]["full_path"]
                        else:
                            result["name"] = "未知"
                            result["full_path"] = "未知路径"

                # 应用 limit 限制
                if limit > 0:
                    results = results[:limit]

                return {
                    "keyword": keyword,
                    "total_results": len(results),
                    "limit": limit,
                    "results": results,
                    "search_type": "api_scripts",
                }

            except Exception as exc:
                return error_response("search_error", f"搜索API脚本失败: {exc}", str(exc))

        @mcp_app.tool(
            name="search_todo_comments",
            description="搜索所有TODO注释。",
            tags={"search", "todo", "comments", "tasks"},
            enabled=False
        )
        def search_todo_comments_tool(
            limit: Annotated[
                int,
                Field(description="返回结果的最大数量，默认5条")
            ] = 5,
        ) -> Dict[str, Any]:
            """搜索TODO注释。"""
            try:
                # 直接使用session发送GET请求
                url = f"{context.settings.base_url}/magic/web/todo"

                # 设置请求头
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": "magicapi-search-manager/1.0",
                }
                context.settings.inject_auth(headers)

                try:
                    http_response = context.http_client.session.get(
                        url,
                        headers=headers,
                        timeout=context.settings.timeout_seconds
                    )
                    http_response.raise_for_status()

                    # 手动处理响应
                    content_type = http_response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        try:
                            data = http_response.json()
                        except json.JSONDecodeError:
                            data = http_response.text
                    else:
                        data = http_response.text

                    response = {
                        "status": http_response.status_code,
                        "headers": dict(http_response.headers),
                        "body": data,
                    }
                    ok = True

                except requests.RequestException as exc:
                    ok = False
                    response = {
                        "code": "network_error",
                        "message": "搜索TODO注释失败",
                        "detail": str(exc),
                    }

                if not ok:
                    return error_response(
                        response.get("code", "network_error"),
                        response.get("message", "搜索TODO注释失败"),
                        response.get("detail")
                    )

                data = response.get("body", {})
                if data.get("code") != 1:
                    return error_response(
                        data.get("code", -1),
                        data.get("message", "搜索TODO注释失败"),
                        data.get("data")
                    )

                results = data.get("data", [])

                # 应用 limit 限制
                if limit > 0:
                    results = results[:limit]

                return {
                    "total_todos": len(results),
                    "limit": limit,
                    "todo_comments": results,
                    "search_type": "todo_comments",
                }

            except Exception as exc:
                return error_response("todo_search_error", f"搜索TODO注释失败: {exc}", str(exc))


