"""Magic-API 配置相关知识库。"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, List

# 配置相关知识文档
CONFIG_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "spring_boot": {
        "title": "Spring Boot 配置",
        "description": "Magic-API 的核心配置文件设置",
        "config": {
            "magic-api.web": {
                "description": "Web页面访问路径配置",
                "default": "/magic/web",
                "example": textwrap.dedent('''
                    magic-api:
                      web: /magic/web  # 访问地址：http://localhost:9999/magic/web
                ''').strip()
            },
            "magic-api.resource.type": {
                "description": "接口存储方式",
                "values": {
                    "file": "文件存储（默认）",
                    "database": "数据库存储",
                    "redis": "Redis存储",
                    "git": "Git存储"
                },
                "example": textwrap.dedent('''
                    magic-api:
                      resource:
                        type: database  # 使用数据库存储
                        table-name: magic_api_file  # 表名
                ''').strip()
            },
            "magic-api.resource.location": {
                "description": "接口文件存储路径",
                "default": "文件存储时的目录路径",
                "example": textwrap.dedent('''
                    magic-api:
                      resource:
                        location: D:/data/magic-api  # Windows路径
                        # location: /usr/local/magic-api  # Linux路径
                ''').strip()
            },
            "magic-api.response": {
                "description": "自定义响应格式",
                "example": textwrap.dedent('''
                    magic-api:
                      response: |-
                        {
                          code: code,
                          message: message,
                          data: data,
                          timestamp: timestamp,
                          executeTime: executeTime
                        }
                ''').strip()
            },
            "magic-api.response-code": {
                "description": "自定义响应状态码",
                "example": textwrap.dedent('''
                    magic-api:
                      response-code:
                        success: 200      # 成功状态码
                        invalid: 400      # 参数验证失败状态码
                        exception: 500    # 异常状态码
                ''').strip()
            },
            "magic-api.page": {
                "description": "分页参数配置",
                "example": textwrap.dedent('''
                    magic-api:
                      page:
                        size: size        # 页大小参数名，默认size
                        page: page        # 页码参数名，默认page
                        default-page: 1   # 默认页码，默认1
                        default-size: 10  # 默认页大小，默认10
                ''').strip()
            },
            "magic-api.security.username": {
                "description": "UI登录用户名",
                "example": textwrap.dedent('''
                    magic-api:
                      security:
                        username: admin
                        password: 123456
                ''').strip()
            },
            "magic-api.security.password": {
                "description": "UI登录密码",
                "example": textwrap.dedent('''
                    magic-api:
                      security:
                        username: admin
                        password: 123456
                ''').strip()
            }
        }
    },
    "editor_config": {
        "title": "编辑器配置",
        "description": "UI编辑器的个性化配置",
        "config": {
            "magic-api.editor-config": {
                "description": "编辑器配置文件路径",
                "example": textwrap.dedent('''
                    magic-api:
                      editor-config: classpath:./magic-editor-config.js
                ''').strip()
            }
        },
        "js_config": {
            "description": "JavaScript配置文件内容",
            "example": textwrap.dedent('''
                // src/main/resources/magic-editor-config.js
                var MAGIC_EDITOR_CONFIG = {
                    // 请求拦截器，在发送请求前调用
                    request: {
                        beforeSend: function(config){
                            // 添加认证头
                            config.headers.token = getToken();
                            return config;
                        }
                    },
                    // 获取Magic认证令牌
                    getMagicTokenValue: function(){
                        return localStorage.getItem('magic_token');
                    },
                    // 自定义快捷键
                    keymap: {
                        'Ctrl-S': function(){
                            // 保存快捷键处理
                        }
                    }
                };
            ''').strip()
        }
    },
    "database": {
        "title": "数据库配置",
        "description": "数据源和数据库相关配置",
        "config": {
            "spring.datasource": {
                "description": "主数据源配置",
                "example": textwrap.dedent('''
                    spring:
                      datasource:
                        driver-class-name: com.mysql.jdbc.Driver
                        url: jdbc:mysql://localhost:3306/magic-api-test
                        username: root
                        password: 123456
                ''').strip()
            },
            "magic-api.resource.datasource": {
                "description": "指定存储接口信息的数据源",
                "example": textwrap.dedent('''
                    # 多数据源时指定使用哪个数据源存储接口
                    magic-api:
                      resource:
                        datasource: magic_ds  # 使用名为magic_ds的数据源
                ''').strip()
            }
        },
        "multi_datasource": {
            "description": "多数据源配置示例",
            "example": textwrap.dedent('''
                spring:
                  datasource:
                    master:
                      driver-class-name: com.mysql.jdbc.Driver
                      url: jdbc:mysql://master:3306/db
                      username: root
                      password: 123456
                    slave:
                      driver-class-name: com.mysql.jdbc.Driver
                      url: jdbc:mysql://slave:3306/db
                      username: root
                      password: 123456

                # 在脚本中使用
                return db.slave.select("SELECT * FROM users");
            ''').strip()
        }
    },
    "cache": {
        "title": "缓存配置",
        "description": "SQL缓存相关配置",
        "config": {
            "magic-api.cache": {
                "description": "缓存配置",
                "example": textwrap.dedent('''
                    magic-api:
                      cache:
                        default-ttl: 3600000  # 默认缓存时间1小时
                        max-size: 1000        # 最大缓存条数
                ''').strip()
            }
        },
        "custom_cache": {
            "description": "自定义缓存实现",
            "example": textwrap.dedent('''
                @Component
                public class CustomSqlCache implements SqlCache {
                    @Override
                    public void put(String name, String key, Object value, long ttl) {
                        // 实现缓存存储逻辑
                    }

                    @Override
                    public Object get(String name, String key) {
                        // 实现缓存获取逻辑
                        return null;
                    }

                    @Override
                    public void delete(String name) {
                        // 实现缓存删除逻辑
                    }
                }
            ''').strip()
        }
    },
    "cluster": {
        "title": "集群配置",
        "description": "多实例集群部署配置",
        "config": {
            "magic-api.instance-id": {
                "description": "实例ID，集群中必须唯一",
                "example": textwrap.dedent('''
                    magic-api:
                      instance-id: instance-01  # 每个实例使用不同的ID
                ''').strip()
            },
            "magic-api.cluster.channel": {
                "description": "Redis频道，用于实例间通信",
                "example": textwrap.dedent('''
                    magic-api:
                      cluster:
                        channel: magic-api:notify:channel
                ''').strip()
            }
        },
        "redis_config": {
            "description": "Redis配置（集群依赖）",
            "example": textwrap.dedent('''
                spring:
                  redis:
                    host: 192.168.1.100
                    port: 6379
                    database: 1
                    password: your_password
            ''').strip()
        }
    },
    "cors": {
        "title": "跨域配置",
        "description": "CORS跨域访问配置",
        "config": {
            "magic-api.cors": {
                "description": "跨域配置",
                "example": textwrap.dedent('''
                    magic-api:
                      cors:
                        allow-credentials: true
                        allowed-headers: "*"
                        allowed-methods: "GET,POST,PUT,DELETE,OPTIONS"
                        allowed-origins: "http://localhost:3000,https://yourdomain.com"
                        max-age: 3600
                ''').strip()
            }
        }
    },
    "debug": {
        "title": "调试配置",
        "description": "开发调试相关配置",
        "config": {
            "magic-api.debug.enabled": {
                "description": "是否启用调试模式",
                "default": "true",
                "example": textwrap.dedent('''
                    magic-api:
                      debug:
                        enabled: true
                ''').strip()
            },
            "logging.level.org.ssssssss.magicapi": {
                "description": "Magic-API日志级别",
                "example": textwrap.dedent('''
                    logging:
                      level:
                        org.ssssssss.magicapi: DEBUG
                ''').strip()
            }
        }
    },
    "backup": {
        "title": "备份配置",
        "description": "接口备份相关配置",
        "config": {
            "magic-api.backup.enable": {
                "description": "是否启用备份功能",
                "default": "false",
                "example": textwrap.dedent('''
                    magic-api:
                      backup:
                        enable: true
                        max-history: 10  # 保留历史版本数量
                        location: /data/magic-api/backup  # 备份文件路径
                ''').strip()
            }
        }
    }
}

def get_config_docs(category: str = None) -> Any:
    """获取配置文档。

    Args:
        category: 配置分类，可选值: spring_boot, editor_config, database, cache, cluster, cors, debug, backup
                  如果不指定则返回所有配置

    Returns:
        指定分类的配置文档或所有配置文档
    """
    if category:
        return CONFIG_KNOWLEDGE.get(category)
    return CONFIG_KNOWLEDGE

def list_config_categories() -> List[str]:
    """获取所有配置分类。"""
    return list(CONFIG_KNOWLEDGE.keys())

def search_config(keyword: str) -> List[Dict[str, Any]]:
    """根据关键词搜索配置项。

    Args:
        keyword: 搜索关键词

    Returns:
        匹配的配置项列表
    """
    results = []
    keyword_lower = keyword.lower()

    for category, category_data in CONFIG_KNOWLEDGE.items():
        # 搜索配置项
        if "config" in category_data:
            for config_key, config_data in category_data["config"].items():
                if (keyword_lower in config_key.lower() or
                    keyword_lower in config_data.get("description", "").lower()):
                    results.append({
                        "category": category,
                        "key": config_key,
                        **config_data
                    })

        # 搜索其他配置示例
        for key, value in category_data.items():
            if key != "config" and isinstance(value, dict):
                if "description" in value and keyword_lower in value["description"].lower():
                    results.append({
                        "category": category,
                        "type": key,
                        **value
                    })

    return results

def get_config_example(category: str, key: str = None) -> str:
    """获取配置示例。

    Args:
        category: 配置分类
        key: 具体的配置键，可选

    Returns:
        配置示例字符串
    """
    if category not in CONFIG_KNOWLEDGE:
        return ""

    category_data = CONFIG_KNOWLEDGE[category]

    if key and "config" in category_data and key in category_data["config"]:
        return category_data["config"][key].get("example", "")
    elif not key:
        # 返回整个分类的示例
        examples = []
        if "config" in category_data:
            for config_item in category_data["config"].values():
                if "example" in config_item:
                    examples.append(config_item["example"])

        for value in category_data.values():
            if isinstance(value, dict) and "example" in value:
                examples.append(value["example"])

        return "\n\n".join(examples)

    return ""

__all__ = [
    "CONFIG_KNOWLEDGE",
    "get_config_docs",
    "list_config_categories",
    "search_config",
    "get_config_example"
]
