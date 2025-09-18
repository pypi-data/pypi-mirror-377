"""
对象操作工具类 (ObjectUtil)
提供对象判空、比较、克隆、序列化等常见对象操作

主要功能：
1. 对象判空和空值处理
2. 对象比较和相等性判断
3. 对象克隆和序列化
4. 对象类型判断和转换
5. 默认值处理
6. 集合对象操作
7. 安全序列化操作

设计原则：
- 空安全：所有方法都正确处理None值
- 类型安全：提供完整的类型注解支持
- 性能优化：避免不必要的计算和内存分配
- 异常安全：合理的异常处理和错误信息

参考实现：
- Java Hutool ObjectUtil
- Python 标准库最佳实践
"""

import copy
import pickle
import threading
from typing import (Any, Union, Optional, Callable, List, Dict, Set, Tuple,
                   TypeVar, Generic, Collection, Iterable, Iterator, Mapping,
                   Sequence, cast)
from numbers import Number
from decimal import Decimal
import collections.abc
import warnings

T = TypeVar('T')
R = TypeVar('R')
K = TypeVar('K')
V = TypeVar('V')

# 线程锁用于序列化操作的线程安全
_SERIALIZE_LOCK = threading.RLock()

class ObjectUtil:
    """
    对象工具类，提供常见的对象操作功能

    所有方法都是静态方法，可以直接调用
    设计参考Java Hutool ObjectUtil，但遵循Python习惯
    """

    @staticmethod
    def equals(obj1: Any, obj2: Any) -> bool:
        """
        比较两个对象是否相等

        相同的条件：
        1. 两个对象都是None
        2. 两个对象通过==比较相等
        3. 对于Decimal类型，使用compare方法比较

        Args:
            obj1: 第一个对象
            obj2: 第二个对象

        Returns:
            bool: 是否相等

        Raises:
            TypeError: 当对象比较出现类型错误时

        Examples:
            >> ObjectUtil.equals(None, None)
            True
            >> ObjectUtil.equals("hello", "hello")
            True
            >> ObjectUtil.equals(123, 123)
            True
            >> ObjectUtil.equals(Decimal('1.0'), Decimal('1.00'))
            True
        """
        if obj1 is None and obj2 is None:
            return True

        if obj1 is None or obj2 is None:
            return False

        # 处理Decimal类型的特殊比较
        if isinstance(obj1, Decimal) and isinstance(obj2, Decimal):
            return obj1.compare(obj2) == 0

        try:
            return obj1 == obj2
        except (TypeError, ValueError):
            return False

    @staticmethod
    def not_equals(obj1: Any, obj2: Any) -> bool:
        """
        比较两个对象是否不相等

        Args:
            obj1: 第一个对象
            obj2: 第二个对象

        Returns:
            bool: 是否不相等

        Examples:
            >> ObjectUtil.not_equals(None, "hello")
            True
            >> ObjectUtil.not_equals("hello", "world")
            True
        """
        return not ObjectUtil.equals(obj1, obj2)

    @staticmethod
    def length(obj: Any) -> int:
        """
        计算对象长度

        支持的类型包括：
        - 字符串: 返回字符串长度
        - 集合类: 返回集合大小
        - 映射: 返回映射大小
        - 数组: 返回数组长度
        - 其他有__len__方法的对象

        Args:
            obj: 被计算长度的对象

        Returns:
            int: 对象长度，如果不支持的类型返回-1

        Examples:
            >> ObjectUtil.length("hello")
            5
            >> ObjectUtil.length([1, 2, 3, 4, 5])
            5
            >> ObjectUtil.length({"a": 1, "b": 2})
            2
            >> ObjectUtil.length(123)
            -1
        """
        if obj is None:
            return 0

        try:
            if isinstance(obj, (str, bytes, bytearray)):
                return len(obj)

            if isinstance(obj, collections.abc.Sized):
                return len(obj)

            if hasattr(obj, '__len__'):
                return len(obj)

            return -1
        except (TypeError, AttributeError):
            return -1

    @staticmethod
    def contains(obj: Any, element: Any) -> bool:
        """
        检查对象中是否包含元素

        支持的对象类型包括：
        - 字符串: 检查是否包含子串
        - 集合: 检查是否包含元素
        - 映射: 检查是否包含键
        - 迭代器: 遍历检查是否包含元素

        Args:
            obj: 要检查的对象
            element: 要查找的元素

        Returns:
            bool: 是否包含元素

        Examples:
            >> ObjectUtil.contains("hello", "ell")
            True
            >> ObjectUtil.contains([1, 2, 3], 2)
            True
            >> ObjectUtil.contains({"a": 1, "b": 2}, "a")
            True
        """
        if obj is None:
            return False

        try:
            if isinstance(obj, str):
                return element in obj

            if isinstance(obj, collections.abc.Collection):
                return element in obj

            if isinstance(obj, collections.abc.Mapping):
                return element in obj

            if isinstance(obj, collections.abc.Iterable):
                for item in obj:
                    if ObjectUtil.equals(item, element):
                        return True
                return False

            return False
        except (TypeError, ValueError):
            return False

    @staticmethod
    def is_null(obj: Any) -> bool:
        """
        检查对象是否为null/None

        Args:
            obj: 要检查的对象

        Returns:
            bool: 是否为None

        Examples:
            >> ObjectUtil.is_null(None)
            True
            >> ObjectUtil.is_null("")
            False
        """
        return obj is None

    @staticmethod
    def is_not_null(obj: Any) -> bool:
        """
        检查对象是否不为null/None

        Args:
            obj: 要检查的对象

        Returns:
            bool: 是否不为None

        Examples:
            >> ObjectUtil.is_not_null("hello")
            True
            >> ObjectUtil.is_not_null(None)
            False
        """
        return not ObjectUtil.is_null(obj)

    @staticmethod
    def is_empty(obj: Any) -> bool:
        """
        判断指定对象是否为空

        支持的类型包括：
        - None: 为空
        - 字符串: 空字符串
        - 集合: 空集合
        - 映射: 空映射
        - 数值: 0视为空
        - 布尔: False视为空

        Args:
            obj: 被判断的对象

        Returns:
            bool: 是否为空

        Examples:
            >> ObjectUtil.is_empty(None)
            True
            >> ObjectUtil.is_empty("")
            True
            >> ObjectUtil.is_empty([])
            True
            >> ObjectUtil.is_empty({})
            True
            >> ObjectUtil.is_empty(0)
            True
            >> ObjectUtil.is_empty(False)
            True
        """
        if obj is None:
            return True

        if isinstance(obj, str):
            return obj == ""

        if isinstance(obj, collections.abc.Collection):
            return len(obj) == 0

        if isinstance(obj, collections.abc.Mapping):
            return len(obj) == 0

        if isinstance(obj, (int, float, complex)):
            return obj == 0

        if isinstance(obj, bool):
            return not obj

        try:
            return len(obj) == 0
        except (TypeError, AttributeError):
            return False

    @staticmethod
    def is_not_empty(obj: Any) -> bool:
        """
        判断指定对象是否为非空

        Args:
            obj: 被判断的对象

        Returns:
            bool: 是否为非空

        Examples:
            >> ObjectUtil.is_not_empty("hello")
            True
            >> ObjectUtil.is_not_empty([1, 2, 3])
            True
            >> ObjectUtil.is_not_empty(None)
            False
        """
        return not ObjectUtil.is_empty(obj)

    @staticmethod
    def default_if_null(obj: Optional[T], default_val: T) -> T:
        """
        如果给定对象为None返回默认值

        Args:
            obj: 被检查对象，可能为None
            default_val: 被检查对象为None时返回的默认值

        Returns:
            T: 被检查对象为None返回默认值，否则返回原值

        Examples:
            >> ObjectUtil.default_if_null(None, "default")
            'default'
            >> ObjectUtil.default_if_null("value", "default")
            'value'
        """
        return obj if ObjectUtil.is_not_null(obj) else default_val

    @staticmethod
    def default_if_null_supplier(obj: Optional[T], default_supplier: Callable[[], T]) -> T:
        """
        如果给定对象为None，返回默认值（由supplier提供）

        Args:
            obj: 被检查对象，可能为None
            default_supplier: 默认值提供函数

        Returns:
            T: 被检查对象为None返回默认值，否则返回原值

        Examples:
            >> ObjectUtil.default_if_null_supplier(None, lambda: "default")
            'default'
            >> ObjectUtil.default_if_null_supplier("value", lambda: "default")
            'value'
        """
        return obj if ObjectUtil.is_not_null(obj) else default_supplier()

    @staticmethod
    def default_if_empty(obj: Optional[T], default_val: T) -> T:
        """
        如果给定对象为None或空返回默认值

        Args:
            obj: 被检查对象，可能为None或空
            default_val: 被检查对象为None或空时返回的默认值

        Returns:
            T: 被检查对象为None或空返回默认值，否则返回原值

        Examples:
            >> ObjectUtil.default_if_empty(None, "default")
            'default'
            >> ObjectUtil.default_if_empty("", "default")
            'default'
            >> ObjectUtil.default_if_empty("value", "default")
            'value'
        """
        return obj if ObjectUtil.is_not_empty(obj) else default_val

    @staticmethod
    def default_if_empty_supplier(obj: Optional[T], default_supplier: Callable[[], T]) -> T:
        """
        如果给定对象为None或空，返回默认值（由supplier提供）

        Args:
            obj: 被检查对象，可能为None或空
            default_supplier: 默认值提供函数

        Returns:
            T: 被检查对象为None或空返回默认值，否则返回原值

        Examples:
            >> ObjectUtil.default_if_empty_supplier(None, lambda: "default")
            'default'
            >> ObjectUtil.default_if_empty_supplier("", lambda: "default")
            'default'
            >> ObjectUtil.default_if_empty_supplier("value", lambda: "default")
            'value'
        """
        return obj if ObjectUtil.is_not_empty(obj) else default_supplier()

    @staticmethod
    def clone(obj: T) -> Optional[T]:
        """
        克隆对象

        尝试使用以下方式克隆：
        1. 使用copy.deepcopy进行深度克隆
        2. 如果对象有clone方法，调用该方法
        3. 如果对象支持序列化，使用序列化方式克隆

        Args:
            obj: 被克隆对象

        Returns:
            Optional[T]: 克隆后的对象，如果克隆失败返回None

        Examples:
            >> original = [1, 2, 3]
            >> cloned = ObjectUtil.clone(original)
            >> cloned == original
            True
            >> cloned is original
            False
        """
        if obj is None:
            return None

        try:
            # 首先尝试深度拷贝（最常用且高效）
            return copy.deepcopy(obj)
        except (TypeError, ValueError, copy.Error):
            pass

        try:
            # 尝试调用对象的clone方法（如果存在）
            if hasattr(obj, 'clone') and callable(getattr(obj, 'clone')):
                return obj.clone()
        except (TypeError, AttributeError, ValueError):
            pass

        try:
            # 最后尝试序列化方式克隆
            return ObjectUtil.clone_by_serialize(obj)
        except (TypeError, pickle.PickleError):
            pass

        return None

    @staticmethod
    def clone_if_possible(obj: T) -> T:
        """
        返回克隆后的对象，如果克隆失败，返回原对象

        Args:
            obj: 对象

        Returns:
            T: 克隆后或原对象

        Examples:
            >> original = [1, 2, 3]
            >> cloned = ObjectUtil.clone_if_possible(original)
            >> cloned == original
            True
            >> cloned is original
            False
        """
        cloned = ObjectUtil.clone(obj)
        return cloned if cloned is not None else obj

    @staticmethod
    def clone_by_serialize(obj: T) -> T:
        """
        序列化方式克隆对象

        Warning:
            使用pickle序列化可能存在安全风险，不要反序列化不可信的数据源

        Args:
            obj: 被克隆对象

        Returns:
            T: 克隆后的对象

        Raises:
            TypeError: 如果对象不支持序列化
            ValueError: 如果序列化过程失败

        Examples:
            >> original = [1, 2, 3]
            >> cloned = ObjectUtil.clone_by_serialize(original)
            >> cloned == original
            True
            >> cloned is original
            False
        """
        with _SERIALIZE_LOCK:  # 确保线程安全
            try:
                return pickle.loads(pickle.dumps(obj))
            except pickle.PickleError as e:
                raise TypeError(f"Object is not serializable: {e}")
            except (AttributeError, ValueError) as e:
                raise ValueError(f"Serialization failed: {e}")

    @staticmethod
    def serialize(obj: Any) -> bytes:
        """
        序列化对象

        Warning:
            使用pickle序列化可能存在安全风险，不要反序列化不可信的数据源

        Args:
            obj: 要被序列化的对象

        Returns:
            bytes: 序列化后的字节码

        Raises:
            TypeError: 如果对象不支持序列化

        Examples:
            >> data = ObjectUtil.serialize([1, 2, 3])
            >> isinstance(data, bytes)
            True
        """
        with _SERIALIZE_LOCK:  # 确保线程安全
            try:
                return pickle.dumps(obj)
            except pickle.PickleError as e:
                raise TypeError(f"Object is not serializable: {e}")

    @staticmethod
    def deserialize(data: bytes) -> Any:
        """
        反序列化对象

        Warning:
            使用pickle反序列化可能存在安全风险，不要反序列化不可信的数据源

        Args:
            data: 反序列化的字节码

        Returns:
            Any: 反序列化后的对象

        Raises:
            TypeError: 如果数据无法反序列化

        Examples:
            >> original = [1, 2, 3]
            >> data = ObjectUtil.serialize(original)
            >> restored = ObjectUtil.deserialize(data)
            >> restored == original
            True
        """
        with _SERIALIZE_LOCK:  # 确保线程安全
            try:
                return pickle.loads(data)
            except pickle.PickleError as e:
                raise TypeError(f"Data is not deserializable: {e}")

    @staticmethod
    def is_basic_type(obj: Any) -> bool:
        """
        是否为基本类型

        基本类型包括：数字、字符串、布尔值、None、字节类型

        Args:
            obj: 被检查对象

        Returns:
            bool: 是否为基本类型

        Examples:
            >> ObjectUtil.is_basic_type(123)
            True
            >> ObjectUtil.is_basic_type("hello")
            True
            >> ObjectUtil.is_basic_type(True)
            True
            >> ObjectUtil.is_basic_type([1, 2, 3])
            False
        """
        if obj is None:
            return True

        return isinstance(obj, (int, float, bool, str, complex, bytes, bytearray, Decimal))

    @staticmethod
    def to_string(obj: Any) -> str:
        """
        将对象转为字符串

        Args:
            obj: 对象

        Returns:
            str: 字符串表示

        Examples:
            >> ObjectUtil.to_string(None)
            'None'
            >> ObjectUtil.to_string("hello")
            'hello'
            >> ObjectUtil.to_string([1, 2, 3])
            '[1, 2, 3]'
        """
        if obj is None:
            return "None"

        return str(obj)

    @staticmethod
    def empty_count(*objs: Any) -> int:
        """
        存在多少个None或空对象

        Args:
            objs: 被检查的对象

        Returns:
            int: 空对象的数量

        Examples:
            >> ObjectUtil.empty_count(None, "", [], {}, [1, 2])
            4
        """
        count = 0
        for obj in objs:
            if ObjectUtil.is_empty(obj):
                count += 1
        return count

    @staticmethod
    def has_null(*objs: Any) -> bool:
        """
        是否存在None对象

        Args:
            objs: 被检查对象

        Returns:
            bool: 是否存在None对象

        Examples:
            >> ObjectUtil.has_null(None, "hello")
            True
            >> ObjectUtil.has_null("hello", "world")
            False
        """
        for obj in objs:
            if ObjectUtil.is_null(obj):
                return True
        return False

    @staticmethod
    def has_empty(*objs: Any) -> bool:
        """
        是否存在None或空对象

        Args:
            objs: 被检查对象

        Returns:
            bool: 是否存在None或空对象

        Examples:
            >> ObjectUtil.has_empty(None, "hello")
            True
            >> ObjectUtil.has_empty("", "hello")
            True
            >> ObjectUtil.has_empty("hello", "world")
            False
        """
        for obj in objs:
            if ObjectUtil.is_empty(obj):
                return True
        return False

    @staticmethod
    def is_all_empty(*objs: Any) -> bool:
        """
        是否全部为None或空对象

        Args:
            objs: 被检查的对象

        Returns:
            bool: 是否全部为空

        Examples:
            >> ObjectUtil.is_all_empty(None, "", [])
            True
            >> ObjectUtil.is_all_empty(None, "hello")
            False
        """
        for obj in objs:
            if ObjectUtil.is_not_empty(obj):
                return False
        return True

    @staticmethod
    def is_all_not_empty(*objs: Any) -> bool:
        """
        是否全部不为None或空对象

        Args:
            objs: 被检查的对象

        Returns:
            bool: 是否全部不为空

        Examples:
            >> ObjectUtil.is_all_not_empty("hello", [1, 2], {"a": 1})
            True
            >> ObjectUtil.is_all_not_empty("hello", None)
            False
        """
        for obj in objs:
            if ObjectUtil.is_empty(obj):
                return False
        return True

    @staticmethod
    def get_first_not_null(*objs: Any) -> Any:
        """
        获取第一个不为None的对象

        Args:
            objs: 被检查的对象

        Returns:
            Any: 第一个不为None的对象，如果全部为None则返回None

        Examples:
            >> ObjectUtil.get_first_not_null(None, "", "hello", "world")
            'hello'
            >> ObjectUtil.get_first_not_null(None, None)
            None
        """
        for obj in objs:
            if ObjectUtil.is_not_null(obj):
                return obj
        return None

    @staticmethod
    def get_first_not_empty(*objs: Any) -> Any:
        """
        获取第一个不为空的对象

        Args:
            objs: 被检查的对象

        Returns:
            Any: 第一个不为空的对象，如果全部为空则返回None

        Examples:
            >> ObjectUtil.get_first_not_empty(None, "", "hello", "world")
            'hello'
            >> ObjectUtil.get_first_not_empty(None, "", [])
            None
        """
        for obj in objs:
            if ObjectUtil.is_not_empty(obj):
                return obj
        return None

    @staticmethod
    def if_present(obj: Optional[T], consumer: Callable[[T], None]) -> None:
        """
        如果对象不为None，则执行消费者函数

        Args:
            obj: 被检查的对象
            consumer: 消费者函数

        Examples:
            >> result = []
            >> ObjectUtil.if_present("hello", result.append)
            >> result
            ['hello']
        """
        if ObjectUtil.is_not_null(obj):
            consumer(obj)

    @staticmethod
    def map_if_present(obj: Optional[T], mapper: Callable[[T], R]) -> Optional[R]:
        """
        如果对象不为None，则执行映射函数

        Args:
            obj: 被检查的对象
            mapper: 映射函数

        Returns:
            Optional[R]: 映射结果，如果对象为None则返回None

        Examples:
            >> ObjectUtil.map_if_present("hello", len)
            5
            >> ObjectUtil.map_if_present(None, len)
            None
        """
        return mapper(obj) if ObjectUtil.is_not_null(obj) else None

    @staticmethod
    def filter_not_null(iterable: Iterable[Optional[T]]) -> List[T]:
        """
        过滤掉Iterable中的None值

        Args:
            iterable: 可迭代对象

        Returns:
            List[T]: 过滤后的列表

        Examples:
            >> ObjectUtil.filter_not_null([1, None, 2, None, 3])
            [1, 2, 3]
        """
        return [item for item in iterable if ObjectUtil.is_not_null(item)]

    @staticmethod
    def filter_not_empty(iterable: Iterable[Optional[T]]) -> List[T]:
        """
        过滤掉Iterable中的空值

        Args:
            iterable: 可迭代对象

        Returns:
            List[T]: 过滤后的列表

        Examples:
            >> ObjectUtil.filter_not_empty(["a", "", "b", None, "c"])
            ['a', 'b', 'c']
        """
        return [item for item in iterable if ObjectUtil.is_not_empty(item)]

    @staticmethod
    def require_non_null(obj: Optional[T], message: str = "Object must not be null") -> T:
        """
        要求对象不为None，否则抛出异常

        Args:
            obj: 被检查的对象
            message: 异常消息

        Returns:
            T: 非空对象

        Raises:
            ValueError: 当对象为None时

        Examples:
            >> ObjectUtil.require_non_null("hello")
            'hello'
            >> ObjectUtil.require_non_null(None)
            Traceback (most recent call last):
                ...
            ValueError: Object must not be null
        """
        if ObjectUtil.is_null(obj):
            raise ValueError(message)
        return cast(T, obj)

    @staticmethod
    def require_non_empty(obj: Optional[T], message: str = "Object must not be empty") -> T:
        """
        要求对象不为空，否则抛出异常

        Args:
            obj: 被检查的对象
            message: 异常消息

        Returns:
            T: 非空对象

        Raises:
            ValueError: 当对象为空时

        Examples:
            >> ObjectUtil.require_non_empty("hello")
            'hello'
            >> ObjectUtil.require_non_empty("")
            Traceback (most recent call last):
                ...
            ValueError: Object must not be empty
        """
        if ObjectUtil.is_empty(obj):
            raise ValueError(message)
        return cast(T, obj)

    @staticmethod
    def coalesce(*objs: Any) -> Any:
        """
        返回第一个不为None的对象

        Args:
            objs: 被检查的对象

        Returns:
            Any: 第一个不为None的对象，如果全部为None则返回None

        Examples:
            >> ObjectUtil.coalesce(None, "", "hello", "world")
            ''
            >> ObjectUtil.coalesce(None, None)
            None
        """
        for obj in objs:
            if ObjectUtil.is_not_null(obj):
                return obj
        return None

    @staticmethod
    def coalesce_empty(*objs: Any) -> Any:
        """
        返回第一个不为空的对象

        Args:
            objs: 被检查的对象

        Returns:
            Any: 第一个不为空的对象，如果全部为空则返回None

        Examples:
            >> ObjectUtil.coalesce_empty(None, "", "hello", "world")
            'hello'
            >> ObjectUtil.coalesce_empty(None, "", [])
            None
        """
        for obj in objs:
            if ObjectUtil.is_not_empty(obj):
                return obj
        return None

    @staticmethod
    def to_dict(obj: Any) -> Dict[str, Any]:
        """
        将对象转换为字典

        Args:
            obj: 要转换的对象

        Returns:
            Dict[str, Any]: 字典表示

        Examples:
            >> class Person:
            ...     def __init__(self, name, age):
            ...         self.name = name
            ...         self.age = age
            >> person = Person("John", 30)
            >> result = ObjectUtil.to_dict(person)
            >> result["name"]
            'John'
            >> result["age"]
            30
        """
        if obj is None:
            return {}

        if isinstance(obj, dict):
            return dict(obj)

        result = {}
        if hasattr(obj, '__dict__'):
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
                    result[key] = value
        else:
            for key in dir(obj):
                if not key.startswith('_'):
                    try:
                        value = getattr(obj, key)
                        if not callable(value):
                            result[key] = value
                    except (AttributeError, TypeError):
                        pass

        return result


