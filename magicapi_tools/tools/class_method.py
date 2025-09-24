"""Magic-API 类和方法检索 MCP 工具。

此模块提供Java类和方法的检索功能，支持：
- 类和方法的分页浏览
- 类详细信息查询
- 方法签名和参数信息获取
- 继承关系和接口实现查询
- 构造函数和静态方法识别

主要工具：
- list_magic_api_classes: 列出所有Magic-API可用的类、扩展和函数，支持翻页浏览
- get_class_details: 获取指定类的详细信息，包括方法、属性和继承关系
- get_method_details: 获取指定方法的详细信息，包括参数类型和返回值
"""

from __future__ import annotations

import json
import re
import requests
from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional

from pydantic import Field

from magicapi_tools.tools.common import error_response

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext


class ClassMethodTools:
    """类和方法检索工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册类和方法检索相关工具。"""

        @mcp_app.tool(
            name="list_magic_api_classes",
            description="列出所有 Magic-API 可用的类、扩展和函数，支持翻页浏览。",
            tags={"class", "method", "list", "browse", "pagination"},
        )
        def list_magic_api_classes_tool(
            page: Annotated[
                int,
                Field(description="页码，从1开始，默认1")
            ] = 1,
            page_size: Annotated[
                int,
                Field(description="每页显示的数量，默认10")
            ] = 10,
            limit: Annotated[
                int,
                Field(description="限制返回的最大结果数量，默认10，节约大模型token")
            ] = 10,
        ) -> Dict[str, Any]:
            """列出所有 Magic-API 可用的类、扩展和函数。"""
            try:
                if page < 1:
                    return error_response("invalid_param", "页码必须大于等于1")
                if page_size < 1:
                    return error_response("invalid_param", "每页大小必须大于等于1")
                if limit < 1:
                    return error_response("invalid_param", "限制数量必须大于等于1")

                # 获取类信息
                classes_url = f"{context.settings.base_url}/magic/web/classes"
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": "magicapi-class-explorer/1.0",
                }
                context.settings.inject_auth(headers)

                try:
                    response = context.http_client.session.post(
                        classes_url,
                        headers=headers,
                        timeout=context.settings.timeout_seconds
                    )
                    response.raise_for_status()

                    # classes 端点返回 JSON，检查 code 字段
                    classes_data = response.json()
                    if classes_data.get("code") != 1:
                        return error_response("api_error", "获取类信息失败", classes_data)
                except requests.RequestException as exc:
                    return error_response("network_error", f"获取类信息失败: {exc}")
                except json.JSONDecodeError:
                    return error_response("api_error", "API 返回格式错误")

                data = classes_data.get("data", {})

                # 收集所有项目
                all_items = []

                # 脚本类
                if "classes" in data and data["classes"]:
                    for class_name in sorted(data["classes"].keys()):
                        all_items.append(("class", class_name))

                # 扩展类
                if "extensions" in data and data["extensions"]:
                    for class_name in sorted(data["extensions"].keys()):
                        all_items.append(("extension", class_name))

                # 函数
                if "functions" in data and data["functions"]:
                    for func_name in sorted(data["functions"].keys()):
                        all_items.append(("function", func_name))

                # 应用翻页
                total_items = len(all_items)
                total_pages = (total_items + page_size - 1) // page_size

                if page > total_pages and total_pages > 0:
                    return error_response("invalid_param", f"页码 {page} 超出范围，总共 {total_pages} 页")

                start_index = (page - 1) * page_size
                end_index = min(start_index + page_size, total_items)
                paginated_items = all_items[start_index:end_index]

                # 应用 limit 限制
                if len(paginated_items) > limit:
                    paginated_items = paginated_items[:limit]

                # 按类别分组结果
                grouped_results = {
                    "classes": [],
                    "extensions": [],
                    "functions": []
                }

                for item_type, item_name in paginated_items:
                    if item_type == "class":
                        grouped_results["classes"].append(item_name)
                    elif item_type == "extension":
                        grouped_results["extensions"].append(item_name)
                    elif item_type == "function":
                        grouped_results["functions"].append(item_name)

                return {
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "displayed_items": len(paginated_items),
                    "limit": limit,
                    "has_more": page < total_pages,
                    "results": grouped_results,
                    "summary": {
                        "classes_count": len(grouped_results["classes"]),
                        "extensions_count": len(grouped_results["extensions"]),
                        "functions_count": len(grouped_results["functions"])
                    }
                }

            except Exception as exc:
                return error_response("list_error", f"列出类信息失败: {exc}")

        @mcp_app.tool(
            name="search_magic_api_classes",
            description="在 Magic-API 类信息中进行增强搜索，支持正则表达式、关键词、多条件过滤。",
            tags={"class", "method", "search", "regex", "filter", "pagination"},
        )
        def search_magic_api_classes_tool(
            pattern: Annotated[
                str,
                Field(description="搜索模式：关键词或正则表达式")
            ],
            search_type: Annotated[
                str,
                Field(description="搜索类型：keyword（关键词）或 regex（正则表达式）", choices=["keyword", "regex"])
            ] = "keyword",
            case_sensitive: Annotated[
                bool,
                Field(description="是否区分大小写，默认false")
            ] = False,
            logic: Annotated[
                str,
                Field(description="多关键词逻辑：and 或 or，默认or", choices=["and", "or"])
            ] = "or",
            scope: Annotated[
                str,
                Field(description="搜索范围：all（全部）、class（仅类名）、method（仅方法）、field（仅字段），默认all", choices=["all", "class", "method", "field"])
            ] = "all",
            exact: Annotated[
                bool,
                Field(description="是否精确匹配，默认false")
            ] = False,
            exclude_pattern: Annotated[
                Optional[str],
                Field(description="排除包含此模式的匹配项")
            ] = None,
            page: Annotated[
                int,
                Field(description="页码，从1开始，默认1")
            ] = 1,
            page_size: Annotated[
                int,
                Field(description="每页显示的数量，默认10")
            ] = 10,
            limit: Annotated[
                int,
                Field(description="限制返回的最大结果数量，默认10，节约大模型token")
            ] = 10,
        ) -> Dict[str, Any]:
            """在 Magic-API 类信息中进行增强搜索。"""
            try:
                if page < 1:
                    return error_response("invalid_param", "页码必须大于等于1")
                if page_size < 1:
                    return error_response("invalid_param", "每页大小必须大于等于1")
                if limit < 1:
                    return error_response("invalid_param", "限制数量必须大于等于1")
                if not pattern.strip():
                    return error_response("invalid_param", "搜索模式不能为空")

                # 验证正则表达式
                if search_type == "regex":
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        return error_response("invalid_param", f"无效的正则表达式: {e}")

                # 获取类信息
                classes_url = f"{context.settings.base_url}/magic/web/classes"
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": "magicapi-class-explorer/1.0",
                }
                context.settings.inject_auth(headers)

                try:
                    response = context.http_client.session.post(
                        classes_url,
                        headers=headers,
                        timeout=context.settings.timeout_seconds
                    )
                    response.raise_for_status()

                    # classes 端点返回 JSON，检查 code 字段
                    classes_data = response.json()
                    if classes_data.get("code") != 1:
                        return error_response("api_error", "获取类信息失败", classes_data)
                except requests.RequestException as exc:
                    return error_response("network_error", f"获取类信息失败: {exc}")
                except json.JSONDecodeError:
                    return error_response("api_error", "API 返回格式错误")

                data = classes_data.get("data", {})

                # 执行搜索
                results = self._perform_enhanced_search(
                    data, pattern, search_type, case_sensitive, logic, scope, exact, exclude_pattern
                )

                # 收集所有匹配的项目用于翻页
                all_matches = []

                # 添加匹配的脚本类
                for class_name in results["classes"]:
                    all_matches.append(("class", class_name, "class"))

                # 添加匹配的扩展类
                for class_name in results["extensions"]:
                    all_matches.append(("extension", class_name, "extension"))

                # 添加匹配的函数
                for func_name in results["functions"]:
                    all_matches.append(("function", func_name, "function"))

                # 添加详细匹配
                for match in results["detailed_matches"]:
                    class_name = match["class_name"]
                    for method in match["methods"]:
                        method_name = method["name"]
                        return_type = method["return_type"]
                        params = method["parameters"]
                        params_str = ", ".join([
                            f"{p.get('type', 'Object')} {p.get('name', 'arg')}"
                            for p in params if isinstance(p, dict)
                        ])
                        details = f"{return_type} {method_name}({params_str})"
                        all_matches.append(("method", f"{class_name}.{method_name}", f"method:{details}"))

                    for field in match["fields"]:
                        field_name = field["name"]
                        field_type = field["type"]
                        details = f"{field_type} {field_name}"
                        all_matches.append(("field", f"{class_name}.{field_name}", f"field:{details}"))

                # 应用翻页
                total_matches = len(all_matches)
                total_pages = (total_matches + page_size - 1) // page_size

                if page > total_pages and total_pages > 0:
                    return error_response("invalid_param", f"页码 {page} 超出范围，总共 {total_pages} 页")

                start_index = (page - 1) * page_size
                end_index = min(start_index + page_size, total_matches)
                paginated_matches = all_matches[start_index:end_index]

                # 应用 limit 限制
                if len(paginated_matches) > limit:
                    paginated_matches = paginated_matches[:limit]

                # 按类别分组结果
                grouped_results = {
                    "classes": [],
                    "extensions": [],
                    "functions": [],
                    "detailed_matches": []
                }

                for category, item_name, item_type in paginated_matches:
                    if category == "class":
                        grouped_results["classes"].append(item_name)
                    elif category == "extension":
                        grouped_results["extensions"].append(item_name)
                    elif category == "function":
                        grouped_results["functions"].append(item_name)
                    elif category in ["method", "field"]:
                        # 解析详细匹配
                        if ":" in item_type:
                            match_type, details = item_type.split(":", 1)
                            grouped_results["detailed_matches"].append({
                                "type": match_type,
                                "name": item_name,
                                "details": details
                            })

                # 计算原始匹配总数
                original_total = (len(results["classes"]) + len(results["extensions"]) +
                                len(results["functions"]) + len(results["detailed_matches"]))

                return {
                    "pattern": pattern,
                    "search_type": search_type,
                    "case_sensitive": case_sensitive,
                    "logic": logic,
                    "scope": scope,
                    "exact": exact,
                    "exclude_pattern": exclude_pattern,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_matches": original_total,
                    "displayed_matches": len(paginated_matches),
                    "limit": limit,
                    "has_more": page < total_pages,
                    "results": grouped_results,
                    "summary": {
                        "classes_count": len(grouped_results["classes"]),
                        "extensions_count": len(grouped_results["extensions"]),
                        "functions_count": len(grouped_results["functions"]),
                        "detailed_matches_count": len(grouped_results["detailed_matches"])
                    }
                }

            except Exception as exc:
                return error_response("search_error", f"搜索类信息失败: {exc}")

        @mcp_app.tool(
            name="search_magic_api_classes_txt",
            description="在 Magic-API 压缩类信息中进行快速搜索。",
            tags={"class", "search", "compressed", "txt", "pagination"},
        )
        def search_magic_api_classes_txt_tool(
            keyword: Annotated[
                str,
                Field(description="搜索关键词")
            ],
            case_sensitive: Annotated[
                bool,
                Field(description="是否区分大小写，默认false")
            ] = False,
            page: Annotated[
                int,
                Field(description="页码，从1开始，默认1")
            ] = 1,
            page_size: Annotated[
                int,
                Field(description="每页显示的数量，默认10")
            ] = 10,
            limit: Annotated[
                int,
                Field(description="限制返回的最大结果数量，默认10，节约大模型token")
            ] = 10,
        ) -> Dict[str, Any]:
            """在压缩类信息中搜索关键词。"""
            try:
                if page < 1:
                    return error_response("invalid_param", "页码必须大于等于1")
                if page_size < 1:
                    return error_response("invalid_param", "每页大小必须大于等于1")
                if limit < 1:
                    return error_response("invalid_param", "限制数量必须大于等于1")
                if not keyword.strip():
                    return error_response("invalid_param", "搜索关键词不能为空")

                # 获取压缩类信息
                classes_txt_url = f"{context.settings.base_url}/magic/web/classes.txt"
                headers = {
                    "Accept": "text/plain",
                    "User-Agent": "magicapi-class-explorer/1.0",
                }
                context.settings.inject_auth(headers)

                try:
                    response = context.http_client.session.get(
                        classes_txt_url,
                        headers=headers,
                        timeout=context.settings.timeout_seconds
                    )
                    response.raise_for_status()
                    classes_txt_data = response.text
                except requests.RequestException as exc:
                    return error_response("network_error", f"获取压缩类信息失败: {exc}")

                # 解析并搜索
                lines = classes_txt_data.strip().split('\n')
                all_matches = []

                for line in lines:
                    if ':' in line:
                        package_name, classes_str = line.split(':', 1)
                        class_list = classes_str.split(',')

                        # 搜索包名
                        if self._match_pattern(package_name, keyword, case_sensitive):
                            for cls in class_list:
                                all_matches.append(("package_match", f"{package_name}.{cls}", "package"))
                            continue

                        # 搜索类名
                        for cls in class_list:
                            if self._match_pattern(cls, keyword, case_sensitive):
                                all_matches.append(("class_match", f"{package_name}.{cls}", "class"))

                # 应用翻页
                total_matches = len(all_matches)
                total_pages = (total_matches + page_size - 1) // page_size

                if page > total_pages and total_pages > 0:
                    return error_response("invalid_param", f"页码 {page} 超出范围，总共 {total_pages} 页")

                start_index = (page - 1) * page_size
                end_index = min(start_index + page_size, total_matches)
                paginated_matches = all_matches[start_index:end_index]

                # 应用 limit 限制
                if len(paginated_matches) > limit:
                    paginated_matches = paginated_matches[:limit]

                # 按类别分组结果
                grouped_results = {
                    "package_matches": [],
                    "class_matches": []
                }

                for category, item_name, match_type in paginated_matches:
                    if category == "package_match":
                        grouped_results["package_matches"].append(item_name)
                    elif category == "class_match":
                        grouped_results["class_matches"].append(item_name)

                return {
                    "keyword": keyword,
                    "case_sensitive": case_sensitive,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_matches": total_matches,
                    "displayed_matches": len(paginated_matches),
                    "limit": limit,
                    "has_more": page < total_pages,
                    "results": grouped_results,
                    "summary": {
                        "package_matches_count": len(grouped_results["package_matches"]),
                        "class_matches_count": len(grouped_results["class_matches"])
                    }
                }

            except Exception as exc:
                return error_response("search_txt_error", f"搜索压缩类信息失败: {exc}")

        @mcp_app.tool(
            name="get_magic_api_class_details",
            description="获取指定 Magic-API 类的详细信息，包括方法和字段。",
            tags={"class", "method", "details", "info"},
        )
        def get_magic_api_class_details_tool(
            class_name: Annotated[
                str,
                Field(description="类名")
            ],
        ) -> Dict[str, Any]:
            """获取指定类的详细信息。"""
            try:
                if not class_name.strip():
                    return error_response("invalid_param", "类名不能为空")

                # 获取类详情
                class_url = f"{context.settings.base_url}/magic/web/class"
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": "magicapi-class-explorer/1.0",
                }
                context.settings.inject_auth(headers)

                try:
                    response = context.http_client.session.post(
                        class_url,
                        data={"className": class_name},
                        headers=headers,
                        timeout=context.settings.timeout_seconds
                    )
                    response.raise_for_status()

                    # class 端点返回 JSON，检查 code 字段
                    class_data = response.json()
                    if class_data.get("code") != 1:
                        return error_response("api_error", f"获取类 '{class_name}' 详情失败", class_data)
                except requests.RequestException as exc:
                    return error_response("network_error", f"获取类详情失败: {exc}")
                except json.JSONDecodeError:
                    return error_response("api_error", "API 返回格式错误")

                script_classes = class_data.get("data", [])

                if not script_classes:
                    return error_response("not_found", f"未找到类 '{class_name}' 的信息")

                # 格式化结果
                formatted_details = []
                for script_class in script_classes:
                    if isinstance(script_class, dict):
                        class_info = {
                            "class_name": class_name,
                            "methods": [],
                            "fields": []
                        }

                        # 处理方法
                        if "methods" in script_class:
                            for method in script_class["methods"]:
                                if isinstance(method, dict):
                                    method_info = {
                                        "name": method.get("name", "unknown"),
                                        "return_type": method.get("returnType", "Object"),
                                        "parameters": []
                                    }

                                    # 处理参数
                                    if "parameters" in method and isinstance(method["parameters"], list):
                                        for param in method["parameters"]:
                                            if isinstance(param, dict):
                                                method_info["parameters"].append({
                                                    "name": param.get("name", "arg"),
                                                    "type": param.get("type", "Object")
                                                })

                                    class_info["methods"].append(method_info)

                        # 处理字段
                        if "fields" in script_class:
                            for field in script_class["fields"]:
                                if isinstance(field, dict):
                                    class_info["fields"].append({
                                        "name": field.get("name", "unknown"),
                                        "type": field.get("type", "Object")
                                    })

                        formatted_details.append(class_info)

                return {
                    "class_name": class_name,
                    "details": formatted_details,
                    "summary": {
                        "total_details": len(formatted_details),
                        "methods_count": sum(len(detail["methods"]) for detail in formatted_details),
                        "fields_count": sum(len(detail["fields"]) for detail in formatted_details)
                    }
                }

            except Exception as exc:
                return error_response("details_error", f"获取类详情失败: {exc}")

    def _match_pattern(self, text: str, pattern: str, case_sensitive: bool = False,
                      exact: bool = False, is_regex: bool = False) -> bool:
        """检查文本是否匹配搜索模式。"""
        if not text:
            return False

        if is_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                return bool(re.search(pattern, text, flags))
            except re.error:
                return False

        # 关键词匹配
        if exact:
            if case_sensitive:
                return pattern == text
            else:
                return pattern.lower() == text.lower()

        # 包含匹配
        if case_sensitive:
            return pattern in text
        else:
            return pattern.lower() in text.lower()

    def _perform_enhanced_search(self, data: Dict[str, Any], pattern: str, search_type: str,
                               case_sensitive: bool, logic: str, scope: str, exact: bool,
                               exclude_pattern: Optional[str] = None) -> Dict[str, Any]:
        """执行增强搜索。"""
        is_regex = (search_type == "regex")

        # 处理多关键词
        keywords = [kw.strip() for kw in pattern.split() if kw.strip()]

        results = {
            "classes": [],
            "extensions": [],
            "functions": [],
            "detailed_matches": []
        }

        # 搜索脚本类
        if "classes" in data and scope in ["all", "class"]:
            for class_name in data["classes"].keys():
                if self._matches_keywords(class_name, keywords, logic, case_sensitive, exact, is_regex, exclude_pattern):
                    results["classes"].append(class_name)

        # 搜索扩展类
        if "extensions" in data and scope in ["all", "class"]:
            for class_name in data["extensions"].keys():
                if self._matches_keywords(class_name, keywords, logic, case_sensitive, exact, is_regex, exclude_pattern):
                    results["extensions"].append(class_name)

        # 搜索函数
        if "functions" in data and scope in ["all", "class"]:
            for func_name in data["functions"].keys():
                if self._matches_keywords(func_name, keywords, logic, case_sensitive, exact, is_regex, exclude_pattern):
                    results["functions"].append(func_name)

        return results

    def _matches_keywords(self, text: str, keywords: List[str], logic: str, case_sensitive: bool,
                         exact: bool, is_regex: bool, exclude_pattern: Optional[str]) -> bool:
        """检查文本是否匹配关键词列表。"""
        if not keywords:
            return False

        # 检查排除模式
        if exclude_pattern and self._match_pattern(text, exclude_pattern, case_sensitive, False, False):
            return False

        if logic == "and":
            return all(self._match_pattern(text, kw, case_sensitive, exact, is_regex) for kw in keywords)
        else:  # "or"
            return any(self._match_pattern(text, kw, case_sensitive, exact, is_regex) for kw in keywords)
