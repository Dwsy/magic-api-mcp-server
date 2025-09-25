"""MagicAPI 工具集合模块。"""

from magicapi_mcp.settings import MagicAPISettings, DEFAULT_SETTINGS
from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import error_response
from magicapi_tools.utils.http_client import MagicAPIHTTPClient
from magicapi_tools.utils.resource_manager import MagicAPIResourceManager, MagicAPIResourceTools
from magicapi_tools.utils.ws import (
    MagicAPIWebSocketClient,
    MagicAPIDebugClient,
    MagicAPIDebugTools,
    DebugCompleter,
    run_custom_api_call,
    parse_call_arg,
    setup_readline,
)
from magicapi_tools.utils.extractor import (
    load_resource_tree,
    extract_api_endpoints,
    find_api_id_by_path,
    find_api_detail_by_path,
    filter_endpoints,
    format_file_detail,
    _flatten_tree,
    _filter_nodes,
    _nodes_to_csv,
    MagicAPIExtractorError,
)
__all__ = [
    "MagicAPISettings",
    "DEFAULT_SETTINGS",
    "MagicAPIHTTPClient",
    "MagicAPIResourceManager",
    "MagicAPIExtractorError",
    "MagicAPIResourceTools",
    "MagicAPIWebSocketClient",
    "MagicAPIDebugClient",
    "MagicAPIDebugTools",
    "DebugCompleter",
    "run_custom_api_call",
    "parse_call_arg",
    "setup_readline",
    "load_resource_tree",
    "extract_api_endpoints",
    "error_response",
    "find_api_id_by_path",
    "find_api_detail_by_path",
    "filter_endpoints",
    "format_file_detail",
    "_flatten_tree",
    "_filter_nodes",
    "_nodes_to_csv",
    "get_logger",
]


