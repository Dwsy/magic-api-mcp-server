"""Magic-API 插件系统知识库。"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, List

# 插件系统知识文档
PLUGINS_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "cluster": {
        "name": "集群插件",
        "title": "magic-api-plugin-cluster",
        "description": "支持多实例集群部署，实现接口自动同步",
        "features": [
            "接口变更自动同步到集群所有实例",
            "基于Redis的发布订阅机制",
            "支持实例状态监控",
            "防止接口信息不一致问题"
        ],
        "dependencies": textwrap.dedent('''
            <dependency>
                <groupId>org.ssssssss</groupId>
                <artifactId>magic-api-plugin-cluster</artifactId>
                <version>magic-api-lastest-version</version>
            </dependency>
        ''').strip(),
        "configuration": {
            "instance_id": {
                "key": "magic-api.instance-id",
                "description": "实例唯一标识",
                "example": "instance-01"
            },
            "channel": {
                "key": "magic-api.cluster.channel",
                "description": "Redis频道名称",
                "example": "magic-api:notify:channel"
            }
        },
        "redis_config": textwrap.dedent('''
            spring:
              redis:
                host: 192.168.1.100
                port: 6379
                database: 1
                password: your_password
        ''').strip(),
        "doc": "https://www.ssssssss.org/magic-api/pages/plugin/cluster/"
    },
    "task": {
        "name": "定时任务插件",
        "title": "magic-api-plugin-task",
        "description": "支持在Magic-API中编写定时任务脚本",
        "features": [
            "支持cron表达式配置",
            "可视化任务管理界面",
            "任务执行日志记录",
            "支持动态启停任务",
            "集群环境任务防重复执行"
        ],
        "dependencies": textwrap.dedent('''
            <dependency>
                <groupId>org.ssssssss</groupId>
                <artifactId>magic-api-plugin-task</artifactId>
                <version>magic-api-lastest-version</version>
            </dependency>
        ''').strip(),
        "configuration": {
            "thread_pool": {
                "key": "magic-api.task.pool.size",
                "description": "线程池大小",
                "default": "CPU核心数",
                "example": "8"
            },
            "thread_name": {
                "key": "magic-api.task.thread-name-prefix",
                "description": "线程名称前缀",
                "example": "magic-task-"
            }
        },
        "usage": textwrap.dedent('''
            // 定时任务脚本示例
            import db;
            import log;

            // 查询需要处理的订单
            var orders = db.select("SELECT * FROM orders WHERE status = 'pending'");
            log.info("处理 {} 个待处理订单", orders.size());

            // 处理订单逻辑
            orders.each(order => {
                try {
                    // 处理单个订单
                    db.update("UPDATE orders SET status = 'processed' WHERE id = ?", order.id);
                    log.info("订单 {} 处理完成", order.id);
                } catch(e) {
                    log.error("订单 {} 处理失败: {}", order.id, e.message);
                }
            });
        ''').strip(),
        "doc": "https://www.ssssssss.org/magic-api/pages/plugin/task/"
    },
    "redis": {
        "name": "Redis插件",
        "title": "magic-api-plugin-redis",
        "description": "集成Redis缓存和数据存储功能",
        "features": [
            "将接口信息存储在Redis中",
            "支持Redis作为缓存后端",
            "提供redis模块用于脚本操作",
            "支持Redis集群和哨兵模式"
        ],
        "dependencies": textwrap.dedent('''
            <dependency>
                <groupId>org.ssssssss</groupId>
                <artifactId>magic-api-plugin-redis</artifactId>
                <version>magic-api-lastest-version</version>
            </dependency>
        ''').strip(),
        "configuration": {
            "storage": {
                "description": "使用Redis存储接口信息",
                "example": textwrap.dedent('''
                    magic-api:
                      resource:
                        type: redis
                        prefix: magic-api
                        readonly: false
                ''').strip()
            }
        },
        "usage": textwrap.dedent('''
            import redis;

            // 基本的key-value操作
            redis.set('user:123', '{"name":"张三","age":20}');
            var user = redis.get('user:123');

            // Hash操作
            redis.hset('user:123', 'email', 'zhangsan@example.com');
            var email = redis.hget('user:123', 'email');

            // List操作
            redis.lpush('queue', 'task1', 'task2');
            var task = redis.rpop('queue');

            // Set操作
            redis.sadd('tags', 'java', 'python', 'javascript');
            var tags = redis.smembers('tags');

            // 有序集合
            redis.zadd('scores', 95, 'user:123');
            var rank = redis.zrevrank('scores', 'user:123');
        ''').strip(),
        "doc": "https://www.ssssssss.org/magic-api/pages/plugin/redis/"
    },
    "mongodb": {
        "name": "MongoDB插件",
        "title": "magic-api-plugin-mongo",
        "description": "集成MongoDB数据库操作功能",
        "features": [
            "提供mongo模块进行数据库操作",
            "支持文档的增删改查",
            "支持聚合管道操作",
            "支持索引管理",
            "支持GridFS文件存储"
        ],
        "dependencies": textwrap.dedent('''
            <dependency>
                <groupId>org.ssssssss</groupId>
                <artifactId>magic-api-plugin-mongo</artifactId>
                <version>magic-api-lastest-version</version>
            </dependency>
        ''').strip(),
        "configuration": textwrap.dedent('''
            spring:
              data:
                mongodb:
                  host: localhost
                  port: 27017
                  database: magicapi
                  username: magicapi
                  password: 123456
        ''').strip(),
        "usage": textwrap.dedent('''
            import mongo;

            // 插入文档
            mongo.database('mydb').collection('users').insert({
                name: '张三',
                age: 20,
                email: 'zhangsan@example.com'
            });

            // 查询文档
            var users = mongo.database('mydb').collection('users')
                .find({age: {$gte: 18}})
                .sort({age: -1})
                .limit(10)
                .list();

            // 更新文档
            mongo.database('mydb').collection('users')
                .update(
                    {name: '张三'},
                    {$set: {age: 21}}
                );

            // 删除文档
            mongo.database('mydb').collection('users')
                .remove({age: {$lt: 18}});

            // 聚合查询
            var result = mongo.database('mydb').collection('orders')
                .aggregate([
                    {$match: {status: 'completed'}},
                    {$group: {_id: '$userId', total: {$sum: '$amount'}}},
                    {$sort: {total: -1}},
                    {$limit: 10}
                ]);
        ''').strip(),
        "doc": "https://www.ssssssss.org/magic-api/pages/plugin/mongo/"
    },
    "elasticsearch": {
        "name": "ElasticSearch插件",
        "title": "magic-api-plugin-elasticsearch",
        "description": "集成ElasticSearch搜索引擎功能",
        "features": [
            "提供elasticsearch模块进行搜索操作",
            "支持索引的创建、删除和管理",
            "支持文档的增删改查",
            "支持复杂查询DSL",
            "支持聚合分析"
        ],
        "dependencies": textwrap.dedent('''
            <dependency>
                <groupId>org.ssssssss</groupId>
                <artifactId>magic-api-plugin-elasticsearch</artifactId>
                <version>magic-api-lastest-version</version>
            </dependency>
        ''').strip(),
        "configuration": textwrap.dedent('''
            spring:
              elasticsearch:
                rest:
                  uris: http://127.0.0.1:9200
                  username: elastic
                  password: 123456789
        ''').strip(),
        "usage": textwrap.dedent('''
            import elasticsearch;

            // 创建索引
            elasticsearch.index('users').create({
                mappings: {
                    properties: {
                        name: {type: 'text'},
                        age: {type: 'integer'},
                        email: {type: 'keyword'}
                    }
                }
            });

            // 索引文档
            elasticsearch.index('users').index('user-1', {
                name: '张三',
                age: 20,
                email: 'zhangsan@example.com'
            });

            // 搜索文档
            var result = elasticsearch.index('users').search({
                query: {
                    bool: {
                        must: [
                            {match: {name: '张三'}}
                        ],
                        filter: [
                            {range: {age: {gte: 18}}}
                        ]
                    }
                },
                sort: [{age: {order: 'desc'}}],
                from: 0,
                size: 10
            });

            // 更新文档
            elasticsearch.index('users').update('user-1', {
                doc: {age: 21}
            });

            // 删除文档
            elasticsearch.index('users').delete('user-1');
        ''').strip(),
        "doc": "https://www.ssssssss.org/magic-api/pages/plugin/elasticsearch/"
    },
    "swagger": {
        "name": "Swagger插件",
        "title": "magic-api-plugin-swagger",
        "description": "生成Swagger API文档",
        "features": [
            "自动生成API文档",
            "支持在线测试接口",
            "集成Swagger UI界面",
            "支持API分组管理"
        ],
        "dependencies": textwrap.dedent('''
            <dependency>
                <groupId>org.ssssssss</groupId>
                <artifactId>magic-api-plugin-swagger</artifactId>
                <version>magic-api-lastest-version</version>
            </dependency>
        ''').strip(),
        "configuration": {
            "version": {
                "key": "magic-api.swagger.version",
                "description": "API版本",
                "default": "1.0"
            },
            "title": {
                "key": "magic-api.swagger.title",
                "description": "API文档标题",
                "default": "MagicAPI Swagger Docs"
            }
        },
        "note": "Spring Boot 3.x 请使用 springdoc 插件替代",
        "doc": "https://www.ssssssss.org/magic-api/pages/plugin/swagger/"
    },
    "springdoc": {
        "name": "SpringDoc插件",
        "title": "magic-api-plugin-springdoc",
        "description": "生成OpenAPI 3.0文档（Spring Boot 3.x）",
        "features": [
            "兼容Spring Boot 3.x",
            "生成OpenAPI 3.0规范文档",
            "集成Swagger UI",
            "支持API分组和标签"
        ],
        "dependencies": textwrap.dedent('''
            <dependency>
                <groupId>org.ssssssss</groupId>
                <artifactId>magic-api-plugin-springdoc</artifactId>
                <version>magic-api-lastest-version</version>
            </dependency>
        ''').strip(),
        "note": "专为Spring Boot 3.x设计，不兼容2.x版本",
        "doc": "https://www.ssssssss.org/magic-api/pages/plugin/springdoc/"
    },
    "git": {
        "name": "Git插件",
        "title": "magic-api-plugin-git",
        "description": "使用Git作为接口版本控制和存储",
        "features": [
            "接口版本控制",
            "多人协作开发",
            "变更历史追踪",
            "分支管理支持"
        ],
        "dependencies": textwrap.dedent('''
            <dependency>
                <groupId>org.ssssssss</groupId>
                <artifactId>magic-api-plugin-git</artifactId>
                <version>magic-api-lastest-version</version>
            </dependency>
        ''').strip(),
        "configuration": {
            "repository": {
                "key": "magic-api.resource.git.url",
                "description": "Git仓库地址",
                "example": "git@github.com:user/repo.git"
            },
            "branch": {
                "key": "magic-api.resource.git.branch",
                "description": "分支名称",
                "default": "master"
            },
            "auth": {
                "description": "认证配置",
                "ssh_key": "magic-api.resource.git.privateKey",
                "username": "magic-api.resource.git.username",
                "password": "magic-api.resource.git.password"
            }
        },
        "note": "目前处于预览阶段，SSH密钥需要使用PEM格式",
        "doc": "https://www.ssssssss.org/magic-api/pages/plugin/git/"
    },
    "nebula": {
        "name": "Nebula插件",
        "title": "magic-api-plugin-nebula",
        "description": "集成Nebula图数据库操作",
        "features": [
            "图数据库查询支持",
            "nGQL语法执行",
            "图数据可视化",
            "支持复杂图查询"
        ],
        "dependencies": textwrap.dedent('''
            <dependency>
                <groupId>org.ssssssss</groupId>
                <artifactId>magic-api-plugin-nebula</artifactId>
                <version>magic-api-lastest-version</version>
            </dependency>
        ''').strip(),
        "configuration": textwrap.dedent('''
            nebula:
              hostAddress: localhost:9669
              userName: root
              password: nebula
        ''').strip(),
        "usage": textwrap.dedent('''
            import nebula;

            // 图查询
            var ngsl = """
                USE db_name;
                MATCH p_=(p:`assignee`)-[*3]-(p2:`transferor`)
                WHERE id(p2) == "阿里巴巴" or id(p)== "阿里巴巴"
                RETURN p_ LIMIT 1000
            """;

            var result = nebula.executeJson(ngsl);
            var graphData = nebula.convert(result);
            return graphData; // 返回nodes和edges结构
        ''').strip(),
        "doc": "https://www.ssssssss.org/magic-api/pages/plugin/nebula/"
    }
}

def get_plugin_docs(plugin_name: str = None) -> Any:
    """获取插件文档。

    Args:
        plugin_name: 插件名称，可选值: cluster, task, redis, mongodb, elasticsearch, swagger, springdoc, git, nebula
                     如果不指定则返回所有插件

    Returns:
        指定插件的文档或所有插件文档
    """
    if plugin_name:
        return PLUGINS_KNOWLEDGE.get(plugin_name)
    return PLUGINS_KNOWLEDGE

def list_available_plugins() -> List[str]:
    """获取所有可用插件名称。"""
    return list(PLUGINS_KNOWLEDGE.keys())

def search_plugins(keyword: str) -> List[Dict[str, Any]]:
    """根据关键词搜索插件。

    Args:
        keyword: 搜索关键词

    Returns:
        匹配的插件列表
    """
    results = []
    keyword_lower = keyword.lower()

    for plugin_name, plugin_data in PLUGINS_KNOWLEDGE.items():
        if (keyword_lower in plugin_name.lower() or
            keyword_lower in plugin_data.get("description", "").lower() or
            any(keyword_lower in feature.lower() for feature in plugin_data.get("features", []))):
            results.append(plugin_data)

    return results

def get_plugin_dependencies(plugin_name: str) -> str:
    """获取插件的Maven依赖配置。

    Args:
        plugin_name: 插件名称

    Returns:
        Maven依赖XML字符串
    """
    plugin = PLUGINS_KNOWLEDGE.get(plugin_name)
    if plugin and "dependencies" in plugin:
        return plugin["dependencies"]
    return ""

def get_plugin_config_example(plugin_name: str) -> str:
    """获取插件配置示例。

    Args:
        plugin_name: 插件名称

    Returns:
        配置示例字符串
    """
    plugin = PLUGINS_KNOWLEDGE.get(plugin_name)
    if not plugin:
        return ""

    examples = []

    # 添加配置项示例
    if "configuration" in plugin:
        config_items = []
        for config_item in plugin["configuration"].values():
            if isinstance(config_item, dict) and "key" in config_item and "example" in config_item:
                config_items.append(f"{config_item['key']}: {config_item['example']}")
        if config_items:
            examples.append("\n".join(config_items))

    # 添加其他配置示例
    for key, value in plugin.items():
        if key not in ["name", "title", "description", "features", "dependencies", "configuration", "note", "doc"] and isinstance(value, str) and "example" in key.lower():
            examples.append(value)

    return "\n\n".join(examples) if examples else ""

__all__ = [
    "PLUGINS_KNOWLEDGE",
    "get_plugin_docs",
    "list_available_plugins",
    "search_plugins",
    "get_plugin_dependencies",
    "get_plugin_config_example"
]