# 单元测试和示例
if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)

    # 示例用法
    print("ObjectUtil示例:")
    print("=" * 50)

    # 对象判空示例
    print("\n1. 对象判空示例:")
    print(f"is_null(None): {ObjectUtil.is_null(None)}")
    print(f"is_empty(''): {ObjectUtil.is_empty('')}")
    print(f"is_not_empty('hello'): {ObjectUtil.is_not_empty('hello')}")

    # 对象比较示例
    print("\n2. 对象比较示例:")
    print(f"equals('hello', 'hello'): {ObjectUtil.equals('hello', 'hello')}")
    print(f"not_equals('hello', 'world'): {ObjectUtil.not_equals('hello', 'world')}")

    # 默认值处理示例
    print("\n3. 默认值处理示例:")
    print(f"default_if_null(None, 'default'): {ObjectUtil.default_if_null(None, 'default')}")
    print(f"default_if_empty('', 'default'): {ObjectUtil.default_if_empty('', 'default')}")

    # 对象克隆示例
    print("\n4. 对象克隆示例:")
    original_list = [1, 2, 3, {"a": 1, "b": 2}]
    cloned_list = ObjectUtil.clone(original_list)
    print(f"Original: {original_list}")
    print(f"Cloned: {cloned_list}")
    print(f"Same object: {original_list is cloned_list}")
    print(f"Equal: {original_list == cloned_list}")

    # 对象序列化示例
    print("\n5. 对象序列化示例:")
    data = ObjectUtil.serialize(original_list)
    restored = ObjectUtil.deserialize(data)
    print(f"Serialized data length: {len(data)} bytes")
    print(f"Restored equals original: {restored == original_list}")

    # 集合操作示例
    print("\n6. 集合操作示例:")
    print(f"length('hello'): {ObjectUtil.length('hello')}")
    print(f"contains([1, 2, 3], 2): {ObjectUtil.contains([1, 2, 3], 2)}")

    # 批量检查示例
    print("\n7. 批量检查示例:")
    print(f"has_null(None, 'hello'): {ObjectUtil.has_null(None, 'hello')}")
    print(f"has_empty('', 'hello'): {ObjectUtil.has_empty('', 'hello')}")
    print(f"is_all_empty(None, '', []): {ObjectUtil.is_all_empty(None, '', [])}")
    print(f"is_all_not_empty('hello', [1]): {ObjectUtil.is_all_not_empty('hello', [1])}")

    # 新功能示例
    print("\n8. 新功能示例:")
    print(f"get_first_not_null(None, '', 'hello'): {ObjectUtil.get_first_not_null(None, '', 'hello')}")
    print(f"filter_not_null([1, None, 2, None, 3]): {ObjectUtil.filter_not_null([1, None, 2, None, 3])}")
    print(f"coalesce_empty(None, '', 'hello'): {ObjectUtil.coalesce_empty(None, '', 'hello')}")

    print("\n测试完成!")