"""
JSON 工具类 (JSONUtil)
参考 Java Hutool JSONUtil 设计，基于 orjson 提供高性能 JSON 处理

主要功能：
1. JSON 对象和数组的创建
2. JSON 字符串解析和转换
3. JSON 文件读写操作
4. JSON 与对象之间的转换
5. JSON 路径操作
6. JSON 格式化和类型判断
7. XML 与 JSON 互转（可选功能）

设计特点：
1. 使用 orjson 作为底层库，提供高性能 JSON 处理
2. 兼容 Python 标准库 json 的 API 设计
3. 支持多种数据类型的序列化和反序列化
4. 提供丰富的配置选项和错误处理机制
"""
import dataclasses
import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Union, Optional, List, Dict, Type, TypeVar

import orjson

T = TypeVar('T')


class JSONUtil:
    """
    JSON 工具类
    参考 Java Hutool JSONUtil 实现，基于 orjson 提供高性能 JSON 处理
    """

    # orjson 选项常量
    OPT_INDENT_2 = orjson.OPT_INDENT_2
    OPT_SORT_KEYS = orjson.OPT_SORT_KEYS
    OPT_NON_STR_KEYS = orjson.OPT_NON_STR_KEYS
    OPT_UTC_Z = orjson.OPT_UTC_Z

    @staticmethod
    def create_obj() -> Dict[str, Any]:
        """
        创建 JSON 对象（字典）

        :return: 空字典

        >> obj = JSONUtil.create_obj()
        >> isinstance(obj, dict)
        True
        >> len(obj)
        0
        """
        return {}

    @staticmethod
    def create_array() -> List[Any]:
        """
        创建 JSON 数组（列表）

        :return: 空列表

        >> arr = JSONUtil.create_array()
        >> isinstance(arr, list)
        True
        >> len(arr)
        0
        """
        return []

    @staticmethod
    def parse_obj(json_str: Union[str, bytes]) -> Dict[str, Any]:
        """
        JSON 字符串转 JSON 对象（字典）

        :param json_str: JSON 字符串或字节
        :return: 字典对象

        >> obj = JSONUtil.parse_obj('{"name": "John", "age": 30}')
        >> obj["name"]
        'John'
        >> obj["age"]
        30
        """
        if isinstance(json_str, str):
            json_str = json_str.encode('utf-8')
        return orjson.loads(json_str)

    @staticmethod
    def parse_array(json_str: Union[str, bytes]) -> List[Any]:
        """
        JSON 字符串转 JSON 数组（列表）

        :param json_str: JSON 字符串或字节
        :return: 列表对象

        >> arr = JSONUtil.parse_array('[1, 2, 3, "hello"]')
        >> arr[0]
        1
        >> arr[3]
        'hello'
        """
        if isinstance(json_str, str):
            json_str = json_str.encode('utf-8')
        result = orjson.loads(json_str)
        if not isinstance(result, list):
            raise ValueError("JSON string is not an array")
        return result

    @staticmethod
    def parse(json_str: Union[str, bytes]) -> Any:
        """
        解析 JSON 字符串，自动判断是对象还是数组

        :param json_str: JSON 字符串或字节
        :return: 解析后的对象（字典或列表）

        >> obj = JSONUtil.parse('{"name": "John"}')
        >> isinstance(obj, dict)
        True
        >> arr = JSONUtil.parse('[1, 2, 3]')
        >> isinstance(arr, list)
        True
        """
        if isinstance(json_str, str):
            json_str = json_str.encode('utf-8')
        return orjson.loads(json_str)

    @staticmethod
    def to_json_str(obj: Any, options: Optional[int] = None) -> str:
        """
        将对象转换为 JSON 字符串

        :param obj: 要转换的对象
        :param options: orjson 选项
        :return: JSON 字符串

        >> JSONUtil.to_json_str({"name": "John", "age": 30})
        '{"name":"John","age":30}'
        """
        if options is None:
            options = 0

        # 处理特殊类型
        if isinstance(obj, (datetime, date)):
            return orjson.dumps(obj.isoformat(), option=options).decode('utf-8')
        elif isinstance(obj, Decimal):
            return orjson.dumps(float(obj), option=options).decode('utf-8')
        elif isinstance(obj, Enum):
            return orjson.dumps(obj.value, option=options).decode('utf-8')
        elif dataclasses.is_dataclass(obj):
            return orjson.dumps(dataclasses.asdict(obj), option=options).decode('utf-8')

        try:
            return orjson.dumps(obj, option=options).decode('utf-8')
        except (TypeError, ValueError):
            # 回退到标准 json 库处理不支持的类型
            return json.dumps(obj, default=JSONUtil._json_serializer)

    @staticmethod
    def to_json_pretty_str(obj: Any) -> str:
        """
        将对象转换为格式化的 JSON 字符串（缩进2个空格）

        :param obj: 要转换的对象
        :return: 格式化的 JSON 字符串

        >> pretty_str = JSONUtil.to_json_pretty_str({"name": "John", "age": 30})
        >> '\\n' in pretty_str
        True
        """
        return JSONUtil.to_json_str(obj, options=orjson.OPT_INDENT_2)

    @staticmethod
    def _json_serializer(obj):
        """
        JSON 序列化辅助方法，处理特殊类型

        :param obj: 要序列化的对象
        :return: 可序列化的对象
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif isinstance(obj, (set, frozenset)):
            return list(obj)
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    @staticmethod
    def read_json(file_path: Union[str, Path], encoding: str = 'utf-8') -> Any:
        """
        从文件读取 JSON 内容

        :param file_path: 文件路径
        :param encoding: 文件编码
        :return: JSON 对象

        >> import tempfile
        >> with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as f:
        ...     f.write(b'{"name": "John", "age": 30}')
        ...     temp_path = f.name
        >> obj = JSONUtil.read_json(temp_path)
        >> obj["name"]
        'John'
        >> import os
        >> os.unlink(temp_path)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'rb') as f:
            content = f.read()

        return orjson.loads(content)

    @staticmethod
    def read_json_obj(file_path: Union[str, Path], encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        从文件读取 JSON 对象

        :param file_path: 文件路径
        :param encoding: 文件编码
        :return: JSON 对象（字典）
        """
        content = JSONUtil.read_json(file_path, encoding)
        if not isinstance(content, dict):
            raise ValueError("JSON content is not an object")

        return content

    @staticmethod
    def read_json_array(file_path: Union[str, Path], encoding: str = 'utf-8') -> List[Any]:
        """
        从文件读取 JSON 数组

        :param file_path: 文件路径
        :param encoding: 文件编码
        :return: JSON 数组（列表）
        """
        content = JSONUtil.read_json(file_path, encoding)
        if not isinstance(content, list):
            raise ValueError("JSON content is not an array")

        return content

    @staticmethod
    def write_json(file_path: Union[str, Path], obj: Any, options: Optional[int] = None):
        """
        将对象写入 JSON 文件

        :param file_path: 文件路径
        :param obj: 要写入的对象
        :param options: orjson 选项
        """
        file_path = Path(file_path)
        json_bytes = orjson.dumps(obj, option=options)

        with open(file_path, 'wb') as f:
            f.write(json_bytes)

    @staticmethod
    def to_bean(json_str: Union[str, bytes], bean_class: Type[T]) -> T:
        """
        JSON 字符串转为 Bean 对象

        :param json_str: JSON 字符串或字节
        :param bean_class: Bean 类
        :return: Bean 对象

        >> class Person:
        ...     def __init__(self, name, age):
        ...         self.name = name
        ...         self.age = age
        >> person = JSONUtil.to_bean('{"name": "Alice", "age": 25}', Person)
        >> person.name
        'Alice'
        >> person.age
        25
        """
        if isinstance(json_str, str):
            json_str = json_str.encode('utf-8')

        data = orjson.loads(json_str)
        return JSONUtil._dict_to_bean(data, bean_class)

    @staticmethod
    def _dict_to_bean(obj_dict: Dict[str, Any], bean_class: Type[T]) -> T:
        """
        将字典转换为 Bean 对象

        :param obj_dict: 字典对象
        :param bean_class: Bean 类
        :return: Bean 对象
        """
        if not obj_dict or not bean_class:
            return None

        # 创建 Bean 实例
        try:
            # 尝试使用字典解包方式创建对象
            return bean_class(**obj_dict)
        except TypeError:
            # 如果失败，使用反射方式设置属性
            instance = bean_class()
            for key, value in obj_dict.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            return instance

    @staticmethod
    def to_list(json_array_str: Union[str, bytes], element_type: Type[T]) -> List[T]:
        """
        将 JSON 数组字符串转换为 Bean 列表

        :param json_array_str: JSON 数组字符串
        :param element_type: 元素类型
        :return: Bean 列表

        >> class Person:
        ...     def __init__(self, name, age):
        ...         self.name = name
        ...         self.age = age
        >> persons = JSONUtil.to_list('[{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]', Person)
        >> len(persons)
        2
        >> persons[0].name
        'John'
        """
        if isinstance(json_array_str, str):
            json_array_str = json_array_str.encode('utf-8')

        array = orjson.loads(json_array_str)
        return [JSONUtil._dict_to_bean(item, element_type) for item in array if isinstance(item, dict)]

    @staticmethod
    def get_by_path(json_obj: Any, path: str, default: Any = None) -> Any:
        """
        通过路径表达式获取 JSON 中的值

        路径表达式支持：
        - .表达式：获取对象中的属性
        - []表达式：获取数组中的元素

        :param json_obj: JSON 对象
        :param path: 路径表达式
        :param default: 默认值
        :return: 路径对应的值

        >> obj = {"person": {"name": "John", "age": 30, "hobbies": ["reading", "swimming"]}}
        >> JSONUtil.get_by_path(obj, "person.name")
        'John'
        >> JSONUtil.get_by_path(obj, "person.hobbies[1]")
        'swimming'
        """
        if not json_obj or not path:
            return default

        try:
            # 分割路径
            parts = path.split('.')
            current = json_obj

            for part in parts:
                if '[' in part and part.endswith(']'):
                    # 处理数组索引
                    key = part.split('[')[0]
                    index = int(part.split('[')[1].rstrip(']'))

                    if key:
                        current = current[key]
                    current = current[index]
                else:
                    # 处理对象属性
                    current = current[part]

            return current
        except (KeyError, IndexError, TypeError):
            return default

    @staticmethod
    def put_by_path(json_obj: Any, path: str, value: Any):
        """
        通过路径表达式设置 JSON 中的值

        :param json_obj: JSON 对象
        :param path: 路径表达式
        :param value: 要设置的值
        """
        if not json_obj or not path:
            return

        # 分割路径
        parts = path.split('.')
        current = json_obj

        # 遍历到路径的父级
        for i, part in enumerate(parts[:-1]):
            if '[' in part and part.endswith(']'):
                # 处理数组索引
                key = part.split('[')[0]
                index = int(part.split('[')[1].rstrip(']'))

                if key:
                    if key not in current:
                        current[key] = []
                    current = current[key]

                while len(current) <= index:
                    current.append(None)
                current = current[index]
            else:
                # 处理对象属性
                if part not in current:
                    current[part] = {}
                current = current[part]

        # 设置最终值
        last_part = parts[-1]
        if '[' in last_part and last_part.endswith(']'):
            # 处理数组索引
            key = last_part.split('[')[0]
            index = int(last_part.split('[')[1].rstrip(']'))

            if key:
                if key not in current:
                    current[key] = []
                current = current[key]

            while len(current) <= index:
                current.append(None)
            current[index] = value
        else:
            # 处理对象属性
            current[last_part] = value

    @staticmethod
    def quote(string: str) -> str:
        """
        对字符串进行 JSON 引号转义处理

        :param string: 要转义的字符串
        :return: 转义后的字符串

        >> JSONUtil.quote('Hello "World"')
        'Hello \\\\"World\\\\"'
        """
        if string is None:
            return "null"

        return orjson.dumps(string).decode('utf-8')

    @staticmethod
    def is_type_json(json_str: str) -> bool:
        """
        判断字符串是否为 JSON 类型（对象或数组）

        :param json_str: 要判断的字符串
        :return: 是否为 JSON 类型

        >> JSONUtil.is_type_json('{"name": "John"}')
        True
        >> JSONUtil.is_type_json('[1, 2, 3]')
        True
        >> JSONUtil.is_type_json('Hello World')
        False
        """
        if not json_str or not json_str.strip():
            return False

        trimmed = json_str.strip()
        return (trimmed.startswith('{') and trimmed.endswith('}')) or \
            (trimmed.startswith('[') and trimmed.endswith(']'))

    @staticmethod
    def is_type_json_object(json_str: str) -> bool:
        """
        判断字符串是否为 JSON 对象类型

        :param json_str: 要判断的字符串
        :return: 是否为 JSON 对象类型

        >> JSONUtil.is_type_json_object('{"name": "John"}')
        True
        >> JSONUtil.is_type_json_object('[1, 2, 3]')
        False
        """
        if not json_str or not json_str.strip():
            return False

        trimmed = json_str.strip()
        return trimmed.startswith('{') and trimmed.endswith('}')

    @staticmethod
    def is_type_json_array(json_str: str) -> bool:
        """
        判断字符串是否为 JSON 数组类型

        :param json_str: 要判断的字符串
        :return: 是否为 JSON 数组类型

        >> JSONUtil.is_type_json_array('[1, 2, 3]')
        True
        >> JSONUtil.is_type_json_array('{"name": "John"}')
        False
        """
        if not json_str or not json_str.strip():
            return False

        trimmed = json_str.strip()
        return trimmed.startswith('[') and trimmed.endswith(']')

    @staticmethod
    def format_json_str(json_str: str) -> str:
        """
        格式化 JSON 字符串

        :param json_str: JSON 字符串
        :return: 格式化后的 JSON 字符串

        >> json_str = '{"name":"John","age":30,"hobbies":["reading","swimming"]}'
        >> formatted = JSONUtil.format_json_str(json_str)
        >> '\\n' in formatted
        True
        """
        if not JSONUtil.is_type_json(json_str):
            return json_str

        try:
            obj = orjson.loads(json_str.encode('utf-8'))
            return orjson.dumps(obj, option=orjson.OPT_INDENT_2).decode('utf-8')
        except orjson.JSONDecodeError:
            return json_str

    @staticmethod
    def xml_to_json(xml_str: str) -> Dict[str, Any]:
        """
        XML 字符串转为 JSON 对象（需要安装 xmltodict 库）

        :param xml_str: XML 字符串
        :return: JSON 对象

        >> xml = '<person><name>John</name><age>30</age></person>'
        >> obj = JSONUtil.xml_to_json(xml)
        >> obj['person']['name']
        'John'
        """
        try:
            import xmltodict
            return xmltodict.parse(xml_str)
        except ImportError:
            raise ImportError("xmltodict library is required for XML to JSON conversion")

    @staticmethod
    def json_to_xml(json_obj: Dict[str, Any]) -> str:
        """
        JSON 对象转为 XML 字符串（需要安装 xmltodict 库）

        :param json_obj: JSON 对象
        :return: XML 字符串

        >> obj = {"person": {"name": "John", "age": 30}}
        >> xml = JSONUtil.json_to_xml(obj)
        >> '<name>John</name>' in xml
        True
        """
        try:
            import xmltodict
            return xmltodict.unparse(json_obj, pretty=True)
        except ImportError:
            raise ImportError("xmltodict library is required for JSON to XML conversion")


# 单元测试和示例
if __name__ == "__main__":
    import doctest

    doctest.testmod()

    print("JSONUtil示例:")

    # 基本功能示例
    print("\n1. 基本功能示例:")
    json_str = '{"name": "John", "age": 30, "hobbies": ["reading", "swimming"]}'
    obj = JSONUtil.parse_obj(json_str)
    print(f"解析JSON对象: {obj}")

    formatted = JSONUtil.format_json_str(json_str)
    print(f"格式化JSON: {formatted}")

    # 文件操作示例
    print("\n2. 文件操作示例:")
    import tempfile

    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as f:
        f.write(json_str.encode('utf-8'))
        temp_path = f.name

    # 读取文件
    file_obj = JSONUtil.read_json(temp_path)
    print(f"从文件读取JSON: {file_obj}")

    # 写入文件
    new_obj = {"new": "data", "list": [1, 2, 3]}
    JSONUtil.write_json(temp_path, new_obj)
    print(f"写入文件后内容: {JSONUtil.read_json(temp_path)}")

    # 清理临时文件
    import os

    os.unlink(temp_path)

    # 对象转换示例
    print("\n3. 对象转换示例:")


    class Person:
        def __init__(self, name=None, age=None):
            self.name = name
            self.age = age

        def __repr__(self):
            return f"Person(name={self.name}, age={self.age})"


    person_json = '{"name": "Alice", "age": 25}'
    person = JSONUtil.to_bean(person_json, Person)
    print(f"JSON转对象: {person}")

    # 路径操作示例
    print("\n4. 路径操作示例:")
    complex_json = {
        "users": [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ],
        "metadata": {"version": "1.0"}
    }

    name = JSONUtil.get_by_path(complex_json, "users[0].name")
    print(f"路径获取值: {name}")

    JSONUtil.put_by_path(complex_json, "users[1].age", 26)
    print(f"路径设置值后: {complex_json['users'][1]}")

    # 特殊类型支持示例
    print("\n5. 特殊类型支持示例:")
    from datetime import datetime
    from enum import Enum


    class Status(Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"


    special_data = {
        "timestamp": datetime.now(),
        "status": Status.ACTIVE,
        "price": Decimal("19.99")
    }

    special_json = JSONUtil.to_json_str(special_data)
    print(f"特殊类型JSON: {special_json}")

    # 类型判断示例
    print("\n6. 类型判断示例:")
    print(f"是否为JSON对象:",JSONUtil.is_type_json_object('{"name": "John"}'))
    print(f"是否为JSON数组:",JSONUtil.is_type_json_object('{"name": "John"}'))
    print(f"是否为JSON: ",JSONUtil.is_type_json('{"name": "John"}'))

    # 引号转义示例
    print("\n7. 引号转义示例:")
    text = 'Hello "World"'
    quoted = JSONUtil.quote(text)
    print(f"引号转义: {text} -> {quoted}")

    # 性能测试示例
    print("\n8. 性能测试示例:")
    import time

    # 创建大型测试数据
    large_data = {"items": [{"id": i, "value": f"item_{i}"} for i in range(10000)]}

    # 序列化性能测试
    start_time = time.time()
    json_str = JSONUtil.to_json_str(large_data)
    orjson_time = time.time() - start_time

    start_time = time.time()
    json_str_std = json.dumps(large_data)
    std_json_time = time.time() - start_time

    print(f"orjson序列化时间: {orjson_time:.6f}s")
    print(f"标准json序列化时间: {std_json_time:.6f}s")
    # 添加安全检查以避免除零错误
    if orjson_time < 1e-9:  # 小于1纳秒，视为0
        print("性能提升: orjson太快了，无法测量倍数")
    else:
        print(f"性能提升: {std_json_time / orjson_time:.1f}倍")

    # 反序列化性能测试
    start_time = time.time()
    data_back = JSONUtil.parse_obj(json_str)
    orjson_time = time.time() - start_time

    start_time = time.time()
    data_back_std = json.loads(json_str)
    std_json_time = time.time() - start_time

    print(f"orjson反序列化时间: {orjson_time:.6f}s")
    print(f"标准json反序列化时间: {std_json_time:.6f}s")
    print(f"性能提升: {std_json_time / orjson_time:.1f}倍")
