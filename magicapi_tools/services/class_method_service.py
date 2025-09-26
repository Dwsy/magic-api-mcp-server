"""类和方法检索业务服务。

处理所有类和方法检索相关的业务逻辑。
"""

from __future__ import annotations

import json
import re
import requests
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import (
    create_operation_error,
)
from magicapi_tools.domain.dtos.class_method_dtos import (
    ClassSearchRequest,
    ClassSearchResponse,
    ClassDetailRequest,
    ClassDetailResponse,
    ClassInfo,
    MethodInfo,
    FieldInfo,
)

from .base_service import BaseService

if TYPE_CHECKING:
    from magicapi_mcp.tool_registry import ToolContext

logger = get_logger('services.class_method')


class ClassMethodService(BaseService):
    """类和方法检索业务服务类。"""

    def list_magic_classes(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> ClassSearchResponse:
        """列出所有 Magic-API 可用的类、扩展和函数。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.class_method')

        log_operation_start("列出类信息", {"page": page, "page_size": page_size})

        try:
            result = self._list_magic_classes_impl(page, page_size)

            # 如果_impl方法返回Dict，转换为DTO
            if isinstance(result, dict):
                if "error" in result:
                    response = ClassSearchResponse(
                        success=False,
                        query_type="list",
                        page=page,
                        page_size=page_size,
                        summary={"error": result["error"]}
                    )
                else:
                    response = ClassSearchResponse(
                        success=True,
                        query_type="list",
                        page=page,
                        page_size=page_size,
                        total_count=result.get("total_items", 0),
                        total_pages=result.get("total_pages", 0),
                        displayed_count=result.get("displayed_items", 0),
                        has_more=result.get("has_more", False),
                        classes=result.get("results", {}).get("classes", []),
                        extensions=result.get("results", {}).get("extensions", []),
                        functions=result.get("results", {}).get("functions", []),
                        summary=result.get("summary", {})
                    )
            else:
                response = result

            log_operation_end("列出类信息", response.success)
            return response
        except Exception as e:
            logger.error(f"列出类信息失败: {e}")
            return ClassSearchResponse(
                success=False,
                query_type="list",
                page=page,
                page_size=page_size,
                summary={"error": str(e)}
            )

    def _list_magic_classes_impl(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """列出所有 Magic-API 可用的类、扩展和函数的实现。"""
        # 获取类信息
        classes_url = f"{self.settings.base_url}/magic/web/classes"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "magicapi-class-explorer/1.0",
        }
        self.settings.inject_auth(headers)

        try:
            logger.info(f"🔍 [ClassService] 发送HTTP请求: POST {classes_url}")
            logger.info(f"🔍 [ClassService] 请求头: {headers}")
            response = self.http_client.session.post(
                classes_url,
                headers=headers,
                timeout=self.settings.timeout_seconds
            )
            response.raise_for_status()

            # classes 端点返回 JSON，检查 code 字段
            classes_data = response.json()
            if classes_data.get("code") != 1:
                return create_operation_error("获取类信息", "api_error", "获取类信息失败", classes_data)
        except requests.RequestException as exc:
            return create_operation_error("获取类信息", "network_error", f"获取类信息失败: {exc}")
        except json.JSONDecodeError:
            return create_operation_error("获取类信息", "api_error", "API 返回格式错误")

        data = classes_data.get("data", {})

        # 收集所有项目
        all_items = []

        # 脚本类
        class_names = self._extract_names(data.get("classes", {}))
        for class_name in sorted(class_names):
            all_items.append(("class", class_name))

        # 扩展类
        extension_names = self._extract_names(data.get("extensions", {}))
        for class_name in sorted(extension_names):
            all_items.append(("extension", class_name))

        # 函数
        function_names = self._extract_names(data.get("functions", {}))
        for func_name in sorted(function_names):
            all_items.append(("function", func_name))

        # 应用翻页
        total_items = len(all_items)

        # 基于每页大小计算总页数
        total_pages = (total_items + page_size - 1) // page_size

        if page > total_pages and total_pages > 0:
            return create_operation_error("分页", "invalid_param", f"页码 {page} 超出范围，总共 {total_pages} 页")

        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_items)
        paginated_items = all_items[start_index:end_index]

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
            "has_more": page < total_pages,
            "results": grouped_results,
            "summary": {
                "classes_count": len(grouped_results["classes"]),
                "extensions_count": len(grouped_results["extensions"]),
                "functions_count": len(grouped_results["functions"])
            }
        }

    def search_magic_classes(
        self,
        request: ClassSearchRequest
    ) -> ClassSearchResponse:
        """在 Magic-API 类信息中进行增强搜索。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.class_method')

        # 验证请求
        if not request.validate():
            errors = request.get_validation_errors()
            return ClassSearchResponse(
                success=False,
                query_type="search",
                page=request.page,
                page_size=request.page_size,
                limit=request.limit,
                summary={"validation_errors": errors}
            )

        log_operation_start("搜索类信息", {
            "pattern": request.pattern,
            "search_type": request.search_type,
            "page": request.page
        })

        try:
            result = self._search_magic_classes_impl(request)

            # 如果_impl方法返回Dict，转换为DTO
            if isinstance(result, dict):
                if "error" in result:
                    response = ClassSearchResponse(
                        success=False,
                        query_type="search",
                        page=request.page,
                        page_size=request.page_size,
                        limit=request.limit,
                        summary={"error": result["error"]}
                    )
                else:
                    # 计算有效的每页大小（与_impl方法保持一致）
                    effective_page_size = min(request.page_size, request.limit) if request.limit is not None and request.limit > 0 else request.page_size

                    response = ClassSearchResponse(
                        success=True,
                        query_type="search",
                        pattern=request.pattern,
                        page=request.page,
                        page_size=effective_page_size,
                        total_pages=result.get("total_pages", 0),
                        displayed_count=result.get("displayed_matches", 0),
                        limit=request.limit,
                        has_more=result.get("has_more", False),
                        classes=result.get("results", {}).get("classes", []),
                        extensions=result.get("results", {}).get("extensions", []),
                        functions=result.get("results", {}).get("functions", []),
                        detailed_matches=result.get("results", {}).get("detailed_matches", []),
                        summary=result.get("summary", {})
                    )
            else:
                response = result

            log_operation_end("搜索类信息", response.success)
            return response
        except Exception as e:
            logger.error(f"搜索类信息失败: {e}")
            return ClassSearchResponse(
                success=False,
                query_type="search",
                pattern=request.pattern,
                page=request.page,
                page_size=request.page_size,
                limit=request.limit,
                summary={"error": str(e)}
            )

    def _search_magic_classes_impl(self, request: ClassSearchRequest) -> Dict[str, Any]:
        """在 Magic-API 类信息中进行增强搜索的实现。"""
        # 验证正则表达式
        if request.search_type == "regex":
            try:
                re.compile(request.pattern)
            except re.error as e:
                return create_operation_error("正则表达式验证", "invalid_param", f"无效的正则表达式: {e}")

        # 获取类信息
        classes_url = f"{self.settings.base_url}/magic/web/classes"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "magicapi-class-explorer/1.0",
        }
        self.settings.inject_auth(headers)

        try:
            logger.info(f"🔍 [ClassService] 发送HTTP请求: POST {classes_url}")
            logger.info(f"🔍 [ClassService] 请求头: {headers}")
            response = self.http_client.session.post(
                classes_url,
                headers=headers,
                timeout=self.settings.timeout_seconds
            )
            response.raise_for_status()

            # classes 端点返回 JSON，检查 code 字段
            classes_data = response.json()
            if classes_data.get("code") != 1:
                return create_operation_error("获取类信息", "api_error", "获取类信息失败", classes_data)
        except requests.RequestException as exc:
            return create_operation_error("获取类信息", "network_error", f"获取类信息失败: {exc}")
        except json.JSONDecodeError:
            return create_operation_error("获取类信息", "api_error", "API 返回格式错误")

        data = classes_data.get("data", {})

        # 执行搜索
        results = self._perform_enhanced_search(
            data, request.pattern, request.search_type, request.case_sensitive,
            request.logic, request.scope, request.exact, request.exclude_pattern
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

        # 应用翻页和限制
        total_matches = len(all_matches)

        # 计算有效的每页大小（受limit限制）
        effective_page_size = min(request.page_size, request.limit) if request.limit is not None and request.limit > 0 else request.page_size

        # 基于有效每页大小计算总页数
        total_pages = (total_matches + effective_page_size - 1) // effective_page_size

        if request.page > total_pages and total_pages > 0:
            return create_operation_error("分页", "invalid_param", f"页码 {request.page} 超出范围，总共 {total_pages} 页")

        start_index = (request.page - 1) * effective_page_size
        end_index = min(start_index + effective_page_size, total_matches)
        paginated_matches = all_matches[start_index:end_index]

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
            "pattern": request.pattern,
            "search_type": request.search_type,
            "case_sensitive": request.case_sensitive,
            "logic": request.logic,
            "scope": request.scope,
            "exact": request.exact,
            "exclude_pattern": request.exclude_pattern,
            "page": request.page,
            "page_size": request.page_size,
            "total_pages": total_pages,
            "total_matches": original_total,
            "displayed_matches": len(paginated_matches),
            "limit": request.limit,
            "has_more": request.page < total_pages,
            "results": grouped_results,
            "summary": {
                "classes_count": len(grouped_results["classes"]),
                "extensions_count": len(grouped_results["extensions"]),
                "functions_count": len(grouped_results["functions"]),
                "detailed_matches_count": len(grouped_results["detailed_matches"])
            }
        }

    def search_magic_classes_txt(
        self,
        keyword: str,
        case_sensitive: bool = False,
        page: int = 1,
        page_size: int = 10
    ) -> ClassSearchResponse:
        """在压缩类信息中搜索关键词。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.class_method')

        log_operation_start("搜索压缩类信息", {"keyword": keyword, "page": page})

        try:
            result = self._search_magic_classes_txt_impl(keyword, case_sensitive, page, page_size)

            # 如果_impl方法返回Dict，转换为DTO
            if isinstance(result, dict):
                if "error" in result:
                    response = ClassSearchResponse(
                        success=False,
                        query_type="search_txt",
                        page=page,
                        page_size=page_size,
                        summary={"error": result["error"]}
                    )
                else:
                    response = ClassSearchResponse(
                        success=True,
                        query_type="search_txt",
                        page=page,
                        page_size=page_size,
                        total_pages=result.get("total_pages", 0),
                        displayed_count=result.get("displayed_matches", 0),
                        has_more=result.get("has_more", False),
                        package_matches=result.get("results", {}).get("package_matches", []),
                        class_matches=result.get("results", {}).get("class_matches", []),
                        summary=result.get("summary", {})
                    )
            else:
                response = result

            log_operation_end("搜索压缩类信息", response.success)
            return response
        except Exception as e:
            logger.error(f"搜索压缩类信息失败: {e}")
            return ClassSearchResponse(
                success=False,
                query_type="search_txt",
                page=page,
                page_size=page_size,
                summary={"error": str(e)}
            )

    def _search_magic_classes_txt_impl(
        self,
        keyword: str,
        case_sensitive: bool = False,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """在压缩类信息中搜索关键词的实现。"""
        # 获取压缩类信息
        classes_txt_url = f"{self.settings.base_url}/magic/web/classes.txt"
        headers = {
            "Accept": "text/plain",
            "User-Agent": "magicapi-class-explorer/1.0",
        }
        self.settings.inject_auth(headers)

        try:
            logger.info(f"🔍 [ClassService] 发送HTTP请求: GET {classes_txt_url}")
            logger.info(f"🔍 [ClassService] 请求头: {headers}")
            response = self.http_client.session.get(
                classes_txt_url,
                headers=headers,
                timeout=self.settings.timeout_seconds
            )
            response.raise_for_status()
            classes_txt_data = response.text
        except requests.RequestException as exc:
            return create_operation_error("获取压缩类信息", "network_error", f"获取压缩类信息失败: {exc}")

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

        # 基于每页大小计算总页数
        total_pages = (total_matches + page_size - 1) // page_size

        if page > total_pages and total_pages > 0:
            return create_operation_error("分页", "invalid_param", f"页码 {page} 超出范围，总共 {total_pages} 页")

        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_matches)
        paginated_matches = all_matches[start_index:end_index]

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
            "has_more": page < total_pages,
            "results": grouped_results,
            "summary": {
                "package_matches_count": len(grouped_results["package_matches"]),
                "class_matches_count": len(grouped_results["class_matches"])
            }
        }

    def get_magic_api_class_details(self, request: ClassDetailRequest) -> ClassDetailResponse:
        """获取指定 Magic-API 类的详细信息。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.class_method')

        # 验证请求
        if not request.validate():
            errors = request.get_validation_errors()
            return ClassDetailResponse(
                success=False,
                class_name=request.class_name,
                summary={"validation_errors": errors}
            )

        log_operation_start("获取类详情", {"class_name": request.class_name})

        try:
            result = self._get_magic_api_class_details_impl(request.class_name)

            # 如果_impl方法返回Dict，转换为DTO
            if isinstance(result, dict):
                if "error" in result:
                    response = ClassDetailResponse(
                        success=False,
                        class_name=request.class_name,
                        summary={"error": result["error"]}
                    )
                else:
                    # 转换class_details
                    class_details = []
                    for detail in result.get("details", []):
                        if isinstance(detail, dict):
                            methods = []
                            fields = []

                            # 处理方法
                            for method_data in detail.get("methods", []):
                                if isinstance(method_data, dict):
                                    methods.append(MethodInfo(
                                        name=method_data.get("name", "unknown"),
                                        return_type=method_data.get("return_type", "Object"),
                                        parameters=method_data.get("parameters", [])
                                    ))

                            # 处理字段
                            for field_data in detail.get("fields", []):
                                if isinstance(field_data, dict):
                                    fields.append(FieldInfo(
                                        name=field_data.get("name", "unknown"),
                                        type=field_data.get("type", "Object")
                                    ))

                            class_details.append(ClassInfo(
                                class_name=detail.get("class_name", request.class_name),
                                methods=methods,
                                fields=fields
                            ))

                    response = ClassDetailResponse(
                        success=True,
                        class_name=request.class_name,
                        class_details=class_details,
                        summary=result.get("summary", {})
                    )
            else:
                response = result

            log_operation_end("获取类详情", response.success)
            return response
        except Exception as e:
            logger.error(f"获取类详情失败: {e}")
            return ClassDetailResponse(
                success=False,
                class_name=request.class_name,
                summary={"error": str(e)}
            )

    def _get_magic_api_class_details_impl(self, class_name: str) -> Dict[str, Any]:
        """获取指定 Magic-API 类的详细信息的实现。"""
        # 获取类详情
        class_url = f"{self.settings.base_url}/magic/web/class"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "magicapi-class-explorer/1.0",
        }
        self.settings.inject_auth(headers)

        try:
            logger.info(f"🔍 [ClassService] 发送HTTP请求: POST {class_url}")
            logger.info(f"🔍 [ClassService] 请求头: {headers}")
            logger.info(f"🔍 [ClassService] 请求数据: {{\"className\": \"{class_name}\"}}")
            response = self.http_client.session.post(
                class_url,
                data={"className": class_name},
                headers=headers,
                timeout=self.settings.timeout_seconds
            )
            response.raise_for_status()

            # class 端点返回 JSON，检查 code 字段
            class_data = response.json()
            if class_data.get("code") != 1:
                return create_operation_error("获取类详情", "api_error", f"获取类 '{class_name}' 详情失败", class_data)
        except requests.RequestException as exc:
            return create_operation_error("获取类详情", "network_error", f"获取类详情失败: {exc}")
        except json.JSONDecodeError:
            return create_operation_error("获取类详情", "api_error", "API 返回格式错误")

        script_classes = class_data.get("data", [])

        if not script_classes:
            return create_operation_error("类不存在", "not_found", f"未找到类 '{class_name}' 的信息")

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

    def _extract_names(self, data: Any) -> List[str]:
        """从字典或列表中提取名称。

        Args:
            data: 字典（取键）或列表（取元素）

        Returns:
            名称列表
        """
        if isinstance(data, dict):
            return list(data.keys())
        elif isinstance(data, list):
            return [str(item) for item in data]
        else:
            return []

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
            class_names = self._extract_names(data["classes"])
            for class_name in class_names:
                if self._matches_keywords(class_name, keywords, logic, case_sensitive, exact, is_regex, exclude_pattern):
                    results["classes"].append(class_name)

        # 搜索扩展类
        if "extensions" in data and scope in ["all", "class"]:
            extension_names = self._extract_names(data["extensions"])
            for class_name in extension_names:
                if self._matches_keywords(class_name, keywords, logic, case_sensitive, exact, is_regex, exclude_pattern):
                    results["extensions"].append(class_name)

        # 搜索函数
        if "functions" in data and scope in ["all", "class"]:
            function_names = self._extract_names(data["functions"])
            for func_name in function_names:
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
