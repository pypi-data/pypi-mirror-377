"""
随机数工具类 (RandomUtil)
参考Java Hutool RandomUtil设计，提供各种类型的随机数生成功能

主要功能：
1. 基础随机数生成（整数、浮点数、布尔值、字节数组）
2. 安全随机数生成（加密强度）
3. 字符串随机生成
4. 集合元素随机选择
5. 权重随机功能
6. 日期随机生成
7. 概率分布随机数生成

设计原则：
- 安全性：区分普通随机和加密强度随机数
- 性能：在安全性和性能之间取得平衡
- 易用性：提供简洁的API和完整的文档
- 可扩展性：支持自定义随机数生成器和字符集

参考实现：
- Java Hutool RandomUtil
- Python random和secrets模块最佳实践
"""

import random
import secrets
import string
import threading
from datetime import datetime
from typing import List, Set, Union, Sequence, TypeVar

T = TypeVar('T')


class RandomUtil:
    """
    随机数工具类
    提供各种类型的随机数生成功能，支持普通随机和加密强度随机

    所有方法都是静态方法，可以直接调用
    设计参考Java Hutool RandomUtil，但遵循Python习惯
    """

    # 字符常量定义
    BASE_NUMBER: str = "0123456789"
    BASE_CHAR_LOWER: str = "abcdefghijklmnopqrstuvwxyz"
    BASE_CHAR_UPPER: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    BASE_CHAR: str = BASE_CHAR_LOWER
    BASE_CHAR_NUMBER_LOWER: str = BASE_CHAR_LOWER + BASE_NUMBER
    BASE_CHAR_NUMBER: str = BASE_CHAR_UPPER + BASE_CHAR_NUMBER_LOWER

    # 中文常用字符范围（基本汉字 + 常用扩展）
    CHINESE_CHARS: str = "".join(
        chr(code_point) for code_point in range(0x4E00, 0x9FFF + 1)
        if '\u4e00' <= chr(code_point) <= '\u9fff'  # 基本汉字
    )

    # 线程锁用于确保线程安全
    _lock = threading.RLock()

    # region ----- 随机数生成器获取方法

    @staticmethod
    def get_random() -> random.Random:
        """
        获取线程安全的随机数生成器实例

        Returns:
            random.Random: 随机数生成器实例

        Note:
            使用全局随机实例，通过线程锁确保线程安全

        Examples:
            >> rng = RandomUtil.get_random()
            >> isinstance(rng, random.Random)
            True
        """
        with RandomUtil._lock:
            return random.Random()

    @staticmethod
    def get_secure_random() -> secrets.SystemRandom:
        """
        获取安全随机数生成器（加密强度）
        使用secrets模块提供的加密强度随机数生成器

        :return: secrets.SystemRandom实例
        """
        return secrets.SystemRandom()

    @staticmethod
    def get_random_instance(secure: bool = False) -> Union[random.Random, random.SystemRandom]:
        """
        获取随机数生成器实例

        Args:
            secure: 是否使用安全随机数生成器（加密强度）

        Returns:
            Union[random.Random, random.SystemRandom]: 随机数生成器实例

        Examples:
            >> rng = RandomUtil.get_random_instance(False)
            >> isinstance(rng, random.Random)
            True
            >> secure_rng = RandomUtil.get_random_instance(True)
            >> isinstance(secure_rng, random.SystemRandom)
            True
        """
        return RandomUtil.get_secure_random() if secure else RandomUtil.get_random()

    # endregion

    # region ----- 基础随机数生成方法

    @staticmethod
    def random_bool(secure: bool = False) -> bool:
        """
        生成随机布尔值

        Args:
            secure: 是否使用安全随机数生成器

        Returns:
            bool: 随机布尔值（True或False）

        Examples:
            >> result = RandomUtil.random_bool()
            >> isinstance(result, bool)
            True
        """
        rng = RandomUtil.get_random_instance(secure)
        return rng.getrandbits(1) == 1

    @staticmethod
    def random_int(secure: bool = False) -> int:
        """
        生成随机整数（32位范围）

        Args:
            secure: 是否使用安全随机数生成器

        Returns:
            int: 随机整数（-2^31到2^31-1之间）

        Examples:
            >> result = RandomUtil.random_int()
            >> -2**31 <= result <= 2**31-1
            True
        """
        rng = RandomUtil.get_random_instance(secure)
        return rng.randint(-2 ** 31, 2 ** 31 - 1)

    @staticmethod
    def random_int_range(limit_exclude: int, secure: bool = False) -> int:
        """
        生成[0, limit)范围内的随机整数

        Args:
            limit_exclude: 上限（不包含）
            secure: 是否使用安全随机数生成器

        Returns:
            int: [0, limit)范围内的随机整数

        Raises:
            ValueError: 如果limit_exclude <= 0

        Examples:
            >> result = RandomUtil.random_int_range(10)
            >> 0 <= result < 10
            True
        """
        if limit_exclude <= 0:
            raise ValueError("limit_exclude must be positive")

        rng = RandomUtil.get_random_instance(secure)
        return rng.randrange(limit_exclude)

    @staticmethod
    def random_int_between(min_include: int, max_exclude: int, secure: bool = False) -> int:
        """
        生成[min, max)范围内的随机整数

        Args:
            min_include: 下限（包含）
            max_exclude: 上限（不包含）
            secure: 是否使用安全随机数生成器

        Returns:
            int: [min, max)范围内的随机整数

        Raises:
            ValueError: 如果min_include >= max_exclude

        Examples:
            >> result = RandomUtil.random_int_between(5, 15)
            >> 5 <= result < 15
            True
        """
        if min_include >= max_exclude:
            raise ValueError("min_include must be less than max_exclude")

        rng = RandomUtil.get_random_instance(secure)
        return rng.randrange(min_include, max_exclude)

    @staticmethod
    def random_long(secure: bool = False) -> int:
        """
        生成随机长整数（64位范围）

        Args:
            secure: 是否使用安全随机数生成器

        Returns:
            int: 随机长整数（-2^63到2^63-1之间）

        Examples:
            >> result = RandomUtil.random_long()
            >> -2**63 <= result <= 2**63-1
            True
        """
        rng = RandomUtil.get_random_instance(secure)
        return rng.randint(-2 ** 63, 2 ** 63 - 1)

    @staticmethod
    def random_float(secure: bool = False) -> float:
        """
        生成[0.0, 1.0)范围内的随机浮点数

        Args:
            secure: 是否使用安全随机数生成器

        Returns:
            float: [0.0, 1.0)范围内的随机浮点数

        Examples:
            >> result = RandomUtil.random_float()
            >> 0.0 <= result < 1.0
            True
        """
        rng = RandomUtil.get_random_instance(secure)
        return rng.random()

    @staticmethod
    def random_float_range(min_include: float, max_exclude: float, secure: bool = False) -> float:
        """
        生成[min, max)范围内的随机浮点数

        Args:
            min_include: 下限（包含）
            max_exclude: 上限（不包含）
            secure: 是否使用安全随机数生成器

        Returns:
            float: [min, max)范围内的随机浮点数

        Raises:
            ValueError: 如果min_include >= max_exclude

        Examples:
            >> result = RandomUtil.random_float_range(1.5, 2.5)
            >> 1.5 <= result < 2.5
            True
        """
        if min_include >= max_exclude:
            raise ValueError("min_include must be less than max_exclude")

        rng = RandomUtil.get_random_instance(secure)
        return rng.uniform(min_include, max_exclude)

    @staticmethod
    def random_double(secure: bool = False) -> float:
        """
        生成[0.0, 1.0)范围内的随机双精度浮点数
        Python中float是双精度浮点数，此方法是random_float的别名

        Args:
            secure: 是否使用安全随机数生成器

        Returns:
            float: [0.0, 1.0)范围内的随机双精度浮点数

        Examples:
            >> result = RandomUtil.random_double()
            >> 0.0 <= result < 1.0
            True
        """
        return RandomUtil.random_float(secure)

    @staticmethod
    def random_bytes(length: int, secure: bool = False) -> bytes:
        """
        生成随机字节数组

        Args:
            length: 字节数组长度
            secure: 是否使用安全随机数生成器（加密强度）

        Returns:
            bytes: 随机字节数组

        Raises:
            ValueError: 如果length < 0

        Examples:
            >> result = RandomUtil.random_bytes(10)
            >> len(result)
            10
            >> isinstance(result, bytes)
            True
        """
        if length < 0:
            raise ValueError("length must be non-negative")

        if length == 0:
            return b""

        if secure:
            return secrets.token_bytes(length)

        rng = RandomUtil.get_random_instance(False)
        return bytes(rng.getrandbits(8) for _ in range(length))

    # endregion

    # region ----- 概率分布随机数生成方法

    @staticmethod
    def random_normal(mean: float = 0.0, stddev: float = 1.0, secure: bool = False) -> float:
        """
        生成正态分布随机数

        Args:
            mean: 均值
            stddev: 标准差
            secure: 是否使用安全随机数生成器

        Returns:
            float: 正态分布随机数

        Examples:
            >> result = RandomUtil.random_normal(0, 1)
            >> isinstance(result, float)
            True
        """
        rng = RandomUtil.get_random_instance(secure)
        return rng.gauss(mean, stddev)

    @staticmethod
    def random_exponential(lambd: float = 1.0, secure: bool = False) -> float:
        """
        生成指数分布随机数

        Args:
            lambd: 速率参数（1/均值）
            secure: 是否使用安全随机数生成器

        Returns:
            float: 指数分布随机数

        Raises:
            ValueError: 如果lambd <= 0

        Examples:
            >> result = RandomUtil.random_exponential(1.0)
            >> result >= 0
            True
        """
        if lambd <= 0:
            raise ValueError("lambd must be positive")

        rng = RandomUtil.get_random_instance(secure)
        return rng.expovariate(lambd)

    @staticmethod
    def random_beta(alpha: float, beta: float, secure: bool = False) -> float:
        """
        生成Beta分布随机数

        Args:
            alpha: Alpha参数
            beta: Beta参数
            secure: 是否使用安全随机数生成器

        Returns:
            float: Beta分布随机数

        Raises:
            ValueError: 如果alpha <= 0或beta <= 0

        Examples:
            >> result = RandomUtil.random_beta(2, 2)
            >> 0 <= result <= 1
            True
        """
        if alpha <= 0 or beta <= 0:
            raise ValueError("alpha and beta must be positive")

        # Beta分布生成算法
        rng = RandomUtil.get_random_instance(secure)
        x = rng.gammavariate(alpha, 1)
        y = rng.gammavariate(beta, 1)
        return x / (x + y) if (x + y) > 0 else 0.0

    # endregion

    # region ----- 集合元素随机选择方法

    @staticmethod
    def random_ele(collection: Union[Sequence[T], Set[T]], secure: bool = False) -> T:
        """
        随机选择集合中的一个元素

        Args:
            collection: 集合（列表、元组、集合等）
            secure: 是否使用安全随机数生成器

        Returns:
            T: 随机选择的元素

        Raises:
            ValueError: 如果集合为空

        Examples:
            >> items = ["apple", "banana", "orange"]
            >> result = RandomUtil.random_ele(items)
            >> result in items
            True
        """
        if not collection:
            raise ValueError("Collection cannot be empty")

        rng = RandomUtil.get_random_instance(secure)
        return rng.choice(collection) if isinstance(collection, Sequence) else rng.choice(list(collection))

    @staticmethod
    def random_eles(collection: Union[Sequence[T], Set[T]], count: int,
                    secure: bool = False, allow_duplicates: bool = True) -> List[T]:
        """
        随机选择集合中的多个元素

        Args:
            collection: 集合（列表、元组、集合等）
            count: 需要选择的元素数量
            secure: 是否使用安全随机数生成器
            allow_duplicates: 是否允许重复元素

        Returns:
            List[T]: 随机选择的元素列表

        Raises:
            ValueError: 如果集合为空或count无效

        Examples:
            >> items = ["apple", "banana", "orange"]
            >> result = RandomUtil.random_eles(items, 2)
            >> len(result)
            2
            >> all(item in items for item in result)
            True
        """
        if not collection:
            raise ValueError("Collection cannot be empty")

        if count < 0:
            raise ValueError("Count must be non-negative")

        if count == 0:
            return []

        rng = RandomUtil.get_random_instance(secure)

        if allow_duplicates:
            # 允许重复元素
            collection_list = list(collection) if not isinstance(collection, Sequence) else collection
            return [rng.choice(collection_list) for _ in range(count)]
        else:
            # 不允许重复元素
            if count > len(collection):
                raise ValueError("Count cannot be larger than collection size when duplicates are not allowed")

            return rng.sample(list(collection), count)

    @staticmethod
    def random_ele_list(collection: Union[Sequence[T], Set[T]], count: int,
                        secure: bool = False) -> List[T]:
        """
        随机选择集合中的多个不重复元素（列表形式）

        Args:
            collection: 集合（列表、元组、集合等）
            count: 需要选择的元素数量
            secure: 是否使用安全随机数生成器

        Returns:
            List[T]: 随机选择的元素列表

        Examples:
            >> items = ["apple", "banana", "orange"]
            >> result = RandomUtil.random_ele_list(items, 2)
            >> len(result)
            2
            >> len(set(result)) == len(result)  # 确保没有重复
            True
        """
        return RandomUtil.random_eles(collection, count, secure, False)

    @staticmethod
    def random_ele_set(collection: Union[Sequence[T], Set[T]], count: int,
                       secure: bool = False) -> Set[T]:
        """
        随机选择集合中的多个不重复元素（集合形式）

        Args:
            collection: 集合（列表、元组、集合等）
            count: 需要选择的元素数量
            secure: 是否使用安全随机数生成器

        Returns:
            Set[T]: 随机选择的元素集合

        Examples:
            >> items = ["apple", "banana", "orange"]
            >> result = RandomUtil.random_ele_set(items, 2)
            >> len(result)
            2
        """
        return set(RandomUtil.random_ele_list(collection, count, secure))

    @staticmethod
    def shuffle(collection: List[T], secure: bool = False) -> List[T]:
        """
        随机打乱列表顺序

        Args:
            collection: 要打乱的列表
            secure: 是否使用安全随机数生成器

        Returns:
            List[T]: 打乱后的列表

        Examples:
            >> items = [1, 2, 3, 4, 5]
            >> result = RandomUtil.shuffle(items)
            >> set(result) == set(items)  # 元素相同但顺序可能不同
            True
        """
        if not collection:
            return []

        rng = RandomUtil.get_random_instance(secure)
        shuffled = collection.copy()
        rng.shuffle(shuffled)
        return shuffled

    # endregion

    # region ----- 字符串随机生成方法

    @staticmethod
    def random_string(length: int, secure: bool = False) -> str:
        """
        生成随机字符串（包含数字和字母）

        Args:
            length: 字符串长度
            secure: 是否使用安全随机数生成器

        Returns:
            str: 随机字符串

        Raises:
            ValueError: 如果length < 0

        Examples:
            >> result = RandomUtil.random_string(10)
            >> len(result)
            10
            >> all(c in RandomUtil.BASE_CHAR_NUMBER for c in result)
            True
        """
        if length < 0:
            raise ValueError("length must be non-negative")

        if length == 0:
            return ""

        rng = RandomUtil.get_random_instance(secure)
        return ''.join(rng.choices(RandomUtil.BASE_CHAR_NUMBER, k=length))

    @staticmethod
    def random_string_upper(length: int, secure: bool = False) -> str:
        """
        生成随机字符串（只包含数字和大写字母）

        Args:
            length: 字符串长度
            secure: 是否使用安全随机数生成器

        Returns:
            str: 随机字符串

        Examples:
            >> result = RandomUtil.random_string_upper(10)
            >> all(c in (RandomUtil.BASE_CHAR_UPPER + RandomUtil.BASE_NUMBER) for c in result)
            True
        """
        if length <= 0:
            return ""

        charset = RandomUtil.BASE_CHAR_UPPER + RandomUtil.BASE_NUMBER
        rng = RandomUtil.get_random_instance(secure)
        return ''.join(rng.choices(charset, k=length))

    @staticmethod
    def random_string_lower(length: int, secure: bool = False) -> str:
        """
        生成随机字符串（只包含数字和小写字母）

        Args:
            length: 字符串长度
            secure: 是否使用安全随机数生成器

        Returns:
            str: 随机字符串

        Examples:
            >> result = RandomUtil.random_string_lower(10)
            >> all(c in RandomUtil.BASE_CHAR_NUMBER_LOWER for c in result)
            True
        """
        if length <= 0:
            return ""

        rng = RandomUtil.get_random_instance(secure)
        return ''.join(rng.choices(RandomUtil.BASE_CHAR_NUMBER_LOWER, k=length))

    @staticmethod
    def random_numbers(length: int, secure: bool = False) -> str:
        """
        生成随机数字字符串

        Args:
            length: 字符串长度
            secure: 是否使用安全随机数生成器

        Returns:
            str: 随机数字字符串

        Examples:
            >> result = RandomUtil.random_numbers(6)
            >> len(result)
            6
            >> all(c in RandomUtil.BASE_NUMBER for c in result)
            True
        """
        if length <= 0:
            return ""

        rng = RandomUtil.get_random_instance(secure)
        return ''.join(rng.choices(RandomUtil.BASE_NUMBER, k=length))

    @staticmethod
    def random_string_custom(charset: str, length: int, secure: bool = False) -> str:
        """
        从自定义字符集中生成随机字符串

        Args:
            charset: 字符集
            length: 字符串长度
            secure: 是否使用安全随机数生成器

        Returns:
            str: 随机字符串

        Raises:
            ValueError: 如果字符集为空或length无效

        Examples:
            >> result = RandomUtil.random_string_custom("ABC", 5)
            >> len(result)
            5
            >> all(c in "ABC" for c in result)
            True
        """
        if not charset:
            raise ValueError("Charset cannot be empty")

        if length < 0:
            raise ValueError("length must be non-negative")

        if length == 0:
            return ""

        rng = RandomUtil.get_random_instance(secure)
        return ''.join(rng.choices(charset, k=length))

    @staticmethod
    def random_char(secure: bool = False) -> str:
        """
        随机生成一个字符（数字或字母）

        Args:
            secure: 是否使用安全随机数生成器

        Returns:
            str: 随机字符

        Examples:
            >> result = RandomUtil.random_char()
            >> len(result)
            1
            >> result in RandomUtil.BASE_CHAR_NUMBER
            True
        """
        return RandomUtil.random_string_custom(RandomUtil.BASE_CHAR_NUMBER, 1, secure)

    @staticmethod
    def random_chinese(length: int = 1, secure: bool = False) -> str:
        """
        随机生成中文字符

        Args:
            length: 字符长度
            secure: 是否使用安全随机数生成器

        Returns:
            str: 随机中文字符串

        Examples:
            >> result = RandomUtil.random_chinese(2)
            >> len(result)
            2
            >> all('\u4e00' <= c <= '\u9fff' for c in result)
            True
        """
        if length <= 0:
            return ""

        rng = RandomUtil.get_random_instance(secure)
        return ''.join(rng.choices(RandomUtil.CHINESE_CHARS, k=length))

    # endregion

    # region ----- 权重随机方法

    @staticmethod
    def weight_random(items: List[T], weights: List[float], secure: bool = False) -> T:
        """
        权重随机选择

        Args:
            items: 选项列表
            weights: 权重列表
            secure: 是否使用安全随机数生成器

        Returns:
            T: 随机选择的项目

        Raises:
            ValueError: 如果参数无效

        Examples:
            >> items = ["A", "B", "C"]
            >> weights = [1, 2, 3]
            >> result = RandomUtil.weight_random(items, weights)
            >> result in items
            True
        """
        if not items:
            raise ValueError("Items cannot be empty")

        if len(items) != len(weights):
            raise ValueError("Items and weights must have the same length")

        if all(w == 0 for w in weights):
            raise ValueError("At least one weight must be positive")

        rng = RandomUtil.get_random_instance(secure)
        return rng.choices(items, weights=weights, k=1)[0]

    @staticmethod
    def weight_random_multi(items: List[T], weights: List[float], count: int,
                            secure: bool = False) -> List[T]:
        """
        权重随机选择多个元素

        Args:
            items: 选项列表
            weights: 权重列表
            count: 需要选择的元素数量
            secure: 是否使用安全随机数生成器

        Returns:
            List[T]: 随机选择的项目列表

        Examples:
            >> items = ["A", "B", "C"]
            >> weights = [1, 2, 3]
            >> result = RandomUtil.weight_random_multi(items, weights, 2)
            >> len(result)
            2
            >> all(item in items for item in result)
            True
        """
        if not items or count <= 0:
            return []

        if len(items) != len(weights):
            raise ValueError("Items and weights must have the same length")

        if all(w == 0 for w in weights):
            raise ValueError("At least one weight must be positive")

        rng = RandomUtil.get_random_instance(secure)
        return rng.choices(items, weights=weights, k=count)

    # endregion

    # region ----- 日期随机方法

    @staticmethod
    def random_date(start_date: datetime, end_date: datetime,
                    secure: bool = False) -> datetime:
        """
        随机生成指定范围内的日期时间

        Args:
            start_date: 开始日期（包含）
            end_date: 结束日期（包含）
            secure: 是否使用安全随机数生成器

        Returns:
            datetime: 随机日期时间

        Raises:
            ValueError: 如果开始日期晚于结束日期

        Examples:
            >> from datetime import datetime, timedelta
            >> start = datetime(2023, 1, 1)
            >> end = datetime(2023, 12, 31)
            >> result = RandomUtil.random_date(start, end)
            >> start <= result <= end
            True
        """
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")

        if start_date == end_date:
            return start_date

        rng = RandomUtil.get_random_instance(secure)

        # 计算日期范围的总秒数
        delta = end_date - start_date
        total_seconds = delta.total_seconds()

        # 生成随机秒数偏移量
        random_seconds = rng.uniform(0, total_seconds)

        return start_date + timedelta(seconds=random_seconds)

    @staticmethod
    def random_date_recent(days: int = 30, secure: bool = False) -> datetime:
        """
        生成最近N天内的随机日期

        Args:
            days: 天数范围
            secure: 是否使用安全随机数生成器

        Returns:
            datetime: 随机日期时间

        Examples:
            >> result = RandomUtil.random_date_recent(30)
            >> now = datetime.now()
            >> past_30_days = now - timedelta(days=30)
            >> past_30_days <= result <= now
            True
        """
        if days < 0:
            raise ValueError("Days must be non-negative")

        now = datetime.now()
        past_date = now - timedelta(days=days)
        return RandomUtil.random_date(past_date, now, secure)

    # endregion

    # region ----- 安全随机数专用方法

    @staticmethod
    def random_secure_string(length: int = 32) -> str:
        """
        生成安全随机字符串（加密强度）

        Args:
            length: 字符串长度

        Returns:
            str: 安全随机字符串

        Examples:
            >> result = RandomUtil.random_secure_string(16)
            >> len(result)
            16
        """
        if length <= 0:
            return ""

        # 使用URL安全的Base64编码字符集
        alphabet = string.ascii_letters + string.digits + '-_'
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def random_secure_hex(length: int = 32) -> str:
        """
        生成安全随机十六进制字符串（加密强度）

        Args:
            length: 字符串长度

        Returns:
            str: 安全随机十六进制字符串

        Examples:
            >> result = RandomUtil.random_secure_hex(16)
            >> len(result)
            16
            >> all(c in string.hexdigits for c in result)
            True
        """
        if length <= 0:
            return ""

        # 每个字节产生2个十六进制字符
        byte_length = (length + 1) // 2
        random_bytes = secrets.token_bytes(byte_length)
        return random_bytes.hex()[:length]

    @staticmethod
    def random_uuid() -> str:
        """
        生成随机UUID

        Returns:
            str: UUID字符串

        Examples:
            >> result = RandomUtil.random_uuid()
            >> len(result)
            36
            >> result.count('-')
            4
        """
        import uuid
        return str(uuid.uuid4())

    # endregion


