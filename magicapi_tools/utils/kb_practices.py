"""Magic-API 最佳实践和常见问题知识库。"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, List

# 最佳实践和常见问题知识
PRACTICES_KNOWLEDGE: Dict[str, Any] = {
    "doc_index": [
        {
            "title": "脚本语法总览",
            "url": "https://www.ssssssss.org/magic-api/pages/base/script/",
            "highlights": ["关键字、运算符、数据类型、Lambda"]
        },
        {
            "title": "内置模块 - response",
            "url": "https://www.ssssssss.org/magic-api/pages/module/response/",
            "highlights": ["统一返回体", "错误响应"]
        },
        {
            "title": "集合扩展",
            "url": "https://www.ssssssss.org/magic-api/pages/extension/collection/",
            "highlights": ["map/filter/each", "join/shuffle"]
        }
    ],
    "best_practices": [
        "SQL 参数一律使用 `#{}` 绑定，避免 `${}` 拼接",
        "接口返回统一通过 `response` 模块封装，按需选择 json/page/text/download",
        "接口参数校验优先使用界面配置的 required/validate/expression，脚本内仅做兜底",
        "复杂写操作使用 `db.transaction` 并捕获异常或 `exit` 指定业务码回滚",
        "使用 `exit code, message, data` 快速返回标准结构，结合 response 模块保持接口格式统一",
        "分页接口使用 `response.page(total, list)` 并保证 count/limit 同步",
        "链式分页优先使用 `db.table(...).page()`，继承全局分页配置并减少手写 offset/limit",
        "二进制/文件输出使用 `response.download`、`response.image` 或 `response.end`，并设置必要的 Header/状态码",
        "公共逻辑抽取至模块并使用 `import '@:/xxx'` 复用，调用端保留 `Magic-Request-Client-Id` 等追踪信息",
        "大对象序列化注意性能，使用 `transient` 标记临时字段，复杂对象考虑分页或流式处理",
        "异步操作使用 `async` 关键字，注意线程安全和异常处理",
        "缓存使用时注意失效时间和内存占用，重要数据定期刷新",
        "日志记录使用 `log` 模块，区分 debug/info/warn/error 级别",
        "类型转换使用 `::type(defaultValue)` 语法，提供默认值避免空指针",
        "集合操作优先使用函数式编程：`map`/`filter`/`group` 等，提高代码可读性"
    ],
    "pitfalls": [
        "0.4.6+ 逻辑运算对非布尔类型短路，与旧版本不同",
        "`exit` 会跳过 `finally`，涉及事务需谨慎",
        "`asDate()` 需要区分 10 位秒/13 位毫秒时间戳",
        "大 JSON 响应需分页或拆分，避免 UI 卡顿",
        "Token 鉴权与 UI 会话不同步，注意 Header 注入",
        "多数据源切换时注意事务一致性",
        "缓存未设置过期时间可能导致内存泄漏",
        "异步操作中修改外部变量可能出现线程安全问题",
        "正则表达式性能敏感，复杂模式考虑预编译",
        "文件上传注意大小限制和类型校验",
        "数据库连接池配置不当导致连接耗尽",
        "循环中频繁创建对象影响垃圾回收",
        "深层递归调用可能导致栈溢出",
        "时间比较注意时区和格式一致性",
        "浮点数精度问题，使用 BigDecimal 处理金额",
        "集合遍历时删除元素注意并发修改异常"
    ],
    "workflows": {
        "create_api": {
            "description": "从需求到上线的接口创建流程",
            "steps": [
                "resource_tree → path_to_id：查找相近接口/分组",
                "api_detail：对齐脚本结构与模块导入",
                "syntax/examples：补齐语法与参考实现",
                "编写脚本并在 Magic-API UI 保存",
                "call：使用 MCP 工具或 `magic_api_client.py` 验证",
                "best_practices/pitfalls：检查风险项",
                "部署上线并监控运行状态"
            ]
        },
        "diagnose": {
            "description": "故障排查流程",
            "steps": [
                "call：复现请求并采集日志",
                "magic_api_debug_client.py：设置断点观察变量",
                "api_detail：确认最新脚本内容",
                "pitfalls：对照常见问题归因",
                "performance：检查SQL和逻辑性能瓶颈",
                "fix：修复问题并重新验证"
            ]
        },
        "optimize": {
            "description": "性能优化流程",
            "steps": [
                "profiling：开启SQL和接口执行时间统计",
                "analyze：分析慢查询和热点路径",
                "cache：添加适当缓存层",
                "async：将耗时操作异步化",
                "batch：合并多次数据库操作",
                "test：性能测试验证优化效果"
            ]
        },
        "refactor": {
            "description": "代码重构流程",
            "steps": [
                "identify：识别代码异味和重复逻辑",
                "extract：提取公共函数和模块",
                "simplify：简化复杂条件和嵌套",
                "document：完善注释和文档",
                "test：确保重构后功能一致",
                "review：代码审查确保质量"
            ]
        }
    },
    "performance_tips": {
        "database": [
            "使用 `#{}` 参数绑定防止SQL注入并提升性能",
            "合理使用索引，避免全表扫描",
            "分页查询注意内存占用，设置合理的页大小",
            "批量操作使用 `batchUpdate` 而不是循环单条",
            "复杂查询考虑使用视图或存储过程",
            "读写分离，将查询操作路由到从库"
        ],
        "cache": [
            "热点数据使用缓存减少数据库压力",
            "设置合理的缓存过期时间",
            "缓存穿透使用空值缓存或布隆过滤器",
            "缓存雪崩设置随机过期时间",
            "大对象考虑压缩存储",
            "缓存更新使用主动更新而非被动失效"
        ],
        "async": [
            "IO密集型操作使用异步提高并发",
            "注意线程池大小，避免创建过多线程",
            "异步操作设置合理的超时时间",
            "异步结果处理注意异常捕获",
            "避免在异步操作中修改共享状态"
        ],
        "memory": [
            "大集合分页处理，避免一次性加载全部数据",
            "及时释放不需要的对象引用",
            "循环中避免创建大量临时对象",
            "使用流式处理大文件",
            "监控内存使用情况，及时发现泄漏"
        ]
    },
    "security_practices": {
        "input_validation": [
            "所有用户输入必须校验类型和格式",
            "SQL参数使用 `#{}` 绑定防止注入",
            "文件上传限制类型、大小和数量",
            "正则表达式避免ReDoS攻击",
            "JSON解析设置大小限制"
        ],
        "authentication": [
            "敏感接口要求身份认证",
            "Token要有过期时间",
            "使用HTTPS传输敏感数据",
            "实现登录失败次数限制",
            "定期更换加密密钥"
        ],
        "authorization": [
            "实现基于角色的访问控制",
            "敏感操作要求二次确认",
            "接口权限细粒度控制",
            "审计重要操作日志",
            "数据脱敏显示"
        ],
        "data_protection": [
            "敏感数据加密存储",
            "日志中避免记录敏感信息",
            "API密钥妥善保管",
            "数据库备份加密",
            "传输数据压缩和加密"
        ]
    },
    "debugging_guide": {
        "common_issues": [
            {
                "symptom": "接口返回500错误",
                "causes": ["语法错误", "空指针异常", "数据库连接问题", "权限不足"],
                "solutions": ["检查日志", "使用debug模式", "验证参数", "测试数据库连接"]
            },
            {
                "symptom": "SQL执行报错",
                "causes": ["参数绑定错误", "表名/字段名错误", "权限不足", "连接超时"],
                "solutions": ["检查SQL语法", "验证参数值", "确认数据库权限", "检查连接配置"]
            },
            {
                "symptom": "性能问题",
                "causes": ["SQL未使用索引", "循环查询", "内存泄漏", "线程阻塞"],
                "solutions": ["查看执行计划", "使用批量操作", "监控内存使用", "异步处理"]
            },
            {
                "symptom": "数据不一致",
                "causes": ["事务未提交", "并发修改", "缓存未更新", "集群同步延迟"],
                "solutions": ["检查事务边界", "使用乐观锁", "主动更新缓存", "等待同步完成"]
            }
        ],
        "debug_tools": [
            "使用 `log` 模块记录关键步骤",
            "开启SQL执行时间统计",
            "使用断点调试复杂逻辑",
            "监控内存和CPU使用情况",
            "分析网络请求延迟",
            "检查第三方服务状态"
        ]
    },
    "migration_guide": {
        "from_1x_to_2x": [
            "备份现有接口数据",
            "升级Maven依赖版本",
            "更新配置文件项名称",
            "重新导入接口数据",
            "测试所有接口功能",
            "检查权限配置是否正常"
        ],
        "from_2x_to_3x": [
            "备份数据库和配置文件",
            "升级Spring Boot到3.x",
            "更换swagger插件为springdoc",
            "更新Java代码兼容性",
            "测试所有功能是否正常",
            "监控性能是否有变化"
        ]
    },
    "deployment_best_practices": {
        "development": [
            "使用文件存储便于开发调试",
            "开启debug模式和详细日志",
            "配置本地数据库环境",
            "设置合理的缓存时间",
            "启用热重载功能"
        ],
        "staging": [
            "使用数据库存储接口信息",
            "配置独立的测试数据库",
            "开启SQL执行日志",
            "设置中等缓存时间",
            "配置监控和告警"
        ],
        "production": [
            "使用集群模式确保高可用",
            "配置生产数据库连接池",
            "设置合适的日志级别",
            "配置长效缓存策略",
            "启用安全加固措施",
            "定期备份数据",
            "监控系统性能指标"
        ]
    }
}

def get_best_practices() -> List[str]:
    """获取最佳实践列表。"""
    return PRACTICES_KNOWLEDGE["best_practices"]

def get_pitfalls() -> List[str]:
    """获取常见问题列表。"""
    return PRACTICES_KNOWLEDGE["pitfalls"]

def get_workflow(task: str = None) -> Dict[str, Any] | List[Dict[str, Any]]:
    """获取工作流指南。

    Args:
        task: 工作流任务类型，可选值: create_api, diagnose, optimize, refactor
              如果不指定则返回所有工作流

    Returns:
        指定工作流的详细信息或所有工作流列表
    """
    workflows = PRACTICES_KNOWLEDGE["workflows"]
    if task:
        return workflows.get(task, {})
    return list(workflows.values())

def get_performance_tips(category: str = None) -> Dict[str, Any] | List[str]:
    """获取性能优化建议。

    Args:
        category: 性能分类，可选值: database, cache, async, memory
                  如果不指定则返回所有分类

    Returns:
        指定分类的性能建议或所有建议
    """
    tips = PRACTICES_KNOWLEDGE["performance_tips"]
    if category:
        return tips.get(category, [])
    return tips

def get_security_practices(category: str = None) -> Dict[str, Any] | List[str]:
    """获取安全实践建议。

    Args:
        category: 安全分类，可选值: input_validation, authentication, authorization, data_protection
                  如果不指定则返回所有分类

    Returns:
        指定分类的安全建议或所有建议
    """
    practices = PRACTICES_KNOWLEDGE["security_practices"]
    if category:
        return practices.get(category, [])
    return practices

def get_debugging_guide(section: str = None) -> Any:
    """获取调试指南。

    Args:
        section: 调试部分，可选值: common_issues, debug_tools
                 如果不指定则返回整个调试指南

    Returns:
        指定部分的调试指南或完整指南
    """
    guide = PRACTICES_KNOWLEDGE["debugging_guide"]
    if section:
        return guide.get(section, [])
    return guide

def get_migration_guide(version: str = None) -> Dict[str, Any] | List[Dict[str, Any]]:
    """获取迁移指南。

    Args:
        version: 版本迁移，可选值: from_1x_to_2x, from_2x_to_3x
                 如果不指定则返回所有迁移指南

    Returns:
        指定版本的迁移步骤或所有迁移指南
    """
    guide = PRACTICES_KNOWLEDGE["migration_guide"]
    if version:
        return guide.get(version, {})
    return list(guide.values())

def get_deployment_best_practices(env: str = None) -> Dict[str, Any] | List[Dict[str, Any]]:
    """获取部署最佳实践。

    Args:
        env: 环境类型，可选值: development, staging, production
             如果不指定则返回所有环境的实践

    Returns:
        指定环境的部署实践或所有环境的实践
    """
    practices = PRACTICES_KNOWLEDGE["deployment_best_practices"]
    if env:
        return practices.get(env, [])
    return practices

def search_practices(keyword: str) -> List[Dict[str, Any]]:
    """根据关键词搜索实践内容。

    Args:
        keyword: 搜索关键词

    Returns:
        匹配的实践内容列表
    """
    results = []
    keyword_lower = keyword.lower()

    # 搜索最佳实践
    for practice in PRACTICES_KNOWLEDGE["best_practices"]:
        if keyword_lower in practice.lower():
            results.append({
                "type": "best_practice",
                "content": practice,
                "category": "最佳实践"
            })

    # 搜索常见问题
    for pitfall in PRACTICES_KNOWLEDGE["pitfalls"]:
        if keyword_lower in pitfall.lower():
            results.append({
                "type": "pitfall",
                "content": pitfall,
                "category": "常见问题"
            })

    # 搜索性能建议
    for category, tips in PRACTICES_KNOWLEDGE["performance_tips"].items():
        for tip in tips:
            if keyword_lower in tip.lower():
                results.append({
                    "type": "performance_tip",
                    "content": tip,
                    "category": f"性能优化-{category}"
                })

    # 搜索安全实践
    for category, practices in PRACTICES_KNOWLEDGE["security_practices"].items():
        for practice in practices:
            if keyword_lower in practice.lower():
                results.append({
                    "type": "security_practice",
                    "content": practice,
                    "category": f"安全实践-{category}"
                })

    return results

__all__ = [
    "PRACTICES_KNOWLEDGE",
    "get_best_practices",
    "get_pitfalls",
    "get_workflow",
    "get_performance_tips",
    "get_security_practices",
    "get_debugging_guide",
    "get_migration_guide",
    "get_deployment_best_practices",
    "search_practices"
]
