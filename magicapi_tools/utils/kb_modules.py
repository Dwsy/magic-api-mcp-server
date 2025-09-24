"""Magic-API 内置模块API文档知识库。"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, List

# 内置模块API文档
MODULES_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "db": {
        "name": "db",
        "title": "数据库操作模块",
        "description": "提供完整的数据库CRUD操作、事务管理、缓存支持等功能",
        "auto_import": True,
        "methods": {
            "select": {
                "signature": "select(sql: String) -> List<Map<String,Object>>",
                "description": "执行查询操作",
                "example": 'return db.select("select * from sys_user");'
            },
            "selectInt": {
                "signature": "selectInt(sql: String) -> Integer",
                "description": "查询单个整数值",
                "example": 'return db.selectInt("select count(*) from sys_user");'
            },
            "selectOne": {
                "signature": "selectOne(sql: String) -> Map<String,Object>",
                "description": "查询单个对象",
                "example": 'return db.selectOne("select * from sys_user limit 1");'
            },
            "selectValue": {
                "signature": "selectValue(sql: String) -> Object",
                "description": "查询单个值",
                "example": 'return db.selectValue("select user_name from sys_user limit 1");'
            },
            "page": {
                "signature": "page(sql: String, limit?: long, offset?: long) -> Object",
                "description": "分页查询",
                "example": 'return db.page("select * from sys_user");'
            },
            "update": {
                "signature": "update(sql: String) -> Integer",
                "description": "执行增删改操作",
                "example": 'return db.update("delete from sys_user");'
            },
            "insert": {
                "signature": "insert(sql: String, id?: String) -> Object",
                "description": "插入数据",
                "example": 'return db.insert("insert into sys_user(username,password) values(\'admin\',\'admin\')");'
            },
            "call": {
                "signature": "call(sql: String) -> Map<String,Object>",
                "description": "调用存储过程",
                "example": textwrap.dedent('''
                    return db.call("""
                        call test(#{cs1}, @{height(cs2), INTEGER}, @{v_area, VARCHAR})
                    """)
                ''').strip()
            },
            "batchUpdate": {
                "signature": "batchUpdate(sql: String, batchArgs: List<Object[]>) -> int",
                "description": "批量更新操作",
                "example": textwrap.dedent('''
                    return db.batchUpdate("""
                        update sys_dict set is_del = ? where is_del = ?
                    """, [
                        ["1", "0"].toArray()
                    ])
                ''').strip()
            },
            "cache": {
                "signature": "cache(cacheName: String, ttl?: long) -> db",
                "description": "使用缓存",
                "example": 'return db.cache(\'user\').select("select * from sys_user");'
            },
            "deleteCache": {
                "signature": "deleteCache(cacheName: String) -> db",
                "description": "删除缓存",
                "example": 'db.deleteCache(\'user\');'
            },
            "transaction": {
                "signature": "transaction(callback?: Function) -> Object",
                "description": "事务操作",
                "example": textwrap.dedent('''
                    var val = db.transaction(()=>{
                        var v1 = db.update('...');
                        var v2 = db.update('....');
                        return v2;
                    });
                    return val;
                ''').strip()
            },
            "table": {
                "signature": "table(tableName: String) -> TableAPI",
                "description": "单表操作API",
                "example": 'return db.table(\'sys_user\').select();'
            }
        },
        "table_api": {
            "logic": {
                "signature": "logic() -> TableAPI",
                "description": "设置逻辑删除",
                "example": 'db.table(\'user\').logic().select()'
            },
            "withBlank": {
                "signature": "withBlank() -> TableAPI",
                "description": "设置插入时不过滤空值",
                "example": 'db.table(\'user\').withBlank().insert({name: ""})'
            },
            "column": {
                "signature": "column(column: String, value?: Object) -> TableAPI",
                "description": "设置查询列或列值",
                "example": 'db.table(\'user\').column(\'name\').select()'
            },
            "primary": {
                "signature": "primary(primary: String, defaultValue?: Object) -> TableAPI",
                "description": "设置主键列",
                "example": 'db.table(\'user\').primary(\'id\').update({id: 1, name: "test"})'
            },
            "insert": {
                "signature": "insert(data?: Map) -> Object",
                "description": "插入数据",
                "example": 'db.table(\'user\').insert({name: "张三", age: 20})'
            },
            "update": {
                "signature": "update(data?: Map, isUpdateBlank?: boolean) -> Integer",
                "description": "更新数据",
                "example": 'db.table(\'user\').primary(\'id\').update({id: 1, name: "李四"})'
            },
            "save": {
                "signature": "save(data?: Map, beforeQuery?: boolean) -> Object",
                "description": "保存数据（插入或更新）",
                "example": 'db.table(\'user\').primary(\'id\').save({id: 1, name: "王五"})'
            },
            "select": {
                "signature": "select() -> List<Map>",
                "description": "查询数据",
                "example": 'db.table(\'user\').select()'
            },
            "page": {
                "signature": "page() -> Object",
                "description": "分页查询",
                "example": 'db.table(\'user\').page()'
            },
            "where": {
                "signature": "where() -> WhereAPI",
                "description": "设置查询条件",
                "example": textwrap.dedent('''
                    db.table('user')
                        .where()
                        .like('name','%张%')
                        .eq('status', 1)
                        .select()
                ''').strip()
            }
        },
        "column_mapping": {
            "normal": "列名保持原样",
            "camel": "列名使用驼峰命名",
            "pascal": "列名使用帕斯卡命名",
            "upper": "列名保持全大写",
            "lower": "列名保持全小写"
        },
        "doc": "https://www.ssssssss.org/magic-api/pages/module/db/"
    },
    "http": {
        "name": "http",
        "title": "HTTP请求模块",
        "description": "基于RestTemplate封装的HTTP客户端，支持各种HTTP方法",
        "auto_import": False,
        "methods": {
            "connect": {
                "signature": "connect(url: String) -> HttpModule",
                "description": "创建HTTP请求对象",
                "example": 'http.connect("http://localhost:9999/api/test")'
            },
            "param": {
                "signature": "param(key: String, value: Object) -> HttpModule",
                "description": "设置URL参数",
                "example": 'http.param(\'id\', 123).param({name: \'test\'})'
            },
            "data": {
                "signature": "data(key: String, value: Object) -> HttpModule",
                "description": "设置表单参数",
                "example": 'http.data(\'name\', \'test\').data({age: 20})'
            },
            "header": {
                "signature": "header(key: String, value: String) -> HttpModule",
                "description": "设置请求头",
                "example": 'http.header(\'token\', \'abc123\').header({contentType: \'application/json\'})'
            },
            "body": {
                "signature": "body(body: Object) -> HttpModule",
                "description": "设置请求体",
                "example": 'http.body({name: \'test\', age: 20})'
            },
            "contentType": {
                "signature": "contentType(contentType: String) -> HttpModule",
                "description": "设置内容类型",
                "example": 'http.contentType(\'application/json\')'
            },
            "get": {
                "signature": "get() -> ResponseEntity",
                "description": "执行GET请求",
                "example": 'return http.connect(\'/api/users\').get().getBody()'
            },
            "post": {
                "signature": "post() -> ResponseEntity",
                "description": "执行POST请求",
                "example": 'return http.connect(\'/api/users\').body(userData).post().getBody()'
            },
            "put": {
                "signature": "put() -> ResponseEntity",
                "description": "执行PUT请求",
                "example": 'return http.connect(\'/api/users/1\').body(userData).put().getBody()'
            },
            "delete": {
                "signature": "delete() -> ResponseEntity",
                "description": "执行DELETE请求",
                "example": 'return http.connect(\'/api/users/1\').delete().getBody()'
            }
        },
        "doc": "https://www.ssssssss.org/magic-api/pages/module/http/"
    },
    "response": {
        "name": "response",
        "title": "响应处理模块",
        "description": "统一响应格式封装，提供JSON、分页、文件下载等功能",
        "auto_import": False,
        "methods": {
            "json": {
                "signature": "json(value: Object) -> ResponseEntity",
                "description": "返回JSON响应",
                "example": 'return response.json({success: true, data: result})'
            },
            "page": {
                "signature": "page(total: long, values: List) -> Object",
                "description": "返回分页响应",
                "example": 'return response.page(100, records)'
            },
            "text": {
                "signature": "text(value: String) -> ResponseEntity",
                "description": "返回文本响应",
                "example": 'return response.text(\'操作成功\')'
            },
            "redirect": {
                "signature": "redirect(url: String) -> ResponseEntity",
                "description": "重定向",
                "example": 'return response.redirect(\'/login\')'
            },
            "download": {
                "signature": "download(value: Object, filename: String) -> ResponseEntity",
                "description": "文件下载",
                "example": 'return response.download(fileContent, \'test.txt\')'
            },
            "image": {
                "signature": "image(value: Object, mine: String) -> ResponseEntity",
                "description": "图片输出",
                "example": 'return response.image(imageBytes, \'image/png\')'
            },
            "addHeader": {
                "signature": "addHeader(key: String, value: String) -> void",
                "description": "添加响应头",
                "example": 'response.addHeader(\'token\', \'abc123\')'
            },
            "setHeader": {
                "signature": "setHeader(key: String, value: String) -> void",
                "description": "设置响应头",
                "example": 'response.setHeader(\'content-type\', \'application/json\')'
            },
            "addCookie": {
                "signature": "addCookie(key: String, value: String, options?: Map) -> void",
                "description": "添加Cookie",
                "example": 'response.addCookie(\'session\', \'abc123\', {maxAge: 3600})'
            },
            "addCookies": {
                "signature": "addCookies(cookies: Map, options?: Map) -> void",
                "description": "批量添加Cookie",
                "example": 'response.addCookies({session: \'abc123\', user: \'test\'})'
            },
            "getOutputStream": {
                "signature": "getOutputStream() -> OutputStream",
                "description": "获取输出流",
                "example": 'var out = response.getOutputStream(); // 然后使用 out.write()'
            },
            "end": {
                "signature": "end() -> void",
                "description": "结束响应处理",
                "example": 'response.end()'
            }
        },
        "doc": "https://www.ssssssss.org/magic-api/pages/module/response/"
    },
    "request": {
        "name": "request",
        "title": "请求处理模块",
        "description": "获取请求参数、文件上传、请求头等信息",
        "auto_import": False,
        "methods": {
            "getFile": {
                "signature": "getFile(name: String) -> MultipartFile",
                "description": "获取上传的文件",
                "example": 'var file = request.getFile(\'image\')'
            },
            "getFiles": {
                "signature": "getFiles(name: String) -> List<MultipartFile>",
                "description": "获取上传的文件列表",
                "example": 'var files = request.getFiles(\'images\')'
            },
            "getValues": {
                "signature": "getValues(name: String) -> List<String>",
                "description": "获取数组参数",
                "example": 'var values = request.getValues(\'tags\')'
            },
            "getHeaders": {
                "signature": "getHeaders(name: String) -> List<String>",
                "description": "获取请求头数组",
                "example": 'var headers = request.getHeaders(\'accept\')'
            },
            "get": {
                "signature": "get() -> MagicHttpServletRequest",
                "description": "获取请求对象",
                "example": 'var req = request.get()'
            },
            "getClientIP": {
                "signature": "getClientIP() -> String",
                "description": "获取客户端IP",
                "example": 'var ip = request.getClientIP()'
            }
        },
        "doc": "https://www.ssssssss.org/magic-api/pages/module/request/"
    },
    "log": {
        "name": "log",
        "title": "日志模块",
        "description": "基于SLF4J的日志输出功能",
        "auto_import": True,
        "methods": {
            "trace": {
                "signature": "trace(message: String, args...: Object) -> void",
                "description": "TRACE级别日志",
                "example": 'log.trace(\'处理请求: {}\', requestId)'
            },
            "debug": {
                "signature": "debug(message: String, args...: Object) -> void",
                "description": "DEBUG级别日志",
                "example": 'log.debug(\'调试信息: {}\', data)'
            },
            "info": {
                "signature": "info(message: String, args...: Object) -> void",
                "description": "INFO级别日志",
                "example": 'log.info(\'用户{}登录成功\', username)'
            },
            "warn": {
                "signature": "warn(message: String, args...: Object) -> void",
                "description": "WARN级别日志",
                "example": 'log.warn(\'参数异常: {}\', param)'
            },
            "error": {
                "signature": "error(message: String, args...: Object) -> void",
                "description": "ERROR级别日志",
                "example": 'log.error(\'系统异常\', exception)'
            }
        },
        "doc": "https://www.ssssssss.org/magic-api/pages/module/log/"
    },
    "env": {
        "name": "env",
        "title": "环境变量模块",
        "description": "获取Spring Boot配置属性",
        "auto_import": False,
        "methods": {
            "get": {
                "signature": "get(key: String, defaultValue?: String) -> String",
                "description": "获取配置属性",
                "example": 'var port = env.get(\'server.port\', \'8080\')'
            }
        },
        "doc": "https://www.ssssssss.org/magic-api/pages/module/env/"
    },
    "magic": {
        "name": "magic",
        "title": "内部调用模块",
        "description": "在脚本内部调用其他Magic-API接口或函数",
        "auto_import": False,
        "methods": {
            "call": {
                "signature": "call(method: String, path: String, parameters: Map) -> Object",
                "description": "调用接口（带状态码）",
                "example": 'return magic.call(\'get\', \'/api/users\', {page: 1})'
            },
            "execute": {
                "signature": "execute(method: String, path: String, parameters: Map) -> Object",
                "description": "调用接口（原始数据）",
                "example": 'return magic.execute(\'post\', \'/api/users\', userData)'
            },
            "invoke": {
                "signature": "invoke(path: String, parameters: Map) -> Object",
                "description": "调用函数",
                "example": 'return magic.invoke(\'/common/encode/md5\', {text: \'hello\'})'
            }
        },
        "doc": "https://www.ssssssss.org/magic-api/pages/module/magic/"
    }
}

def get_module_api(module_name: str) -> Dict[str, Any] | None:
    """获取指定模块的API文档。"""
    return MODULES_KNOWLEDGE.get(module_name)

def list_available_modules() -> List[str]:
    """获取所有可用的模块名称。"""
    return list(MODULES_KNOWLEDGE.keys())

def get_auto_import_modules() -> List[str]:
    """获取自动导入的模块。"""
    return [name for name, module in MODULES_KNOWLEDGE.items() if module.get("auto_import", False)]

__all__ = [
    "MODULES_KNOWLEDGE",
    "get_module_api",
    "list_available_modules",
    "get_auto_import_modules"
]
