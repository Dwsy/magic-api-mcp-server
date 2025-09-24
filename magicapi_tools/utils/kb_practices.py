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
        "mcp_tool_driven": {
            "description": "MCP 工具优先的 Magic-API 助手通用流程",
            "principles": [
                "所有回答必须依据 MCP 工具返回的数据或状态，不得凭记忆或猜测输出结论",
                "遇到信息缺口时优先调用文档、查询、搜索类工具补充事实，再继续推理",
                "关键操作需在执行前后通过相关工具进行快照或校验，确保可回溯、可回滚"
            ],
            "steps": [
                "🧭 准备阶段 → 调用 `system.get_assistant_metadata` 确认环境、鉴权与可用工具，如需流程参考使用 `get_development_workflow`。",
                "🎯 需求拆解 → 使用 `get_magic_api_docs`、`get_best_practices`、`get_development_workflow` 等工具梳理目标与约束，形成行动计划。",
                "🔍 信息采集 → 通过 `search_api_scripts`、`get_api_details_by_path`、`get_resource_tree`、`search_api_endpoints` 等工具获取最新代码与资源状态。",
                "🛠️ 行动执行 → 在掌握信息后，调用 `call_magic_api`、`save_api_endpoint`、`replace_api_script`、`copy_resource`、`move_resource`、`set_breakpoint`、`call_api_with_debug` 等工具完成具体操作。",
                "✅ 结果校验 → 使用 `call_magic_api`、`get_practices_guide(guide_type='debugging')`、`list_backups` 或 `get_common_pitfalls` 复核效果与风险点。",
                "📄 输出总结 → 基于工具返回内容陈述结论，明确指出使用过的核心工具及关键数据，若缺乏足够工具证据需说明限制。"
            ],
            "tool_hints": {
                "准备": ["system.get_assistant_metadata", "get_development_workflow"],
                "调研": ["get_magic_api_docs", "get_best_practices", "get_common_pitfalls", "get_practices_guide"],
                "资产盘点": ["get_resource_tree", "get_api_details_by_path", "get_api_details_by_id", "search_api_endpoints", "search_api_scripts"],
                "执行": ["call_magic_api", "save_api_endpoint", "replace_api_script", "copy_resource", "move_resource", "call_api_with_debug", "set_breakpoint"],
                "收尾": ["list_backups", "rollback_backup", "get_practices_guide", "get_common_pitfalls"]
            }
        },
        "api_script_development": {
            "description": "从需求到上线的API脚本开发流程（包含创建和编辑）",
            "principles": [
                "脚本实现前必须确认目标分组与路径，避免覆盖现有接口",
                "接口发布前通过工具完成至少一次功能与风险检查"
            ],
            "steps": [
                "📂 资源定位 → 使用 `get_resource_tree` 与 `search_api_endpoints` 审阅分组结构和已有接口路径。",
                "🧩 设计对齐 → 借助 `get_magic_script_syntax`、`get_best_practices`、`list_examples` 完成脚本结构与依赖模块评估。",
                "✍️ 脚本准备 → 使用 `get_api_details_by_path` 或 `get_api_details_by_id` 获取参考脚本，确保参数与响应模型一致。",
                "🧪 功能验证 → 通过 `call_magic_api` 或 `call_api_with_debug` 调用接口，核对响应、日志与断点状态。",
                "🛡️ 质量检查 → 使用 `get_practices_guide(guide_type='performance')`、`get_practices_guide(guide_type='security')` 以及 `get_common_pitfalls` 检查性能与安全风险。",
                "🚀 上线发布 → 调用 `save_api_endpoint` 完成保存或复制，通过 `get_resource_tree`、`list_backups` 确认资源已同步。"
            ],
            "tool_hints": {
                "结构规划": ["get_resource_tree", "search_api_endpoints", "get_development_workflow"],
                "脚本设计": ["get_magic_script_syntax", "get_best_practices", "list_examples", "get_magic_api_docs"],
                "校验": ["call_magic_api", "call_api_with_debug", "get_practices_guide", "get_common_pitfalls"],
                "发布": ["save_api_endpoint", "replace_api_script", "copy_resource", "get_resource_tree", "list_backups"]
            }
        },
        "diagnose": {
            "description": "故障排查流程",
            "principles": [
                "复现问题必须通过 MCP 工具采集请求与日志数据",
                "排查过程中避免直接修改线上资源，必要时通过备份工具做好回滚保障"
            ],
            "steps": [
                "🎯 明确症状 → 使用 `call_magic_api` 或 `call_api_with_debug` 复现错误并记录返回体、日志与断点信息。",
                "🔎 定位脚本 → 借助 `get_api_details_by_id`、`get_api_details_by_path`、`search_api_scripts`、`get_resource_tree` 找到问题脚本与版本。",
                "🪲 深入调试 → 调用 `set_breakpoint`、`step_over_breakpoint`、`resume_breakpoint_execution`、`list_breakpoints` 检查关键变量与流程。",
                "📚 对照知识库 → 使用 `get_practices_guide(guide_type='debugging')` 与 `get_common_pitfalls` 匹配常见错误模式。",
                "🔁 修复验证 → 修复后重新执行 `call_magic_api` 或 `call_api_with_debug`，确认异常消失并检查副作用。",
                "🧾 结果固化 → 通过 `create_full_backup` 或 `list_backups` 记录变更前后状态，并整理结论输出。"
            ],
            "tool_hints": {
                "复现": ["call_magic_api", "call_api_with_debug"],
                "定位": ["get_api_details_by_id", "get_api_details_by_path", "search_api_scripts", "get_resource_tree"],
                "调试": ["set_breakpoint", "step_over_breakpoint", "resume_breakpoint_execution", "list_breakpoints"],
                "知识库": ["get_practices_guide", "get_common_pitfalls"],
                "收尾": ["create_full_backup", "list_backups", "call_magic_api"]
            }
        },
        "optimize": {
            "description": "性能优化流程",
            "principles": [
                "优化前后都要通过工具记录基线与优化结果，便于量化收益",
                "优先定位查询与脚本中的热点路径，避免大范围无效改动"
            ],
            "steps": [
                "📊 建立基线 → 使用 `call_magic_api` 收集响应数据，并通过 `get_practices_guide(guide_type='performance')` 明确指标。",
                "🔎 瓶颈定位 → 借助 `search_api_scripts` 与 `get_api_details_by_path` 检查循环、慢查询及可疑脚本片段。",
                "🧠 策略制定 → 参考 `get_best_practices`、`get_practices_guide(guide_type='performance', category='database')` 等建议制定优化方案。",
                "🛠️ 实施优化 → 使用 `save_api_endpoint`、`replace_api_script`、`copy_resource` 或 `move_resource` 调整资源，必要时结合 `call_api_with_debug` 验证 SQL。",
                "🧪 效果验证 → 再次调用 `call_magic_api` 比对响应指标，并利用 `get_practices_guide(guide_type='performance')` 复盘剩余瓶颈。",
                "📈 持续监控 → 通过 `list_backups`、`get_resource_tree` 记录优化快照，定期复测保证性能稳定。"
            ],
            "tool_hints": {
                "基线": ["call_magic_api", "get_practices_guide"],
                "分析": ["search_api_scripts", "get_api_details_by_path", "get_best_practices"],
                "实施": ["save_api_endpoint", "replace_api_script", "copy_resource", "move_resource", "call_api_with_debug"],
                "验证": ["call_magic_api", "get_practices_guide"],
                "监控": ["list_backups", "get_resource_tree"]
            }
        },
        "refactor": {
            "description": "代码重构流程",
            "principles": [
                "重构范围需通过工具锁定受影响脚本，保证变更可控",
                "重构后必须依靠调用和备份工具验证行为未发生回归"
            ],
            "steps": [
                "🧭 范围识别 → 使用 `search_api_scripts`、`get_api_details_by_path`、`get_resource_tree` 确定重复逻辑与依赖。",
                "🧱 模块抽取 → 参考 `list_examples` 与 `get_best_practices` 设计公共模块或脚本结构。",
                "⚙️ 实施变更 → 借助 `save_api_endpoint`、`copy_resource`、`move_resource` 分步调整资源结构。",
                "🧪 行为校验 → 使用 `call_magic_api`、`call_api_with_debug`、`set_breakpoint` 确认核心路径无回归。",
                "🧰 文档同步 → 通过 `get_development_workflow`、`get_magic_api_docs` 更新说明，必要时生成示例。",
                "🧾 变更固化 → 借助 `create_full_backup` 或 `list_backups` 留存版本，便于审计与回滚。"
            ],
            "tool_hints": {
                "识别": ["search_api_scripts", "get_api_details_by_path", "get_resource_tree"],
                "设计": ["list_examples", "get_best_practices", "get_development_workflow"],
                "实施": ["save_api_endpoint", "copy_resource", "move_resource"],
                "验证": ["call_magic_api", "call_api_with_debug", "set_breakpoint"],
                "归档": ["create_full_backup", "list_backups"]
            }
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
        task: 工作流任务类型，可选值: api_script_development, diagnose, optimize, refactor
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
