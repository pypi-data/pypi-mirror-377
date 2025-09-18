"""
数字处理工具类 (NumberUtil)
提供高精度数字运算、转换、格式化和验证功能

主要功能：
1. 高精度十进制计算（基于Decimal）
2. 数字格式化和解析
3. 数学运算和计算函数
4. 数字类型验证和转换
5. 进制转换和位操作
6. 统计和聚合函数
7. 金融和科学计算辅助函数

设计原则：
- 精度优先：所有计算默认使用Decimal保证精度
- 异常安全：提供合理的默认值和清晰的错误信息
- 性能均衡：在精度和性能之间取得平衡
- 易于使用：提供简洁的API和完整的文档

参考实现：
- Java Hutool NumberUtil
- Python decimal模块最佳实践
- 金融计算常用算法
"""

import math
import re
import decimal
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, ROUND_HALF_EVEN, InvalidOperation
from typing import Optional, List, Union, Any, Tuple, Dict, Callable
from functools import reduce
import random
import statistics


class NumberUtil:
    """
    数字工具类，提供精确的数字运算和转换方法

    所有方法都是静态方法，可以直接调用
    默认使用Decimal进行高精度计算，避免浮点数精度问题
    """

    # 默认除法运算精度（小数点后位数）
    DEFAULT_DIV_SCALE = 10

    # 默认舍入模式
    DEFAULT_ROUNDING_MODE = ROUND_HALF_UP

    # 0-20对应的阶乘，超过20的阶乘会使用math.factorial计算
    FACTORIALS = [
        1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800,
        39916800, 479001600, 6227020800, 87178291200, 1307674368000,
        20922789888000, 355687428096000, 6402373705728000,
        121645100408832000, 2432902008176640000
    ]

    # 数字格式模式正则表达式
    NUMBER_PATTERN = re.compile(r'^[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?$')

    # 内存缓存：常用Decimal值
    _DECIMAL_CACHE = {
        '0': Decimal('0'),
        '1': Decimal('1'),
        '10': Decimal('10'),
        '100': Decimal('100'),
        '1000': Decimal('1000'),
    }

    @staticmethod
    def to_decimal(value: Any, default: Optional[Decimal] = None) -> Decimal:
        """
        将任意值安全转换为Decimal类型

        Args:
            value: 要转换的值，可以是数字、字符串等
            default: 转换失败时的默认值，默认为Decimal('0')

        Returns:
            Decimal对象

        Raises:
            TypeError: 当value类型不支持转换时
            ValueError: 当value格式不正确时

        Examples:
            >> NumberUtil.to_decimal(10)
            Decimal('10')
            >> NumberUtil.to_decimal("3.14")
            Decimal('3.14')
            >> NumberUtil.to_decimal("abc", Decimal('0'))
            Decimal('0')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        if value is None:
            return default

        # 已经是Decimal类型，直接返回
        if isinstance(value, Decimal):
            return value

        # 处理布尔值
        if isinstance(value, bool):
            return Decimal('1') if value else Decimal('0')

        # 处理整数和浮点数
        if isinstance(value, (int, float)):
            try:
                # 使用字符串转换避免浮点数精度问题
                return Decimal(str(value))
            except (ValueError, InvalidOperation):
                return default

        # 处理字符串
        if isinstance(value, str):
            # 去除空格和可能的分隔符（如逗号）
            cleaned_value = value.strip().replace(',', '')
            if not cleaned_value:
                return default

            try:
                return Decimal(cleaned_value)
            except (ValueError, InvalidOperation):
                return default

        # 处理其他可转换为数字的类型
        try:
            # 尝试转换为字符串再处理
            str_value = str(value)
            return NumberUtil.to_decimal(str_value, default)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def add(*values: Any, default: Optional[Decimal] = None) -> Decimal:
        """
        提供精确的加法运算

        Args:
            values: 多个被加值
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            和

        Examples:
            >> NumberUtil.add(0.1, 0.2)
            Decimal('0.3')
            >> NumberUtil.add(1, 2, 3)
            Decimal('6')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        if not values:
            return default

        try:
            result = NumberUtil._DECIMAL_CACHE['0']
            for value in values:
                if value is not None:
                    result += NumberUtil.to_decimal(value, default)
            return result
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def sub(*values: Any, default: Optional[Decimal] = None) -> Decimal:
        """
        提供精确的减法运算

        Args:
            values: 多个被减值，第一个为被减数，其余为减数
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            差

        Examples:
            >> NumberUtil.sub(10, 3)
            Decimal('7')
            >> NumberUtil.sub(10, 2, 1)
            Decimal('7')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        if not values:
            return default

        try:
            result = NumberUtil.to_decimal(values[0], default)
            for value in values[1:]:
                if value is not None:
                    result -= NumberUtil.to_decimal(value, default)
            return result
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def mul(*values: Any, default: Optional[Decimal] = None) -> Decimal:
        """
        提供精确的乘法运算

        Args:
            values: 多个被乘值
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            积

        Examples:
            >> NumberUtil.mul(2, 3)
            Decimal('6')
            >> NumberUtil.mul(1.5, 2)
            Decimal('3.0')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        if not values:
            return default

        try:
            result = NumberUtil._DECIMAL_CACHE['1']
            for value in values:
                if value is not None:
                    result *= NumberUtil.to_decimal(value, default)
            return result
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def div(dividend: Any, divisor: Any, scale: int = DEFAULT_DIV_SCALE,
            rounding_mode: str = DEFAULT_ROUNDING_MODE,
            default: Optional[Decimal] = None) -> Decimal:
        """
        提供(相对)精确的除法运算

        Args:
            dividend: 被除数
            divisor: 除数
            scale: 精确度，小数点后位数
            rounding_mode: 舍入模式
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            商

        Raises:
            ZeroDivisionError: 当除数为零时

        Examples:
            >> NumberUtil.div(10, 3)
            Decimal('3.3333333333')
            >> NumberUtil.div(10, 4, scale=2)
            Decimal('2.50')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        try:
            divisor_decimal = NumberUtil.to_decimal(divisor)
            if divisor_decimal == NumberUtil._DECIMAL_CACHE['0']:
                raise ZeroDivisionError("Division by zero")

            dividend_decimal = NumberUtil.to_decimal(dividend)
            result = dividend_decimal / divisor_decimal

            # 应用舍入
            return result.quantize(
                Decimal('1.' + '0' * scale),
                rounding=rounding_mode
            )
        except (TypeError, ValueError, InvalidOperation, ZeroDivisionError):
            return default

    @staticmethod
    def round(value: Any, scale: int = 0,
              rounding_mode: str = DEFAULT_ROUNDING_MODE,
              default: Optional[Decimal] = None) -> Decimal:
        """
        保留固定位数小数

        Args:
            value: 要舍入的值
            scale: 保留小数位数
            rounding_mode: 舍入模式
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            舍入后的值

        Examples:
            >> NumberUtil.round(3.14159, 2)
            Decimal('3.14')
            >> NumberUtil.round(2.678, 0)
            Decimal('3')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        try:
            decimal_value = NumberUtil.to_decimal(value)
            return decimal_value.quantize(
                Decimal('1.' + '0' * scale),
                rounding=rounding_mode
            )
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def round_half_even(value: Any, scale: int = 0,
                       default: Optional[Decimal] = None) -> Decimal:
        """
        四舍六入五成双计算法（银行家舍入法）

        Args:
            value: 要舍入的值
            scale: 保留小数位数
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            舍入后的值

        Examples:
            >> NumberUtil.round_half_even(2.5, 0)
            Decimal('2')
            >> NumberUtil.round_half_even(3.5, 0)
            Decimal('4')
        """
        return NumberUtil.round(value, scale, ROUND_HALF_EVEN, default)

    @staticmethod
    def round_down(value: Any, scale: int = 0,
                  default: Optional[Decimal] = None) -> Decimal:
        """
        保留固定小数位数，舍去多余位数

        Args:
            value: 要舍入的值
            scale: 保留小数位数
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            舍入后的值

        Examples:
            >> NumberUtil.round_down(3.14159, 2)
            Decimal('3.14')
            >> NumberUtil.round_down(3.999, 0)
            Decimal('3')
        """
        return NumberUtil.round(value, scale, ROUND_DOWN, default)

    @staticmethod
    def decimal_format(value: Any, pattern: str,
                      default: Optional[str] = None) -> str:
        """
        格式化数字输出

        Args:
            value: 要格式化的值
            pattern: 格式模式，支持：
                    ",##0.00" - 千分位分隔，两位小数
                    "0.00"    - 两位小数
                    "0"       - 整数
                    "0.##"    - 最多两位小数
                    "0.0###"  - 最多四位小数，至少一位
                    "percent" - 百分比格式
                    "scientific" - 科学计数法
            default: 格式化失败时的默认值，默认为"0"

        Returns:
            格式化后的字符串

        Examples:
            >> NumberUtil.decimal_format(1234.567, ",##0.00")
            '1,234.57'
            >> NumberUtil.decimal_format(0.25, "percent")
            '25.00%'
        """
        if default is None:
            default = "0"

        try:
            decimal_value = NumberUtil.to_decimal(value)

            if pattern == ",##0.00":
                # 千分位分隔，两位小数
                return f"{decimal_value:,.2f}"
            elif pattern == "0.00":
                # 两位小数
                return f"{decimal_value:.2f}"
            elif pattern == "0":
                # 整数
                return f"{decimal_value:.0f}"
            elif pattern == "0.##":
                # 最多两位小数
                return f"{decimal_value:.2f}".rstrip('0').rstrip('.')
            elif pattern == "0.0###":
                # 最多四位小数，至少一位
                formatted = f"{decimal_value:.4f}"
                return formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
            elif pattern == "percent":
                # 百分比格式
                return f"{decimal_value * 100:.2f}%"
            elif pattern == "scientific":
                # 科学计数法
                return f"{decimal_value:.2e}"
            else:
                # 默认实现
                return str(decimal_value)
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def is_number(value: Any) -> bool:
        """
        判断是否为数字

        Args:
            value: 要判断的值

        Returns:
            是否为数字

        Examples:
            >> NumberUtil.is_number(123)
            True
            >> NumberUtil.is_number("abc")
            False
            >> NumberUtil.is_number("123.45")
            True
        """
        if value is None:
            return False

        if isinstance(value, (int, float, Decimal)):
            return True

        if isinstance(value, str):
            # 去除可能的分隔符和空格
            cleaned_value = value.strip().replace(',', '')
            if not cleaned_value:
                return False

            # 检查是否为数字格式
            return NumberUtil.NUMBER_PATTERN.match(cleaned_value) is not None

        # 检查其他可转换为数字的类型
        try:
            NumberUtil.to_decimal(value)
            return True
        except (TypeError, ValueError, InvalidOperation):
            return False

    @staticmethod
    def is_integer(value: Any) -> bool:
        """
        判断是否为整数

        Args:
            value: 要判断的值

        Returns:
            是否为整数

        Examples:
            >> NumberUtil.is_integer(123)
            True
            >> NumberUtil.is_integer(123.45)
            False
            >> NumberUtil.is_integer("123")
            True
        """
        if not NumberUtil.is_number(value):
            return False

        try:
            decimal_value = NumberUtil.to_decimal(value)
            return decimal_value == decimal_value.to_integral_value()
        except (TypeError, ValueError, InvalidOperation):
            return False

    @staticmethod
    def is_float(value: Any) -> bool:
        """
        判断是否为浮点数（有小数部分）

        Args:
            value: 要判断的值

        Returns:
            是否为浮点数

        Examples:
            >> NumberUtil.is_float(123)
            False
            >> NumberUtil.is_float(123.45)
            True
            >> NumberUtil.is_float("123.45")
            True
        """
        if not NumberUtil.is_number(value):
            return False

        try:
            decimal_value = NumberUtil.to_decimal(value)
            return decimal_value != decimal_value.to_integral_value()
        except (TypeError, ValueError, InvalidOperation):
            return False

    @staticmethod
    def factorial(n: int) -> int:
        """
        计算阶乘

        Args:
            n: 阶乘数，必须大于等于0

        Returns:
            阶乘结果

        Raises:
            ValueError: 当n为负数或超过系统限制时

        Examples:
            >> NumberUtil.factorial(5)
            120
            >> NumberUtil.factorial(0)
            1
        """
        if n < 0:
            raise ValueError("Factorial must have n >= 0")

        if n <= 20:
            return NumberUtil.FACTORIALS[n]
        else:
            # 对于大于20的数，使用math.factorial
            return math.factorial(n)

    @staticmethod
    def max(*values: Any, default: Optional[Decimal] = None) -> Decimal:
        """
        取最大值

        Args:
            values: 多个值
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            最大值

        Examples:
            >> NumberUtil.max(1, 2, 3)
            Decimal('3')
            >> NumberUtil.max()
            Decimal('0')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        if not values:
            return default

        try:
            decimal_values = [NumberUtil.to_decimal(v, default) for v in values if v is not None]
            return max(decimal_values) if decimal_values else default
        except (TypeError, ValueError):
            return default

    @staticmethod
    def min(*values: Any, default: Optional[Decimal] = None) -> Decimal:
        """
        取最小值

        Args:
            values: 多个值
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            最小值

        Examples:
            >> NumberUtil.min(1, 2, 3)
            Decimal('1')
            >> NumberUtil.min()
            Decimal('0')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        if not values:
            return default

        try:
            decimal_values = [NumberUtil.to_decimal(v, default) for v in values if v is not None]
            return min(decimal_values) if decimal_values else default
        except (TypeError, ValueError):
            return default

    @staticmethod
    def equals(value1: Any, value2: Any, precision: Optional[int] = None) -> bool:
        """
        比较两个数字是否相等（可指定精度）

        Args:
            value1: 第一个值
            value2: 第二个值
            precision: 比较精度（小数点后位数），None表示精确比较

        Returns:
            是否相等

        Examples:
            >> NumberUtil.equals(0.1 + 0.2, 0.3)
            True
            >> NumberUtil.equals(1.2345, 1.2346, 3)
            True
        """
        try:
            decimal1 = NumberUtil.to_decimal(value1)
            decimal2 = NumberUtil.to_decimal(value2)

            if precision is None:
                return decimal1 == decimal2
            else:
                # 使用指定精度比较
                rounded1 = NumberUtil.round(decimal1, precision)
                rounded2 = NumberUtil.round(decimal2, precision)
                return rounded1 == rounded2
        except (TypeError, ValueError, InvalidOperation):
            return False

    @staticmethod
    def is_greater(value1: Any, value2: Any) -> bool:
        """
        比较第一个值是否大于第二个值

        Args:
            value1: 第一个值
            value2: 第二个值

        Returns:
            是否大于

        Examples:
            >> NumberUtil.is_greater(3, 2)
            True
            >> NumberUtil.is_greater(1, 2)
            False
        """
        try:
            decimal1 = NumberUtil.to_decimal(value1)
            decimal2 = NumberUtil.to_decimal(value2)
            return decimal1 > decimal2
        except (TypeError, ValueError, InvalidOperation):
            return False

    @staticmethod
    def is_less(value1: Any, value2: Any) -> bool:
        """
        比较第一个值是否小于第二个值

        Args:
            value1: 第一个值
            value2: 第二个值

        Returns:
            是否小于

        Examples:
            >> NumberUtil.is_less(1, 2)
            True
            >> NumberUtil.is_less(3, 2)
            False
        """
        try:
            decimal1 = NumberUtil.to_decimal(value1)
            decimal2 = NumberUtil.to_decimal(value2)
            return decimal1 < decimal2
        except (TypeError, ValueError, InvalidOperation):
            return False

    @staticmethod
    def to_str(value: Any, scale: Optional[int] = None,
              default: Optional[str] = None) -> str:
        """
        数字转字符串

        Args:
            value: 要转换的值
            scale: 保留小数位数，None表示不处理
            default: 转换失败时的默认值，默认为"0"

        Returns:
            字符串表示

        Examples:
            >> NumberUtil.to_str(1234.567, 2)
            '1234.57'
            >> NumberUtil.to_str(1234.567)
            '1234.567'
        """
        if default is None:
            default = "0"

        try:
            decimal_value = NumberUtil.to_decimal(value)

            if scale is not None:
                decimal_value = NumberUtil.round(decimal_value, scale)

            # 去除末尾多余的0和小数点
            result = str(decimal_value).rstrip('0').rstrip('.')
            return result if result != '' else '0'
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def to_int(value: Any, default: Optional[int] = None) -> int:
        """
        转换为整数

        Args:
            value: 要转换的值
            default: 转换失败时的默认值，默认为0

        Returns:
            整数值

        Examples:
            >> NumberUtil.to_int("123")
            123
            >> NumberUtil.to_int("123.45")
            123
        """
        if default is None:
            default = 0

        try:
            decimal_value = NumberUtil.to_decimal(value)
            return int(decimal_value.to_integral_value())
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def to_float(value: Any, default: Optional[float] = None) -> float:
        """
        转换为浮点数

        Args:
            value: 要转换的值
            default: 转换失败时的默认值，默认为0.0

        Returns:
            浮点数值

        Examples:
            >> NumberUtil.to_float("123.45")
            123.45
            >> NumberUtil.to_float("abc", 0.0)
            0.0
        """
        if default is None:
            default = 0.0

        try:
            decimal_value = NumberUtil.to_decimal(value)
            return float(decimal_value)
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def parse_number(number_str: str, default: Optional[Decimal] = None) -> Decimal:
        """
        解析数字字符串

        Args:
            number_str: 数字字符串
            default: 解析失败时的默认值，默认为Decimal('0')

        Returns:
            Decimal值

        Examples:
            >> NumberUtil.parse_number("1,234.56")
            Decimal('1234.56')
            >> NumberUtil.parse_number("abc")
            Decimal('0')
        """
        return NumberUtil.to_decimal(number_str, default)

    @staticmethod
    def generate_random_number(begin: int, end: int, count: int) -> List[int]:
        """
        生成不重复随机数

        Args:
            begin: 起始值（包含）
            end: 结束值（不包含）
            count: 生成数量

        Returns:
            随机数列表

        Raises:
            ValueError: 当count大于范围或参数无效时

        Examples:
            >> random_nums = NumberUtil.generate_random_number(1, 10, 5)
            >> len(random_nums)
            5
        """
        if count > (end - begin):
            raise ValueError("Count cannot be larger than the range")

        if count < 0:
            raise ValueError("Count cannot be negative")

        if begin >= end:
            raise ValueError("Begin must be less than end")

        return random.sample(range(begin, end), count)

    @staticmethod
    def range(begin: int, end: int, step: int = 1) -> List[int]:
        """
        生成整数范围列表

        Args:
            begin: 起始值
            end: 结束值
            step: 步长

        Returns:
            整数列表

        Examples:
            >> NumberUtil.range(1, 5)
            [1, 2, 3, 4]
            >> NumberUtil.range(1, 10, 2)
            [1, 3, 5, 7, 9]
        """
        if step == 0:
            raise ValueError("Step cannot be zero")

        return list(range(begin, end, step))

    @staticmethod
    def percent(value: Any, total: Any, scale: int = 2,
               default: Optional[Decimal] = None) -> Decimal:
        """
        计算百分比

        Args:
            value: 部分值
            total: 总值
            scale: 保留小数位数
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            百分比

        Examples:
            >> NumberUtil.percent(25, 100)
            Decimal('25.00')
            >> NumberUtil.percent(1, 3, 1)
            Decimal('33.3')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        try:
            total_decimal = NumberUtil.to_decimal(total)
            if total_decimal == NumberUtil._DECIMAL_CACHE['0']:
                return default

            percent_value = (NumberUtil.to_decimal(value) / total_decimal) * 100
            return NumberUtil.round(percent_value, scale)
        except (TypeError, ValueError, InvalidOperation, ZeroDivisionError):
            return default

    @staticmethod
    def is_prime(n: int) -> bool:
        """
        判断是否为质数（素数）

        Args:
            n: 要判断的数字

        Returns:
            是否为质数

        Examples:
            >> NumberUtil.is_prime(7)
            True
            >> NumberUtil.is_prime(8)
            False
        """
        if n < 2:
            return False

        if n == 2:
            return True

        if n % 2 == 0:
            return False

        # 检查从3到sqrt(n)的奇数
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False

        return True

    @staticmethod
    def gcd(a: int, b: int) -> int:
        """
        计算最大公约数

        Args:
            a: 第一个数
            b: 第二个数

        Returns:
            最大公约数

        Examples:
            >> NumberUtil.gcd(12, 18)
            6
            >> NumberUtil.gcd(0, 5)
            5
        """
        while b != 0:
            a, b = b, a % b
        return abs(a)

    @staticmethod
    def lcm(a: int, b: int) -> int:
        """
        计算最小公倍数

        Args:
            a: 第一个数
            b: 第二个数

        Returns:
            最小公倍数

        Examples:
            >> NumberUtil.lcm(12, 18)
            36
            >> NumberUtil.lcm(0, 5)
            0
        """
        if a == 0 or b == 0:
            return 0
        return abs(a * b) // NumberUtil.gcd(a, b)

    @staticmethod
    def to_binary(n: int) -> str:
        """
        转换为二进制字符串

        Args:
            n: 整数

        Returns:
            二进制字符串

        Examples:
            >> NumberUtil.to_binary(10)
            '1010'
            >> NumberUtil.to_binary(0)
            '0'
        """
        return bin(n)[2:]

    @staticmethod
    def from_binary(binary_str: str) -> int:
        """
        从二进制字符串转换为整数

        Args:
            binary_str: 二进制字符串

        Returns:
            整数值

        Examples:
            >> NumberUtil.from_binary("1010")
            10
            >> NumberUtil.from_binary("0")
            0
        """
        return int(binary_str, 2)

    @staticmethod
    def to_hex(n: int) -> str:
        """
        转换为十六进制字符串

        Args:
            n: 整数

        Returns:
            十六进制字符串

        Examples:
            >> NumberUtil.to_hex(255)
            'ff'
            >> NumberUtil.to_hex(0)
            '0'
        """
        return hex(n)[2:]

    @staticmethod
    def from_hex(hex_str: str) -> int:
        """
        从十六进制字符串转换为整数

        Args:
            hex_str: 十六进制字符串

        Returns:
            整数值

        Examples:
            >> NumberUtil.from_hex("ff")
            255
            >> NumberUtil.from_hex("0")
            0
        """
        return int(hex_str, 16)

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        格式化文件大小显示

        Args:
            size_bytes: 字节大小

        Returns:
            格式化后的字符串

        Examples:
            >> NumberUtil.format_size(1024)
            '1.00 KB'
            >> NumberUtil.format_size(1536)
            '1.50 KB'
        """
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        i = 0
        size = float(size_bytes)

        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024
            i += 1

        # 根据大小选择合适的精度
        if i == 0:  # B
            precision = 0
        elif size < 10:  # 小于10用2位小数
            precision = 2
        elif size < 100:  # 小于100用1位小数
            precision = 1
        else:  # 大于100用0位小数
            precision = 0

        return f"{size:.{precision}f} {size_names[i]}"

    @staticmethod
    def scientific_notation(value: Any, precision: int = 4,
                           default: Optional[str] = None) -> str:
        """
        转换为科学计数法表示

        Args:
            value: 要转换的值
            precision: 精度
            default: 转换失败时的默认值，默认为"0"

        Returns:
            科学计数法字符串

        Examples:
            >> NumberUtil.scientific_notation(123456789)
            '1.2346e+08'
            >> NumberUtil.scientific_notation(0.0000123456, 2)
            '1.23e-05'
        """
        if default is None:
            default = "0"

        try:
            decimal_value = NumberUtil.to_decimal(value)
            return f"{decimal_value:.{precision}E}"
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def mean(*values: Any, default: Optional[Decimal] = None) -> Decimal:
        """
        计算平均值

        Args:
            values: 多个值
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            平均值

        Examples:
            >> NumberUtil.mean(1, 2, 3, 4, 5)
            Decimal('3')
            >> NumberUtil.mean()
            Decimal('0')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        if not values:
            return default

        try:
            decimal_values = [NumberUtil.to_decimal(v, default) for v in values if v is not None]
            if not decimal_values:
                return default

            sum_val = sum(decimal_values)
            return sum_val / len(decimal_values)
        except (TypeError, ValueError, InvalidOperation, ZeroDivisionError):
            return default

    @staticmethod
    def median(*values: Any, default: Optional[Decimal] = None) -> Decimal:
        """
        计算中位数

        Args:
            values: 多个值
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            中位数

        Examples:
            >> NumberUtil.median(1, 2, 3, 4, 5)
            Decimal('3')
            >> NumberUtil.median(1, 2, 3, 4)
            Decimal('2.5')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        if not values:
            return default

        try:
            decimal_values = [NumberUtil.to_decimal(v, default) for v in values if v is not None]
            if not decimal_values:
                return default

            decimal_values.sort()
            n = len(decimal_values)

            if n % 2 == 1:
                return decimal_values[n // 2]
            else:
                mid = n // 2
                return (decimal_values[mid - 1] + decimal_values[mid]) / 2
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def clamp(value: Any, min_val: Any, max_val: Any,
             default: Optional[Decimal] = None) -> Decimal:
        """
        将值限制在指定范围内

        Args:
            value: 要限制的值
            min_val: 最小值
            max_val: 最大值
            default: 计算失败时的默认值，默认为Decimal('0')

        Returns:
            限制后的值

        Examples:
            >> NumberUtil.clamp(15, 0, 10)
            Decimal('10')
            >> NumberUtil.clamp(-5, 0, 10)
            Decimal('0')
        """
        if default is None:
            default = NumberUtil._DECIMAL_CACHE['0']

        try:
            decimal_value = NumberUtil.to_decimal(value, default)
            decimal_min = NumberUtil.to_decimal(min_val, default)
            decimal_max = NumberUtil.to_decimal(max_val, default)

            if decimal_value < decimal_min:
                return decimal_min
            elif decimal_value > decimal_max:
                return decimal_max
            else:
                return decimal_value
        except (TypeError, ValueError, InvalidOperation):
            return default

    @staticmethod
    def is_between(value: Any, min_val: Any, max_val: Any) -> bool:
        """
        判断值是否在指定范围内

        Args:
            value: 要判断的值
            min_val: 最小值
            max_val: 最大值

        Returns:
            是否在范围内

        Examples:
            >> NumberUtil.is_between(5, 0, 10)
            True
            >> NumberUtil.is_between(15, 0, 10)
            False
        """
        try:
            decimal_value = NumberUtil.to_decimal(value)
            decimal_min = NumberUtil.to_decimal(min_val)
            decimal_max = NumberUtil.to_decimal(max_val)

            return decimal_min <= decimal_value <= decimal_max
        except (TypeError, ValueError, InvalidOperation):
            return False


# 单元测试和示例
if __name__ == '__main__':
    # 测试基本功能
    print("数字工具类测试")
    print("=" * 50)

    # 1. 基本计算
    print("\n1. 基本计算:")
    print(f"0.1 + 0.2 = {NumberUtil.add(0.1, 0.2)}")
    print(f"10 / 3 (保留5位小数) = {NumberUtil.div(10, 3, 5)}")

    # 2. 舍入测试
    print("\n2. 舍入测试:")
    print(f"3.14159 舍入到2位小数: {NumberUtil.round(3.14159, 2)}")
    print(f"2.5 银行家舍入: {NumberUtil.round_half_even(2.5, 0)}")
    print(f"3.5 银行家舍入: {NumberUtil.round_half_even(3.5, 0)}")

    # 3. 数字判断
    print("\n3. 数字判断:")
    print(f"'123.45' 是数字吗? {NumberUtil.is_number('123.45')}")
    print(f"'abc' 是数字吗? {NumberUtil.is_number('abc')}")
    print(f"123 是整数吗? {NumberUtil.is_integer(123)}")
    print(f"123.45 是浮点数吗? {NumberUtil.is_float(123.45)}")

    # 4. 数学计算
    print("\n4. 数学计算:")
    print(f"5的阶乘: {NumberUtil.factorial(5)}")
    print(f"12和18的最大公约数: {NumberUtil.gcd(12, 18)}")
    print(f"12和18的最小公倍数: {NumberUtil.lcm(12, 18)}")
    print(f"7是质数吗? {NumberUtil.is_prime(7)}")

    # 5. 格式化测试
    print("\n5. 格式化测试:")
    print(f"1234.567 千分位格式化: {NumberUtil.decimal_format(1234.567, ',##0.00')}")
    print(f"0.25 百分比格式化: {NumberUtil.decimal_format(0.25, 'percent')}")
    print(f"123456789 科学计数法: {NumberUtil.scientific_notation(123456789, 2)}")
    print(f"1024 文件大小格式化: {NumberUtil.format_size(1024)}")

    # 6. 进制转换
    print("\n6. 进制转换:")
    print(f"10 转二进制: {NumberUtil.to_binary(10)}")
    print(f"'1010' 转十进制: {NumberUtil.from_binary('1010')}")
    print(f"255 转十六进制: {NumberUtil.to_hex(255)}")
    print(f"'ff' 转十进制: {NumberUtil.from_hex('ff')}")

    # 7. 统计函数
    print("\n7. 统计函数:")
    print(f"1,2,3,4,5 的平均值: {NumberUtil.mean(1, 2, 3, 4, 5)}")
    print(f"1,2,3,4,5 的中位数: {NumberUtil.median(1, 2, 3, 4, 5)}")

    # 8. 范围限制
    print("\n8. 范围限制:")
    print(f"15 限制在0-10范围内: {NumberUtil.clamp(15, 0, 10)}")
    print(f"5 是否在0-10范围内? {NumberUtil.is_between(5, 0, 10)}")

    print("\n测试完成!")