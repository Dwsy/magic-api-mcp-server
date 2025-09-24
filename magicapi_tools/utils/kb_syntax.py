"""Magic-API 脚本语法知识库。"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, List

# Magic-Script 语法知识块
SYNTAX_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "keywords": {
        "title": "关键字与保留字",
        "summary": "Magic-Script 使用 Java 风格的关键字，注意 `exit` 在 v0.5.0+ 直接终止脚本。",
        "sections": [
            {
                "heading": "流程控制",
                "items": [
                    "`if` / `else`：条件分支，0、空串、空集合视为 false",
                    "`for ... in`：可遍历 List、Map、range(起,止)" ,
                    "`while`：与 Java 类似，配合 `break`、`continue`",
                ],
            },
            {
                "heading": "异常与提前结束",
                "items": [
                    "`try` / `catch` / `finally`：捕获异常，结合 `response.error` 统一输出",
                    "`exit code, message`：直接结束脚本并返回指定响应 (0.5.0+)",
                    "`assert`：1.3.4+ 内置断言，失败抛出异常",
                ],
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/base/script/#%E5%85%B3%E9%94%AE%E5%AD%97",
    },
    "operators": {
        "title": "运算符与短路逻辑",
        "summary": "遵循 Java 基本规则，但 0.4.6+ 对非布尔短路与 JS 对齐。",
        "sections": [
            {
                "heading": "算术与赋值",
                "code": textwrap.dedent(
                    '''
                    var total = 1 + 2 * 3 / 4 % 2;
                    total += 5; // 复合赋值
                    '''
                ).strip(),
                "notes": "复合赋值支持 +=/-=/...，但 `range` 循环内不支持。",
            },
            {
                "heading": "逻辑增强",
                "code": textwrap.dedent(
                    '''
                    var left0 = 0 && 'hello';   // 0 (v0.4.6+)
                    var right0 = 0 || 'world'; // 'world'
                    '''
                ).strip(),
                "notes": "空集合、null、0 均视为 false，确保空值校验。",
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/base/script/#%E8%BF%90%E7%AE%97%E7%AC%A6",
    },
    "types": {
        "title": "数据类型与转换",
        "summary": "支持 Java 基础数值、集合、Lambda 与 Pattern 类型。",
        "sections": [
            {
                "heading": "字面量",
                "items": [
                    "`123l` Long、`123m` BigDecimal、`/\\d+/g` 正则",
                    '多行 SQL 使用 `"""` 包裹',
                ],
            },
            {
                "heading": "类型转换",
                "code": textwrap.dedent(
                    '''
                    var amount = '123.45'::decimal(0);
                    var date = '2020-01-01'::date('yyyy-MM-dd');
                    var fallback = 'abc'::int(111); // 默认值
                    '''
                ).strip(),
                "notes": "`::type(default)` 支持默认值，减少空指针判断。",
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/base/script/#%E6%95%B0%E6%8D%AE%E7%B1%BB%E5%9E%8B",
    },
    "collections": {
        "title": "集合操作",
        "summary": "内置高阶函数 `map`/`filter`/`each`/`join`，支持解构展开。",
        "sections": [
            {
                "heading": "遍历与过滤",
                "code": textwrap.dedent(
                    '''
                    var users = db.select("select id,name from user");
                    return users.filter((u) => u.status == 1)
                                .map(u => u.name);
                    '''
                ).strip(),
            },
            {
                "heading": "展开语法",
                "code": "var merged = [1,2,...[3,4]]; // [1,2,3,4]",
                "notes": "`{key1:1,...map}` 可合并 Map，注意索引键为字符串。",
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/extension/collection/",
    },
    "db": {
        "title": "数据库与事务",
        "summary": "`db` 模块支持 CRUD、事务与缓存。务必使用参数绑定。",
        "sections": [
            {
                "heading": "查询",
                "code": textwrap.dedent(
                    '''
                    import response;
                    var rows = db.select("""
                        select id,name from users
                        where status = #{status}
                    """, {status: 1});
                    return response.json(rows);
                    '''
                ).strip(),
                "notes": "参数一律使用 `#{}`，避免 `${}` 拼接 SQL。",
            },
            {
                "heading": "事务",
                "code": textwrap.dedent(
                    '''
                    return db.transaction(() => {
                        var id = db.insert("insert into t(a) values(#{a})", {a:1});
                        if(!id){ exit 500,'插入失败'; }
                        return {success:true, id:id};
                    });
                    '''
                ).strip(),
                "notes": "异常抛出自动回滚，可自定义 `exit` 返回业务码。",
            },
            {
                "heading": "链式表操作",
                "code": textwrap.dedent(
                    '''
                    var result = db.table("magic_api_info")
                                    .columns("api_method", "api_path")
                                    .page();
                    '''
                ).strip(),
                "notes": "使用 `db.table(...).page()` 继承全局分页配置，可在 `config/spring-boot/#page` 自定义页码参数。",
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/base/db/",
    },
    "response": {
        "title": "响应统一封装",
        "summary": "导入 `response` 模块统一输出 JSON/Page/Text。",
        "sections": [
            {
                "heading": "分页响应",
                "code": textwrap.dedent(
                    '''
                    import response;
                    return response.page(total, records);
                    '''
                ).strip(),
            },
            {
                "heading": "错误输出",
                "code": textwrap.dedent(
                    '''
                    import response;
                    if(list.isEmpty()){
                        return response.error(404, '数据不存在');
                    }
                    '''
                ).strip(),
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/module/response/",
    },
    "loops": {
        "title": "循环语句",
        "summary": "支持 for...in 循环遍历集合和指定次数循环。",
        "sections": [
            {
                "heading": "遍历集合",
                "code": textwrap.dedent(
                    '''
                    import 'java.lang.System' as System;
                    var list = [1,2,3];
                    for(index,item in list){    //如果不需要index，也可以写成for(item in list)
                        System.out.println(index + ":" + item);
                    }
                    // 结果：
                    // 0:1
                    // 1:2
                    // 2:3
                    '''
                ).strip(),
            },
            {
                "heading": "指定次数循环",
                "code": textwrap.dedent(
                    '''
                    var sum = 0;
                    for(value in range(0,100)){    //包括0包括100
                        sum = sum + value; //不支持+= -= *= /= ++ -- 这种运算
                    }
                    return sum; // 结果：5050
                    '''
                ).strip(),
            },
            {
                "heading": "遍历Map",
                "code": textwrap.dedent(
                    '''
                    import 'java.lang.System' as System;
                    var map = {
                        key1 : 123,
                        key2 : 456
                    };
                    for(key,value in map){    //如果不需要key，也可以写成for(value in map)
                        System.out.println(key + ":" + value);
                    }
                    // 结果：
                    // key1:123
                    // key2:456
                    '''
                ).strip(),
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/base/script/#for%E5%BE%AA%E7%8E%AF",
    },
    "imports": {
        "title": "导入语句",
        "summary": "支持导入Java类、Spring Bean和自定义模块。",
        "sections": [
            {
                "heading": "导入Java类",
                "code": textwrap.dedent(
                    '''
                    import 'java.lang.System' as System;//导入静态类并赋值给system作为变量
                    import 'javax.sql.DataSource' as ds;//从spring中获取DataSource并将值赋值给ds作为变量
                    import 'org.apache.commons.lang3.StringUtils' as string;//导入静态类并赋值给ds作为变量
                    import 'java.text.*'    //此写法跟Java一致，在1.3.4中新增
                    System.out.println('调用System打印');//调用静态方法
                    '''
                ).strip(),
            },
            {
                "heading": "导入模块",
                "code": textwrap.dedent(
                    '''
                    import log; //导入log模块，并定义一个与模块名相同的变量名
                    //import log as logger; //导入log模块，并赋值给变量 logger
                    log.info('Hello {}','Magic API!')
                    '''
                ).strip(),
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/base/script/#Import%E5%AF%BC%E5%85%A5",
    },
    "async": {
        "title": "异步调用",
        "summary": "使用 async 关键字实现异步操作，提高并发性能。",
        "sections": [
            {
                "heading": "异步方法调用",
                "code": textwrap.dedent(
                    '''
                    // 使用async关键字，会启动一个线程去执行，返回Future类型，并不等待结果继续执行后续代码
                    var user1 = async db.select("select * from sys_user where id = 1");
                    var user2 = async db.select("select * from sys_user where id = 2");
                    // 调用get方法表示阻塞等待获取结果
                    return [user1.get(),user2.get()];
                    '''
                ).strip(),
            },
            {
                "heading": "异步Lambda",
                "code": textwrap.dedent(
                    '''
                    var list = [];
                    for(index in range(1,10)){
                        // 当异步中使用外部变量时，为了确保线程安全的变量，可以将其放在形参中
                        list.add(async (index)=>db.select("select * from sys_user where id = #{index}"));
                    }
                    return list.map(item=>item.get());  // 循环获取结果
                    '''
                ).strip(),
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/base/async/",
    },
    "lambda_expressions": {
        "title": "Lambda 表达式",
        "summary": "支持现代函数式编程，提供 map、filter、group 等高阶函数。",
        "sections": [
            {
                "heading": "映射(map)",
                "code": textwrap.dedent(
                    '''
                    var list = [
                        {sex : 0,name : '小明',age : 19},
                        {sex : 1,name : '小花',age : 18}
                    ];
                    var getAge = (age) => age > 18 ? '成人' : '未成年'
                    // 利用map函数对list进行过滤
                    return list.map(item => {
                        age : getAge(item.age),
                        sex : item.sex == 0 ? '男' : '女',
                        name : item.name
                    });
                    '''
                ).strip(),
                "notes": "支持对象转换和条件判断",
            },
            {
                "heading": "过滤(filter)",
                "code": textwrap.dedent(
                    '''
                    var list = [
                        {sex : 0,name : '小明'},
                        {sex : 1,name : '小花'}
                    ]
                    // 利用filter函数对list进行过滤
                    return list.filter(item => item.sex == 0);
                    '''
                ).strip(),
                "notes": "等价于 SQL 中的 WHERE 子句",
            },
            {
                "heading": "分组(group)",
                "code": textwrap.dedent(
                    '''
                    var result = [
                        { xxx : 1, yyy : 2, value : 11},
                        { xxx : 1, yyy : 2, value : 22},
                        { xxx : 2, yyy : 2, value : 33}
                    ];

                    return result.group(item => item.xxx + '_' + item.yyy)
                    '''
                ).strip(),
                "notes": "支持自定义聚合函数",
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/base/lambda/",
    },
    "linq": {
        "title": "Linq 查询",
        "summary": "提供类似 SQL 的查询语法，支持关联、转换、分组等操作。",
        "sections": [
            {
                "heading": "基本语法",
                "code": textwrap.dedent(
                    '''
                    select
                        tableAlias.*|[tableAlias.]field[ columnAlias]
                        [,tableAlias.field2[ columnAlias2][,…]]
                    from expr[,…] tableAlias
                    [[left ]join expr tableAlias2 on condition]
                    [where condition]
                    [group by tableAlias.field[,...]]
                    [having condition]
                    [order by tableAlias.field[asc|desc][,tableAlias.field[asc|desc]]]
                    [limit expr [offset expr]]
                    '''
                ).strip(),
            },
            {
                "heading": "查询示例",
                "code": textwrap.dedent(
                    '''
                    return select
                        t.name, sum(t.score) score,
                        t.*
                    from results t
                    where t.status = 1
                    group by t.name
                    having count(t.name) > 1
                    order by score desc
                    limit 10
                    '''
                ).strip(),
            },
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/base/linq/",
    },
    "mybatis_syntax": {
        "title": "MyBatis 动态SQL语法",
        "summary": "Magic-API 支持 MyBatis 风格的动态SQL语法，提供强大的条件查询和动态更新能力。",
        "sections": [
            {
                "heading": "if 条件判断",
                "description": "使用 <if> 标签进行条件判断，只有当条件成立时才会包含其中的SQL片段。",
                "code": textwrap.dedent(
                    '''
                    return db.select("""
                        select * from hrm_org
                        <if test="params.name != null">
                            where org_name like concat('%', #{params.name}, '%')
                        </if>
                        <if test="params.status != null">
                            and status = #{params.status}
                        </if>
                    """)
                    '''
                ).strip(),
                "notes": [
                    "test属性中的变量直接访问，无需额外声明",
                    "支持JavaScript表达式，如比较运算、逻辑运算等",
                    "支持字符串拼接函数concat等"
                ]
            },
            {
                "heading": "elseif / else 条件分支",
                "description": "使用 <elseif> 和 <else> 创建条件分支结构。",
                "code": textwrap.dedent(
                    '''
                    const val = 1
                    return db.select("""
                        select api_name from magic_api_info
                        where
                        <if test="val == 2">
                            api_name is not null
                        </if>
                        <elseif test="val == 1">
                            api_name = '测试'
                        </elseif>
                        <else>
                            api_name is null
                        </else>
                    """)
                    '''
                ).strip(),
                "notes": [
                    "elseif必须紧跟if标签之后",
                    "else标签不需要test条件",
                    "支持多层嵌套条件判断"
                ]
            },
            {
                "heading": "foreach 循环遍历",
                "description": "使用 <foreach> 标签遍历集合，生成重复的SQL片段。",
                "code": textwrap.dedent(
                    '''
                    const idList = ['1', '2', '3']
                    return db.select("""
                        select id from magic_api_info
                        where id in
                        <foreach collection="idList" open="(" separator="," close=")" item="item">
                            #{item}
                        </foreach>
                    """)
                    '''
                ).strip(),
                "attributes": {
                    "collection": "要遍历的集合变量名",
                    "item": "集合中每个元素的变量名",
                    "index": "集合中元素的索引变量名（可选）",
                    "open": "循环开始时插入的字符串",
                    "close": "循环结束时插入的字符串",
                    "separator": "元素之间的分隔符"
                },
                "notes": [
                    "collection属性指定要遍历的变量",
                    "支持数组、List等集合类型",
                    "常用于IN条件和批量插入"
                ]
            },
            {
                "heading": "set 动态更新",
                "description": "使用 <set> 标签动态生成UPDATE语句的SET子句，会自动处理逗号和前缀。",
                "code": textwrap.dedent(
                    '''
                    var sql = """
                        update test_data
                        <set>
                            <if test="params.name != null">
                                name = #{params.name},
                            </if>
                            <if test="params.content != null">
                                content = #{params.content},
                            </if>
                        </set>
                        where id = #{params.id}
                    """
                    return db.update(sql, params)
                    '''
                ).strip(),
                "notes": [
                    "set标签会自动添加SET关键字",
                    "自动处理字段间的逗号分隔",
                    "避免更新语句中出现多余的逗号"
                ]
            },
            {
                "heading": "where 条件封装",
                "description": "使用 <where> 标签自动处理WHERE子句，会自动添加WHERE关键字并处理AND/OR逻辑。",
                "code": textwrap.dedent(
                    '''
                    return db.select("""
                        select * from users
                        <where>
                            <if test="params.name != null">
                                and name like concat('%', #{params.name}, '%')
                            </if>
                            <if test="params.status != null">
                                and status = #{params.status}
                            </if>
                        </where>
                    """)
                    '''
                ).strip(),
                "notes": [
                    "where标签会自动添加WHERE关键字",
                    "自动处理第一个AND关键字",
                    "避免出现空WHERE子句"
                ]
            },
            {
                "heading": "trim 字符串处理",
                "description": "使用 <trim> 标签自定义SQL片段的格式。",
                "code": textwrap.dedent(
                    '''
                    return db.select("""
                        select * from users
                        <trim prefix="WHERE" prefixOverrides="AND |OR ">
                            <if test="params.name != null">
                                AND name like concat('%', #{params.name}, '%')
                            </if>
                            <if test="params.status != null">
                                OR status = #{params.status}
                            </if>
                        </trim>
                    """)
                    '''
                ).strip(),
                "attributes": {
                    "prefix": "添加的前缀",
                    "suffix": "添加的后缀",
                    "prefixOverrides": "移除的前缀",
                    "suffixOverrides": "移除的后缀"
                }
            },
            {
                "heading": "choose / when / otherwise 选择结构",
                "description": "使用 <choose> 创建多条件选择结构。",
                "code": textwrap.dedent(
                    '''
                    return db.select("""
                        select * from orders
                        <where>
                            <choose>
                                <when test="params.vipUser">
                                    and user_level = 'VIP'
                                </when>
                                <when test="params.newUser">
                                    and create_time > date_sub(now(), interval 30 day)
                                </when>
                                <otherwise>
                                    and status = 'active'
                                </otherwise>
                            </choose>
                        </where>
                    """)
                    '''
                ).strip(),
                "notes": [
                    "choose内只能有一个otherwise标签",
                    "when条件按顺序匹配，第一个匹配的执行",
                    "otherwise是可选的默认分支"
                ]
            }
        ],
        "advanced_features": [
            {
                "name": "变量绑定",
                "description": "使用 #{variable} 进行参数绑定，防止SQL注入",
                "example": "where name = #{params.name} and age > #{params.age}"
            },
            {
                "name": "字符串拼接",
                "description": "使用 ${variable} 进行字符串拼接（有SQL注入风险）",
                "example": "where name like '%${params.name}%'"
            },
            {
                "name": "OGNL表达式",
                "description": "支持OGNL表达式语法进行复杂条件判断",
                "example": '<if test="params.userList != null and params.userList.size() > 0">'
            },
            {
                "name": "集合操作",
                "description": "支持对集合进行size()、isEmpty()等操作",
                "example": '<if test="params.ids != null and !params.ids.isEmpty()">'
            }
        ],
        "best_practices": [
            "优先使用 #{param} 进行参数绑定，避免 ${param} 的SQL注入风险",
            "合理使用 <where> 标签避免出现空的WHERE子句",
            "使用 <set> 标签简化UPDATE语句的字段设置",
            "<foreach> 常用于IN查询和批量插入操作",
            "复杂条件建议使用 <choose> 而不是多个 <if> 嵌套",
            "注意变量作用域，test属性中的变量要确保存在"
        ],
        "doc": "https://www.ssssssss.org/magic-api/pages/quick/crud/#mybatis%E8%AF%AD%E6%B3%95%E6%94%AF%E6%8C%81"
    },
    "script_syntax": {
        "title": "脚本语法示例",
        "description": "Magic-API脚本语言的核心语法示例和最佳实践",
        "examples": {
            "if_statement": {
                "title": "if条件判断",
                "description": "if语句的各种使用形式和条件判断规则",
                "code": textwrap.dedent('''
                    /*
                        if 测试
                    */
                    if(a == 1){
                        return 1;
                    }else if(a == 2){
                        return 2;
                    }else{
                        return 0;
                    }

                    /*
                    对于条件判断，特意支持了简写的方式
                    如 可以直接写
                    1、if(a)
                    2、else if(a)
                    3、while(a)
                    4、a ? 1 : 0

                    当a的值是以下情况时为false
                    null
                    空集合
                    空Map
                    数值 == 0
                    空字符串（length == 0）
                    false
                    其它情况一律视为true
                    */
                    ''').strip(),
                "notes": [
                    "支持完整的if-else if-else结构",
                    "支持条件简写形式",
                    "false值的判断规则与JavaScript类似",
                    "支持三元运算符 a ? b : c"
                ],
                "tags": ["条件判断", "控制流", "布尔值"]
            },
            "exit_statement": {
                "title": "exit语句",
                "description": "使用exit语句提前终止执行并返回指定结果",
                "code": textwrap.dedent('''
                    if(0){
                        exit 400,'参数填写有误'
                    }
                    // 第一个参数为code，第二个为message，第三个为data，至少要填写一个参数。
                    exit 200,'success','ok'
                    ''').strip(),
                "notes": [
                    "exit后可以跟1-3个参数：状态码、消息、数据",
                    "会立即终止脚本执行",
                    "常用于参数验证失败或错误处理",
                    "类似于HTTP状态码返回"
                ],
                "tags": ["退出", "错误处理", "状态码"]
            },
            "type_conversion": {
                "title": "类型转换",
                "description": "Magic-API支持的三种类型转换方法",
                "code": textwrap.dedent('''
                    var a = 123;
                    var str = "456.0";

                    /* 目前转换的办法一共有三种，
                        1、使用Java相关函数，如Integer.parseInt
                        2、是使用脚本提供的语法::进行转换，支持::int ::double ::string ::byte ::long ::short ::float ::date
                        3、使用扩展方法，xxx.asXXX(); 如 a.asInt()
                    */

                    return {
                        '::string': a::string,  // 使用::转换，好处是它是语法级的，不会产生空指针，
                        '::int' : str::int(0),  // 转换失败是使用默认值0，
                        'ext': a.asString(),   // 使用扩展方法转换
                        'toDate' : '2020-01-01'::date('yyyy-MM-dd'),
                        "obj::stringify":{"a":a}::stringify
                    };
                    ''').strip(),
                "notes": [
                    "::语法转换 - 语法级转换，不会产生空指针异常",
                    "支持默认值 - ::int(0) 在转换失败时使用默认值",
                    "扩展方法 - asXXX() 方法系列",
                    "日期转换 - 支持自定义格式化模式"
                ],
                "tags": ["类型转换", "数据类型", "安全转换"]
            },
            "operators": {
                "title": "各类运算符",
                "description": "Magic-API支持的完整运算符集合",
                "code": textwrap.dedent('''
                    var a = 123;    // 定义int型变量，定义变量只能使用var。var可以省略
                    var b = 456;

                    return {
                        '+': a + b,        // 加法
                        '-': a - b,        // 减法
                        '-a' : -a,         // 负数
                        '*': a * b,        // 乘法
                        '/': a / b,        // 除法
                        '%': a % b,        // 取模
                        '++': a++,         // 自增
                        '--': a--,         // 自减
                        '>': a > b,        // 大于
                        '>=': a >= b,      // 大于等于
                        '<': a < b,        // 小于
                        '<=': a <= b,      // 小于等于
                        '==': a == b,      // 等于
                        '===': a === b,    // 严格等于（类型和值都相等）
                        '!=': a != b,      // 不等于
                        '!==': a !== b,    // 严格不等于
                        '&&': a && b,      // 逻辑与
                        '||': a || b,      // 逻辑或
                        '>>':  8 >> 2,     // 右移
                        '>>>': 8 >>> 2,    // 无符号右移
                        '<<' : 1 << 2,     // 左移
                        '^' : 1 ^ 2,       // 异或
                        '&': 1 & 2,        // 按位与
                        '|': 1 | 2         // 按位或
                    };
                    ''').strip(),
                "notes": [
                    "支持完整的算术运算符",
                    "支持比较运算符，包括严格相等",
                    "支持逻辑运算符，短路求值",
                    "支持位运算符",
                    "变量定义使用var关键字"
                ],
                "tags": ["运算符", "算术", "逻辑", "位运算"]
            },
            "lambda_definition": {
                "title": "Lambda表达式定义",
                "description": "定义和使用Lambda表达式的各种形式",
                "code": textwrap.dedent('''
                    /*
                        测试Lambda
                    */
                    var lambda1 = e => e + 1; //单参数单行代码，省略括号,省略{}
                    var lambda2 = (e) => e +1; //单参数单行代码，不省略括号，省略{} 作用同上
                    var lambda4 = e => {e + 1};//单参数无返回值，不能省略{}
                    var lambda5 = e => {return e + 1};//单参数有返回值，省略括号,不省略{}
                    var lambda6 = (e) => {return e + 1};//单参数有返回值，不省略括号,不省略{}，作用同上
                    var lambda7 = (a,b) => a + b; //多参数单行代码，省略{}
                    var lambda8 = (a,b) => {return a + b}; //多参数单行代码，有返回值，作用同上

                    var lambda9 = (a,b) =>{ //多参数多行代码， 无法省略括号和{}
                        a = a + 1;
                        return a + b;
                    };

                    var v1 = lambda1(1);    //返回2
                    var v2 = lambda2(v1);    //返回3
                    return lambda9(v1,lambda7(v1,v2)); //返回8
                    ''').strip(),
                "notes": [
                    "支持多种Lambda定义语法",
                    "单行代码可以省略{}",
                    "多行代码必须使用{}",
                    "支持单参数和多参数",
                    "支持有返回值和无返回值"
                ],
                "tags": ["Lambda", "函数式编程", "匿名函数"]
            },
            "optional_chaining": {
                "title": "可选链操作符",
                "description": "使用?.操作符安全访问嵌套属性，避免空指针异常",
                "code": textwrap.dedent('''
                    var map = {
                        a : {
                            b : 'ok'
                        },
                        c : 1
                    };

                    // ?. 不会报错，.会报错
                    return map.a.bbbb?.c + '-' + map.a?.b;
                    ''').strip(),
                "notes": [
                    "?.操作符在属性不存在时返回undefined，不会抛出异常",
                    ".操作符在属性不存在时会抛出NullPointerException",
                    "适用于安全访问深层嵌套对象",
                    "与JavaScript的可选链操作符类似"
                ],
                "tags": ["可选链", "安全访问", "空指针"]
            },
            "spread_operator": {
                "title": "扩展运算符",
                "description": "使用...运算符展开对象和数组",
                "code": textwrap.dedent('''
                    var map = {
                        a : 1,
                        b : 2
                    };

                    var list = [1,2,3,4,5];

                    return {
                        ...map,     // 展开Map
                        c : 3,
                        d : [...list]   // 展开list
                    };
                    ''').strip(),
                "notes": [
                    "支持展开对象属性",
                    "支持展开数组元素",
                    "常用于对象合并和数组复制",
                    "与ES6扩展运算符语法相同"
                ],
                "tags": ["扩展运算符", "对象展开", "数组展开"]
            },
            "async_execution": {
                "title": "异步执行",
                "description": "使用async关键字进行异步操作",
                "code": textwrap.dedent('''
                    var list = [];
                    for(index in range(1,10)){
                        // 执行SQL时，为了线程安全，需要把index参数放入lambda参数中。
                        list.add(async (index)=>db.selectInt('select #{index}'));
                    }
                    return list.map(f => f.get());
                    ''').strip(),
                "notes": [
                    "async标记的Lambda会异步执行",
                    "返回Future对象，需要调用.get()获取结果",
                    "常用于并发数据库查询",
                    "线程安全考虑"
                ],
                "tags": ["异步", "并发", "Future", "线程安全"]
            },
            "java_interaction": {
                "title": "与Java交互",
                "description": "在Magic-API脚本中导入和使用Java类",
                "code": textwrap.dedent('''
                    import 'java.util.Date' as Date;
                    import 'java.text.SimpleDateFormat' as SimpleDateFormat;

                    var now = new Date();   // 创建对象
                    var df = new SimpleDateFormat('yyyy-MM-dd');

                    return df.format(now);  // 调用方法
                    ''').strip(),
                "notes": [
                    "使用import语句导入Java类",
                    "支持as关键字设置别名",
                    "可以创建Java对象实例",
                    "可以调用Java对象的方法",
                    "支持Java的所有类和方法"
                ],
                "tags": ["Java集成", "类导入", "对象创建", "方法调用"]
            },
            "try_catch": {
                "title": "异常处理",
                "description": "使用try-catch-finally进行异常处理",
                "code": textwrap.dedent('''
                    try{
                        var c = 1 / 0;
                    }catch(e){  //不用写类型，只写变量即可
                        return e.getMessage();
                    }finally{
                        return 'finally';
                    }
                    // catch 和finally 都可以不写。
                    return 'ok';
                    ''').strip(),
                "notes": [
                    "catch块中的变量e即为异常对象",
                    "不需要指定异常类型",
                    "finally块总是会执行",
                    "catch和finally都是可选的",
                    "支持完整的异常处理机制"
                ],
                "tags": ["异常处理", "try-catch", "finally", "错误处理"]
            },
            "loop_operations": {
                "title": "循环操作",
                "description": "Magic-API支持的各种循环操作，包括for循环、while循环和函数式循环",
                "code": textwrap.dedent('''
                    // 1. for-in循环List
                    var list1 = [1,2,3,4,5];
                    var listSum = 0;
                    for(val in list1){
                        listSum = listSum + val;
                    }

                    // 2. for-in循环Map
                    var map1 = {key1: 1, key2: 2, key3: 3};
                    var mapSum = 0;
                    var keys = '';
                    for(key,value in map1){
                        mapSum = mapSum + value;
                        keys = keys + key;
                    }

                    // 3. 传统for循环
                    var rangeSum = 0;
                    for(val in range(0,100)){   // 包括0和100
                        if(val > 90){
                            break;  // 跳出循环
                        }
                        if(val % 3 == 0){
                            continue;   // 进入下一次循环
                        }
                        rangeSum = rangeSum + val;
                    }

                    // 4. Lambda循环List
                    var list2 = [1,2,3,4,5,6,7,8,9,10];
                    var lambdaListSum = 0;
                    list2.each(it => lambdaListSum += it + 1);

                    // 5. Lambda循环Map
                    var map2 = {key1: 1, key2: 2, key3: 3};
                    var lambdaMapSum = 0;
                    var lambdaKeys = '';
                    map2.each((key,value) => {
                        lambdaKeys += key;
                        lambdaMapSum += value;
                    });

                    // 6. while循环
                    var index = 0;
                    var whileSum = 0;
                    while(index < 100){
                        whileSum += index++;
                    }

                    return {
                        listSum: listSum,
                        mapResult: keys + '-' + mapSum,
                        rangeSum: rangeSum,
                        lambdaListSum: lambdaListSum,
                        lambdaMapResult: lambdaKeys + '-' + lambdaMapSum,
                        whileSum: whileSum
                    };
                    ''').strip(),
                "notes": [
                    "for-in循环 - 直接遍历集合元素",
                    "Map循环 - for(key,value in map)同时获取键值",
                    "range函数 - range(start,end)包括起始和结束值",
                    "break和continue - 支持跳出和继续循环",
                    "Lambda循环 - each()方法使用Lambda表达式",
                    "while循环 - 标准的while条件循环"
                ],
                "tags": ["循环", "for循环", "while循环", "Lambda循环", "集合遍历"]
            }
        }
    },
}

def get_syntax(topic: str) -> Dict[str, Any] | None:
    """获取指定语法主题的详细信息。"""
    return SYNTAX_KNOWLEDGE.get(topic)

def list_syntax_topics() -> List[str]:
    """获取所有可用的语法主题。"""
    return list(SYNTAX_KNOWLEDGE.keys())

__all__ = [
    "SYNTAX_KNOWLEDGE",
    "get_syntax",
    "list_syntax_topics"
]