# 单元测试和示例
if __name__ == "__main__":
    import doctest

    # 运行文档测试
    doctest.testmod(verbose=True)

    print("RandomUtil示例:")
    print("=" * 50)

    # 1. 基础随机数示例
    print("\n1. 基础随机数示例:")
    print(f"随机整数: {RandomUtil.random_int()}")
    print(f"范围随机整数 [0, 100): {RandomUtil.random_int_range(100)}")
    print(f"范围随机整数 [10, 20): {RandomUtil.random_int_between(10, 20)}")
    print(f"随机浮点数: {RandomUtil.random_float()}")
    print(f"随机布尔值: {RandomUtil.random_bool()}")

    # 2. 概率分布示例
    print("\n2. 概率分布示例:")
    print(f"正态分布随机数: {RandomUtil.random_normal(0, 1)}")
    print(f"指数分布随机数: {RandomUtil.random_exponential(1.0)}")
    print(f"Beta分布随机数: {RandomUtil.random_beta(2, 2)}")

    # 3. 字符串生成示例
    print("\n3. 字符串生成示例:")
    print(f"随机字符串: {RandomUtil.random_string(10)}")
    print(f"随机数字串: {RandomUtil.random_numbers(6)}")
    print(f"随机大写字符串: {RandomUtil.random_string_upper(8)}")
    print(f"随机中文字符: {RandomUtil.random_chinese(2)}")

    # 4. 集合操作示例
    print("\n4. 集合操作示例:")
    items = ["苹果", "香蕉", "橙子", "葡萄", "西瓜"]
    print(f"随机选择水果: {RandomUtil.random_ele(items)}")
    print(f"随机选择多个水果: {RandomUtil.random_eles(items, 3)}")
    print(f"随机选择不重复水果: {RandomUtil.random_ele_list(items, 3)}")
    print(f"打乱列表顺序: {RandomUtil.shuffle(items)}")

    # 5. 权重随机示例
    print("\n5. 权重随机示例:")
    prizes = ["一等奖", "二等奖", "三等奖", "参与奖"]
    weights = [1, 2, 3, 94]  # 权重百分比
    print(f"权重随机抽奖: {RandomUtil.weight_random(prizes, weights)}")
    print(f"权重随机多个: {RandomUtil.weight_random_multi(prizes, weights, 3)}")

    # 6. 日期随机示例
    print("\n6. 日期随机示例:")
    from datetime import datetime, timedelta

    start = datetime(2023, 1, 1)
    end = datetime(2023, 12, 31)
    print(f"随机日期: {RandomUtil.random_date(start, end)}")
    print(f"最近30天随机日期: {RandomUtil.random_date_recent(30)}")

    # 7. 安全随机示例
    print("\n7. 安全随机示例:")
    print(f"安全随机字符串: {RandomUtil.random_secure_string(16)}")
    print(f"安全随机十六进制: {RandomUtil.random_secure_hex(16)}")
    print(f"UUID: {RandomUtil.random_uuid()}")

    print("\n测试完成!")
