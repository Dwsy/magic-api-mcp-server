#!/usr/bin/env python3
"""Magic-API 类和方法检索脚本（工程化重构）。"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from typing import Any, Dict, List, Optional

import requests
from urllib.parse import urljoin


class MagicAPIClassExplorerError(Exception):
    """类探索器错误。"""
    pass


DEFAULT_BASE_URL = "http://127.0.0.1:10712"


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="检索 Magic-API 类和方法信息，支持搜索和详情查看",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_BASE_URL,
        help=f"Magic-API 服务器基础 URL（默认: {DEFAULT_BASE_URL}/）",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有可用的类、扩展和函数",
    )
    parser.add_argument(
        "--search",
        metavar="KEYWORD",
        help="搜索包含关键词的类、扩展或函数",
    )
    parser.add_argument(
        "--regex",
        metavar="PATTERN",
        help="使用正则表达式搜索类、扩展或函数",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="搜索时区分大小写（默认不区分）",
    )
    parser.add_argument(
        "--logic",
        choices=["and", "or"],
        default="or",
        help="多关键词搜索逻辑：and（同时包含）或 or（任一包含），默认 or",
    )
    parser.add_argument(
        "--scope",
        choices=["all", "class", "method", "field"],
        default="all",
        help="搜索范围：all（全部）、class（仅类名）、method（仅方法）、field（仅字段），默认 all",
    )
    parser.add_argument(
        "--exact",
        action="store_true",
        help="精确匹配关键词（默认包含匹配）",
    )
    parser.add_argument(
        "--exclude",
        metavar="EXCLUDE_KEYWORD",
        help="排除包含指定关键词的结果",
    )
    parser.add_argument(
        "--txt",
        action="store_true",
        help="显示压缩格式的类信息（classes.txt）",
    )
    parser.add_argument(
        "--txt-search",
        metavar="TXT_KEYWORD",
        help="在压缩格式类信息中搜索关键词",
    )
    parser.add_argument(
        "--class",
        dest="class_name",
        metavar="CLASS_NAME",
        help="显示指定类的详细信息",
    )
    parser.add_argument(
        "--method",
        metavar="METHOD_NAME",
        help="搜索包含指定方法名的类",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出结果",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="以 CSV 格式输出结果",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="限制输出结果的最大数量（默认: 10，节约大模型 token）",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="指定页码进行翻页浏览（默认: 1，从第1页开始）",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=10,
        help="每页显示的数量（默认: 10，与 limit 配合使用）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP 请求超时时间（秒，默认: 30）",
    )
    return parser.parse_args()


class MagicAPIClassClient:
    """Magic-API 类信息客户端。"""

    def __init__(self, base_url: str, timeout: int = 30):
        """初始化客户端。"""
        self.base_url = base_url.rstrip("/")
        # 确保 base_url 以 http:// 或 https:// 开头
        if not self.base_url.startswith(('http://', 'https://')):
            self.base_url = 'http://' + self.base_url.lstrip('http://').lstrip('https://')
        self.timeout = timeout
        self.session = requests.Session()

    def get_all_classes(self) -> Dict[str, Any]:
        """获取所有类信息。"""
        url = self.base_url + "/magic/web/classes"
        try:
            response = self.session.post(url, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            if result.get("success") and "data" in result:
                return result["data"]
            else:
                raise MagicAPIClassExplorerError(f"API 返回错误: {result}")
        except requests.RequestException as e:
            raise MagicAPIClassExplorerError(f"获取类信息失败: {e}")

    def get_class_details(self, class_name: str) -> List[Dict[str, Any]]:
        """获取指定类的详细信息。"""
        url = self.base_url + "/magic/web/class"
        try:
            response = self.session.post(
                url,
                data={"className": class_name},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            if result.get("success") and "data" in result:
                return result["data"] if isinstance(result["data"], list) else []
            else:
                return []
        except requests.RequestException as e:
            raise MagicAPIClassExplorerError(f"获取类 '{class_name}' 详情失败: {e}")

    def get_classes_txt(self) -> str:
        """获取压缩格式的类信息文本。"""
        url = self.base_url + "/magic/web/classes.txt"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise MagicAPIClassExplorerError(f"获取压缩类信息失败: {e}")


class MagicAPIClassExplorer:
    """Magic-API 类探索器。"""

    def __init__(self, client: MagicAPIClassClient):
        """初始化探索器。"""
        self.client = client
        self._classes_data: Optional[Dict[str, Any]] = None
        self._classes_txt_data: Optional[str] = None

    def _load_classes_data(self) -> None:
        """加载类数据。"""
        if self._classes_data is None:
            self._classes_data = self.client.get_all_classes()

    def _load_classes_txt_data(self) -> None:
        """加载压缩格式的类数据。"""
        if self._classes_txt_data is None:
            self._classes_txt_data = self.client.get_classes_txt()

    def _format_method_info(self, method: Any) -> str:
        """格式化方法信息。"""
        if isinstance(method, dict):
            name = method.get("name", "unknown")
            return_type = method.get("returnType", "void")
            params = method.get("parameters", [])
            param_str = ", ".join([
                f"{p.get('type', 'Object')} {p.get('name', 'arg')}"
                for p in params if isinstance(p, dict)
            ])
            return f"{return_type} {name}({param_str})"
        elif isinstance(method, str):
            return method
        else:
            return str(method)

    def _format_field_info(self, field: Any) -> str:
        """格式化字段信息。"""
        if isinstance(field, dict):
            name = field.get("name", "unknown")
            field_type = field.get("type", "Object")
            return f"{field_type} {name}"
        elif isinstance(field, str):
            return field
        else:
            return str(field)

    def _paginate_items(self, items: list, page: int, page_size: int) -> tuple[list, int, int]:
        """分页处理项目列表。返回 (分页后的项目, 总页数, 总数)"""
        total_items = len(items)
        total_pages = (total_items + page_size - 1) // page_size  # 向上取整

        if page > total_pages:
            return [], total_pages, total_items

        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_items)
        paginated_items = items[start_index:end_index]

        return paginated_items, total_pages, total_items

    def list_all_classes(self, output_json: bool = False, output_csv: bool = False, limit: int = 10,
                        page: int = 1, page_size: int = 10) -> None:
        """列出所有类信息。"""
        self._load_classes_data()

        if output_json:
            import json
            print(json.dumps(self._classes_data, ensure_ascii=False, indent=2))
            return

        if output_csv:
            writer = csv.writer(sys.stdout)
            writer.writerow(["type", "name"])

            # 收集所有项目
            all_items = []

            # 脚本类
            if "classes" in self._classes_data and self._classes_data["classes"]:
                for class_name in sorted(self._classes_data["classes"].keys()):
                    all_items.append(("class", class_name))

            # 扩展类
            if "extensions" in self._classes_data and self._classes_data["extensions"]:
                for class_name in sorted(self._classes_data["extensions"].keys()):
                    all_items.append(("extension", class_name))

            # 函数
            if "functions" in self._classes_data and self._classes_data["functions"]:
                for func_name in sorted(self._classes_data["functions"].keys()):
                    all_items.append(("function", func_name))

            # 应用翻页
            paginated_items, total_pages, total_items = self._paginate_items(all_items, page, page_size)

            # 限制每页的最大数量
            if len(paginated_items) > limit:
                paginated_items = paginated_items[:limit]

            # 输出分页结果
            for item_type, item_name in paginated_items:
                writer.writerow([item_type, item_name])

            # 如果有更多内容，添加分页信息注释
            if total_pages > 1:
                print(f"# 页码: {page}/{total_pages}, 总共: {total_items} 项, 每页: {page_size} 项", file=sys.stderr)
            return

        # 收集所有项目
        all_items = []

        # 脚本类
        if "classes" in self._classes_data and self._classes_data["classes"]:
            for class_name in sorted(self._classes_data["classes"].keys()):
                all_items.append(("📦 脚本类", class_name))

        # 扩展类
        if "extensions" in self._classes_data and self._classes_data["extensions"]:
            for class_name in sorted(self._classes_data["extensions"].keys()):
                all_items.append(("🔧 扩展类", class_name))

        # 函数
        if "functions" in self._classes_data and self._classes_data["functions"]:
            for func_name in sorted(self._classes_data["functions"].keys()):
                all_items.append(("⚡ 全局函数", func_name))

        # 应用翻页
        paginated_items, total_pages, total_items = self._paginate_items(all_items, page, page_size)

        # 限制每页的最大数量
        if len(paginated_items) > limit:
            paginated_items = paginated_items[:limit]

        print("=== Magic-API 类和方法检索 ===")

        # 显示翻页信息
        if total_pages > 1:
            print(f"📄 第 {page} 页 / 共 {total_pages} 页 (每页 {page_size} 项, 总共 {total_items} 项)")
            if page > 1:
                print(f"⬅️  上一页: --page {page-1} --page-size {page_size}")
            if page < total_pages:
                print(f"➡️  下一页: --page {page+1} --page-size {page_size}")
            print()

        if not paginated_items:
            if page > total_pages:
                print(f"❌ 第 {page} 页不存在，总共只有 {total_pages} 页")
            else:
                print("未找到任何项目")
            return

        # 按类别分组显示
        current_category = None
        category_items = []

        for category, item_name in paginated_items:
            if category != current_category:
                if category_items:
                    # 显示上一类别
                    print(f"{current_category} ({len(category_items)} 项):")
                    for item in category_items:
                        print(f"  • {item}")
                    print()

                current_category = category
                category_items = [item_name]
            else:
                category_items.append(item_name)

        # 显示最后一个类别
        if category_items:
            print(f"{current_category} ({len(category_items)} 项):")
            for item in category_items:
                print(f"  • {item}")

        # 显示限制信息
        if len(paginated_items) < len(all_items) or total_pages > 1:
            print(f"\n📊 本页显示 {len(paginated_items)}/{total_items} 项")
            if len(paginated_items) == limit and len(paginated_items) < total_items:
                print(f"⚠️  本页结果已限制为 {limit} 项")

    def _match_pattern(self, text: str, pattern: str, case_sensitive: bool = False, exact: bool = False, is_regex: bool = False) -> bool:
        """检查文本是否匹配搜索模式。"""
        if not text:
            return False

        if is_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                return bool(re.search(pattern, text, flags))
            except re.error:
                return False

        # 处理多关键词
        keywords = pattern.split()
        if len(keywords) > 1:
            # 多关键词搜索
            matches = []
            for kw in keywords:
                if case_sensitive:
                    match = (kw == text) if exact else (kw in text)
                else:
                    match = (kw.lower() == text.lower()) if exact else (kw.lower() in text.lower())
                matches.append(match)

            # 根据逻辑组合结果
            return all(matches) if hasattr(self, '_search_logic') and self._search_logic == 'and' else any(matches)

        # 单关键词搜索
        if case_sensitive:
            return (pattern == text) if exact else (pattern in text)
        else:
            return (pattern.lower() == text.lower()) if exact else (pattern.lower() in text.lower())

    def _should_exclude(self, text: str, exclude_pattern: str, case_sensitive: bool = False) -> bool:
        """检查文本是否应该被排除。"""
        if not exclude_pattern or not text:
            return False

        if case_sensitive:
            return exclude_pattern in text
        else:
            return exclude_pattern.lower() in text.lower()

    def _search_in_class_details(self, class_name: str, pattern: str, scope: str, case_sensitive: bool = False,
                                exact: bool = False, is_regex: bool = False, exclude_pattern: str = None) -> Dict[str, Any]:
        """在类详情中搜索匹配的项目。"""
        try:
            class_details = self.client.get_class_details(class_name)
        except Exception:
            return None

        matches = {
            "class_name": class_name,
            "methods": [],
            "fields": []
        }

        found_any = False

        for class_info in class_details:
            if isinstance(class_info, dict):
                # 搜索方法
                if scope in ["all", "method"]:
                    methods = class_info.get("methods", [])
                    for method in methods:
                        if isinstance(method, dict):
                            method_name = method.get("name", "")
                            return_type = method.get("returnType", "")
                            params = method.get("parameters", [])

                            # 根据范围检查不同部分
                            search_targets = []
                            if scope == "all":
                                search_targets.extend([method_name, return_type])
                                search_targets.extend([p.get("type", "") for p in params if isinstance(p, dict)])
                                search_targets.extend([p.get("name", "") for p in params if isinstance(p, dict)])
                            elif scope == "method":
                                search_targets.append(method_name)

                            # 检查是否匹配
                            if any(self._match_pattern(target, pattern, case_sensitive, exact, is_regex)
                                  for target in search_targets if target):
                                if not self._should_exclude(method_name, exclude_pattern, case_sensitive):
                                    matches["methods"].append({
                                        "name": method_name,
                                        "return_type": return_type,
                                        "parameters": params
                                    })
                                    found_any = True

                # 搜索字段
                if scope in ["all", "field"]:
                    fields = class_info.get("fields", [])
                    for field in fields:
                        if isinstance(field, dict):
                            field_name = field.get("name", "")
                            field_type = field.get("type", "")

                            # 根据范围检查
                            search_targets = []
                            if scope == "all":
                                search_targets.extend([field_name, field_type])
                            elif scope == "field":
                                search_targets.append(field_name)

                            # 检查是否匹配
                            if any(self._match_pattern(target, pattern, case_sensitive, exact, is_regex)
                                  for target in search_targets if target):
                                if not self._should_exclude(field_name, exclude_pattern, case_sensitive):
                                    matches["fields"].append({
                                        "name": field_name,
                                        "type": field_type
                                    })
                                    found_any = True

        return matches if found_any else None

    def search_enhanced(self, pattern: str, search_type: str = "keyword", output_json: bool = False, output_csv: bool = False,
                       case_sensitive: bool = False, logic: str = "or", scope: str = "all", exact: bool = False,
                       exclude_pattern: str = None, limit: int = 10, page: int = 1, page_size: int = 10) -> None:
        """增强的搜索功能。"""
        self._load_classes_data()
        is_regex = (search_type == "regex")

        # 保存搜索逻辑用于多关键词处理
        self._search_logic = logic

        results = {
            "classes": [],
            "extensions": [],
            "functions": [],
            "detailed_matches": []  # 存储详细匹配信息
        }

        # 搜索顶级类和函数
        if scope in ["all", "class"]:
            # 搜索脚本类
            if "classes" in self._classes_data:
                for class_name in self._classes_data["classes"].keys():
                    if self._match_pattern(class_name, pattern, case_sensitive, exact, is_regex):
                        if not self._should_exclude(class_name, exclude_pattern, case_sensitive):
                            results["classes"].append(class_name)

            # 搜索扩展类
            if "extensions" in self._classes_data:
                for class_name in self._classes_data["extensions"].keys():
                    if self._match_pattern(class_name, pattern, case_sensitive, exact, is_regex):
                        if not self._should_exclude(class_name, exclude_pattern, case_sensitive):
                            results["extensions"].append(class_name)

            # 搜索函数
            if "functions" in self._classes_data:
                for func_name in self._classes_data["functions"].keys():
                    if self._match_pattern(func_name, pattern, case_sensitive, exact, is_regex):
                        if not self._should_exclude(func_name, exclude_pattern, case_sensitive):
                            results["functions"].append(func_name)

        # 搜索类详情中的方法和字段
        if scope in ["all", "method", "field"]:
            all_classes = []
            if "classes" in self._classes_data:
                all_classes.extend(self._classes_data["classes"].keys())
            if "extensions" in self._classes_data:
                all_classes.extend(self._classes_data["extensions"].keys())

            for class_name in all_classes:
                detailed_match = self._search_in_class_details(
                    class_name, pattern, scope, case_sensitive, exact, is_regex, exclude_pattern
                )
                if detailed_match:
                    results["detailed_matches"].append(detailed_match)

        if output_json:
            import json
            print(json.dumps(results, ensure_ascii=False, indent=2))
            return

        if output_csv:
            writer = csv.writer(sys.stdout)
            writer.writerow(["type", "name", "details", "pattern", "scope"])

            # 输出顶级匹配
            for class_name in sorted(results["classes"]):
                writer.writerow(["class", class_name, "", pattern, scope])

            for class_name in sorted(results["extensions"]):
                writer.writerow(["extension", class_name, "", pattern, scope])

            for func_name in sorted(results["functions"]):
                writer.writerow(["function", func_name, "", pattern, scope])

            # 输出详细匹配
            for match in results["detailed_matches"]:
                class_name = match["class_name"]
                for method in match["methods"]:
                    method_name = method["name"]
                    return_type = method["return_type"]
                    params_str = "; ".join([
                        f"{p.get('type', 'Object')} {p.get('name', 'arg')}"
                        for p in method["parameters"] if isinstance(p, dict)
                    ])
                    details = f"{return_type} {method_name}({params_str})"
                    writer.writerow(["method", class_name, details, pattern, scope])

                for field in match["fields"]:
                    field_name = field["name"]
                    field_type = field["type"]
                    details = f"{field_type} {field_name}"
                    writer.writerow(["field", class_name, details, pattern, scope])
            return

        # 收集所有匹配的项目用于翻页
        all_matches = []

        # 添加匹配的脚本类
        for class_name in results["classes"]:
            all_matches.append(("📦 脚本类", class_name, "class"))

        # 添加匹配的扩展类
        for class_name in results["extensions"]:
            all_matches.append(("🔧 扩展类", class_name, "extension"))

        # 添加匹配的函数
        for func_name in results["functions"]:
            all_matches.append(("⚡ 全局函数", func_name, "function"))

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
                all_matches.append(("🔍 方法", f"{class_name}.{method_name}", f"method:{details}"))

            for field in match["fields"]:
                field_name = field["name"]
                field_type = field["type"]
                details = f"{field_type} {field_name}"
                all_matches.append(("🔍 字段", f"{class_name}.{field_name}", f"field:{details}"))

        # 应用翻页
        paginated_matches, total_pages, total_matches = self._paginate_items(all_matches, page, page_size)

        # 应用 limit 限制
        if len(paginated_matches) > limit:
            paginated_matches = paginated_matches[:limit]

        # 为CSV输出准备数据
        if output_csv:
            writer = csv.writer(sys.stdout)
            writer.writerow(["type", "name", "details", "pattern", "scope"])

            for category, item_name, item_type in paginated_matches:
                if ":" in item_type:
                    # 详细匹配项
                    prefix, details = item_type.split(":", 1)
                    writer.writerow([prefix, item_name, details, pattern, scope])
                else:
                    # 简单匹配项
                    writer.writerow([item_type, item_name, "", pattern, scope])

            if total_pages > 1:
                print(f"# 搜索结果翻页: {page}/{total_pages}, 总共: {total_matches} 项, 每页: {page_size} 项", file=sys.stderr)
            return

        # 计算原始匹配总数
        total_original = len(results["classes"]) + len(results["extensions"]) + len(results["functions"]) + len(results["detailed_matches"])

        search_desc = f"正则表达式 '{pattern}'" if is_regex else f"关键词 '{pattern}'"
        options_desc = []
        if case_sensitive:
            options_desc.append("区分大小写")
        if exact:
            options_desc.append("精确匹配")
        if logic == "and":
            options_desc.append("AND逻辑")
        if exclude_pattern:
            options_desc.append(f"排除 '{exclude_pattern}'")
        if scope != "all":
            options_desc.append(f"范围: {scope}")
        if total_pages > 1:
            options_desc.append(f"第{page}页/{total_pages}页")
        if len(paginated_matches) < total_original:
            options_desc.append(f"显示{len(paginated_matches)}/{total_original}项")

        options_str = f" ({', '.join(options_desc)})" if options_desc else ""

        if len(paginated_matches) == 0:
            print(f"🔍 未找到匹配{search_desc} 的类、方法或函数{options_str}")
            return

        print(f"🔍 搜索结果: {search_desc}{options_str}")

        # 显示翻页信息
        if total_pages > 1:
            print(f"📄 第 {page} 页 / 共 {total_pages} 页 (每页 {page_size} 项, 总共 {total_original} 项)")
            if page > 1:
                print(f"⬅️  上一页: --page {page-1} --page-size {page_size}")
            if page < total_pages:
                print(f"➡️  下一页: --page {page+1} --page-size {page_size}")
            print()

        # 按类别分组显示
        current_category = None
        category_items = []

        for category, item_name, item_type in paginated_matches:
            if category != current_category:
                if category_items:
                    # 显示上一类别
                    print(f"{current_category} ({len(category_items)} 项):")
                    for item in category_items:
                        print(f"  • {item}")
                    print()

                current_category = category
                category_items = [item_name]
            else:
                category_items.append(item_name)

        # 显示最后一个类别
        if category_items:
            print(f"{current_category} ({len(category_items)} 项):")
            for item in category_items:
                print(f"  • {item}")

        # 显示限制信息
        if len(paginated_matches) < total_original:
            print(f"\n📊 本页显示 {len(paginated_matches)}/{total_original} 项")
            if len(paginated_matches) == limit:
                print(f"⚠️  本页结果已限制为 {limit} 项")

    def search_classes(self, keyword: str, output_json: bool = False, output_csv: bool = False) -> None:
        """搜索包含关键词的类。"""
        self._load_classes_data()
        keyword_lower = keyword.lower()
        results = {
            "classes": [],
            "extensions": [],
            "functions": []
        }

        # 搜索脚本类
        if "classes" in self._classes_data:
            results["classes"] = [
                name for name in self._classes_data["classes"].keys()
                if keyword_lower in name.lower()
            ]

        # 搜索扩展类
        if "extensions" in self._classes_data:
            results["extensions"] = [
                name for name in self._classes_data["extensions"].keys()
                if keyword_lower in name.lower()
            ]

        # 搜索函数
        if "functions" in self._classes_data:
            results["functions"] = [
                name for name in self._classes_data["functions"].keys()
                if keyword_lower in name.lower()
            ]

        if output_json:
            import json
            print(json.dumps(results, ensure_ascii=False, indent=2))
            return

        if output_csv:
            writer = csv.writer(sys.stdout)
            writer.writerow(["type", "name", "keyword"])

            # 输出匹配的脚本类
            for class_name in sorted(results["classes"]):
                writer.writerow(["class", class_name, keyword])

            # 输出匹配的扩展类
            for class_name in sorted(results["extensions"]):
                writer.writerow(["extension", class_name, keyword])

            # 输出匹配的函数
            for func_name in sorted(results["functions"]):
                writer.writerow(["function", func_name, keyword])
            return

        total_matches = sum(len(matches) for matches in results.values())

        if total_matches == 0:
            print(f"🔍 未找到包含关键词 '{keyword}' 的类或函数")
            return

        print(f"🔍 搜索结果: '{keyword}' (共 {total_matches} 个匹配)\n")

        # 显示匹配的脚本类
        if results["classes"]:
            print(f"📦 匹配的脚本类 ({len(results['classes'])} 个):")
            for class_name in sorted(results["classes"]):
                print(f"  • {class_name}")
            print()

        # 显示匹配的扩展类
        if results["extensions"]:
            print(f"🔧 匹配的扩展类 ({len(results['extensions'])} 个):")
            for class_name in sorted(results["extensions"]):
                print(f"  • {class_name}")
            print()

        # 显示匹配的函数
        if results["functions"]:
            print(f"⚡ 匹配的全局函数 ({len(results['functions'])} 个):")
            for func_name in sorted(results["functions"]):
                print(f"  • {func_name}")

    def search_methods(self, method_name: str, output_json: bool = False, output_csv: bool = False) -> None:
        """搜索包含指定方法名的类。"""
        self._load_classes_data()
        method_lower = method_name.lower()
        results = {
            "classes": [],
            "extensions": []
        }

        # 搜索脚本类中的方法
        if "classes" in self._classes_data:
            for class_name in self._classes_data["classes"].keys():
                try:
                    class_details = self.client.get_class_details(class_name)
                    if self._has_method(class_details, method_lower):
                        results["classes"].append(class_name)
                except Exception:
                    continue  # 跳过无法获取详情的类

        # 搜索扩展类中的方法
        if "extensions" in self._classes_data:
            for class_name in self._classes_data["extensions"].keys():
                try:
                    class_details = self.client.get_class_details(class_name)
                    if self._has_method(class_details, method_lower):
                        results["extensions"].append(class_name)
                except Exception:
                    continue  # 跳过无法获取详情的类

        if output_json:
            import json
            print(json.dumps(results, ensure_ascii=False, indent=2))
            return

        if output_csv:
            writer = csv.writer(sys.stdout)
            writer.writerow(["type", "class_name", "method_name"])

            # 输出匹配的脚本类
            for class_name in sorted(results["classes"]):
                writer.writerow(["class", class_name, method_name])

            # 输出匹配的扩展类
            for class_name in sorted(results["extensions"]):
                writer.writerow(["extension", class_name, method_name])
            return

        total_matches = sum(len(matches) for matches in results.values())

        if total_matches == 0:
            print(f"🔍 未找到包含方法 '{method_name}' 的类")
            return

        print(f"🔍 方法搜索结果: '{method_name}' (共 {total_matches} 个匹配)\n")

        # 显示匹配的脚本类
        if results["classes"]:
            print(f"📦 包含该方法的脚本类 ({len(results['classes'])} 个):")
            for class_name in sorted(results["classes"]):
                print(f"  • {class_name}")
            print()

        # 显示匹配的扩展类
        if results["extensions"]:
            print(f"🔧 包含该方法的扩展类 ({len(results['extensions'])} 个):")
            for class_name in sorted(results["extensions"]):
                print(f"  • {class_name}")

    def _has_method(self, class_details: List[Dict[str, Any]], method_name: str) -> bool:
        """检查类详情中是否包含指定方法。"""
        for class_info in class_details:
            if isinstance(class_info, dict):
                methods = class_info.get("methods", [])
                for method in methods:
                    method_str = self._format_method_info(method)
                    if method_name in method_str.lower():
                        return True
        return False

    def show_class_details(self, class_name: str, output_json: bool = False, output_csv: bool = False) -> None:
        """显示指定类的详细信息。"""
        try:
            class_details = self.client.get_class_details(class_name)
        except MagicAPIClassExplorerError as e:
            print(f"❌ 获取类 '{class_name}' 详情失败: {e}")
            return

        if not class_details:
            print(f"⚠️  类 '{class_name}' 没有可用的详细信息")
            return

        if output_json:
            import json
            result = {
                "class_name": class_name,
                "details": class_details
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        if output_csv:
            writer = csv.writer(sys.stdout)
            writer.writerow(["class_name", "method_name", "return_type", "parameters", "field_name", "field_type"])

            for class_info in class_details:
                if isinstance(class_info, dict):
                    # 输出方法
                    methods = class_info.get("methods", [])
                    for method in methods:
                        if isinstance(method, dict):
                            method_name = method.get("name", "")
                            return_type = method.get("returnType", "")
                            parameters = method.get("parameters", [])
                            param_str = "; ".join([
                                f"{p.get('type', 'Object')} {p.get('name', 'arg')}"
                                for p in parameters if isinstance(p, dict)
                            ])
                            writer.writerow([class_name, method_name, return_type, param_str, "", ""])

                    # 输出字段
                    fields = class_info.get("fields", [])
                    for field in fields:
                        if isinstance(field, dict):
                            field_name = field.get("name", "")
                            field_type = field.get("type", "")
                            writer.writerow([class_name, "", "", "", field_name, field_type])
            return

        print(f"📋 类详情: {class_name}\n")

        for i, class_info in enumerate(class_details, 1):
            if isinstance(class_info, dict):
                print(f"实例 {i}:")

                # 显示方法
                methods = class_info.get("methods", [])
                if methods:
                    print("  方法:")
                    for method in methods:
                        print(f"    • {self._format_method_info(method)}")
                else:
                    print("  无可用方法")

                # 显示字段
                fields = class_info.get("fields", [])
                if fields:
                    print("  字段:")
                    for field in fields:
                        print(f"    • {self._format_field_info(field)}")
                else:
                    print("  无可用字段")

                # 显示其他属性
                for key, value in class_info.items():
                    if key not in ["methods", "fields"]:
                        print(f"  {key}: {value}")

                print()

    def show_classes_txt(self, output_csv: bool = False) -> None:
        """显示压缩格式的类信息。"""
        self._load_classes_txt_data()

        if not self._classes_txt_data:
            print("未找到压缩类信息")
            return

        if output_csv:
            writer = csv.writer(sys.stdout)
            writer.writerow(["package", "classes"])

            lines = self._classes_txt_data.strip().split('\n')
            for line in lines:
                if ':' in line:
                    package_name, classes_str = line.split(':', 1)
                    writer.writerow([package_name, classes_str])
        else:
            print("=== 压缩格式类信息 ===")
            print(self._classes_txt_data)

    def search_classes_txt(self, keyword: str, output_csv: bool = False, case_sensitive: bool = False,
                          limit: int = 10, page: int = 1, page_size: int = 10) -> None:
        """在压缩格式类信息中搜索。"""
        self._load_classes_txt_data()

        if not self._classes_txt_data:
            print("未找到压缩类信息")
            return

        lines = self._classes_txt_data.strip().split('\n')
        all_matches = []

        for line in lines:
            if ':' in line:
                package_name, classes_str = line.split(':', 1)
                class_list = classes_str.split(',')

                # 搜索包名
                if self._match_pattern(package_name, keyword, case_sensitive, is_regex=False):
                    for cls in class_list:
                        all_matches.append(("📦 包匹配", f"{package_name}.{cls}", "package"))
                    continue

                # 搜索类名
                for cls in class_list:
                    if self._match_pattern(cls, keyword, case_sensitive, is_regex=False):
                        all_matches.append(("📦 类匹配", f"{package_name}.{cls}", "class"))

        # 应用翻页
        paginated_matches, total_pages, total_matches = self._paginate_items(all_matches, page, page_size)

        # 应用 limit 限制
        if len(paginated_matches) > limit:
            paginated_matches = paginated_matches[:limit]

        search_desc = f"关键词 '{keyword}'"
        options_desc = "区分大小写" if case_sensitive else "不区分大小写"

        if output_csv:
            writer = csv.writer(sys.stdout)
            writer.writerow(["match_type", "full_name", "keyword", "type"])

            for category, item_name, match_type in paginated_matches:
                writer.writerow([category, item_name, keyword, match_type])

            if total_pages > 1:
                print(f"# 压缩类信息搜索翻页: {page}/{total_pages}, 总共: {total_matches} 项, 每页: {page_size} 项", file=sys.stderr)
            return

        if len(paginated_matches) == 0:
            print(f"🔍 压缩类信息搜索: {search_desc} ({options_desc})")
            if page > total_pages:
                print(f"❌ 第 {page} 页不存在，总共只有 {total_pages} 页")
            else:
                print(f"未找到包含 '{keyword}' 的类或包")
            return

        print(f"🔍 压缩类信息搜索: {search_desc} ({options_desc})")

        # 显示翻页信息
        if total_pages > 1:
            print(f"📄 第 {page} 页 / 共 {total_pages} 页 (每页 {page_size} 项, 总共 {total_matches} 项)")
            if page > 1:
                print(f"⬅️  上一页: --page {page-1} --page-size {page_size}")
            if page < total_pages:
                print(f"➡️  下一页: --page {page+1} --page-size {page_size}")
            print()

        # 按类别分组显示
        current_category = None
        category_items = []

        for category, item_name, match_type in paginated_matches:
            if category != current_category:
                if category_items:
                    # 显示上一类别
                    print(f"{current_category} ({len(category_items)} 项):")
                    for item in category_items:
                        print(f"  • {item}")
                    print()

                current_category = category
                category_items = [item_name]
            else:
                category_items.append(item_name)

        # 显示最后一个类别
        if category_items:
            print(f"{current_category} ({len(category_items)} 项):")
            for item in category_items:
                print(f"  • {item}")

        # 显示限制信息
        if len(paginated_matches) < total_matches:
            print(f"\n📊 本页显示 {len(paginated_matches)}/{total_matches} 项")
            if len(paginated_matches) == limit:
                print(f"⚠️  本页结果已限制为 {limit} 项")


def validate_args(args: argparse.Namespace) -> None:
    """验证命令行参数。"""
    # 检查操作冲突：不能同时指定多个主要操作
    actions = [args.list, (args.search or args.regex), args.class_name, args.method, args.txt, args.txt_search]
    if sum(1 for action in actions if action) != 1:
        raise MagicAPIClassExplorerError(
            "必须且只能指定以下操作之一: --list, --search/--regex, --class, --method, --txt, --txt-search"
        )

    # 检查输出格式冲突
    if args.json and args.csv:
        raise MagicAPIClassExplorerError("--json 和 --csv 参数不能同时使用")

    # 检查搜索参数冲突
    if args.search and args.regex:
        raise MagicAPIClassExplorerError("--search 和 --regex 参数不能同时使用")

    # 验证正则表达式
    if args.regex:
        try:
            re.compile(args.regex)
        except re.error as e:
            raise MagicAPIClassExplorerError(f"无效的正则表达式: {e}")

    # 检查搜索选项的有效性
    if not (args.search or args.regex) and (args.case_sensitive or args.exact or args.exclude or args.logic != "or" or args.scope != "all"):
        raise MagicAPIClassExplorerError("搜索选项 (--case-sensitive, --exact, --exclude, --logic, --scope) 只能与 --search 或 --regex 一起使用")

    # 检查 txt 搜索选项的有效性
    if not args.txt_search and args.case_sensitive and not (args.search or args.regex):
        # 如果只有 --case-sensitive 而没有其他搜索操作，则报错
        if not args.txt_search:
            raise MagicAPIClassExplorerError("--case-sensitive 只能与 --search、--regex 或 --txt-search 一起使用")

    # 检查翻页参数的有效性
    if hasattr(args, 'page') and args.page < 1:
        raise MagicAPIClassExplorerError("--page 页码必须大于等于 1")
    if hasattr(args, 'page_size') and args.page_size < 1:
        raise MagicAPIClassExplorerError("--page-size 页大小必须大于等于 1")


def main() -> None:
    """主函数。"""
    args = parse_args()

    try:
        validate_args(args)

        # 创建客户端和探索器
        client = MagicAPIClassClient(args.url, args.timeout)
        explorer = MagicAPIClassExplorer(client)

        # 执行相应操作
        if args.list:
            explorer.list_all_classes(args.json, args.csv, args.limit, args.page, args.page_size)
        elif args.search or args.regex:
            search_type = "regex" if args.regex else "keyword"
            pattern = args.regex if args.regex else args.search
            explorer.search_enhanced(
                pattern=pattern,
                search_type=search_type,
                output_json=args.json,
                output_csv=args.csv,
                case_sensitive=args.case_sensitive,
                logic=args.logic,
                scope=args.scope,
                exact=args.exact,
                exclude_pattern=args.exclude,
                limit=args.limit,
                page=args.page,
                page_size=args.page_size
            )
        elif args.method:
            explorer.search_methods(args.method, args.json, args.csv)
        elif args.class_name:
            explorer.show_class_details(args.class_name, args.json, args.csv)
        elif args.txt:
            explorer.show_classes_txt(args.csv)
        elif args.txt_search:
            explorer.search_classes_txt(args.txt_search, args.csv, args.case_sensitive,
                                      args.limit, args.page, args.page_size)

    except MagicAPIClassExplorerError as exc:
        print(f"❌ 错误：{exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  操作已取消", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f"❌ 发生未预期的错误：{exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
