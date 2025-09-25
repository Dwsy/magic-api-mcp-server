#!/usr/bin/env python3
"""
API路径提取脚本 - CSV格式输出和详情查看
从数据源提取所有API端点信息，输出为标准CSV格式
支持多种数据源：本地JSON文件或HTTP API端点
支持查看单个接口的详细信息

输出格式：
method,path,name
GET,/api/test,测试接口
POST,/api/data,数据处理

```bash
# 基本使用 - 从默认API获取所有端点
python3 extract_api_paths.py --url

# 按方法过滤 - 只获取POST接口
python3 extract_api_paths.py --url --method POST

# 路径搜索 - 查找包含"WinningReport"的接口
python3 extract_api_paths.py --url --path 'WinningReport'

# 通用搜索 - 同时在路径和名称中搜索"数据"
python3 extract_api_paths.py --url --query '数据'

# 组合过滤 - POST方法且路径包含"db/"
python3 extract_api_paths.py --url --method POST --path '^db/'

# 正则表达式 - 查找报表相关接口
python3 extract_api_paths.py --url --query '.*报表.*|.*report.*'

# 查看接口详情
python3 extract_api_paths.py --detail ad0dbdf495c041409c6a66693a0c06c7

# 通过路径获取ID - 查找指定路径对应的API端点ID（智能路径匹配）
python3 extract_api_paths.py --url --path-to-id '/test00/test0001'     # 带前导斜杠
python3 extract_api_paths.py --url --path-to-id 'test00/test0001'      # 不带前导斜杠
python3 extract_api_paths.py --url --path-to-id 'db/module/list'       # 自动匹配

# 通过路径直接获取详情 - 查找指定路径对应的API端点并直接显示详细信息（智能路径匹配）
python3 extract_api_paths.py --url --path-to-detail '/test00/test0001'  # 带前导斜杠
python3 extract_api_paths.py --url --path-to-detail 'test00/test0001'   # 不带前导斜杠
python3 extract_api_paths.py --url --path-to-detail 'db/module/list'    # 自动匹配
```

适用场景：给大模型或其他程序使用
"""

import json
import sys
import re
import subprocess
from typing import List, Dict, Any, Optional


def clean_path(path: str) -> str:
    """清理路径，移除重复的斜杠"""
    if not path:
        return ""
    # 移除开头和结尾的斜杠，然后用单个斜杠替换多个斜杠
    path = path.strip('/')
    while '//' in path:
        path = path.replace('//', '/')
    return path


def traverse_api_tree(node: Dict[str, Any], parent_path: str = "", results: List[str] = None) -> List[str]:
    """
    递归遍历API树结构，提取所有端点信息

    Args:
        node: 当前节点
        parent_path: 父路径
        results: 结果列表

    Returns:
        包含所有API端点的列表
    """
    if results is None:
        results = []

    node_info = node.get('node', {})
    current_path = node_info.get('path', '')
    current_name = node_info.get('name', '')
    method = node_info.get('method')

    # 构建完整路径
    if current_path and parent_path:
        full_path = f"{parent_path}/{current_path}"
    elif current_path:
        full_path = current_path
    elif parent_path:
        full_path = parent_path
    else:
        full_path = ""

    # 清理路径
    full_path = clean_path(full_path)

    # 如果有HTTP方法，则为API端点
    if method and full_path:
        if current_name and current_name != current_path:
            result = f"{method} {full_path} [{current_name}]"
        else:
            result = f"{method} {full_path}"
        results.append(result)

    # 递归处理子节点
    children = node.get('children', [])
    if children:
        for child in children:
            traverse_api_tree(child, full_path, results)

    return results


def normalize_path(path: str) -> str:
    """
    规范化路径，智能处理前导斜杠和多余斜杠

    Args:
        path: 原始路径

    Returns:
        规范化后的路径
    """
    if not path:
        return ""

    # 移除前导和尾随斜杠，然后用单个斜杠替换多个斜杠
    path = path.strip('/')
    while '//' in path:
        path = path.replace('//', '/')
    return path


