"""Magic-API 代码生成工具。

此模块提供智能代码生成功能，支持：
- CRUD API接口自动生成
- 数据库查询代码生成
- API测试代码生成
- 工作流模板代码生成

主要工具：
- generate_crud_api: 生成完整的CRUD API接口代码
- generate_database_query: 生成数据库查询代码
- generate_api_test: 生成API接口测试代码
- generate_workflow_code: 生成工作流模板代码

注意：此模块当前被禁用，如需使用请取消 __init__.py 中的注释。
"""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import Field

from magicapi_tools.utils.knowledge_base import (
    get_examples,
    get_function_docs,
    get_module_api,
    get_workflow,
)

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext


class CodeGenerationTools:
    """代码生成工具模块，提供智能代码生成功能。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册代码生成相关工具。"""

        @mcp_app.tool(
            name="generate_crud_api",
            description="生成完整的CRUD API接口代码",
            tags={"codegen", "crud", "api"},
            meta={"version": "1.0", "category": "generation"},
        )
        def generate_crud_api(
            table_name: str = Field(description="数据库表名"),
            entity_name: str = Field(description="实体名称，用于生成API路径"),
            include_fields: Optional[List[str]] = Field(default=None, description="包含的字段列表，为空则包含所有字段"),
            exclude_fields: Optional[List[str]] = Field(default=None, description="排除的字段列表"),
            primary_key: str = Field(default="id", description="主键字段名"),
            enable_pagination: bool = Field(default=True, description="是否启用分页查询"),
            enable_validation: bool = Field(default=True, description="是否启用参数校验"),
        ) -> Dict[str, Any]:
            """生成完整的CRUD API代码"""
            code_templates = self._generate_crud_templates(
                table_name=table_name,
                entity_name=entity_name,
                include_fields=include_fields,
                exclude_fields=exclude_fields,
                primary_key=primary_key,
                enable_pagination=enable_pagination,
                enable_validation=enable_validation
            )

            return {
                "table_name": table_name,
                "entity_name": entity_name,
                "generated_code": code_templates,
                "api_endpoints": [
                    f"GET /{entity_name}/list - 查询列表",
                    f"GET /{entity_name}/{{id}} - 查询详情",
                    f"POST /{entity_name} - 创建记录",
                    f"PUT /{entity_name}/{{id}} - 更新记录",
                    f"DELETE /{entity_name}/{{id}} - 删除记录"
                ]
            }

        @mcp_app.tool(
            name="generate_database_query",
            description="生成数据库查询代码片段",
            tags={"codegen", "database", "query"},
            meta={"version": "1.0", "category": "generation"},
        )
        def generate_database_query(
            operation_type: str = Field(description="操作类型: select, insert, update, delete"),
            table_name: str = Field(description="表名"),
            conditions: Optional[Dict[str, Any]] = Field(default=None, description="查询条件"),
            fields: Optional[List[str]] = Field(default=None, description="查询字段"),
            include_pagination: bool = Field(default=False, description="是否包含分页"),
            use_dynamic_sql: bool = Field(default=True, description="是否使用动态SQL"),
        ) -> Dict[str, Any]:
            """生成数据库查询代码"""
            code = self._generate_query_code(
                operation_type=operation_type,
                table_name=table_name,
                conditions=conditions,
                fields=fields,
                include_pagination=include_pagination,
                use_dynamic_sql=use_dynamic_sql
            )

            return {
                "operation_type": operation_type,
                "table_name": table_name,
                "generated_code": code,
                "tips": [
                    "记得使用 #{param} 进行参数绑定",
                    "复杂条件考虑使用动态SQL",
                    "分页查询注意count和limit同步"
                ]
            }

        @mcp_app.tool(
            name="generate_api_from_example",
            description="基于现有示例生成定制化的API代码",
            tags={"codegen", "example", "api"},
            meta={"version": "1.0", "category": "generation"},
        )
        def generate_api_from_example(
            example_category: str = Field(description="示例分类，如: basic_crud, advanced_queries, transactions"),
            example_key: str = Field(description="具体示例的key"),
            customizations: Optional[Dict[str, Any]] = Field(default=None, description="定制化参数"),
        ) -> Dict[str, Any]:
            """基于示例生成定制化代码"""
            examples = get_examples(example_category)
            if not examples or "examples" not in examples:
                return {"error": f"未找到分类 '{example_category}' 的示例"}

            example_data = None
            for ex_key, ex_data in examples["examples"].items():
                if ex_key == example_key:
                    example_data = ex_data
                    break

            if not example_data:
                return {"error": f"在分类 '{example_category}' 中未找到示例 '{example_key}'"}

            customized_code = self._customize_example_code(example_data, customizations or {})

            return {
                "original_example": example_data["title"],
                "category": example_category,
                "customized_code": customized_code,
                "modifications": customizations or {}
            }

        @mcp_app.tool(
            name="generate_error_handling",
            description="生成错误处理和异常捕获代码",
            tags={"codegen", "error-handling", "best-practices"},
            meta={"version": "1.0", "category": "generation"},
        )
        def generate_error_handling(
            error_type: str = Field(description="错误类型: validation, database, network, business"),
            include_retry: bool = Field(default=False, description="是否包含重试逻辑"),
            custom_message: Optional[str] = Field(default=None, description="自定义错误消息"),
        ) -> Dict[str, Any]:
            """生成错误处理代码"""
            code = self._generate_error_handling_code(
                error_type=error_type,
                include_retry=include_retry,
                custom_message=custom_message
            )

            return {
                "error_type": error_type,
                "include_retry": include_retry,
                "generated_code": code,
                "best_practices": [
                    "使用 response.error() 统一错误格式",
                    "业务异常使用 exit 直接返回",
                    "数据库异常考虑事务回滚",
                    "网络异常考虑重试机制"
                ]
            }

        @mcp_app.tool(
            name="generate_transaction_code",
            description="生成数据库事务处理代码",
            tags={"codegen", "transaction", "database"},
            meta={"version": "1.0", "category": "generation"},
        )
        def generate_transaction_code(
            operations: List[str] = Field(description="要执行的操作列表"),
            rollback_strategy: str = Field(default="auto", description="回滚策略: auto, manual"),
            error_handling: str = Field(default="throw", description="错误处理: throw, return, log"),
        ) -> Dict[str, Any]:
            """生成事务代码"""
            code = self._generate_transaction_code(
                operations=operations,
                rollback_strategy=rollback_strategy,
                error_handling=error_handling
            )

            return {
                "operations_count": len(operations),
                "rollback_strategy": rollback_strategy,
                "error_handling": error_handling,
                "generated_code": code,
                "tips": [
                    "事务中所有数据库操作要放在同一个transaction回调中",
                    "异常会自动触发回滚",
                    "可以使用exit返回业务错误码"
                ]
            }

        @mcp_app.tool(
            name="generate_lambda_operations",
            description="生成Lambda表达式和函数式编程代码",
            tags={"codegen", "lambda", "functional"},
            meta={"version": "1.0", "category": "generation"},
        )
        def generate_lambda_operations(
            data_structure: str = Field(description="数据结构: array, map, collection"),
            operations: List[str] = Field(description="要执行的操作: map, filter, group, sort等"),
            input_data: Optional[str] = Field(default=None, description="输入数据示例"),
        ) -> Dict[str, Any]:
            """生成Lambda操作代码"""
            code = self._generate_lambda_code(
                data_structure=data_structure,
                operations=operations,
                input_data=input_data
            )

            return {
                "data_structure": data_structure,
                "operations": operations,
                "generated_code": code,
                "functional_programming_tips": [
                    "map用于数据转换",
                    "filter用于数据筛选",
                    "group用于数据分组统计",
                    "sort用于数据排序",
                    "Lambda表达式让代码更简洁"
                ]
            }

    def _generate_crud_templates(self, table_name: str, entity_name: str, include_fields: List[str] = None,
                                exclude_fields: List[str] = None, primary_key: str = "id",
                                enable_pagination: bool = True, enable_validation: bool = True) -> Dict[str, str]:
        """生成CRUD模板代码"""

        # 确定查询字段
        if include_fields:
            select_fields = ", ".join(include_fields)
        else:
            select_fields = "*"

        # 生成校验条件
        validation_code = ""
        if enable_validation:
            validation_code = f"""
                    if(!params.{primary_key}){{
                        exit 400, '{primary_key}参数不能为空';
                    }}"""

        # 分页代码
        pagination_code = ""
        if enable_pagination:
            pagination_code = f"""
                    var total = db.selectInt("SELECT COUNT(*) FROM {table_name}");
                    var page = params.page ? params.page : 1;
                    var size = params.size ? params.size : 10;
                    var offset = (page - 1) * size;"""

        # 生成各个API的代码
        templates = {}

        # 查询列表
        if enable_pagination:
            list_code = f"""
                import response;

                var total = db.selectInt("SELECT COUNT(*) FROM {table_name}");
                var page = params.page ? params.page : 1;
                var size = params.size ? params.size : 10;
                var offset = (page - 1) * size;
                var sql = "SELECT {select_fields} FROM {table_name} ORDER BY create_time DESC LIMIT #{{offset}}, #{{size}}";

                var list = db.select(sql, {{offset: offset, size: size}});
                return response.page(total, list);
            """
        else:
            list_code = f"""
                import response;

                var sql = "SELECT {select_fields} FROM {table_name} ORDER BY create_time DESC";

                var list = db.select(sql, {{}});
                return response.page(list.size(), list);
            """
        templates["list"] = list_code.strip()

        # 查询详情
        detail_code = f"""
                import response;

                {validation_code}
                var sql = "SELECT {select_fields} FROM {table_name} WHERE {primary_key} = #{primary_key}";
                var data = db.selectOne(sql, params);

                if(!data){{
                    exit 404, '记录不存在';
                }}

                return response.json({{success: true, data: data}});
        """
        templates["detail"] = detail_code.strip()

        # 创建记录
        create_code = f"""
                import response;

                // 校验必填字段
                if(!body.name){{
                    exit 400, '名称不能为空';
                }}

                var insertSql = `INSERT INTO {table_name}({select_fields}) VALUES({','.join(['#' + f for f in (include_fields or ['name', 'create_time']) if f != primary_key])})`;
                var id = db.insert(insertSql, body);

                return response.json({{
                    success: true,
                    message: '创建成功',
                    data: {{id: id}}
                }});
        """
        templates["create"] = create_code.strip()

        # 更新记录
        update_code = f"""
                import response;

                {validation_code}

                // 检查记录是否存在
                var exist = db.selectOne("SELECT {primary_key} FROM {table_name} WHERE {primary_key} = #{primary_key}", params);
                if(!exist){{
                    exit 404, '记录不存在';
                }}

                var updateSql = `UPDATE {table_name} SET ${{body.keySet().join(' = #,')}} = # WHERE {primary_key} = #{primary_key}`;
                db.update(updateSql, body);

                return response.json({{
                    success: true,
                    message: '更新成功'
                }});
        """
        templates["update"] = update_code.strip()

        # 删除记录
        delete_code = f"""
                import response;

                {validation_code}

                // 检查记录是否存在
                var exist = db.selectOne("SELECT {primary_key} FROM {table_name} WHERE {primary_key} = #{primary_key}", params);
                if(!exist){{
                    exit 404, '记录不存在';
                }}

                db.update("UPDATE {table_name} SET deleted = 1 WHERE {primary_key} = #{primary_key}", params);

                return response.json({{
                    success: true,
                    message: '删除成功'
                }});
        """
        templates["delete"] = delete_code.strip()

        return templates

    def _generate_query_code(self, operation_type: str, table_name: str, conditions: Dict[str, Any] = None,
                           fields: List[str] = None, include_pagination: bool = False,
                           use_dynamic_sql: bool = True) -> str:
        """生成查询代码"""

        conditions = conditions or {}
        fields = fields or ["*"]
        select_fields = ", ".join(fields)

        # 构建基础SQL
        if operation_type == "select":
            base_sql = f"SELECT {select_fields} FROM {table_name}"
        elif operation_type == "insert":
            placeholders = ", ".join([f"#{field}" for field in fields if field != "id"])
            base_sql = f"INSERT INTO {table_name}({','.join([f for f in fields if f != 'id'])}) VALUES({placeholders})"
        elif operation_type == "update":
            set_clause = ", ".join([f"{field} = #{field}" for field in fields if field != "id"])
            base_sql = f"UPDATE {table_name} SET {set_clause} WHERE id = #id"
        elif operation_type == "delete":
            base_sql = f"DELETE FROM {table_name} WHERE id = #id"
        else:
            return "// 不支持的操作类型"

        # 添加动态条件
        if operation_type == "select" and conditions and use_dynamic_sql:
            where_parts = []
            for key, value in conditions.items():
                if isinstance(value, str):
                    where_parts.append(f"?{{{key}, AND {key} = #{key}}}")
                else:
                    where_parts.append(f"?{{{key} != null, AND {key} = #{key}}}")

            if where_parts:
                base_sql += " WHERE 1=1 " + " ".join(where_parts)

        # 添加分页
        if operation_type == "select" and include_pagination:
            base_sql += " LIMIT #{offset}, #{size}"

        # 生成完整代码
        code_lines = [f"var sql = `{base_sql}`;"]

        if operation_type == "select":
            if include_pagination:
                code_lines.extend([
                    "var page = params.page ? params.page : 1;",
                    "var size = params.size ? params.size : 10;",
                    "var offset = (page - 1) * size;",
                    "",
                    "var total = db.selectInt(`SELECT COUNT(*) FROM {table_name}`);",
                    "var list = db.select(sql, {page: page, size: size, offset: offset, **conditions});",
                    "return response.page(total, list);"
                ])
            else:
                code_lines.extend([
                    "var result = db.select(sql, conditions);",
                    "return response.json({success: true, data: result});"
                ])
        elif operation_type in ["insert", "update", "delete"]:
            if operation_type == "insert":
                code_lines.append("var result = db.insert(sql, data);")
            else:
                code_lines.append("var result = db.update(sql, data);")

            code_lines.extend([
                "return response.json({",
                "    success: true,",
                "    message: '操作成功',",
                f"    data: {{affectedRows: result}}",
                "});"
            ])

        return "\n".join(code_lines)

    def _customize_example_code(self, example_data: Dict[str, Any], customizations: Dict[str, Any]) -> str:
        """定制化示例代码"""
        code = example_data.get("code", "")

        # 应用定制化
        for key, value in customizations.items():
            if f"{{{{{key}}}}}" in code:
                code = code.replace(f"{{{{{key}}}}}", str(value))
            elif f"#{key}" in code:
                code = code.replace(f"#{key}", str(value))
            elif f"${{{key}}}" in code:
                code = code.replace(f"${{{key}}}", str(value))

        return code

    def _generate_error_handling_code(self, error_type: str, include_retry: bool = False,
                                    custom_message: str = None) -> str:
        """生成错误处理代码"""

        if error_type == "validation":
            code = f"""
                // 参数校验
                if(!params.requiredParam){{
                    exit 400, '{custom_message or '参数不能为空'}';
                }}

                if(params.email && !params.email.matches('^[\\\\w.-]+@[\\\\w.-]+\\\\.[a-zA-Z]{{2,6}}$')){{
                    exit 400, '{custom_message or '邮箱格式不正确'}';
                }}
            """
        elif error_type == "database":
            code = f"""
                try {{
                    // 数据库操作
                    var result = db.update(sql, params);
                    if(result == 0){{
                        exit 404, '{custom_message or '数据不存在或无权限'}';
                    }}
                }} catch(e) {{
                    log.error('数据库操作失败', e);
                    exit 500, '{custom_message or '数据库操作失败'}';
                }}
            """
        elif error_type == "network":
            retry_code = ""
            if include_retry:
                retry_code = """
                    var maxRetries = 3;
                    var retryCount = 0;
                    var result = null;

                    while(retryCount < maxRetries && !result){
                        try {
                            result = http.get('http://api.example.com/data');
                        } catch(e) {
                            retryCount++;
                            if(retryCount < maxRetries){
                                Thread.sleep(1000 * retryCount); // 递增延时
                            }
                        }
                    }

                    if(!result){
                        exit 502, '服务暂时不可用，请稍后重试';
                    }
                """

            code = f"""
                try {{
                    var response = http.get('http://api.example.com/data');
                    if(response.status != 200){{
                        exit 502, '{custom_message or '外部服务异常'}';
                    }}
                    var data = JSON.parse(response.body);
                }} catch(e) {{
                    log.error('网络请求失败', e);
                    exit 502, '{custom_message or '网络请求失败'}';
                }}
                {retry_code if include_retry else ''}
            """
        elif error_type == "business":
            code = f"""
                // 业务逻辑校验
                var userId = params.userId;
                var permission = params.permission;

                if(!userId){{
                    exit 400, '用户ID不能为空';
                }}

                var user = db.selectOne('SELECT status FROM user WHERE id = #{{userId}}', params);
                if(!user){{
                    exit 404, '{custom_message or '用户不存在'}';
                }}

                if(user.status != 'active'){{
                    exit 403, '{custom_message or '用户状态异常'}';
                }}

                if(!permission){{
                    exit 400, '权限代码不能为空';
                }}

                // 检查权限
                var hasPermission = db.selectInt(`
                    SELECT COUNT(*) FROM user_role ur
                    JOIN role_permission rp ON ur.role_id = rp.role_id
                    WHERE ur.user_id = #{{userId}} AND rp.permission_code = #{{permission}}
                `, params);

                if(hasPermission == 0){{
                    exit 403, '{custom_message or '权限不足'}';
                }}
            """
        else:
            code = f"""
                try {{
                    // 业务代码
                }} catch(e) {{
                    log.error('操作失败', e);
                    exit 500, '{custom_message or '操作失败，请稍后重试'}';
                }}
            """

        return code.strip()

    def _generate_transaction_code(self, operations: List[str], rollback_strategy: str = "auto",
                                 error_handling: str = "throw") -> str:
        """生成事务代码"""

        operation_code = "\n                    ".join([f"// {op}" for op in operations])

        if rollback_strategy == "auto":
            if error_handling == "throw":
                code = f"""
                    var result = db.transaction(() => {{
                        {operation_code}
                        return {{success: true, message: '操作成功'}};
                    }});

                    return response.json(result);
                """
            elif error_handling == "return":
                code = f"""
                    try {{
                        var result = db.transaction(() => {{
                            {operation_code}
                            return {{success: true, message: '操作成功'}};
                        }});

                        return response.json(result);
                    }} catch(e) {{
                        return response.json({{
                            success: false,
                            message: '操作失败: ' + e.message
                        }});
                    }}
                """
            else:  # log
                code = f"""
                    try {{
                        var result = db.transaction(() => {{
                            {operation_code}
                            return {{success: true, message: '操作成功'}};
                        }});

                        return response.json(result);
                    }} catch(error) {{
                        log.error('事务执行失败', error);
                        return response.json({{
                            success: false,
                            message: '操作失败，请稍后重试'
                        }});
                    }}
                """
        else:  # manual
            if error_handling == "throw":
                error_message = "'操作失败: ' + error.message"
            else:
                error_message = "'操作失败，请稍后重试'"

            code = f"""
                var tx = db.transaction(); // 开启事务
                try {{
                    {operation_code}

                    tx.commit(); // 提交事务
                    return response.json({{
                        success: true,
                        message: '操作成功'
                    }});

                }} catch(error) {{
                    tx.rollback(); // 回滚事务
                    {'log.error(\'事务回滚\', error);' if error_handling == 'log' else ''}
                    return response.json({{
                        success: false,
                        message: {error_message}
                    }});
                }}
            """

        return code.strip()

    def _generate_lambda_code(self, data_structure: str, operations: List[str],
                            input_data: str = None) -> str:
        """生成Lambda操作代码"""

        # 默认输入数据
        if not input_data:
            if data_structure == "array":
                input_data = "[{name: '张三', age: 20}, {name: '李四', age: 25}, {name: '王五', age: 30}]"
            elif data_structure == "map":
                input_data = "{user1: {name: '张三', age: 20}, user2: {name: '李四', age: 25}}"
            else:
                input_data = "[1, 2, 3, 4, 5]"

        code_lines = [f"var data = {input_data};", ""]

        for operation in operations:
            if operation == "map":
                if data_structure == "array":
                    code_lines.append("// 映射转换每个元素")
                    code_lines.append("var mapped = data.map(item => ({")
                    code_lines.append("    name: item.name,")
                    code_lines.append("    age: item.age,")
                    code_lines.append("    ageGroup: item.age > 25 ? '成年' : '青年'")
                    code_lines.append("}));")
                    code_lines.append("")
                else:
                    code_lines.append("// 映射转换Map值")
                    code_lines.append("var mapped = data.map((key, value) => value.name + '(' + value.age + '岁)');")
                    code_lines.append("")

            elif operation == "filter":
                if data_structure == "array":
                    code_lines.append("// 筛选符合条件的元素")
                    code_lines.append("var filtered = data.filter(item => item.age >= 25);")
                    code_lines.append("")
                else:
                    code_lines.append("// 筛选Map中值符合条件的条目")
                    code_lines.append("var filtered = data.filter((key, value) => value.age >= 25);")
                    code_lines.append("")

            elif operation == "group":
                if data_structure == "array":
                    code_lines.append("// 按年龄段分组统计")
                    code_lines.append("var grouped = data.group(item => {")
                    code_lines.append("    if(item.age < 25) return '青年';")
                    code_lines.append("    else if(item.age < 35) return '中年';")
                    code_lines.append("    else return '老年';")
                    code_lines.append("}, list => ({")
                    code_lines.append("    count: list.size(),")
                    code_lines.append("    avgAge: list.avg(item => item.age)")
                    code_lines.append("}));")
                    code_lines.append("")

            elif operation == "sort":
                if data_structure == "array":
                    code_lines.append("// 按年龄降序排序")
                    code_lines.append("var sorted = data.sort((a, b) => b.age - a.age);")
                    code_lines.append("")

            elif operation == "each":
                code_lines.append("// 遍历每个元素执行操作")
                code_lines.append("data.each(item => {")
                code_lines.append("    println(item.name + '的年龄是' + item.age);")
                code_lines.append("});")
                code_lines.append("")

        code_lines.append("return mapped ? mapped : (filtered ? filtered : (grouped ? grouped : (sorted ? sorted : data)));")

        return "\n".join(code_lines)
