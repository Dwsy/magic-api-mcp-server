"""Magic-API 内置函数库知识库。"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, List

# 内置函数库文档
FUNCTIONS_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "aggregation": {
        "title": "聚合函数",
        "description": "提供集合数据的聚合计算功能",
        "functions": {
            "count": {
                "signature": "count(target: Object) -> int",
                "description": "计算集合大小",
                "example": textwrap.dedent('''
                    var list = [1,2,3,4,5]
                    return count(list);  // 5
                ''').strip()
            },
            "sum": {
                "signature": "sum(target: Object) -> Number",
                "description": "对集合进行求和",
                "example": textwrap.dedent('''
                    var list = [1,2,3,4,5]
                    return sum(list);  // 15
                ''').strip()
            },
            "max": {
                "signature": "max(target: Object) -> Object",
                "description": "求集合最大值",
                "example": textwrap.dedent('''
                    var list = [1,2,3,4,5]
                    return max(list);  // 5
                ''').strip()
            },
            "min": {
                "signature": "min(target: Object) -> Object",
                "description": "求集合最小值",
                "example": textwrap.dedent('''
                    var list = [1,2,3,4,5]
                    return min(list);  // 1
                ''').strip()
            },
            "avg": {
                "signature": "avg(target: Object) -> Number",
                "description": "求集合平均值",
                "example": textwrap.dedent('''
                    var list = [1,2,3,4,5]
                    return avg(list);  // 3
                ''').strip()
            },
            "group_concat": {
                "signature": "group_concat(target: Object, separator?: String) -> String",
                "description": "将集合拼接起来",
                "example": textwrap.dedent('''
                    var list = [1,2,3,4,5]
                    return group_concat(list);  // "1,2,3,4,5"
                    return group_concat(list, '|');  // "1|2|3|4|5"
                ''').strip()
            }
        }
    },
    "date": {
        "title": "日期函数",
        "description": "日期时间处理相关函数",
        "functions": {
            "date_format": {
                "signature": "date_format(target: Date, pattern?: String) -> String",
                "description": "日期格式化",
                "example": textwrap.dedent('''
                    return date_format(new Date());  // 2020-01-01 20:30:30
                    return date_format(new Date(),'yyyy-MM-dd');  // 2020-01-01
                ''').strip()
            },
            "now": {
                "signature": "now() -> Date",
                "description": "返回当前日期",
                "example": 'return now(); // 等同于 new Date();'
            },
            "current_timestamp_millis": {
                "signature": "current_timestamp_millis() -> long",
                "description": "取当前时间戳(毫秒)",
                "example": 'return current_timestamp_millis(); // 等同于 System.currentTimeMillis();'
            },
            "current_timestamp": {
                "signature": "current_timestamp() -> long",
                "description": "取当前时间戳(秒)",
                "example": 'return current_timestamp(); // 等同于 current_timestamp_millis() / 1000;'
            }
        }
    },
    "string": {
        "title": "字符串函数",
        "description": "字符串处理相关函数",
        "functions": {
            "uuid": {
                "signature": "uuid() -> String",
                "description": "生成32位无-的UUID",
                "example": 'return uuid(); // 等同于 UUID.randomUUID().toString().replace("-", "");'
            },
            "is_blank": {
                "signature": "is_blank(target: String) -> boolean",
                "description": "判断字符串是否为空",
                "example": 'return is_blank(\'\'); // true'
            },
            "not_blank": {
                "signature": "not_blank(target: String) -> boolean",
                "description": "判断字符串是否不为空",
                "example": 'return not_blank(\'\'); // false'
            }
        }
    },
    "array": {
        "title": "数组函数",
        "description": "数组创建和处理函数",
        "functions": {
            "new_int_array": {
                "signature": "new_int_array(size: int) -> int[]",
                "description": "创建int类型的数组",
                "example": 'return new_int_array(1); // [0]'
            },
            "new_long_array": {
                "signature": "new_long_array(size: int) -> long[]",
                "description": "创建long类型的数组",
                "example": 'return new_long_array(1); // [0]'
            },
            "new_double_array": {
                "signature": "new_double_array(size: int) -> double[]",
                "description": "创建double类型的数组",
                "example": 'return new_double_array(1); // [0.0]'
            },
            "new_float_array": {
                "signature": "new_float_array(size: int) -> float[]",
                "description": "创建float类型的数组",
                "example": 'return new_float_array(1); // [0.0]'
            },
            "new_short_array": {
                "signature": "new_short_array(size: int) -> short[]",
                "description": "创建short类型的数组",
                "example": 'return new_short_array(1); // [0]'
            },
            "new_byte_array": {
                "signature": "new_byte_array(size: int) -> byte[]",
                "description": "创建byte类型的数组",
                "example": 'return new_byte_array(1); // [0]'
            },
            "new_boolean_array": {
                "signature": "new_boolean_array(size: int) -> boolean[]",
                "description": "创建boolean类型的数组",
                "example": 'return new_boolean_array(1); // [false]'
            },
            "new_char_array": {
                "signature": "new_char_array(size: int) -> char[]",
                "description": "创建char类型的数组",
                "example": 'return new_char_array(1); // [0]'
            },
            "new_array": {
                "signature": "new_array(type?: Class, size?: int) -> Object[]",
                "description": "创建Object类型的数组",
                "example": textwrap.dedent('''
                    return new_array(1); // [null] Object类型的数组
                    return new_array(String.class, 1); // [null] String类型的数组
                ''').strip()
            }
        }
    },
    "math": {
        "title": "数学函数",
        "description": "数学计算相关函数",
        "functions": {
            "round": {
                "signature": "round(number: Number, len?: int) -> Number",
                "description": "四舍五入保留N位小数",
                "example": textwrap.dedent('''
                    return round(123.456d, 2);  // 123.46
                    return round(123.456d);     // 123
                ''').strip()
            },
            "floor": {
                "signature": "floor(number: Number) -> Number",
                "description": "向下取整",
                "example": 'return floor(123.456d);  // 123;'
            },
            "ceil": {
                "signature": "ceil(number: Number) -> Number",
                "description": "向上取整",
                "example": 'return ceil(123.456d);  // 124;'
            },
            "percent": {
                "signature": "percent(number: Number, len?: int) -> String",
                "description": "将数值转为百分比",
                "example": textwrap.dedent('''
                    return percent(0.1289999999, 2);  // "12.90%"
                    return percent(0.5);              // "50%"
                ''').strip()
            }
        }
    },
    "other": {
        "title": "其他工具函数",
        "description": "其他实用工具函数",
        "functions": {
            "print": {
                "signature": "print(target: Object) -> void",
                "description": "打印（不换行）",
                "example": 'print(\'abc\'); // 等同于 System.out.print("abc");'
            },
            "println": {
                "signature": "println(target: Object) -> void",
                "description": "打印并换行",
                "example": 'println(\'abc\'); // 等同于 System.out.println("abc");'
            },
            "printf": {
                "signature": "printf(format: String, args...: Object) -> void",
                "description": "按照格式打印并换行",
                "example": 'printf(\'%s:%s\', \'a\',\'b\'); // 等同于 System.out.printf("%s:%S", "a", "b");'
            },
            "not_null": {
                "signature": "not_null(target: Object) -> boolean",
                "description": "判断值不是null",
                "example": 'return not_null(target); // 等同于 target != null'
            },
            "is_null": {
                "signature": "is_null(target: Object) -> boolean",
                "description": "判断值是null",
                "example": 'return is_null(target); // 等同于 target == null'
            },
            "ifnull": {
                "signature": "ifnull(target: Object, trueValue: Object, falseValue?: Object) -> Object",
                "description": "对空值进行判断，返回特定值",
                "example": textwrap.dedent('''
                    return ifnull(null, 1)        // 1
                    return ifnull(0, 1)          // 0
                    return ifnull(null, 'a', 'b') // 'a'
                ''').strip()
            }
        }
    },
    "range": {
        "title": "范围函数",
        "description": "创建数值范围的函数",
        "functions": {
            "range": {
                "signature": "range(start: int, end: int) -> Iterable",
                "description": "创建整数范围（包含起始值，包含结束值）",
                "example": textwrap.dedent('''
                    for(value in range(0, 100)){
                        // 循环从0到100
                    }
                ''').strip()
            }
        }
    }
}

def get_function_docs(category: str = None) -> Any:
    """获取函数文档。

    Args:
        category: 函数分类，可选值: aggregation, date, string, array, math, other, range
                  如果不指定则返回所有分类

    Returns:
        指定分类的函数文档或所有分类文档
    """
    if category:
        return FUNCTIONS_KNOWLEDGE.get(category)
    return FUNCTIONS_KNOWLEDGE

def list_function_categories() -> List[str]:
    """获取所有函数分类。"""
    return list(FUNCTIONS_KNOWLEDGE.keys())

def search_functions(keyword: str) -> List[Dict[str, Any]]:
    """根据关键词搜索函数。

    Args:
        keyword: 搜索关键词

    Returns:
        匹配的函数列表
    """
    results = []
    keyword_lower = keyword.lower()

    for category, category_data in FUNCTIONS_KNOWLEDGE.items():
        if "functions" in category_data:
            for func_name, func_data in category_data["functions"].items():
                if (keyword_lower in func_name.lower() or
                    keyword_lower in func_data.get("description", "").lower()):
                    results.append({
                        "category": category,
                        "name": func_name,
                        **func_data
                    })

    return results

__all__ = [
    "FUNCTIONS_KNOWLEDGE",
    "get_function_docs",
    "list_function_categories",
    "search_functions"
]
