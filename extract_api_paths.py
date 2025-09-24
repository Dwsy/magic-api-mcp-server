#!/usr/bin/env python3
"""Magic-API 资源树提取脚本（工程化重构）。"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from magicapi_tools import (
    MagicAPIHTTPClient,
    MagicAPISettings,
    extract_api_endpoints,
    find_api_detail_by_path,
    find_api_id_by_path,
    filter_endpoints,
    format_file_detail,
    load_resource_tree,
)
from magicapi_tools import MagicAPIExtractorError, ResourceTree

DEFAULT_RESOURCE_URL = "http://127.0.0.1:10712/magic/web/resource"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="提取 Magic-API 资源树信息，支持 CSV 输出和详情查看",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("source", nargs="?", help="本地 JSON 数据源路径")
    parser.add_argument(
        "--url",
        nargs="?",
        const=DEFAULT_RESOURCE_URL,
        help="资源树 HTTP URL，省略值则使用默认地址",
    )
    parser.add_argument("--detail", help="根据接口 ID 输出详情")
    parser.add_argument("--path-to-id", dest="path_to_id", help="路径 → ID 查询")
    parser.add_argument("--path-to-detail", dest="path_to_detail", help="路径 → 详情查询")
    parser.add_argument("--method", dest="method_filter", help="按 HTTP 方法过滤")
    parser.add_argument("--path", dest="path_filter", help="按路径正则过滤")
    parser.add_argument("--name", dest="name_filter", help="按名称正则过滤")
    parser.add_argument("--query", dest="query_filter", help="路径/名称模糊匹配")
    return parser.parse_args()


def build_http_client(target_url: Optional[str]) -> Optional[MagicAPIHTTPClient]:
    if not target_url:
        return None
    base_url = target_url.rstrip("/")
    if base_url.endswith("/magic/web/resource"):
        base_url = base_url[: -len("/magic/web/resource")]
    settings = MagicAPISettings(base_url=base_url)
    return MagicAPIHTTPClient(settings=settings)


def ensure_tree(
    *,
    client: Optional[MagicAPIHTTPClient],
    source: Optional[str],
) -> ResourceTree:
    if client:
        return load_resource_tree(client=client)
    if source:
        return load_resource_tree(source)
    raise MagicAPIExtractorError("缺少资源树数据源，请提供本地文件或 --url")


def handle_detail(detail_id: str, client: Optional[MagicAPIHTTPClient]) -> None:
    http_client = client or MagicAPIHTTPClient()
    ok, payload = http_client.api_detail(detail_id)
    if not ok:
        raise MagicAPIExtractorError(payload)
    print(format_file_detail(payload))


def handle_path_to_id(tree: ResourceTree, path_expr: str) -> None:
    matches = find_api_id_by_path(tree, path_expr)
    if not matches:
        print(f"未找到路径为 '{path_expr}' 的 API 端点")
        return
    for match in matches:
        print(match["id"])


def handle_path_to_detail(client: MagicAPIHTTPClient, path_expr: str) -> None:
    details = find_api_detail_by_path(path_expr, client=client)
    if not details:
        print(f"未找到路径为 '{path_expr}' 的 API 端点")
        return
    if len(details) > 1:
        print(f"找到 {len(details)} 个匹配端点，显示全部详情：\n")
    for item in details:
        meta = item.get("meta", {})
        print(f"=== {meta.get('method')} {meta.get('path')} (ID: {meta.get('id')}) ===")
        if "detail" in item:
            print(format_file_detail(item["detail"]))
        else:
            print(f"错误：{item.get('error')}")
        print()


def handle_list(
    tree: ResourceTree,
    *,
    method_filter: Optional[str],
    path_filter: Optional[str],
    name_filter: Optional[str],
    query_filter: Optional[str],
) -> None:
    endpoints = extract_api_endpoints(tree)
    endpoints = filter_endpoints(
        endpoints,
        path_filter=path_filter,
        name_filter=name_filter,
        method_filter=method_filter,
        query_filter=query_filter,
    )
    if not endpoints:
        print("未找到符合条件的接口")
        return
    print("method,path,name")
    for entry in endpoints:
        if "[" in entry and "]" in entry:
            method_path, name = entry.split(" [", 1)
            name = name.rstrip("]")
        else:
            method_path, name = entry, ""
        method, path = method_path.split(" ", 1)
        print(f"{method},{path},{name}")


def validate_args(args: argparse.Namespace) -> None:
    exclusive = [args.detail, args.path_to_id, args.path_to_detail]
    if sum(1 for item in exclusive if item) > 1:
        raise MagicAPIExtractorError("--detail/--path-to-id/--path-to-detail 参数互斥")
    if args.path_to_id and not args.url:
        raise MagicAPIExtractorError("--path-to-id 需配合 --url 使用")
    if args.path_to_detail and not args.url:
        raise MagicAPIExtractorError("--path-to-detail 需配合 --url 使用")


def main() -> None:
    args = parse_args()
    try:
        validate_args(args)
        client = build_http_client(args.url)

        if args.detail:
            handle_detail(args.detail, client)
            return

        if args.path_to_id:
            tree = ensure_tree(client=client, source=args.source)
            handle_path_to_id(tree, args.path_to_id)
            return

        if args.path_to_detail:
            if not client:
                raise MagicAPIExtractorError("--path-to-detail 需配合 --url 使用")
            handle_path_to_detail(client, args.path_to_detail)
            return

        tree = ensure_tree(client=client, source=args.source)
        handle_list(
            tree,
            method_filter=args.method_filter,
            path_filter=args.path_filter,
            name_filter=args.name_filter,
            query_filter=args.query_filter,
        )
    except MagicAPIExtractorError as exc:
        print(f"错误：{exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
