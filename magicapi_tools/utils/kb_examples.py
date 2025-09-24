"""Magic-API 使用示例知识库。"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, List

# 使用示例知识库
EXAMPLES_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "basic_crud": {
        "title": "基础CRUD操作",
        "description": "最常用的数据库增删改查操作示例",
        "examples": {
            "select_users": {
                "title": "查询用户列表",
                "description": "分页查询用户信息",
                "code": textwrap.dedent('''
                    import response;

                    // 查询用户列表（带分页）
                    var page = params.page ? params.page : 1;
                    var size = params.size ? params.size : 10;
                    var keyword = params.keyword;

                    // 查询总数
                    var totalSql = """
                        SELECT COUNT(*) as total
                        FROM sys_user
                        WHERE 1=1
                        ?{keyword, AND (user_name LIKE CONCAT('%', #{keyword}, '%')
                                      OR phone LIKE CONCAT('%', #{keyword}, '%'))}
                    """;
                    var total = db.selectInt(totalSql, {keyword: keyword});

                    // 查询数据
                    var dataSql = """
                        SELECT id, user_name, phone, email, create_time, status
                        FROM sys_user
                        WHERE 1=1
                        ?{keyword, AND (user_name LIKE CONCAT('%', #{keyword}, '%')
                                      OR phone LIKE CONCAT('%', #{keyword}, '%'))}
                        ORDER BY create_time DESC
                        LIMIT #{offset}, #{size}
                    """;
                    var list = db.select(dataSql, {
                        keyword: keyword,
                        offset: (page - 1) * size,
                        size: size
                    });

                    return response.page(total, list);
                ''').strip(),
                "tags": ["查询", "分页", "搜索"]
            },
            "create_user": {
                "title": "创建用户",
                "description": "新增用户信息",
                "code": textwrap.dedent('''
                    import response;

                    // 参数校验
                    if(!body.userName || !body.phone){
                        exit 400, '用户名和手机号不能为空';
                    }

                    // 检查手机号是否已存在
                    var exist = db.selectInt("""
                        SELECT COUNT(*) FROM sys_user WHERE phone = #{phone}
                    """, {phone: body.phone});

                    if(exist > 0){
                        exit 400, '手机号已存在';
                    }

                    // 创建用户
                    var userId = db.insert("""
                        INSERT INTO sys_user(user_name, phone, email, status, create_time)
                        VALUES(#{userName}, #{phone}, #{email}, 1, NOW())
                    """, body);

                    return response.json({
                        success: true,
                        message: '用户创建成功',
                        data: {userId: userId}
                    });
                ''').strip(),
                "tags": ["创建", "校验", "事务"]
            },
            "update_user": {
                "title": "更新用户信息",
                "description": "修改用户基本信息",
                "code": textwrap.dedent('''
                    import response;

                    // 校验参数
                    if(!body.id){
                        exit 400, '用户ID不能为空';
                    }

                    // 检查用户是否存在
                    var user = db.selectOne("""
                        SELECT id, user_name FROM sys_user WHERE id = #{id}
                    """, {id: body.id});

                    if(!user){
                        exit 404, '用户不存在';
                    }

                    // 更新用户信息
                    db.update("""
                        UPDATE sys_user
                        SET user_name = #{userName},
                            phone = #{phone},
                            email = #{email},
                            update_time = NOW()
                        WHERE id = #{id}
                    """, body);

                    return response.json({
                        success: true,
                        message: '用户信息更新成功'
                    });
                ''').strip(),
                "tags": ["更新", "校验"]
            },
            "delete_user": {
                "title": "删除用户",
                "description": "软删除用户信息",
                "code": textwrap.dedent('''
                    import response;

                    if(!params.id){
                        exit 400, '用户ID不能为空';
                    }

                    // 检查用户是否存在
                    var user = db.selectOne("""
                        SELECT id, status FROM sys_user WHERE id = #{id}
                    """, {id: params.id});

                    if(!user){
                        exit 404, '用户不存在';
                    }

                    // 软删除用户
                    db.update("""
                        UPDATE sys_user
                        SET status = 0,
                            delete_time = NOW()
                        WHERE id = #{id}
                    """, {id: params.id});

                    return response.json({
                        success: true,
                        message: '用户删除成功'
                    });
                ''').strip(),
                "tags": ["删除", "软删除"]
            }
        }
    },
    "advanced_queries": {
        "title": "高级查询",
        "description": "复杂的查询操作示例",
        "examples": {
            "complex_search": {
                "title": "复杂条件搜索",
                "description": "多条件组合查询",
                "code": textwrap.dedent('''
                    import response;

                    var conditions = [];
                    var params = {};

                    // 动态构建查询条件
                    if(params.userName){
                        conditions.add("AND user_name LIKE CONCAT('%', #{userName}, '%')");
                        params.userName = params.userName;
                    }

                    if(params.status != null){
                        conditions.add("AND status = #{status}");
                        params.status = params.status;
                    }

                    if(params.startDate){
                        conditions.add("AND create_time >= #{startDate}");
                        params.startDate = params.startDate;
                    }

                    if(params.endDate){
                        conditions.add("AND create_time <= #{endDate}");
                        params.endDate = params.endDate;
                    }

                    var whereClause = conditions.isEmpty() ? "" : "WHERE 1=1 " + conditions.join(" ");

                    var sql = """
                        SELECT id, user_name, phone, email, status, create_time
                        FROM sys_user
                    """ + whereClause + """
                        ORDER BY create_time DESC
                        LIMIT #{offset}, #{size}
                    """;

                    var countSql = "SELECT COUNT(*) FROM sys_user " + whereClause;

                    params.offset = (params.page ? params.page : 1 - 1) * (params.size ? params.size : 10);
                    params.size = params.size ? params.size : 10;

                    var total = db.selectInt(countSql, params);
                    var list = db.select(sql, params);

                    return response.page(total, list);
                ''').strip(),
                "tags": ["动态查询", "多条件", "分页"]
            },
            "join_query": {
                "title": "关联查询",
                "description": "多表关联查询示例",
                "code": textwrap.dedent('''
                    import response;

                    // 查询用户及其角色信息
                    var sql = """
                        SELECT u.id, u.user_name, u.phone, u.email,
                               r.role_name, r.role_code
                        FROM sys_user u
                        LEFT JOIN sys_user_role ur ON u.id = ur.user_id
                        LEFT JOIN sys_role r ON ur.role_id = r.id
                        WHERE u.status = 1
                        ORDER BY u.create_time DESC
                        LIMIT #{offset}, #{size}
                    """;

                    var users = db.select(sql, {
                        offset: (params.page ? params.page : 1 - 1) * (params.size ? params.size : 10),
                        size: params.size ? params.size : 10
                    });

                    // 按用户分组，聚合角色信息
                    var userMap = users.group(item => item.id, list => {
                        var user = {
                            id: list[0].id,
                            userName: list[0].user_name,
                            phone: list[0].phone,
                            email: list[0].email,
                            roles: list.filter(item => item.role_name != null)
                                     .map(item => ({
                                         roleName: item.role_name,
                                         roleCode: item.role_code
                                     }))
                        };
                        return user;
                    });

                    var result = userMap.values().toList();
                    return response.json({
                        success: true,
                        data: result
                    });
                ''').strip(),
                "tags": ["关联查询", "分组聚合", "多表"]
            },
            "statistical_query": {
                "title": "统计查询",
                "description": "数据统计和聚合查询",
                "code": textwrap.dedent('''
                    import response;

                    // 用户状态统计
                    var statusStats = db.select("""
                        SELECT status,
                               COUNT(*) as count,
                               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
                        FROM sys_user
                        GROUP BY status
                        ORDER BY status
                    """);

                    // 每日注册用户统计
                    var dailyStats = db.select("""
                        SELECT DATE(create_time) as date,
                               COUNT(*) as register_count
                        FROM sys_user
                        WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                        GROUP BY DATE(create_time)
                        ORDER BY date DESC
                    """);

                    // 用户年龄段分布
                    var ageStats = db.select("""
                        SELECT
                            CASE
                                WHEN age < 18 THEN '18岁以下'
                                WHEN age BETWEEN 18 AND 25 THEN '18-25岁'
                                WHEN age BETWEEN 26 AND 35 THEN '26-35岁'
                                WHEN age BETWEEN 36 AND 50 THEN '36-50岁'
                                ELSE '50岁以上'
                            END as age_group,
                            COUNT(*) as count
                        FROM sys_user
                        WHERE age IS NOT NULL
                        GROUP BY
                            CASE
                                WHEN age < 18 THEN '18岁以下'
                                WHEN age BETWEEN 18 AND 25 THEN '18-25岁'
                                WHEN age BETWEEN 26 AND 35 THEN '26-35岁'
                                WHEN age BETWEEN 36 AND 50 THEN '36-50岁'
                                ELSE '50岁以上'
                            END
                        ORDER BY count DESC
                    """);

                    return response.json({
                        success: true,
                        data: {
                            statusStats: statusStats,
                            dailyStats: dailyStats,
                            ageStats: ageStats
                        }
                    });
                ''').strip(),
                "tags": ["统计", "聚合", "分组"]
            }
        }
    },
    "transactions": {
        "title": "事务处理",
        "description": "数据库事务操作示例",
        "examples": {
            "simple_transaction": {
                "title": "简单事务",
                "description": "基本的数据库事务操作",
                "code": textwrap.dedent('''
                    import response;

                    // 使用自动事务
                    var result = db.transaction(() => {
                        // 扣减账户余额
                        db.update("""
                            UPDATE account
                            SET balance = balance - #{amount}
                            WHERE id = #{fromAccount} AND balance >= #{amount}
                        """, {
                            fromAccount: body.fromAccount,
                            amount: body.amount
                        });

                        // 增加目标账户余额
                        db.update("""
                            UPDATE account
                            SET balance = balance + #{amount}
                            WHERE id = #{toAccount}
                        """, {
                            toAccount: body.toAccount,
                            amount: body.amount
                        });

                        // 记录转账记录
                        db.insert("""
                            INSERT INTO transfer_record(from_account, to_account, amount, create_time)
                            VALUES(#{fromAccount}, #{toAccount}, #{amount}, NOW())
                        """, body);

                        return {success: true, message: '转账成功'};
                    });

                    return response.json(result);
                ''').strip(),
                "tags": ["事务", "转账", "数据一致性"]
            },
            "manual_transaction": {
                "title": "手动事务",
                "description": "手动控制事务的提交和回滚",
                "code": textwrap.dedent('''
                    import response;

                    var tx = db.transaction(); // 开启事务
                    try {
                        // 第一步操作
                        var result1 = db.update("""
                            UPDATE inventory
                            SET quantity = quantity - #{qty}
                            WHERE product_id = #{productId} AND quantity >= #{qty}
                        """, body);

                        if(result1 == 0){
                            throw '库存不足';
                        }

                        // 第二步操作
                        db.insert("""
                            INSERT INTO order_item(order_id, product_id, quantity, price)
                            VALUES(#{orderId}, #{productId}, #{qty}, #{price})
                        """, body);

                        // 更新订单总金额
                        db.update("""
                            UPDATE order_master
                            SET total_amount = total_amount + #{total}
                            WHERE id = #{orderId}
                        """, {
                            orderId: body.orderId,
                            total: body.qty * body.price
                        });

                        tx.commit(); // 提交事务

                        return response.json({
                            success: true,
                            message: '订单创建成功'
                        });

                    } catch(e) {
                        tx.rollback(); // 回滚事务
                        return response.json({
                            success: false,
                            message: '订单创建失败: ' + e
                        });
                    }
                ''').strip(),
                "tags": ["手动事务", "异常处理", "回滚"]
            },
            "nested_transaction": {
                "title": "嵌套事务",
                "description": "在事务中调用其他事务操作",
                "code": textwrap.dedent('''
                    import response;

                    // 定义可重用的业务方法
                    var createOrder = (orderData) => {
                        return db.transaction(() => {
                            // 创建订单主表
                            var orderId = db.insert("""
                                INSERT INTO order_master(user_id, total_amount, status, create_time)
                                VALUES(#{userId}, #{totalAmount}, 'pending', NOW())
                            """, orderData);

                            // 创建订单明细
                            orderData.items.each(item => {
                                db.insert("""
                                    INSERT INTO order_item(order_id, product_id, quantity, price, amount)
                                    VALUES(#{orderId}, #{productId}, #{quantity}, #{price}, #{amount})
                                """, {
                                    orderId: orderId,
                                    productId: item.productId,
                                    quantity: item.quantity,
                                    price: item.price,
                                    amount: item.quantity * item.price
                                });

                                // 扣减库存
                                db.update("""
                                    UPDATE product
                                    SET stock = stock - #{quantity}
                                    WHERE id = #{productId} AND stock >= #{quantity}
                                """, item);
                            });

                            return orderId;
                        });
                    };

                    // 调用业务方法
                    try {
                        var orderId = createOrder(body);
                        return response.json({
                            success: true,
                            message: '订单创建成功',
                            data: {orderId: orderId}
                        });
                    } catch(e) {
                        return response.json({
                            success: false,
                            message: '订单创建失败: ' + e
                        });
                    }
                ''').strip(),
                "tags": ["嵌套事务", "业务封装", "库存管理"]
            }
        }
    },
    "lambda_operations": {
        "title": "Lambda操作",
        "description": "函数式编程操作示例",
        "examples": {
            "data_transformation": {
                "title": "数据转换",
                "description": "使用map进行数据结构转换",
                "code": textwrap.dedent('''
                    import response;

                    // 查询原始数据
                    var users = db.select("""
                        SELECT id, user_name, phone, email, create_time, status
                        FROM sys_user
                        WHERE status = 1
                    """);

                    // 数据转换：格式化时间，转换状态
                    var result = users.map(user => ({
                        id: user.id,
                        userName: user.user_name,
                        phone: user.phone,
                        email: user.email,
                        status: user.status == 1 ? '正常' : '禁用',
                        createTime: user.create_time.format('yyyy-MM-dd HH:mm:ss'),
                        // 计算注册天数
                        daysSinceRegister: (new Date().getTime() - user.create_time.getTime()) / (1000 * 60 * 60 * 24)
                    }));

                    return response.json({
                        success: true,
                        data: result
                    });
                ''').strip(),
                "tags": ["数据转换", "map", "格式化"]
            },
            "data_filtering": {
                "title": "数据筛选",
                "description": "使用filter进行数据筛选",
                "code": textwrap.dedent('''
                    import response;

                    var users = db.select("SELECT * FROM sys_user");

                    // 多条件筛选
                    var filteredUsers = users.filter(user => {
                        // 状态正常的用户
                        if(user.status != 1) return false;

                        // 有邮箱的用户
                        if(!user.email) return false;

                        // 手机号以138开头的用户
                        if(!user.phone || !user.phone.startsWith('138')) return false;

                        // 注册时间在最近30天的用户
                        var thirtyDaysAgo = new Date();
                        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
                        if(user.create_time < thirtyDaysAgo) return false;

                        return true;
                    }).map(user => ({
                        id: user.id,
                        userName: user.user_name,
                        phone: user.phone,
                        email: user.email
                    }));

                    return response.json({
                        success: true,
                        data: filteredUsers,
                        total: filteredUsers.size()
                    });
                ''').strip(),
                "tags": ["数据筛选", "filter", "多条件"]
            },
            "data_grouping": {
                "title": "数据分组",
                "description": "使用group进行数据分组统计",
                "code": textwrap.dedent('''
                    import response;

                    var orders = db.select("""
                        SELECT u.user_name, u.phone,
                               o.total_amount, o.create_time,
                               DATE_FORMAT(o.create_time, '%Y-%m') as month
                        FROM sys_user u
                        JOIN order_master o ON u.id = o.user_id
                        WHERE o.create_time >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                    """);

                    // 按月分组统计
                    var monthlyStats = orders.group(order => order.month, list => ({
                        month: list[0].month,
                        orderCount: list.size(),
                        totalAmount: list.sum(item => item.total_amount),
                        avgAmount: list.avg(item => item.total_amount),
                        users: list.distinct(item => item.user_name).size()
                    }));

                    // 按用户分组统计
                    var userStats = orders.group(order => order.user_name, list => ({
                        userName: list[0].user_name,
                        phone: list[0].phone,
                        orderCount: list.size(),
                        totalAmount: list.sum(item => item.total_amount),
                        lastOrderTime: list.max(item => item.create_time).format('yyyy-MM-dd HH:mm:ss')
                    }));

                    return response.json({
                        success: true,
                        data: {
                            monthlyStats: monthlyStats.values().sort((a,b) => a.month > b.month ? -1 : 1),
                            userStats: userStats.values().sort((a,b) => b.totalAmount - a.totalAmount)
                        }
                    });
                ''').strip(),
                "tags": ["数据分组", "统计", "聚合"]
            },
            "data_join": {
                "title": "数据关联",
                "description": "使用join进行数据关联操作",
                "code": textwrap.dedent('''
                    import response;

                    // 用户数据
                    var users = db.select("""
                        SELECT id, user_name, phone, create_time
                        FROM sys_user
                        WHERE status = 1
                    """);

                    // 订单数据
                    var orders = db.select("""
                        SELECT user_id, COUNT(*) as order_count,
                               SUM(total_amount) as total_amount,
                               MAX(create_time) as last_order_time
                        FROM order_master
                        WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                        GROUP BY user_id
                    """);

                    // 关联查询：用户及其最近30天订单统计
                    var result = users.join(orders,
                        (user, order) => user.id == order.user_id,
                        (user, order) => ({
                            id: user.id,
                            userName: user.user_name,
                            phone: user.phone,
                            registerTime: user.create_time.format('yyyy-MM-dd'),
                            orderCount: order ? order.order_count : 0,
                            totalAmount: order ? order.total_amount : 0,
                            lastOrderTime: order ? order.last_order_time.format('yyyy-MM-dd HH:mm:ss') : null
                        })
                    );

                    // 按订单金额降序排序
                    result = result.sort((a,b) => b.totalAmount - a.totalAmount);

                    return response.json({
                        success: true,
                        data: result
                    });
                ''').strip(),
                "tags": ["数据关联", "join", "统计"]
            }
        }
    },
    "async_operations": {
        "title": "异步操作",
        "description": "异步编程示例",
        "examples": {
            "parallel_queries": {
                "title": "并行查询",
                "description": "同时执行多个数据库查询",
                "code": textwrap.dedent('''
                    import response;

                    // 并行查询用户信息和订单信息
                    var userQuery = async db.select("""
                        SELECT id, user_name, phone, email
                        FROM sys_user
                        WHERE id = #{userId}
                    """, {userId: params.userId});

                    var orderQuery = async db.select("""
                        SELECT id, total_amount, status, create_time
                        FROM order_master
                        WHERE user_id = #{userId}
                        ORDER BY create_time DESC
                        LIMIT 10
                    """, {userId: params.userId});

                    var addressQuery = async db.select("""
                        SELECT id, receiver_name, phone, address, is_default
                        FROM user_address
                        WHERE user_id = #{userId}
                    """, {userId: params.userId});

                    // 等待所有查询完成
                    var user = userQuery.get();
                    var orders = orderQuery.get();
                    var addresses = addressQuery.get();

                    if(!user || user.isEmpty()){
                        exit 404, '用户不存在';
                    }

                    return response.json({
                        success: true,
                        data: {
                            user: user[0],
                            orders: orders,
                            addresses: addresses
                        }
                    });
                ''').strip(),
                "tags": ["异步", "并行查询", "性能优化"]
            },
            "batch_processing": {
                "title": "批量异步处理",
                "description": "批量异步处理大量数据",
                "code": textwrap.dedent('''
                    import response;

                    // 查询需要处理的订单
                    var pendingOrders = db.select("""
                        SELECT id, user_id, total_amount
                        FROM order_master
                        WHERE status = 'pending' AND create_time < DATE_SUB(NOW(), INTERVAL 1 HOUR)
                        LIMIT 100
                    """);

                    if(pendingOrders.isEmpty()){
                        return response.json({
                            success: true,
                            message: '暂无待处理订单'
                        });
                    }

                    // 异步批量处理订单
                    var processTasks = pendingOrders.map(order => {
                        return async (order) => {
                            try {
                                // 检查库存（模拟业务处理）
                                var hasStock = db.selectInt("""
                                    SELECT COUNT(*) FROM order_item oi
                                    JOIN product p ON oi.product_id = p.id
                                    WHERE oi.order_id = #{orderId} AND p.stock >= oi.quantity
                                """, {orderId: order.id});

                                if(hasStock == 0){
                                    // 更新订单状态为失败
                                    db.update("""
                                        UPDATE order_master
                                        SET status = 'failed', fail_reason = '库存不足'
                                        WHERE id = #{orderId}
                                    """, {orderId: order.id});

                                    return {orderId: order.id, success: false, reason: '库存不足'};
                                } else {
                                    // 更新订单状态为成功
                                    db.update("""
                                        UPDATE order_master SET status = 'paid'
                                        WHERE id = #{orderId}
                                    """, {orderId: order.id});

                                    return {orderId: order.id, success: true};
                                }
                            } catch(e) {
                                return {orderId: order.id, success: false, reason: e.toString()};
                            }
                        };
                    });

                    // 等待所有任务完成
                    var results = processTasks.map(task => task.get());

                    var successCount = results.filter(r => r.success).size();
                    var failCount = results.filter(r => !r.success).size();

                    return response.json({
                        success: true,
                        message: `处理完成：成功${successCount}个，失败${failCount}个`,
                        data: {
                            total: results.size(),
                            success: successCount,
                            failed: failCount,
                            details: results
                        }
                    });
                ''').strip(),
                "tags": ["异步", "批量处理", "订单处理"]
            }
        }
    },
    "file_operations": {
        "title": "文件操作",
        "description": "文件上传下载处理示例",
        "examples": {
            "file_upload": {
                "title": "文件上传",
                "description": "处理用户头像上传",
                "code": textwrap.dedent('''
                    import response;

                    // 获取上传的文件
                    var avatarFile = request.getFile('avatar');
                    if(!avatarFile){
                        exit 400, '请上传头像文件';
                    }

                    // 校验文件类型
                    var allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
                    if(allowedTypes.indexOf(avatarFile.getContentType()) == -1){
                        exit 400, '只支持JPG、PNG、GIF格式的图片';
                    }

                    // 校验文件大小（最大5MB）
                    if(avatarFile.getSize() > 5 * 1024 * 1024){
                        exit 400, '文件大小不能超过5MB';
                    }

                    // 生成文件名
                    var fileName = params.userId + '_' + current_timestamp() + '_' +
                                  avatarFile.getOriginalFilename();

                    // 保存文件信息到数据库
                    var fileId = db.insert("""
                        INSERT INTO user_file(user_id, file_name, file_size, file_type, upload_time)
                        VALUES(#{userId}, #{fileName}, #{fileSize}, #{fileType}, NOW())
                    """, {
                        userId: params.userId,
                        fileName: fileName,
                        fileSize: avatarFile.getSize(),
                        fileType: avatarFile.getContentType()
                    });

                    // TODO: 实际保存文件到磁盘或云存储
                    // saveFileToDisk(avatarFile, fileName);

                    return response.json({
                        success: true,
                        message: '头像上传成功',
                        data: {
                            fileId: fileId,
                            fileName: fileName
                        }
                    });
                ''').strip(),
                "tags": ["文件上传", "校验", "头像"]
            },
            "file_download": {
                "title": "文件下载",
                "description": "下载用户文件",
                "code": textwrap.dedent('''
                    // 查询文件信息
                    var fileInfo = db.selectOne("""
                        SELECT file_name, file_path, file_type
                        FROM user_file
                        WHERE id = #{fileId} AND user_id = #{userId}
                    """, params);

                    if(!fileInfo){
                        exit 404, '文件不存在或无权限访问';
                    }

                    // TODO: 从磁盘或云存储读取文件内容
                    // var fileContent = readFileFromDisk(fileInfo.file_path);

                    // 模拟文件内容
                    var fileContent = '这是文件内容示例';

                    // 设置响应头并返回文件
                    response.setHeader('Content-Disposition',
                        'attachment; filename="' + fileInfo.file_name + '"');
                    response.setHeader('Content-Type', fileInfo.file_type ? fileInfo.file_type : 'application/octet-stream');

                    return response.download(fileContent, fileInfo.file_name);
                ''').strip(),
                "tags": ["文件下载", "权限校验"]
            }
        }
    },
    "spring_integration": {
        "title": "Spring框架集成",
        "description": "使用Spring Boot各种功能的集成示例",
        "examples": {
            "dependency_injection": {
                "title": "依赖注入 - 使用Spring Bean",
                "description": "在Magic-API脚本中注入和使用Spring管理的Bean",
                "code": textwrap.dedent('''
                    import response;
                    import 'com.example.service.UserService' as userService;
                    import 'com.example.mapper.UserMapper' as userMapper;

                    // 使用注入的Service
                    var user = userService.getUserById(params.userId);
                    if(!user){
                        exit 404, '用户不存在';
                    }

                    // 使用注入的Mapper
                    var userDetails = userMapper.selectUserWithRoles(params.userId);

                    return response.json({
                        success: true,
                        data: {
                            user: user,
                            details: userDetails
                        }
                    });
                ''').strip(),
                "tags": ["Spring", "依赖注入", "Bean", "Service"]
            },
            "configuration_usage": {
                "title": "配置管理 - 读取应用配置",
                "description": "使用env模块读取Spring Boot配置属性",
                "code": textwrap.dedent('''
                    import response;
                    import env;

                    // 读取基础配置
                    var appName = env.get('spring.application.name', 'Magic-API');
                    var serverPort = env.get('server.port', '9999');
                    var activeProfile = env.get('spring.profiles.active', 'default');

                    // 读取业务配置
                    var apiVersion = env.get('api.version', 'v1.0');
                    var enableCache = env.get('feature.cache.enabled', 'false') == 'true';
                    var maxRetries = env.get('api.retry.max-attempts', '3');

                    // 读取数据库配置
                    var dbConfig = {
                        url: env.get('spring.datasource.url'),
                        username: env.get('spring.datasource.username'),
                        maxPoolSize: env.get('spring.datasource.hikari.maximum-pool-size', '10')
                    };

                    return response.json({
                        success: true,
                        config: {
                            appName: appName,
                            serverPort: serverPort,
                            activeProfile: activeProfile,
                            apiVersion: apiVersion,
                            enableCache: enableCache,
                            maxRetries: maxRetries,
                            database: dbConfig
                        }
                    });
                ''').strip(),
                "tags": ["Spring", "配置", "env", "application.yml"]
            }
        }
    },
    "custom_results": {
        "title": "自定义结果处理",
        "description": "自定义API响应结果的各种处理方式",
        "examples": {
            "mock_pagination": {
                "title": "模拟分页响应",
                "description": "使用response.page()返回标准的分页响应格式",
                "code": textwrap.dedent('''
                    import response;

                    // 模拟总记录数和当前页数据
                    var total = 5;  // 总共有多少条数据
                    var list = [1, 2];   // 当前页的数据项

                    // 返回标准分页格式
                    return response.page(total, list);
                    ''').strip(),
                "tags": ["分页", "response", "模拟数据"]
            },
            "generate_captcha": {
                "title": "生成图片验证码",
                "description": "使用Java AWT生成动态图片验证码",
                "code": textwrap.dedent('''
                    import 'java.awt.image.BufferedImage' as BufferedImage;
                    import 'java.awt.Color' as Color;
                    import 'java.awt.Font' as Font;
                    import 'java.io.ByteArrayOutputStream' as ByteArrayOutputStream;
                    import 'java.util.Random' as Random;
                    import 'javax.imageio.ImageIO' as ImageIO;
                    import response;
                    import log;

                    // 创建图片画布
                    var width = 200;
                    var height = 69;
                    var image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
                    var graphics = image.getGraphics();

                    // 设置背景色
                    graphics.setColor(Color.WHITE);
                    graphics.fillRect(0, 0, width, height);

                    // 设置字体
                    graphics.setFont(new Font("微软雅黑", Font.BOLD, 40));

                    // 字符集
                    var letter = '123456789abcdefghijklmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ';
                    var random = new Random();

                    // 随机颜色生成函数
                    var randomColor = () => new Color(
                        random.nextInt(256),
                        random.nextInt(256),
                        random.nextInt(256)
                    );

                    // 生成验证码字符
                    var x = 10;
                    var code = '';
                    for (i in range(0, 3)) { // 生成3位验证码
                        graphics.setColor(randomColor());
                        var degree = random.nextInt() % 30;
                        var ch = letter.charAt(random.nextInt(letter.length()));
                        code = code + ch;

                        // 旋转文字
                        graphics.rotate(degree * 3.1415926535 / 180, x, 45);
                        graphics.drawString(ch + '', x, 45);
                        graphics.rotate(-degree * 3.1415926535 / 180, x, 45);
                        x = x + 48;
                    }

                    log.info('生成的验证码:{}', code);

                    // 添加干扰线
                    for (i in range(0, 6)) {
                        graphics.setColor(randomColor());
                        graphics.drawLine(
                            random.nextInt(width), random.nextInt(height),
                            random.nextInt(width), random.nextInt(height)
                        );
                    }

                    // 添加噪点
                    for (i in range(0, 30)) {
                        graphics.setColor(randomColor());
                        graphics.fillRect(random.nextInt(width), random.nextInt(height), 2, 2);
                    }

                    graphics.dispose();

                    // 输出图片
                    var baos = new ByteArrayOutputStream();
                    ImageIO.write(image, "png", baos);
                    baos.flush();
                    baos.close();

                    return response.image(baos.toByteArray(), 'image/png');
                    ''').strip(),
                "tags": ["验证码", "图片生成", "AWT", "安全"]
            },
            "file_download": {
                "title": "文件下载处理",
                "description": "处理文件下载请求并返回文件流",
                "code": textwrap.dedent('''
                    import response;

                    // 方式1：直接返回文本内容下载
                    // return response.download('中文测试', 'str.txt');

                    // 方式2：使用OutputStream自定义响应
                    response.getOutputStream().write("Internal Server Error: Something went wrong!".getBytes());

                    // 设置响应头
                    response.setHeader("Status", "200");

                    // 记录日志
                    log.info("文件下载请求处理完成");

                    // 结束响应
                    return response.end();
                    ''').strip(),
                "tags": ["文件下载", "OutputStream", "响应头"]
            },
            "custom_json_response": {
                "title": "自定义JSON响应",
                "description": "使用response.json()返回自定义格式的JSON响应",
                "code": textwrap.dedent('''
                    import response;

                    // 注意：这种方式仅适合临时输出的格式
                    // 如果需要全局统一JSON结果，请参考文档配置

                    return response.json({
                        success: true,
                        message: '执行成功',
                        timestamp: new Date().getTime(),
                        version: '1.0.0'
                    });
                    ''').strip(),
                "tags": ["JSON响应", "自定义格式", "response"]
            },
            "generate_images": {
                "title": "动态图片生成",
                "description": "使用Java AWT生成各种类型的图片（验证码、分形图、数学图形）",
                "code": textwrap.dedent('''
                    // 方式1：简单验证码生成
                    import 'java.awt.image.BufferedImage' as BufferedImage;
                    import 'java.awt.Color' as Color;
                    import 'java.awt.Font' as Font;
                    import 'java.awt.Graphics2D' as Graphics2D;
                    import 'java.io.ByteArrayOutputStream' as ByteArrayOutputStream;
                    import 'java.util.Random' as Random;
                    import 'javax.imageio.ImageIO' as ImageIO;
                    import response;

                    var width = 120;
                    var height = 40;
                    var codeLength = 4;

                    var image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
                    var graphics = image.createGraphics() as Graphics2D;

                    graphics.setColor(Color.WHITE);
                    graphics.fillRect(0, 0, width, height);

                    graphics.setFont(new Font("Arial", Font.BOLD, 25));

                    var random = new Random();
                    var characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
                    var code = "";

                    for (i in range(0, codeLength)) {{
                        var character = characters.charAt(random.nextInt(characters.length()));
                        code += character;
                        graphics.setColor(new Color(random.nextInt(256), random.nextInt(256), random.nextInt(256)));
                        graphics.drawString(character + "", i * 30 + 10, 25);
                    }}

                    graphics.dispose();

                    var baos = new ByteArrayOutputStream();
                    ImageIO.write(image, "png", baos);
                    baos.flush();
                    baos.close();

                    return response.image(baos.toByteArray(), 'image/png');

                    // 方式2：分形树生成
                    var width = 800;
                    var height = 600;

                    var image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
                    var graphics = image.createGraphics() as Graphics2D;

                    graphics.setColor(Color.WHITE);
                    graphics.fillRect(0, 0, width, height);

                    graphics.setColor(Color.BLACK);

                    // 分形树递归函数
                    var drawFractalTree = (x1, y1, angle, depth) => {{
                        if (depth === 0) {{
                            return;
                        }}

                        var x2 = x1 + (Math.cos(angle) * depth * 10.0);
                        var y2 = y1 + (Math.sin(angle) * depth * 10.0);

                        graphics.drawLine(x1::int, y1::int, x2::int, y2::int);

                        drawFractalTree(x2, y2, angle - 0.3, depth - 1);
                        drawFractalTree(x2, y2, angle + 0.3, depth - 1);
                    }}

                    drawFractalTree(width / 2, height - 50, -Math.PI / 2, 8);

                    graphics.dispose();

                    var baos = new ByteArrayOutputStream();
                    ImageIO.write(image, "png", baos);
                    baos.flush();
                    baos.close();

                    return response.image(baos.toByteArray(), 'image/png');

                    // 方式3：Mandelbrot集生成
                    var width = 800;
                    var height = 500;
                    var maxIter = 100;
                    var zoom = 200;
                    var moveX = 0.5;
                    var moveY = 0;

                    var image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);

                    // 计算每个像素点的Mandelbrot集归属
                    for(x in range(0, width-1)) {{
                        for(y in range(0, height-1)) {{
                            var zx = 0.0;
                            var zy = 0.0;
                            var cX = (x - width/2.0) / zoom - moveX;
                            var cY = (y - height/2.0) / zoom - moveY;
                            var iter = maxIter;

                            while(zx * zx + zy * zy < 4.0 && iter > 0) {{
                                var tmp = zx * zx - zy * zy + cX;
                                zy = 2.0 * zx * zy + cY;
                                zx = tmp;
                                iter = iter - 1;
                            }}

                            try {{
                                if(iter > 0) {{
                                    // 使用HSB颜色模型创建渐变色
                                    var hue = (iter % 100) / 120.0;
                                    var saturation = 0.6622;
                                    var brightness = 1.0;
                                    var rgb = Color.HSBtoRGB(hue::float, saturation::float, brightness::float);
                                    image.setRGB(x, y, rgb);
                                }} else {{
                                    // Mandelbrot集内部点为黑色
                                    image.setRGB(x, y, Color.BLACK.getRGB());
                                }}
                            }} catch(e) {{
                                image.setRGB(x, y, Color.BLACK.getRGB());
                            }}
                        }}
                    }}

                    var baos = new ByteArrayOutputStream();
                    ImageIO.write(image, "png", baos);
                    baos.flush();
                    var imageBytes = baos.toByteArray();
                    baos.close();

                    return response.image(imageBytes, 'image/png');
                    ''').strip(),
                "tags": ["图片生成", "验证码", "分形图", "数学图形", "AWT", "Graphics2D"]
            }
        }
    },
    "advanced_operations": {
        "title": "高级操作",
        "description": "Magic-API的高级功能和操作示例",
        "examples": {
            "call_function": {
                "title": "调用自定义函数",
                "description": "在API中调用其他Magic-API函数",
                "code": textwrap.dedent('''
                    // 导入自定义函数
                    import '@/test/add' as add;
                    import '@/test/nested' as nested;

                    // 调用函数并返回结果
                    return {
                        'add': add(1, 2),           // 调用加法函数
                        'nested': nested()          // 调用嵌套函数
                    };
                    ''').strip(),
                "tags": ["函数调用", "模块化", "代码复用"]
            },
            "call_other_api": {
                "title": "调用其他接口",
                "description": "在当前API中调用其他Magic-API接口",
                "code": textwrap.dedent('''
                    // 导入其他接口（通过路径）
                    import '@get:/base/module/assert' as test;

                    // 准备参数
                    var id = '1';
                    var message = 'hello';

                    // 调用接口
                    return test();
                    ''').strip(),
                "tags": ["接口调用", "内部调用", "API组合"]
            },
            "use_spring_bean": {
                "title": "使用Spring Bean",
                "description": "在Magic-API脚本中注入和使用Spring容器中的Bean",
                "code": textwrap.dedent('''
                    // 导入Spring环境对象
                    import 'org.springframework.core.env.Environment' as env;

                    // 返回Spring Environment对象
                    // 可以通过env.getProperty('key')等方式获取配置
                    return env;
                    ''').strip(),
                "tags": ["Spring", "依赖注入", "Environment", "配置"]
            },
            "number_conversion": {
                "title": "数值类型转换",
                "description": "使用Magic-API提供的数值转换和处理方法",
                "code": textwrap.dedent('''
                    return {
                        'fixed': 123.455.toFixed(2),    // 仿JS toFixed，返回字符串
                        'round': 123.452.round(2),      // 四舍五入保留小数
                        'percent': 0.456789.asPercent(2), // 转为百分比
                        'ceil': 1.1.ceil(),              // 向上取整
                        'floor': 1.9.floor(),            // 向下取整
                        'toInt': '-456.789'::int         // 强制类型转换
                    };
                    ''').strip(),
                "tags": ["数值转换", "数学运算", "类型转换"]
            },
            "json_conversion": {
                "title": "JSON转换操作",
                "description": "对象与JSON字符串之间的转换",
                "code": textwrap.dedent('''
                    // 定义JavaScript对象
                    var json = {
                        "name": "李富贵"
                    };

                    // 定义JSON字符串
                    var jsonString = '{"name": "李富贵"}';

                    return {
                        'jsonObject': jsonString::json,    // 字符串转对象
                        'jsonString': json::stringify      // 对象转字符串
                    };
                    ''').strip(),
                "tags": ["JSON转换", "对象转换", "序列化"]
            }
        }
    },
    "module_examples": {
        "title": "内置模块使用示例",
        "description": "Magic-API内置模块的详细使用示例和最佳实践",
        "examples": {
            "http_module": {
                "title": "HTTP模块使用",
                "description": "使用http模块进行HTTP请求调用",
                "code": textwrap.dedent('''
                    import http;

                    // 相关文档： https://www.ssssssss.org/magic-api/pages/module/http/

                    // 基本GET请求
                    var response = http.connect('http://127.0.0.1:10712/magic/web/index.html')
                        .get();

                    return response.getBody();

                    // 完整的HTTP请求示例
                    var result = http.connect('https://api.example.com/users')
                        .header('Authorization', 'Bearer ' + token)
                        .header('Content-Type', 'application/json')
                        .param('page', 1)
                        .param('size', 10)
                        .timeout(5000)  // 设置超时时间
                        .get()          // 执行GET请求
                        .getBody();     // 获取响应体

                    return JSON.parse(result);
                    ''').strip(),
                "tags": ["HTTP", "网络请求", "API调用", "超时设置"]
            },
            "log_module": {
                "title": "日志模块使用",
                "description": "使用log模块进行日志记录和调试",
                "code": textwrap.dedent('''
                    import log;

                    // 相关文档： https://www.ssssssss.org/magic-api/pages/module/log/

                    // 不同级别的日志记录
                    var message = params.message || 'magic-api';

                    // 信息日志
                    log.info('info日志:{}', message);

                    // 警告日志
                    log.warn('warn日志: 这是一个警告信息');

                    // 尝试执行可能出错的操作
                    try {
                        // 模拟一些操作
                        if(params.testError) {
                            throw new Error('测试错误');
                        }

                        // 执行成功
                        log.info('操作执行成功');
                        return 'ok';

                    } catch(e) {
                        // 错误日志，包含异常信息
                        log.error('error日志: 操作失败', e);

                        // 可以返回错误信息，但不影响日志记录
                        return {
                            success: false,
                            error: e.message
                        };
                    }
                    ''').strip(),
                "tags": ["日志", "调试", "异常处理", "监控"]
            },
            "request_module": {
                "title": "请求模块使用",
                "description": "使用request模块获取请求信息和参数",
                "code": textwrap.dedent('''
                    import request;

                    // 相关文档： https://www.ssssssss.org/magic-api/pages/module/request/

                    // 获取请求头信息
                    var hostHeaders = request.getHeaders("Host");
                    var userAgent = request.getHeaders("User-Agent");
                    var authToken = request.getHeaders("Authorization");

                    // 获取客户端IP地址
                    var clientIP = request.getClientIP();

                    // 获取上传的文件
                    var avatarFile = request.getFile('avatar');
                    var attachments = request.getFiles('files');

                    // 获取数组参数
                    var tags = request.getValues('tags');

                    // 获取请求对象进行更复杂的操作
                    var req = request.get();
                    var method = req.getMethod();
                    var uri = req.getRequestURI();
                    var queryString = req.getQueryString();

                    return {
                        headers: {
                            host: hostHeaders,
                            userAgent: userAgent ? userAgent[0] : null
                        },
                        client: {
                            ip: clientIP
                        },
                        request: {
                            method: method,
                            uri: uri,
                            queryString: queryString
                        },
                        files: {
                            avatar: avatarFile ? avatarFile.getOriginalFilename() : null,
                            attachmentsCount: attachments ? attachments.size() : 0
                        },
                        params: {
                            tags: tags
                        }
                    };
                    ''').strip(),
                "tags": ["请求", "HTTP头", "文件上传", "客户端信息"]
            },
            "response_module": {
                "title": "响应模块使用",
                "description": "使用response模块构造各种类型的响应",
                "code": textwrap.dedent('''
                    import response;

                    // 相关文档： https://www.ssssssss.org/magic-api/pages/module/response/

                    // 方式1：返回自定义JSON（推荐）
                    return response.json({
                        ok: true,
                        message: '操作成功',
                        timestamp: new Date().getTime()
                    });

                    // 方式2：返回纯文本
                    // return response.text('操作成功');

                    // 方式3：返回分页数据
                    // return response.page(totalCount, dataList);

                    // 方式4：重定向
                    // return response.redirect('/login');

                    // 方式5：文件下载
                    // return response.download(fileContent, 'filename.txt');

                    // 方式6：图片输出
                    // return response.image(imageBytes, 'image/png');

                    // 高级用法：自定义响应头
                    response.addHeader('X-API-Version', '1.0.0');
                    response.addHeader('X-Request-ID', 'req_' + new Date().getTime());

                    // 设置Cookie
                    response.addCookie('sessionId', 'abc123', {
                        maxAge: 3600,      // 1小时过期
                        httpOnly: true,    // 仅HTTP访问
                        secure: true       // HTTPS only
                    });

                    return response.json({
                        success: true,
                        message: '响应处理完成'
                    });
                    ''').strip(),
                "tags": ["响应", "JSON", "分页", "重定向", "文件下载", "Cookie"]
            },
            "env_module": {
                "title": "环境变量模块使用",
                "description": "使用env模块读取Spring Boot配置和环境变量",
                "code": textwrap.dedent('''
                    import env;

                    // 相关文档： https://www.ssssssss.org/magic-api/pages/module/env/

                    // 获取基础配置
                    var serverPort = env.get('server.port', '8080');
                    var appName = env.get('spring.application.name', 'Magic-API');
                    var activeProfile = env.get('spring.profiles.active', 'default');

                    // 获取数据库配置
                    var dbConfig = {
                        url: env.get('spring.datasource.url'),
                        username: env.get('spring.datasource.username'),
                        password: env.get('spring.datasource.password'),
                        driver: env.get('spring.datasource.driver-class-name')
                    };

                    // 获取缓存配置
                    var cacheConfig = {
                        enabled: env.get('spring.cache.enabled', 'true') == 'true',
                        type: env.get('spring.cache.type', 'caffeine')
                    };

                    // 获取自定义配置
                    var apiConfig = {
                        version: env.get('api.version', '1.0.0'),
                        timeout: env.get('api.timeout', '30000'),
                        rateLimit: env.get('api.rate-limit.enabled', 'false') == 'true'
                    };

                    // 获取系统环境变量
                    var systemConfig = {
                        javaVersion: env.get('java.version'),
                        osName: env.get('os.name'),
                        userHome: env.get('user.home')
                    };

                    return {
                        application: {
                            name: appName,
                            port: serverPort,
                            profile: activeProfile
                        },
                        database: dbConfig,
                        cache: cacheConfig,
                        api: apiConfig,
                        system: systemConfig
                    };
                    ''').strip(),
                "tags": ["环境变量", "配置", "Spring Boot", "系统属性"]
            },
            "magic_module": {
                "title": "Magic模块使用",
                "description": "使用magic模块在API间进行调用",
                "code": textwrap.dedent('''
                    import magic;

                    // 调用其他API接口
                    var userResult = magic.call('GET', '/api/user/info', {
                        userId: params.userId
                    });

                    // 调用函数
                    var encryptResult = magic.invoke('/common/encrypt', {
                        data: params.data,
                        algorithm: 'AES'
                    });

                    // 异步调用多个接口
                    var userData = async magic.call('GET', '/api/user/profile', {id: params.userId});
                    var permissions = async magic.call('GET', '/api/user/permissions', {id: params.userId});

                    // 等待所有调用完成
                    var userInfo = userData.get();
                    var userPermissions = permissions.get();

                    // 组合结果
                    return {
                        user: userInfo.data,
                        permissions: userPermissions.data,
                        encrypt: encryptResult
                    };
                    ''').strip(),
                "tags": ["API调用", "函数调用", "内部调用", "异步"]
            }
        }
    },
    "plugin_examples": {
        "title": "插件使用示例",
        "description": "Magic-API各种插件的功能使用示例",
        "examples": {
            "redis_get": {
                "title": "Redis数据读取",
                "description": "使用Redis插件读取缓存数据",
                "code": textwrap.dedent('''
                    import redis;

                    // 文档：https://www.ssssssss.org/magic-api/pages/plugin/redis/

                    // 读取字符串数据
                    var data = redis.get('magic-api:test');

                    return response.json({
                        success: true,
                        data: data,
                        message: data ? '数据获取成功' : '数据不存在'
                    });
                    ''').strip(),
                "tags": ["Redis", "缓存", "数据读取", "插件"]
            },
            "redis_set": {
                "title": "Redis数据存储",
                "description": "使用Redis插件存储数据并设置过期时间",
                "code": textwrap.dedent('''
                    import redis;

                    // 文档：https://www.ssssssss.org/magic-api/pages/plugin/redis/

                    // 存储数据并设置60秒过期时间
                    var result = redis.setex('magic-api:test', 60, 'hello magic-api!');

                    return response.json({
                        success: result == 'OK',
                        message: result == 'OK' ? '数据存储成功' : '存储失败',
                        key: 'magic-api:test',
                        ttl: 60
                    });
                    ''').strip(),
                "tags": ["Redis", "缓存", "数据存储", "过期时间", "插件"]
            },
            "redis_hash": {
                "title": "Redis Hash操作",
                "description": "使用Redis Hash数据结构存储复杂对象",
                "code": textwrap.dedent('''
                    import redis;

                    var userKey = 'user:' + params.userId;

                    // 存储用户信息到Hash
                    redis.hset(userKey, 'name', params.name);
                    redis.hset(userKey, 'email', params.email);
                    redis.hset(userKey, 'loginTime', new Date().getTime());

                    // 设置Hash过期时间
                    redis.expire(userKey, 3600); // 1小时过期

                    // 获取Hash中的所有字段
                    var userData = redis.hgetall(userKey);

                    return response.json({
                        success: true,
                        userId: params.userId,
                        data: userData,
                        ttl: redis.ttl(userKey)
                    });
                    ''').strip(),
                "tags": ["Redis", "Hash", "对象存储", "过期时间"]
            },
            "redis_list": {
                "title": "Redis List操作",
                "description": "使用Redis List实现队列和栈功能",
                "code": textwrap.dedent('''
                    import redis;

                    var queueKey = 'task_queue';

                    // 生产者：添加任务到队列
                    if(params.action == 'produce') {
                        var taskId = redis.lpush(queueKey, JSON.stringify({
                            id: 'task_' + new Date().getTime(),
                            type: params.taskType,
                            data: params.taskData,
                            created: new Date().getTime()
                        }));

                        return response.json({
                            success: true,
                            action: 'produce',
                            queueLength: redis.llen(queueKey),
                            message: '任务已添加到队列'
                        });
                    }

                    // 消费者：从队列获取任务
                    if(params.action == 'consume') {
                        var taskJson = redis.rpop(queueKey);
                        if(taskJson) {
                            var task = JSON.parse(taskJson);
                            return response.json({
                                success: true,
                                action: 'consume',
                                task: task,
                                remainingTasks: redis.llen(queueKey)
                            });
                        } else {
                            return response.json({
                                success: true,
                                action: 'consume',
                                message: '队列为空',
                                remainingTasks: 0
                            });
                        }
                    }

                    // 查看队列状态
                    return response.json({
                        success: true,
                        action: 'status',
                        queueLength: redis.llen(queueKey),
                        queueKey: queueKey
                    });
                    ''').strip(),
                "tags": ["Redis", "List", "队列", "生产者消费者"]
            },
            "redis_pubsub": {
                "title": "Redis发布订阅",
                "description": "使用Redis发布订阅模式进行消息通信",
                "code": textwrap.dedent('''
                    import redis;

                    var channel = 'magic-api:notifications';

                    // 发布消息
                    if(params.action == 'publish') {
                        var message = {
                            type: params.messageType,
                            content: params.content,
                            sender: params.sender || 'system',
                            timestamp: new Date().getTime()
                        };

                        var published = redis.publish(channel, JSON.stringify(message));

                        return response.json({
                            success: published > 0,
                            action: 'publish',
                            channel: channel,
                            subscribers: published,
                            message: message
                        });
                    }

                    // 模拟订阅消息（实际订阅应在后台服务中实现）
                    if(params.action == 'subscribe_status') {
                        return response.json({
                            success: true,
                            action: 'subscribe_status',
                            channel: channel,
                            message: '订阅功能需要在后台服务中实现'
                        });
                    }

                    return response.json({
                        success: false,
                        message: '请指定action参数：publish 或 subscribe_status'
                    });
                    ''').strip(),
                "tags": ["Redis", "发布订阅", "消息队列", "异步通信"]
            },
            "redis_cache": {
                "title": "Redis缓存策略",
                "description": "结合数据库查询的Redis缓存使用模式",
                "code": textwrap.dedent('''
                    import redis;

                    var cacheKey = 'user_list:' + (params.page || 1) + ':' + (params.size || 10);

                    // 尝试从缓存获取
                    var cachedData = redis.get(cacheKey);
                    if(cachedData) {
                        var cacheResult = JSON.parse(cachedData);
                        cacheResult.source = 'cache';
                        return response.json(cacheResult);
                    }

                    // 缓存未命中，从数据库查询
                    var offset = ((params.page || 1) - 1) * (params.size || 10);
                    var size = params.size || 10;

                    var users = db.select("""
                        SELECT id, username, email, status, create_time
                        FROM sys_user
                        ORDER BY create_time DESC
                        LIMIT #{offset}, #{size}
                    """, {offset: offset, size: size});

                    var total = db.selectInt("SELECT COUNT(*) FROM sys_user");

                    var result = {
                        success: true,
                        data: users,
                        total: total,
                        page: params.page || 1,
                        size: size,
                        source: 'database'
                    };

                    // 将结果缓存5分钟
                    redis.setex(cacheKey, 300, JSON.stringify(result));

                    return response.json(result);
                    ''').strip(),
                "tags": ["Redis", "缓存", "数据库", "性能优化"]
            },
            "redis_lock": {
                "title": "Redis分布式锁",
                "description": "使用Redis实现分布式锁，防止并发访问",
                "code": textwrap.dedent('''
                    import redis;

                    var lockKey = 'lock:resource:' + params.resourceId;
                    var lockValue = 'lock_' + new Date().getTime() + '_' + Math.random();
                    var lockTimeout = 30; // 30秒锁超时

                    // 尝试获取锁
                    var lockAcquired = redis.set(lockKey, lockValue, 'NX', 'EX', lockTimeout);

                    if(!lockAcquired) {
                        return response.json({
                            success: false,
                            message: '资源正在被其他请求处理，请稍后重试',
                            resourceId: params.resourceId
                        });
                    }

                    try {
                        // 执行需要同步的操作
                        var result = {};

                        if(params.operation == 'update_balance') {
                            // 更新账户余额
                            result = db.update("""
                                UPDATE account
                                SET balance = balance + #{amount},
                                    update_time = NOW()
                                WHERE id = #{accountId}
                            """, params);
                        }

                        if(params.operation == 'transfer') {
                            // 转账操作
                            result = db.transaction(() => {
                                // 扣减转出账户
                                db.update("UPDATE account SET balance = balance - #{amount} WHERE id = #{fromAccount}", params);
                                // 增加转入账户
                                db.update("UPDATE account SET balance = balance + #{amount} WHERE id = #{toAccount}", params);
                                // 记录转账流水
                                db.insert("INSERT INTO transfer_log(from_account, to_account, amount, create_time) VALUES(#{fromAccount}, #{toAccount}, #{amount}, NOW())", params);
                                return {transferred: true};
                            });
                        }

                        return response.json({
                            success: true,
                            operation: params.operation,
                            result: result,
                            lockValue: lockValue
                        });

                    } finally {
                        // 释放锁（只释放自己持有的锁）
                        var currentValue = redis.get(lockKey);
                        if(currentValue == lockValue) {
                            redis.del(lockKey);
                        }
                    }
                    ''').strip(),
                "tags": ["Redis", "分布式锁", "并发控制", "原子操作"]
            }
        }
    },
    "api_integration": {
        "title": "API集成",
        "description": "调用外部API和内部接口示例",
        "examples": {
            "external_api_call": {
                "title": "外部API调用",
                "description": "调用第三方天气API",
                "code": textwrap.dedent('''
                    import response;
                    import http;

                    // 调用第三方天气API
                    try {
                        var weatherResponse = http.connect('https://api.weather.com/v1/weather')
                            .param('location', params.city ? params.city : 'beijing')
                            .param('apikey', 'your-api-key')
                            .get()
                            .getBody();

                        // 处理响应数据
                        var weatherData = JSON.parse(weatherResponse);

                        return response.json({
                            success: true,
                            data: {
                                city: weatherData.location.name,
                                temperature: weatherData.current.temp_c,
                                condition: weatherData.current.condition.text,
                                humidity: weatherData.current.humidity
                            }
                        });

                    } catch(e) {
                        return response.json({
                            success: false,
                            message: '获取天气信息失败: ' + e
                        });
                    }
                ''').strip(),
                "tags": ["外部API", "HTTP调用", "异常处理"]
            },
            "internal_api_call": {
                "title": "内部接口调用",
                "description": "在接口中调用其他Magic-API接口",
                "code": textwrap.dedent('''
                    import response;
                    import magic;

                    // 调用内部用户查询接口
                    var userResult = magic.call('GET', '/api/user/info', {userId: params.userId});
                    if(!userResult.success){
                        exit userResult.code, userResult.message;
                    }

                    // 调用订单统计接口
                    var orderStats = magic.execute('GET', '/api/order/stats', {
                        userId: params.userId,
                        startDate: params.startDate,
                        endDate: params.endDate
                    });

                    // 调用发送通知的函数
                    var notifyResult = magic.invoke('/common/send-notification', {
                        userId: params.userId,
                        type: 'report_generated',
                        title: '数据报表已生成',
                        content: '您请求的数据报表已生成完成，请查看附件。'
                    });

                    return response.json({
                        success: true,
                        data: {
                            user: userResult.data,
                            orderStats: orderStats,
                            notificationSent: notifyResult
                        }
                    });
                ''').strip(),
                "tags": ["内部调用", "接口复用", "业务流程"]
            }
        }
    }
}

def get_examples(category: str = None) -> Any:
    """获取使用示例。

    Args:
        category: 示例分类，可选值: basic_crud, advanced_queries, transactions, lambda_operations,
                  async_operations, file_operations, api_integration
                  如果不指定则返回所有示例

    Returns:
        指定分类的示例或所有示例
    """
    if category:
        return EXAMPLES_KNOWLEDGE.get(category, {})
    return EXAMPLES_KNOWLEDGE

def list_example_categories() -> List[str]:
    """获取所有示例分类。"""
    return list(EXAMPLES_KNOWLEDGE.keys())

def search_examples(keyword: str, category: str = None) -> List[Dict[str, Any]]:
    """根据关键词搜索示例。

    Args:
        keyword: 搜索关键词
        category: 可选的分类过滤

    Returns:
        匹配的示例列表
    """
    results = []
    keyword_lower = keyword.lower()

    categories_to_search = [category] if category else list(EXAMPLES_KNOWLEDGE.keys())

    for cat in categories_to_search:
        if cat not in EXAMPLES_KNOWLEDGE:
            continue

        category_data = EXAMPLES_KNOWLEDGE[cat]
        if "examples" in category_data:
            for example_key, example_data in category_data["examples"].items():
                # 搜索标题、描述、代码和标签
                searchable_text = (
                    example_data.get("title", "").lower() + " " +
                    example_data.get("description", "").lower() + " " +
                    example_data.get("code", "").lower() + " " +
                    " ".join(example_data.get("tags", [])).lower()
                )

                if keyword_lower in searchable_text:
                    results.append({
                        "category": cat,
                        "key": example_key,
                        **example_data
                    })

    return results

def get_example_by_tags(tags: List[str]) -> List[Dict[str, Any]]:
    """根据标签获取示例。

    Args:
        tags: 标签列表

    Returns:
        包含任一标签的示例列表
    """
    results = []

    for category, category_data in EXAMPLES_KNOWLEDGE.items():
        if "examples" in category_data:
            for example_key, example_data in category_data["examples"].items():
                example_tags = example_data.get("tags", [])
                if any(tag in example_tags for tag in tags):
                    results.append({
                        "category": category,
                        "key": example_key,
                        **example_data
                    })

    return results

__all__ = [
    "EXAMPLES_KNOWLEDGE",
    "get_examples",
    "list_example_categories",
    "search_examples",
    "get_example_by_tags"
]
