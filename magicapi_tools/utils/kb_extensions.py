"""Magic-API 类型扩展功能知识库。"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, List

# 类型扩展功能文档
EXTENSIONS_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "object": {
        "title": "Object 类型扩展",
        "description": "所有对象类型的通用扩展方法",
        "extensions": {
            "asInt": {
                "signature": "asInt(defaultValue?: int) -> int",
                "description": "转对象为int类型",
                "example": textwrap.dedent('''
                    var obj = '123';
                    return obj.asInt();        // 123
                    return obj.asInt(1);       // 转换失败时返回1
                ''').strip()
            },
            "asDouble": {
                "signature": "asDouble(defaultValue?: double) -> double",
                "description": "转对象为double类型",
                "example": textwrap.dedent('''
                    var obj = '123.45';
                    return obj.asDouble();     // 123.45
                    return obj.asDouble(1.0);  // 转换失败时返回1.0
                ''').strip()
            },
            "asDecimal": {
                "signature": "asDecimal(defaultValue?: BigDecimal) -> BigDecimal",
                "description": "转对象为BigDecimal类型",
                "example": textwrap.dedent('''
                    var obj = '123.456';
                    return obj.asDecimal();           // 123.456
                    return obj.asDecimal(1.5m);       // 转换失败时返回1.5
                ''').strip()
            },
            "asFloat": {
                "signature": "asFloat(defaultValue?: float) -> float",
                "description": "转对象为float类型",
                "example": textwrap.dedent('''
                    var obj = '123.45';
                    return obj.asFloat();       // 123.45
                    return obj.asFloat(1.0f);   // 转换失败时返回1.0
                ''').strip()
            },
            "asLong": {
                "signature": "asLong(defaultValue?: long) -> long",
                "description": "转对象为long类型",
                "example": textwrap.dedent('''
                    var obj = '123';
                    return obj.asLong();        // 123
                    return obj.asLong(1L);      // 转换失败时返回1
                ''').strip()
            },
            "asByte": {
                "signature": "asByte(defaultValue?: byte) -> byte",
                "description": "转对象为byte类型",
                "example": textwrap.dedent('''
                    var obj = '123';
                    return obj.asByte();        // 123
                    return obj.asByte(1b);      // 转换失败时返回1
                ''').strip()
            },
            "asShort": {
                "signature": "asShort(defaultValue?: short) -> short",
                "description": "转对象为short类型",
                "example": textwrap.dedent('''
                    var obj = '123';
                    return obj.asShort();       // 123
                    return obj.asShort(1s);     // 转换失败时返回1
                ''').strip()
            },
            "asDate": {
                "signature": "asDate(formats...: String) -> Date",
                "description": "转对象为Date类型",
                "example": textwrap.dedent('''
                    var obj = '2020-01-01 08:00:00';
                    return obj.asDate('yyyy-MM-dd HH:mm:ss', 'yyyy-MM-dd HH:mm');
                ''').strip()
            },
            "asString": {
                "signature": "asString(defaultValue?: String) -> String",
                "description": "转对象为String类型",
                "example": textwrap.dedent('''
                    var obj = 123;
                    return obj.asString();           // "123"
                    return obj.asString("empty");    // 转换失败时返回"empty"
                ''').strip()
            },
            "is": {
                "signature": "is(type: String|Class) -> boolean",
                "description": "判断是否是指定类型",
                "example": textwrap.dedent('''
                    var str = 'hello';
                    return str.is('string');         // true
                    return str.is('java.lang.String'); // true
                    return str.is('java.lang.Integer'); // false
                ''').strip()
            },
            "isString": {
                "signature": "isString() -> boolean",
                "description": "判断是否是String类型",
                "example": 'return \'hello\'.isString(); // true'
            },
            "isInt": {
                "signature": "isInt() -> boolean",
                "description": "判断是否是int类型",
                "example": 'return 123.isInt(); // true'
            },
            "isLong": {
                "signature": "isLong() -> boolean",
                "description": "判断是否是long类型",
                "example": 'return 123L.isLong(); // true'
            },
            "isDouble": {
                "signature": "isDouble() -> boolean",
                "description": "判断是否是double类型",
                "example": 'return 123d.isDouble(); // true'
            },
            "isFloat": {
                "signature": "isFloat() -> boolean",
                "description": "判断是否是float类型",
                "example": 'return 123f.isFloat(); // true'
            },
            "isByte": {
                "signature": "isByte() -> boolean",
                "description": "判断是否是byte类型",
                "example": 'return 123b.isByte(); // true'
            },
            "isBoolean": {
                "signature": "isBoolean() -> boolean",
                "description": "判断是否是boolean类型",
                "example": 'return false.isBoolean(); // true'
            },
            "isShort": {
                "signature": "isShort() -> boolean",
                "description": "判断是否是short类型",
                "example": 'return 123s.isShort(); // true'
            },
            "isDecimal": {
                "signature": "isDecimal() -> boolean",
                "description": "判断是否是decimal类型",
                "example": 'return 123m.isDecimal(); // true'
            },
            "isDate": {
                "signature": "isDate() -> boolean",
                "description": "判断是否是Date类型",
                "example": textwrap.dedent('''
                    var date = new Date();
                    return date.isDate(); // true
                ''').strip()
            },
            "isArray": {
                "signature": "isArray() -> boolean",
                "description": "判断是否是数组",
                "example": 'return \'123\'.split(\'\').isArray(); // true'
            },
            "isList": {
                "signature": "isList() -> boolean",
                "description": "判断是否是List",
                "example": 'return [1,2,3].isList(); // true'
            },
            "isMap": {
                "signature": "isMap() -> boolean",
                "description": "判断是否是Map",
                "example": 'return {key: \'value\'}.isMap(); // true'
            },
            "isCollection": {
                "signature": "isCollection() -> boolean",
                "description": "判断是否是集合",
                "example": 'return [1,2,3].isCollection(); // true'
            }
        }
    },
    "number": {
        "title": "Number 类型扩展",
        "description": "数值类型的专用扩展方法",
        "extensions": {
            "round": {
                "signature": "round(len: int) -> Number",
                "description": "四舍五入保留N位小数",
                "example": textwrap.dedent('''
                    var value = 123.456d;
                    return value.round(2);  // 123.46
                ''').strip()
            },
            "toFixed": {
                "signature": "toFixed(len: int) -> String",
                "description": "四舍五入保留N位小数(强制限制位数)",
                "example": textwrap.dedent('''
                    var value = 123.456d;
                    return value.toFixed(10);  // "123.4560000000"
                ''').strip()
            },
            "floor": {
                "signature": "floor() -> Number",
                "description": "向下取整",
                "example": textwrap.dedent('''
                    var value = 123.456d;
                    return value.floor();  // 123
                ''').strip()
            },
            "ceil": {
                "signature": "ceil() -> Number",
                "description": "向上取整",
                "example": textwrap.dedent('''
                    var value = 123.456d;
                    return value.ceil();  // 124
                ''').strip()
            },
            "asPercent": {
                "signature": "asPercent(len?: int) -> String",
                "description": "将数值转为百分比",
                "example": textwrap.dedent('''
                    var value = 0.1289999999;
                    return value.asPercent(2);  // "12.90%"
                ''').strip()
            }
        }
    },
    "collection": {
        "title": "集合类型扩展",
        "description": "List、Map等集合类型的扩展方法",
        "extensions": {
            "map": {
                "signature": "map(func: Function) -> List",
                "description": "映射转换每个元素",
                "example": textwrap.dedent('''
                    var list = [{name: '张三', age: 20}, {name: '李四', age: 25}];
                    return list.map(item => item.name);  // ['张三', '李四']
                ''').strip()
            },
            "filter": {
                "signature": "filter(func: Function) -> List",
                "description": "过滤符合条件的元素",
                "example": textwrap.dedent('''
                    var list = [1,2,3,4,5];
                    return list.filter(item => item > 3);  // [4,5]
                ''').strip()
            },
            "each": {
                "signature": "each(func: Function) -> void",
                "description": "遍历每个元素执行函数",
                "example": textwrap.dedent('''
                    var list = [1,2,3];
                    list.each(item => println(item));  // 打印每个元素
                ''').strip()
            },
            "join": {
                "signature": "join(separator?: String) -> String",
                "description": "将集合元素拼接为字符串",
                "example": textwrap.dedent('''
                    var list = [1,2,3];
                    return list.join(',');  // "1,2,3"
                    return list.join();     // "123"
                ''').strip()
            },
            "group": {
                "signature": "group(func: Function, aggFunc?: Function) -> Map",
                "description": "按条件分组",
                "example": textwrap.dedent('''
                    var list = [{type: 'A', value: 1}, {type: 'A', value: 2}, {type: 'B', value: 3}];
                    return list.group(item => item.type);  // 按type分组
                ''').strip()
            },
            "sum": {
                "signature": "sum() -> Number",
                "description": "求和",
                "example": 'return [1,2,3,4,5].sum(); // 15'
            },
            "avg": {
                "signature": "avg() -> Number",
                "description": "求平均值",
                "example": 'return [1,2,3,4,5].avg(); // 3'
            },
            "max": {
                "signature": "max() -> Object",
                "description": "求最大值",
                "example": 'return [1,2,3,4,5].max(); // 5'
            },
            "min": {
                "signature": "min() -> Object",
                "description": "求最小值",
                "example": 'return [1,2,3,4,5].min(); // 1'
            },
            "count": {
                "signature": "count() -> int",
                "description": "计算元素数量",
                "example": 'return [1,2,3,4,5].count(); // 5'
            },
            "shuffle": {
                "signature": "shuffle() -> List",
                "description": "随机打乱顺序",
                "example": 'return [1,2,3,4,5].shuffle(); // 随机顺序'
            },
            "reverse": {
                "signature": "reverse() -> List",
                "description": "反转顺序",
                "example": 'return [1,2,3,4,5].reverse(); // [5,4,3,2,1]'
            },
            "sort": {
                "signature": "sort(func?: Function) -> List",
                "description": "排序",
                "example": textwrap.dedent('''
                    return [3,1,4,2].sort();                    // [1,2,3,4]
                    return [3,1,4,2].sort((a,b) => b - a);     // [4,3,2,1]
                ''').strip()
            },
            "distinct": {
                "signature": "distinct() -> List",
                "description": "去重",
                "example": 'return [1,2,2,3,3,3].distinct(); // [1,2,3]'
            },
            "contains": {
                "signature": "contains(item: Object) -> boolean",
                "description": "判断是否包含元素",
                "example": 'return [1,2,3].contains(2); // true'
            },
            "isEmpty": {
                "signature": "isEmpty() -> boolean",
                "description": "判断是否为空",
                "example": 'return [].isEmpty(); // true'
            },
            "size": {
                "signature": "size() -> int",
                "description": "获取集合大小",
                "example": 'return [1,2,3].size(); // 3'
            }
        }
    },
    "string": {
        "title": "String 类型扩展",
        "description": "字符串类型的扩展方法",
        "extensions": {
            "length": {
                "signature": "length() -> int",
                "description": "获取字符串长度",
                "example": 'return "hello".length(); // 5'
            },
            "substring": {
                "signature": "substring(start: int, end?: int) -> String",
                "description": "截取子串",
                "example": textwrap.dedent('''
                    return "hello world".substring(6);     // "world"
                    return "hello world".substring(0, 5);  // "hello"
                ''').strip()
            },
            "indexOf": {
                "signature": "indexOf(str: String) -> int",
                "description": "查找子串位置",
                "example": 'return "hello world".indexOf("world"); // 6'
            },
            "lastIndexOf": {
                "signature": "lastIndexOf(str: String) -> int",
                "description": "查找最后出现的位置",
                "example": 'return "hello world world".lastIndexOf("world"); // 12'
            },
            "startsWith": {
                "signature": "startsWith(prefix: String) -> boolean",
                "description": "判断是否以指定字符串开头",
                "example": 'return "hello".startsWith("he"); // true'
            },
            "endsWith": {
                "signature": "endsWith(suffix: String) -> boolean",
                "description": "判断是否以指定字符串结尾",
                "example": 'return "hello".endsWith("lo"); // true'
            },
            "contains": {
                "signature": "contains(str: String) -> boolean",
                "description": "判断是否包含子串",
                "example": 'return "hello world".contains("world"); // true'
            },
            "replace": {
                "signature": "replace(oldStr: String, newStr: String) -> String",
                "description": "替换字符串",
                "example": 'return "hello world".replace("world", "java"); // "hello java"'
            },
            "replaceAll": {
                "signature": "replaceAll(regex: String, replacement: String) -> String",
                "description": "正则替换",
                "example": 'return "hello123".replaceAll("\\d+", ""); // "hello"'
            },
            "split": {
                "signature": "split(regex: String) -> String[]",
                "description": "分割字符串",
                "example": 'return "a,b,c".split(","); // ["a","b","c"]'
            },
            "toLowerCase": {
                "signature": "toLowerCase() -> String",
                "description": "转为小写",
                "example": 'return "HELLO".toLowerCase(); // "hello"'
            },
            "toUpperCase": {
                "signature": "toUpperCase() -> String",
                "description": "转为大写",
                "example": 'return "hello".toUpperCase(); // "HELLO"'
            },
            "trim": {
                "signature": "trim() -> String",
                "description": "去除首尾空格",
                "example": 'return "  hello  ".trim(); // "hello"'
            },
            "isEmpty": {
                "signature": "isEmpty() -> boolean",
                "description": "判断是否为空字符串",
                "example": 'return "".isEmpty(); // true'
            },
            "isBlank": {
                "signature": "isBlank() -> boolean",
                "description": "判断是否为空白字符串",
                "example": 'return "   ".isBlank(); // true'
            }
        }
    },
    "date": {
        "title": "Date 类型扩展",
        "description": "日期类型的扩展方法",
        "extensions": {
            "format": {
                "signature": "format(pattern?: String) -> String",
                "description": "格式化日期",
                "example": textwrap.dedent('''
                    var date = new Date();
                    return date.format();                    // 默认格式
                    return date.format('yyyy-MM-dd HH:mm:ss'); // 指定格式
                ''').strip()
            },
            "getTime": {
                "signature": "getTime() -> long",
                "description": "获取时间戳",
                "example": 'return new Date().getTime(); // 毫秒时间戳'
            },
            "getYear": {
                "signature": "getYear() -> int",
                "description": "获取年份",
                "example": 'return new Date().getYear(); // 2024'
            },
            "getMonth": {
                "signature": "getMonth() -> int",
                "description": "获取月份(0-11)",
                "example": 'return new Date().getMonth(); // 0-11'
            },
            "getDate": {
                "signature": "getDate() -> int",
                "description": "获取日期",
                "example": 'return new Date().getDate(); // 1-31'
            },
            "getHours": {
                "signature": "getHours() -> int",
                "description": "获取小时",
                "example": 'return new Date().getHours(); // 0-23'
            },
            "getMinutes": {
                "signature": "getMinutes() -> int",
                "description": "获取分钟",
                "example": 'return new Date().getMinutes(); // 0-59'
            },
            "getSeconds": {
                "signature": "getSeconds() -> int",
                "description": "获取秒数",
                "example": 'return new Date().getSeconds(); // 0-59'
            }
        }
    }
}

def get_extension_docs(type_name: str = None) -> Any:
    """获取类型扩展文档。

    Args:
        type_name: 类型名称，可选值: object, number, collection, string, date
                   如果不指定则返回所有类型扩展

    Returns:
        指定类型的扩展文档或所有类型扩展文档
    """
    if type_name:
        return EXTENSIONS_KNOWLEDGE.get(type_name)
    return EXTENSIONS_KNOWLEDGE

def list_extension_types() -> List[str]:
    """获取所有支持扩展的类型。"""
    return list(EXTENSIONS_KNOWLEDGE.keys())

def search_extensions(keyword: str) -> List[Dict[str, Any]]:
    """根据关键词搜索扩展方法。

    Args:
        keyword: 搜索关键词

    Returns:
        匹配的扩展方法列表
    """
    results = []
    keyword_lower = keyword.lower()

    for type_name, type_data in EXTENSIONS_KNOWLEDGE.items():
        if "extensions" in type_data:
            for method_name, method_data in type_data["extensions"].items():
                if (keyword_lower in method_name.lower() or
                    keyword_lower in method_data.get("description", "").lower()):
                    results.append({
                        "type": type_name,
                        "method": method_name,
                        **method_data
                    })

    return results

__all__ = [
    "EXTENSIONS_KNOWLEDGE",
    "get_extension_docs",
    "list_extension_types",
    "search_extensions"
]
