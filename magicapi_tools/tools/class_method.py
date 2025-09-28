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

from typing import TYPE_CHECKING, Annotated, Any, Dict, Literal, Optional

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
        ) -> Dict[str, Any]:
            """列出所有 Magic-API 可用的类、扩展和函数。"""
            try:
                if page < 1:
                    return error_response("invalid_param", "页码必须大于等于1")
                if page_size < 1:
                    return error_response("invalid_param", "每页大小必须大于等于1")

                # 使用服务层处理类列表查询
                response = context.class_method_service.list_magic_classes(page, page_size)
                return response.to_dict()

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
                Literal["keyword", "regex"],
                Field(description="搜索类型：keyword（关键词）或 regex（正则表达式）")
            ] = "keyword",
            case_sensitive: Annotated[
                bool,
                Field(description="是否区分大小写，默认false")
            ] = False,
            logic: Annotated[
                Literal["and", "or"],
                Field(description="多关键词逻辑：and 或 or，默认or")
            ] = "or",
            scope: Annotated[
                Literal["all", "class", "method", "field"],
                Field(description="搜索范围：all（全部）、class（仅类名）、method（仅方法）、field（仅字段），默认all")
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
        ) -> Dict[str, Any]:
            """在 Magic-API 类信息中进行增强搜索。"""
            try:
                if page < 1:
                    return error_response("invalid_param", "页码必须大于等于1")
                if page_size < 1:
                    return error_response("invalid_param", "每页大小必须大于等于1")
                if not pattern.strip():
                    return error_response("invalid_param", "搜索模式不能为空")

                # 验证正则表达式
                if search_type == "regex":
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        return error_response("invalid_param", f"无效的正则表达式: {e}")

                # 使用服务层处理类搜索查询
                from magicapi_tools.domain.dtos.class_method_dtos import ClassSearchRequest

                request = ClassSearchRequest(
                    query_type="search",
                    pattern=pattern,
                    search_type=search_type,
                    case_sensitive=case_sensitive,
                    logic=logic,
                    scope=scope,
                    exact=exact,
                    exclude_pattern=exclude_pattern,
                    page=page,
                    page_size=page_size
                )

                response = context.class_method_service.search_magic_classes(request)
                return response.to_dict()

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
        ) -> Dict[str, Any]:
            """在压缩类信息中搜索关键词。"""
            try:
                if page < 1:
                    return error_response("invalid_param", "页码必须大于等于1")
                if page_size < 1:
                    return error_response("invalid_param", "每页大小必须大于等于1")
                if not keyword.strip():
                    return error_response("invalid_param", "搜索关键词不能为空")

                # 使用服务层处理压缩类搜索查询
                response = context.class_method_service.search_magic_classes_txt(
                    keyword, case_sensitive, page, page_size
                )
                return response.to_dict()

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

                # 使用服务层处理类详情查询
                from magicapi_tools.domain.dtos.class_method_dtos import ClassDetailRequest

                request = ClassDetailRequest(class_name=class_name)

                response = context.class_method_service.get_magic_api_class_details(request)
                return response.to_dict()

            except Exception as exc:
                return error_response("details_error", f"获取类详情失败: {exc}")