def find_api_by_path(node: Dict[str, Any], target_path: str, parent_path: str = "", results: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    通过路径查找API端点信息，支持智能路径匹配

    Args:
        node: 当前节点
        target_path: 目标路径（支持多种格式：带/不带前导斜杠）
        parent_path: 父路径
        results: 结果列表

    Returns:
        匹配的API端点信息列表
    """
    if results is None:
        results = []

    node_info = node.get('node', {})
    current_path = node_info.get('path', '')
    current_name = node_info.get('name', '')
    method = node_info.get('method')
    api_id = node_info.get('id')

    # 构建完整路径
    if current_path and parent_path:
        full_path = f"{parent_path}/{current_path}"
    elif current_path:
        full_path = current_path
    elif parent_path:
        full_path = parent_path
    else:
        full_path = ""

    # 清理路径
    full_path = clean_path(full_path)
    # 规范化目标路径
    normalized_target = normalize_path(target_path)

    # 如果有HTTP方法和ID，则为API端点，检查路径是否匹配
    if method and full_path and api_id:
        # 智能路径匹配：规范化后比较
        normalized_full_path = normalize_path(full_path)

        # 支持多种匹配方式：
        # 1. 精确匹配（规范化后）
        # 2. 以目标路径开头的匹配
        # 3. 目标路径以当前路径开头的匹配（处理部分路径的情况）
        if (normalized_full_path == normalized_target or
            normalized_full_path.startswith(normalized_target + '/') or
            normalized_target.startswith(normalized_full_path + '/')):
            results.append({
                'id': api_id,
                'path': full_path,  # 保持原始路径格式
                'method': method,
                'name': current_name,
                'groupId': node_info.get('groupId')
            })

    # 递归处理子节点
    children = node.get('children', [])
    if children:
        for child in children:
            find_api_by_path(child, target_path, full_path, results)

    return results


def fetch_api_data(url: str) -> Dict[str, Any]:
    """
    从API端点获取数据

    Args:
        url: API端点URL

    Returns:
        解析后的JSON数据
    """
    try:
        # 使用curl命令获取数据
        result = subprocess.run([
            'curl', '-s', '-X', 'POST', url
        ], capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"错误：curl命令执行失败 (返回码: {result.returncode})")
            if result.stderr:
                print(f"错误输出: {result.stderr}")
            sys.exit(1)

        # 检查响应是否为空
        if not result.stdout.strip():
            print("错误：API响应为空")
            sys.exit(1)

        return json.loads(result.stdout)

    except subprocess.TimeoutExpired:
        print("错误：API请求超时 (30秒)")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：API响应JSON解析失败 {e}")
        print(f"原始响应: {result.stdout[:200]}...")
        sys.exit(1)
    except Exception as e:
        print(f"错误：获取API数据失败 {e}")
        sys.exit(1)


def fetch_file_detail(file_id: str, base_url: str = 'http://127.0.0.1:10712') -> Dict[str, Any]:
    """
    获取单个API文件的详细信息

    Args:
        file_id: 文件ID
        base_url: 基础URL

    Returns:
        文件详情数据
    """
    try:
        url = f"{base_url}/magic/web/resource/file/{file_id}"

        # 使用curl命令获取文件详情
        result = subprocess.run([
            'curl', '-s', '-X', 'GET', url
        ], capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"错误：curl命令执行失败 (返回码: {result.returncode})")
            if result.stderr:
                print(f"错误输出: {result.stderr}")
            sys.exit(1)

        # 检查响应是否为空
        if not result.stdout.strip():
            print("错误：API响应为空")
            sys.exit(1)

        data = json.loads(result.stdout)

        # 检查API响应状态
        if data.get('code') != 1:
            print(f"错误：获取文件详情失败 {data.get('message', '未知错误')}")
            sys.exit(1)

        return data.get('data', {})

    except subprocess.TimeoutExpired:
        print("错误：API请求超时 (30秒)")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：API响应JSON解析失败 {e}")
        print(f"原始响应: {result.stdout[:200]}...")
        sys.exit(1)
    except Exception as e:
        print(f"错误：获取文件详情失败 {e}")
        sys.exit(1)


def extract_api_endpoints(source: str, use_url: bool = False) -> List[str]:
    """
    从数据源提取所有API端点

    Args:
        source: 数据源（文件路径或URL）
        use_url: 是否使用URL模式

    Returns:
        排序后的API端点列表
    """
    try:
        if use_url:
            # 从URL获取数据
            data = fetch_api_data(source)
        else:
            # 从文件读取数据
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)

        # 提取API部分的children
        api_data = data.get('data', {}).get('api', {})
        api_children = api_data.get('children', [])

        results = []
        for child in api_children:
            traverse_api_tree(child, "", results)

        # 排序结果
        return sorted(results)

    except FileNotFoundError:
        print(f"错误：找不到文件 {source}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：JSON解析失败 {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)


def find_api_id_by_path(source: str, target_path: str, use_url: bool = False) -> List[Dict[str, Any]]:
    """
    通过路径查找API端点ID

    Args:
        source: 数据源（文件路径或URL）
        target_path: 目标路径
        use_url: 是否使用URL模式

    Returns:
        匹配的API端点信息列表
    """
    try:
        if use_url:
            # 从URL获取数据
            data = fetch_api_data(source)
        else:
            # 从文件读取数据
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)

        # 提取API部分的children
        api_data = data.get('data', {}).get('api', {})
        api_children = api_data.get('children', [])

        results = []
        for child in api_children:
            find_api_by_path(child, target_path, "", results)

        return results

    except FileNotFoundError:
        print(f"错误：找不到文件 {source}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：JSON解析失败 {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)


def filter_endpoints(endpoints: List[str], path_filter: Optional[str] = None,
                    name_filter: Optional[str] = None, method_filter: Optional[str] = None,
                    query_filter: Optional[str] = None) -> List[str]:
    """
    过滤API端点列表

    Args:
        endpoints: API端点列表
        path_filter: 路径过滤器(支持正则表达式)
        name_filter: 名称过滤器(支持正则表达式)
        method_filter: HTTP方法过滤器
        query_filter: 通用查询过滤器(同时搜索路径和名称，支持正则表达式)

    Returns:
        过滤后的端点列表
    """
    filtered = endpoints

    # HTTP方法过滤
    if method_filter:
        method_filter = method_filter.upper()
        filtered = [ep for ep in filtered if ep.startswith(f"{method_filter} ")]

    # 通用查询过滤（同时搜索路径和名称）
    if query_filter:
        try:
            query_pattern = re.compile(query_filter, re.IGNORECASE)
            filtered = [ep for ep in filtered if query_pattern.search(ep.split(' ', 1)[1]) or
                       (query_pattern.search(ep) if '[' in ep and ']' in ep else False)]
        except re.error as e:
            print(f"查询过滤器正则表达式错误: {e}")
            return []

    # 路径过滤
    if path_filter:
        try:
            path_pattern = re.compile(path_filter, re.IGNORECASE)
            filtered = [ep for ep in filtered if path_pattern.search(ep.split(' ', 1)[1])]
        except re.error as e:
            print(f"路径过滤器正则表达式错误: {e}")
            return []

    # 名称过滤
    if name_filter:
        try:
            name_pattern = re.compile(name_filter, re.IGNORECASE)
            filtered = [ep for ep in filtered if '[' in ep and ']' in ep and name_pattern.search(ep)]
        except re.error as e:
            print(f"名称过滤器正则表达式错误: {e}")
            return []

    return filtered


def format_file_detail(file_data: Dict[str, Any]) -> str:
    """
    格式化文件详情输出

    Args:
        file_data: 文件详情数据

    Returns:
        格式化的字符串
    """
    lines = []

    # 基本信息
    lines.append("=== API接口详情 ===")
    lines.append(f"ID: {file_data.get('id', 'N/A')}")
    lines.append(f"名称: {file_data.get('name', 'N/A')}")
    lines.append(f"路径: {file_data.get('path', 'N/A')}")
    lines.append(f"方法: {file_data.get('method', 'N/A')}")
    lines.append(f"分组ID: {file_data.get('groupId', 'N/A')}")
    lines.append("")

    # 脚本内容
    script = file_data.get('script', '')
    if script:
        lines.append("=== 脚本内容 ===")
        lines.append(script)
        lines.append("")
    else:
        lines.append("=== 脚本内容 ===")
        lines.append("(无脚本内容)")
        lines.append("")

    # 元数据信息
    lines.append("=== 元数据信息 ===")
    lines.append(f"创建时间: {file_data.get('createTime', 'N/A')}")
    lines.append(f"更新时间: {file_data.get('updateTime', 'N/A')}")
    lines.append(f"创建者: {file_data.get('createBy', 'N/A')}")
    lines.append(f"更新者: {file_data.get('updateBy', 'N/A')}")

    # 描述信息
    description = file_data.get('description')
    if description:
        lines.append("=== 接口描述 ===")
        lines.append(description)
        lines.append("")

    # 请求配置
    lines.append("=== 请求配置 ===")

    # Headers
    headers = file_data.get('headers', [])
    if headers:
        lines.append("请求头 (Headers):")
        for header in headers:
            required = "✓" if header.get('required', False) else "○"
            lines.append(f"  {required} {header.get('name', '')}: {header.get('value', '')} ({header.get('dataType', 'String')})")
        lines.append("")

    # 路径参数 (Paths)
    paths = file_data.get('paths', [])
    if paths:
        lines.append("路径参数 (Path Parameters):")
        for path_param in paths:
            required = "✓" if path_param.get('required', False) else "○"
            lines.append(f"  {required} {path_param.get('name', '')}: {path_param.get('value', '')} ({path_param.get('dataType', 'String')})")
        lines.append("")

    # 查询参数 (Parameters)
    parameters = file_data.get('parameters', [])
    if parameters:
        lines.append("查询参数 (Query Parameters):")
        for param in parameters:
            required = "✓" if param.get('required', False) else "○"
            lines.append(f"  {required} {param.get('name', '')}: {param.get('value', '')} ({param.get('dataType', 'String')})")
        lines.append("")

    # 请求体 (Request Body)
    request_body = file_data.get('requestBody')
    if request_body:
        lines.append("请求体 (Request Body):")
        if isinstance(request_body, str):
            lines.append(request_body)
        else:
            lines.append(json.dumps(request_body, ensure_ascii=False, indent=2))
        lines.append("")

    # 其他配置信息
    properties = file_data.get('properties', {})
    if properties:
        lines.append("属性配置 (Properties):")
        for key, value in properties.items():
            lines.append(f"  {key}: {value}")
        lines.append("")

    options = file_data.get('options', [])
    if options:
        lines.append("选项配置 (Options):")
        for option in options:
            lines.append(f"  {option}")
        lines.append("")

    # 其他扩展字段
    for key, value in file_data.items():
        if key not in ['id', 'name', 'path', 'method', 'groupId', 'script',
                      'createTime', 'updateTime', 'createBy', 'updateBy',
                      'description', 'headers', 'paths', 'parameters',
                      'requestBody', 'properties', 'options']:
            if not isinstance(value, (list, dict)) or value:  # 只显示非空的值
                lines.append(f"{key}: {value}")

    return "\n".join(lines)


def print_usage():
    """打印使用说明"""
    print("API路径提取脚本 - CSV格式输出和详情查看")
    print("用法: python extract_api_paths.py <数据源> [选项] | --detail <接口ID> | --path-to-id <路径> | --path-to-detail <路径>")
    print("\n数据源可以是:")
    print("  - 本地JSON文件路径")
    print("  - --url参数指定API端点URL")
    print("\n输出格式: 标准CSV格式 (method,path,name)")
    print("适用场景: 给大模型或其他程序使用")
    print("\n选项:")
    print("  --url URL           指定API端点URL (默认: http://127.0.0.1:10712/magic/web/resource)")
    print("  --detail ID         查看指定接口ID的详细信息")
    print("  --path-to-id PATH   通过接口路径获取对应的ID（智能路径匹配，支持带/不带前导斜杠）")
    print("  --path-to-detail PATH 通过接口路径直接获取详细信息（智能路径匹配，支持带/不带前导斜杠）")
    print("  --query PATTERN     通用查询(同时搜索路径和名称，支持正则表达式)")
    print("  --method METHOD     按HTTP方法过滤 (GET, POST, DELETE)")
    print("  --path PATTERN      按路径过滤 (支持正则表达式)")
    print("  --name PATTERN      按名称过滤 (支持正则表达式)")
    print("  --help, -h          显示此帮助信息")
    print("\n示例:")
    print("  # 从本地文件读取")
    print("  python extract_api_paths.py ../sfm_back/response.json")
    print("  ")
    print("  # 从API端点获取")
    print("  python extract_api_paths.py --url http://127.0.0.1:10712/magic/web/resource")
    print("  ")
    print("  # 使用默认API端点")
    print("  python extract_api_paths.py --url")
    print("  ")
    print("  # 查看接口详情")
    print("  python extract_api_paths.py --detail ad0dbdf495c041409c6a66693a0c06c7")
    print("  ")
    print("  # 通过路径获取ID")
    print("  python extract_api_paths.py --path-to-id '/db/module/list'")
    print("  python extract_api_paths.py --url --path-to-id '/db/base'")
    print("  ")
    print("  # 通过路径直接获取详情")
    print("  python extract_api_paths.py --url --path-to-detail '/db/module/list'")
    print("  python extract_api_paths.py --url --path-to-detail 'test00/test0001'")
    print("  ")
    print("  # 各种过滤器示例")
    print("  python extract_api_paths.py ../sfm_back/response.json --query '数据'")
    print("  python extract_api_paths.py --url --method POST")
    print("  python extract_api_paths.py ../sfm_back/response.json --path 'WinningReportFetch'")
    print("  python extract_api_paths.py ../sfm_back/response.json --name '数据'")
    print("  python extract_api_paths.py ../sfm_back/response.json --method GET --path 'db/base'")


def main():
    """主函数"""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h']:
        print_usage()
        sys.exit(0)

    # 解析命令行参数
    data_source = None
    use_url = False
    api_url = 'http://127.0.0.1:10712/magic/web/resource'  # 默认URL
    method_filter = None
    path_filter = None
    name_filter = None
    query_filter = None
    detail_id = None
    path_to_id = None
    path_to_detail = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--url':
            use_url = True
            # 检查是否有指定URL
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--'):
                api_url = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        elif sys.argv[i] == '--detail' and i + 1 < len(sys.argv):
            detail_id = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--path-to-id' and i + 1 < len(sys.argv):
            path_to_id = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--path-to-detail' and i + 1 < len(sys.argv):
            path_to_detail = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--method' and i + 1 < len(sys.argv):
            method_filter = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--path' and i + 1 < len(sys.argv):
            path_filter = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--name' and i + 1 < len(sys.argv):
            name_filter = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--query' and i + 1 < len(sys.argv):
            query_filter = sys.argv[i + 1]
            i += 2
        elif not sys.argv[i].startswith('--'):
            # 如果不是以--开头的参数，认为是数据源
            if data_source is None:
                data_source = sys.argv[i]
            i += 1
        else:
            print(f"未知参数: {sys.argv[i]}")
            print_usage()
            sys.exit(1)

    # 如果指定了--detail参数，则获取接口详情
    if detail_id:
        if data_source or use_url or method_filter or path_filter or name_filter or query_filter or path_to_id:
            print("错误：--detail参数不能与其他参数同时使用")
            sys.exit(1)

        print(f"正在获取接口详情 (ID: {detail_id})...")
        # 从默认URL中提取base_url
        base_url = api_url.replace('/magic/web/resource', '')
        file_data = fetch_file_detail(detail_id, base_url)
        print(format_file_detail(file_data))
        return

    # 如果指定了--path-to-id参数，则通过路径获取ID
    if path_to_id:
        if data_source or method_filter or path_filter or name_filter or query_filter or path_to_detail:
            print("错误：--path-to-id参数不能与其他过滤参数同时使用")
            sys.exit(1)


        # 确定数据源
        if not use_url:
            print("错误：--path-to-id需要使用--url参数指定数据源")
            sys.exit(1)

        api_matches = find_api_id_by_path(api_url, path_to_id, use_url)

        if not api_matches:
            print(f"未找到路径为 '{path_to_id}' 的API端点")
            return

        for match in api_matches:
            print(f"{match['id']}")
        return

    # 如果指定了--path-to-detail参数，则通过路径直接获取详情
    if path_to_detail:
        if data_source or method_filter or path_filter or name_filter or query_filter or detail_id:
            print("错误：--path-to-detail参数不能与其他参数同时使用")
            sys.exit(1)

        # 确定数据源
        if not use_url:
            print("错误：--path-to-detail需要使用--url参数指定数据源")
            sys.exit(1)

        print(f"正在通过路径 '{path_to_detail}' 查找API端点...")
        api_matches = find_api_id_by_path(api_url, path_to_detail, use_url)

        if not api_matches:
            print(f"未找到路径为 '{path_to_detail}' 的API端点")
            return

        # 如果找到多个匹配，默认使用第一个
        if len(api_matches) > 1:
            print(f"找到 {len(api_matches)} 个匹配的端点，使用第一个:")
            for i, match in enumerate(api_matches, 1):
                print(f"  {i}. {match['method']} {match['path']} [{match['name']}] (ID: {match['id']})")
            print()

        target_match = api_matches[0]
        print(f"正在获取接口详情 (ID: {target_match['id']}, 路径: {target_match['path']})...")

        # 从默认URL中提取base_url
        base_url = api_url.replace('/magic/web/resource', '')
        file_data = fetch_file_detail(target_match['id'], base_url)
        print(format_file_detail(file_data))
        return

    # 确定数据源
    if use_url:
        if data_source:
            print("错误：不能同时指定文件路径和--url参数")
            sys.exit(1)
        data_source = api_url
    elif data_source is None:
        print("错误：必须指定数据源（文件路径或--url参数）")
        print_usage()
        sys.exit(1)

    print("正在提取API端点信息...")
    api_endpoints = extract_api_endpoints(data_source, use_url)

    # 应用过滤器
    filtered_endpoints = filter_endpoints(api_endpoints, path_filter, name_filter, method_filter, query_filter)

    print(f"\n找到 {len(filtered_endpoints)} 个API端点")

    if path_filter or name_filter or method_filter or query_filter:
        print("(过滤条件: ", end="")
        filters = []
        if method_filter:
            filters.append(f"方法={method_filter}")
        if path_filter:
            filters.append(f"路径='{path_filter}'")
        if name_filter:
            filters.append(f"名称='{name_filter}'")
        if query_filter:
            filters.append(f"查询='{query_filter}'")
        print(", ".join(filters) + ")")

    print()

    # 输出CSV格式头部
    print("method,path,name")

    if not filtered_endpoints:
        print("没有找到匹配的API端点")
        return

    for endpoint in filtered_endpoints:
        # 解析endpoint格式: "METHOD path [name]"
        parts = endpoint.split(' ', 2)
        method = parts[0]
        path = parts[1]

        # 提取name（如果存在）
        name = ""
        if len(parts) > 2 and parts[2].startswith('[') and parts[2].endswith(']'):
            name = parts[2][1:-1]  # 移除方括号

        # CSV转义：如果字段包含逗号、引号或换行符，需要用引号包围并转义
        def escape_csv_field(field):
            if ',' in field or '"' in field or '\n' in field:
                return f'"{field.replace(chr(34), chr(34) + chr(34))}"'
            return field

        print(f"{method},{escape_csv_field(path)},{escape_csv_field(name)}")


if __name__ == "__main__":
    main()
