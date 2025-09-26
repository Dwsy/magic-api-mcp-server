"""查询业务服务。

处理所有查询相关的业务逻辑，包括API详情查询、端点搜索等。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import create_operation_error
from magicapi_tools.domain.dtos.query_dtos import QueryRequest, QueryResponse, EndpointFilter

from .base_service import BaseService

if TYPE_CHECKING:
    from magicapi_mcp.tool_registry import ToolContext

logger = get_logger('services.query')


class QueryService(BaseService):
    """查询业务服务类。"""

    def get_api_details_by_path(self, path: str, fuzzy: bool = True) -> Dict[str, Any]:
        """根据路径获取API详情。"""
        return self.execute_operation(
            "根据路径查询API详情",
            self._get_api_details_by_path_impl,
            path=path,
            fuzzy=fuzzy
        )

    def _get_api_details_by_path_impl(self, path: str, fuzzy: bool = True) -> Dict[str, Any]:
        """根据路径获取API详情的实现。"""
        # 这里应该包含query.py中的路径查询逻辑
        return {"success": True, "path": path, "fuzzy": fuzzy, "results": []}

    def get_api_details_by_id(self, file_id: str) -> Dict[str, Any]:
        """根据ID获取API详情。"""
        return self.execute_operation(
            "根据ID查询API详情",
            self._get_api_details_by_id_impl,
            file_id=file_id
        )

    def _get_api_details_by_id_impl(self, file_id: str) -> Dict[str, Any]:
        """根据ID获取API详情的实现。"""
        ok, payload = self.http_client.api_detail(file_id)
        if not ok:
            return create_operation_error("查询API详情", "api_detail_failed", "无法获取API详情", payload)

        if not payload:
            return create_operation_error("查询API详情", "api_not_found", f"API不存在: {file_id}")

        # 从payload中提取body作为实际的API响应数据
        api_response_body = payload.get("body", payload) if isinstance(payload, dict) else payload

        # 检查API业务逻辑响应码
        from magicapi_tools.utils.tool_helpers import check_api_response_success
        api_error = check_api_response_success(api_response_body, self.settings, "查询API详情")
        if api_error:
            return api_error

        # 获取完整的路径
        from magicapi_tools.tools.query import _get_full_path_by_api_details
        method = api_response_body.get("method", "").upper()
        path = api_response_body.get("path", "")
        name = api_response_body.get("name", "")
        full_path = _get_full_path_by_api_details(self.http_client, file_id, method, path, name)

        return {**api_response_body, "full_path": full_path}

    def search_api_endpoints(self, request: QueryRequest) -> QueryResponse:
        """搜索API端点。"""
        # 验证请求
        if not request.validate():
            errors = request.get_validation_errors()
            return QueryResponse(
                success=False,
                query_type=request.query_type,
                summary={"error": "; ".join(errors)}
            )

        return self.execute_operation(
            "搜索API端点",
            self._search_api_endpoints_impl,
            request=request
        )

    # 向后兼容的方法
    def search_api_endpoints_legacy(
        self,
        method_filter: Optional[str] = None,
        path_filter: Optional[str] = None,
        name_filter: Optional[str] = None,
        query_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """搜索API端点（向后兼容版本）。"""
        filters = EndpointFilter(
            method_filter=method_filter,
            path_filter=path_filter,
            name_filter=name_filter,
            query_filter=query_filter
        )

        request = QueryRequest(
            query_type="endpoints",
            filters=filters
        )

        response = self.search_api_endpoints(request)
        return response.to_dict()

    def _search_api_endpoints_impl(self, request: QueryRequest) -> QueryResponse:
        """搜索API端点的实现。"""
        try:
            from magicapi_tools.utils.extractor import extract_api_endpoints, load_resource_tree
            from magicapi_tools.utils.extractor import filter_endpoints, _collect_all_endpoints

            # 获取资源树数据
            tree = load_resource_tree(client=self.http_client)
            endpoints = extract_api_endpoints(tree)

            # 应用过滤条件
            filtered_endpoints = filter_endpoints(
                endpoints,
                method_filter=request.filters.method_filter if request.filters else None,
                path_filter=request.filters.path_filter if request.filters else None,
                name_filter=request.filters.name_filter if request.filters else None,
                query_filter=request.filters.query_filter if request.filters else None,
            )

            # 获取所有端点的详细信息（包含ID和display字符串）
            all_endpoint_details = []
            for child in tree.api_nodes:
                _collect_all_endpoints(child, "", all_endpoint_details)

            # 创建端点字符串到ID的映射
            endpoint_to_id_map = {}
            for detail in all_endpoint_details:
                display = detail.get("display")
                api_id = detail.get("id")
                if display and api_id:
                    endpoint_to_id_map[display] = api_id

            # 构建结果
            results = []
            for endpoint in filtered_endpoints:
                if "[" in endpoint and "]" in endpoint:
                    method_path, name = endpoint.split(" [", 1)
                    name = name.rstrip("]")
                else:
                    method_path, name = endpoint, ""
                method, path_value = method_path.split(" ", 1)

                # 获取对应的ID
                api_id = endpoint_to_id_map.get(endpoint)

                results.append({
                    "method": method,
                    "path": path_value,
                    "name": name,
                    "id": api_id,
                    "display": endpoint,
                })

            return QueryResponse(
                success=True,
                query_type=request.query_type,
                total_count=len(endpoints),
                filtered_count=len(filtered_endpoints),
                returned_count=len(results),
                filters_applied=request.filters,
                results=results,
                summary={
                    "filters_applied": not (request.filters.is_empty() if request.filters else True)
                }
            )

        except Exception as e:
            return QueryResponse(
                success=False,
                query_type=request.query_type,
                summary={"error": str(e)}
            )
