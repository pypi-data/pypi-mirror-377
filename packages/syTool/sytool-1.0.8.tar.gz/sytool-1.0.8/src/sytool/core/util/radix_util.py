"""
任意进制转换工具类 (RadixUtil)
参考Java Hutool RadixUtil设计，提供灵活的进制转换功能

主要功能：
1. 支持任意进制的编码和解码
2. 支持自定义字符集
3. 支持负数处理（使用补码方式）
4. 提供常用预定义字符集（如34进制、59进制）
5. 生成随机字符集以增强安全性

应用场景：
1. 根据ID生成邀请码，缩短长度并隐藏与ID的关联
2. 短链接生成，将ID转换为短链接格式
3. 数字加密，通过不同进制转换让有规律的数字看起来无规律

设计原则：
- 精度优先：确保大数转换的准确性
- 异常安全：合理的错误处理和清晰的错误信息
- 性能均衡：在精度和性能之间取得平衡
- 易于使用：提供简洁的API和完整的文档

参考实现：
- Java Hutool RadixUtil
- Python 标准库最佳实践
"""

import string
import random
import secrets
from typing import Union, Optional, Tuple, List
from numbers import Number


class RadixUtil:
    """
    任意进制转换工具类

    提供任意进制之间的转换功能，支持自定义字符集和负数处理。
    所有方法都是静态方法，无需实例化即可使用。
    """

    # 预定义字符集常量
    RADIXS_34: str = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # 34进制，不含IO字符
    RADIXS_SHUFFLE_34: str = "H3UM16TDFPSBZJ90CW28QYRE45AXKNGV7L"  # 打乱的34进制
    RADIXS_59: str = "0123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"  # 59进制，不含IOl字符
    RADIXS_SHUFFLE_59: str = "vh9wGkfK8YmqbsoENP3764SeCX0dVzrgy1HRtpnTaLjJW2xQiZAcBMUFDu5"  # 打乱的59进制

    # 常用进制字符集
    BINARY: str = "01"  # 二进制
    OCTAL: str = "01234567"  # 八进制
    DECIMAL: str = "0123456789"  # 十进制
    HEXADECIMAL: str = "0123456789ABCDEF"  # 十六进制
    BASE36: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # 36进制
    BASE62: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"  # 62进制

    @staticmethod
    def encode(radixs: str, num: Union[int, str], handle_negative: bool = True) -> str:
        """
        将整数值转换为自定义进制的字符串表示

        Args:
            radixs: 自定义进制字符集，不能有重复字符，至少2个字符
            num: 要转换的数值（整数或数字字符串）
            handle_negative: 是否处理负数（使用补码方式）

        Returns:
            str: 自定义进制字符串

        Raises:
            ValueError: 如果字符集无效或输入数字无效
            TypeError: 如果输入类型不支持

        Examples:
            >> RadixUtil.encode("01", 10)  # 二进制编码
            '1010'
            >> RadixUtil.encode("AB", 10)  # 自定义二进制编码
            'BABA'
            >> RadixUtil.encode(RadixUtil.RADIXS_34, 12345)
            'C7P'
        """
        # 参数验证
        RadixUtil._validate_radixs(radixs)
        num_int = RadixUtil._parse_num(num)

        # 处理负数
        if num_int < 0 and handle_negative:
            # 使用64位补码表示负数（比32位更通用）
            num_int = (1 << 64) + num_int

        base = len(radixs)

        # 特殊情况处理
        if num_int == 0:
            return radixs[0]

        # 计算结果
        result_chars = []
        temp_num = num_int

        while temp_num > 0:
            remainder = temp_num % base
            result_chars.append(radixs[remainder])
            temp_num //= base

        # 反转字符列表得到正确顺序
        result_chars.reverse()

        return ''.join(result_chars)

    @staticmethod
    def encode_long(radixs: str, num: Union[int, str]) -> str:
        """
        将长整数值转换为自定义进制的字符串表示（支持更大范围的数值）

        Args:
            radixs: 自定义进制字符集，不能有重复字符，至少2个字符
            num: 要转换的数值（整数或数字字符串）

        Returns:
            str: 自定义进制字符串

        Raises:
            ValueError: 如果字符集无效、输入数字无效或输入负数

        Examples:
            >> RadixUtil.encode_long(RadixUtil.RADIXS_59, 2**50)
            'Du5vh9wGk'
        """
        # 参数验证
        RadixUtil._validate_radixs(radixs)
        num_int = RadixUtil._parse_num(num)

        if num_int < 0:
            raise ValueError("长整数版本暂不支持负数")

        return RadixUtil.encode(radixs, num_int, handle_negative=False)

    @staticmethod
    def decode(radixs: str, encoded_str: str, handle_negative: bool = True) -> int:
        """
        将自定义进制的字符串还原为整数值

        Args:
            radixs: 自定义进制字符集，需要与encode时使用的保持一致
            encoded_str: 需要转换的自定义进制字符串
            handle_negative: 是否处理负数（补码解码）

        Returns:
            int: 十进制整数值

        Raises:
            ValueError: 如果字符集无效或编码字符串包含无效字符

        Examples:
            >> RadixUtil.decode("01", "1010")  # 二进制解码
            10
            >> RadixUtil.decode("AB", "BABA")  # 自定义二进制解码
            10
        """
        # 参数验证
        RadixUtil._validate_radixs(radixs)

        if not encoded_str:
            return 0

        base = len(radixs)
        result = 0

        for char in encoded_str:
            # 查找字符在字符集中的位置
            index = radixs.find(char)
            if index == -1:
                raise ValueError(f"字符 '{char}' 不在自定义进制字符集中")
            result = result * base + index

        # 处理负数（补码解码）
        if handle_negative and result > (1 << 63):
            result = result - (1 << 64)

        return result

    @staticmethod
    def decode_to_int(radixs: str, encoded_str: str) -> int:
        """
        将自定义进制的字符串还原为整数值
        这是decode方法的别名，为了与Java版本保持API一致性

        Args:
            radixs: 自定义进制字符集
            encoded_str: 编码字符串

        Returns:
            int: 整数值
        """
        return RadixUtil.decode(radixs, encoded_str)

    @staticmethod
    def is_valid_radixs(radixs: str) -> bool:
        """
        检查自定义进制字符集是否有效

        Args:
            radixs: 要检查的字符集

        Returns:
            bool: 是否有效

        Examples:
            >> RadixUtil.is_valid_radixs("ABC")
            True
            >> RadixUtil.is_valid_radixs("AAB")  # 有重复字符
            False
        """
        if not radixs or len(radixs) < 2:
            return False

        return len(set(radixs)) == len(radixs)

    @staticmethod
    def generate_shuffled_radixs(base: int, seed: Optional[int] = None) -> str:
        """
        生成打乱顺序的进制字符集（增强混淆性）

        Args:
            base: 进制基数，必须在2到62之间
            seed: 随机种子（用于确保可重复性），如果为None则使用随机种子

        Returns:
            str: 打乱后的字符集

        Raises:
            ValueError: 如果基数不在2-62之间

        Examples:
            >> shuffled = RadixUtil.generate_shuffled_radixs(16, 42)
            >> len(shuffled)
            16
        """
        if base < 2 or base > 62:
            raise ValueError("进制基数必须在2到62之间")

        # 生成基础字符集（数字+大写字母+小写字母）
        digits = string.digits + string.ascii_uppercase + string.ascii_lowercase
        base_chars = digits[:base]

        # 打乱字符顺序
        chars_list = list(base_chars)
        if seed is not None:
            random.seed(seed)
        random.shuffle(chars_list)

        return ''.join(chars_list)

    @staticmethod
    def generate_random_radixs(base: int) -> str:
        """
        生成随机顺序的进制字符集（增强安全性，使用加密强度随机数）

        Args:
            base: 进制基数，必须在2到62之间

        Returns:
            str: 随机顺序的字符集

        Raises:
            ValueError: 如果基数不在2-62之间

        Examples:
            >> random_radixs = RadixUtil.generate_random_radixs(16)
            >> len(random_radixs)
            16
        """
        if base < 2 or base > 62:
            raise ValueError("进制基数必须在2到62之间")

        # 生成基础字符集（数字+大写字母+小写字母）
        digits = string.digits + string.ascii_uppercase + string.ascii_lowercase
        base_chars = digits[:base]

        # 随机打乱字符顺序（使用加密强度随机数）
        chars_list = list(base_chars)

        # Fisher-Yates洗牌算法（安全版本）
        for i in range(len(chars_list) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            chars_list[i], chars_list[j] = chars_list[j], chars_list[i]

        return ''.join(chars_list)

    @staticmethod
    def convert(radixs_from: str, radixs_to: str, value: str) -> str:
        """
        直接在两个自定义进制之间转换

        Args:
            radixs_from: 源进制字符集
            radixs_to: 目标进制字符集
            value: 要转换的值

        Returns:
            str: 转换后的值

        Examples:
            >> RadixUtil.convert(RadixUtil.DECIMAL, RadixUtil.HEXADECIMAL, "255")
            'FF'
        """
        # 先解码到十进制，再编码到目标进制
        decimal_value = RadixUtil.decode(radixs_from, value)
        return RadixUtil.encode(radixs_to, decimal_value)

    @staticmethod
    def get_min_length(radixs: str, max_value: int) -> int:
        """
        计算表示指定最大值所需的最小字符串长度

        Args:
            radixs: 进制字符集
            max_value: 最大值

        Returns:
            int: 最小字符串长度

        Examples:
            >> RadixUtil.get_min_length(RadixUtil.BINARY, 1024)
            11
        """
        RadixUtil._validate_radixs(radixs)

        base = len(radixs)
        length = 0
        value = max_value

        while value > 0:
            value //= base
            length += 1

        return max(length, 1)  # 至少需要1位

    @staticmethod
    def validate(radixs: str, value: str) -> bool:
        """
        验证值是否在指定进制中有效

        Args:
            radixs: 进制字符集
            value: 要验证的值

        Returns:
            bool: 是否有效

        Examples:
            >> RadixUtil.validate(RadixUtil.HEXADECIMAL, "FF")
            True
            >> RadixUtil.validate(RadixUtil.HEXADECIMAL, "FG")
            False
        """
        if not value:
            return False

        RadixUtil._validate_radixs(radixs)

        for char in value:
            if char not in radixs:
                return False

        return True

    @staticmethod
    def _validate_radixs(radixs: str) -> None:
        """
        验证字符集是否有效

        Args:
            radixs: 字符集

        Raises:
            ValueError: 如果字符集无效
        """
        if not radixs:
            raise ValueError("自定义进制字符集不能为空")

        if len(radixs) < 2:
            raise ValueError("自定义进制字符集至少需要2个字符")

        if len(set(radixs)) != len(radixs):
            raise ValueError("自定义进制字符集不能包含重复字符")

    @staticmethod
    def _parse_num(num: Union[int, str]) -> int:
        """
        解析输入数字为整数

        Args:
            num: 输入数字

        Returns:
            int: 整数值

        Raises:
            ValueError: 如果无法转换为整数
            TypeError: 如果类型不支持
        """
        if isinstance(num, int):
            return num

        if isinstance(num, str):
            try:
                return int(num)
            except ValueError:
                raise ValueError("输入必须是整数或可转换为整数的字符串")

        raise TypeError("输入必须是整数或字符串")


# 单元测试和示例
if __name__ == "__main__":
    import doctest
    import time

    print("RadixUtil示例:")
    print("=" * 50)

    # 1. 基本示例
    print("\n1. 基本示例:")
    print(f"10的二进制: {RadixUtil.encode('01', 10)}")  # 应为BABA
    print(f"10的二进制(AB进制): {RadixUtil.encode('AB', 10)}")  # 应为BABA
    print(f"21的三进制(VIP进制): {RadixUtil.encode('VIP', 21)}")  # 应为PIV

    # 2. 预定义字符集示例
    print("\n2. 预定义字符集示例:")
    test_num = 123456789

    # 34进制转换
    encoded_34 = RadixUtil.encode(RadixUtil.RADIXS_34, test_num)
    decoded_34 = RadixUtil.decode(RadixUtil.RADIXS_34, encoded_34)
    print(f"34进制编码: {test_num} -> {encoded_34} -> {decoded_34}")

    # 打乱34进制转换
    encoded_shuffle_34 = RadixUtil.encode(RadixUtil.RADIXS_SHUFFLE_34, test_num)
    decoded_shuffle_34 = RadixUtil.decode(RadixUtil.RADIXS_SHUFFLE_34, encoded_shuffle_34)
    print(f"打乱34进制编码: {test_num} -> {encoded_shuffle_34} -> {decoded_shuffle_34}")

    # 59进制转换
    encoded_59 = RadixUtil.encode(RadixUtil.RADIXS_59, test_num)
    decoded_59 = RadixUtil.decode(RadixUtil.RADIXS_59, encoded_59)
    print(f"59进制编码: {test_num} -> {encoded_59} -> {decoded_59}")

    # 3. 大数测试
    print("\n3. 大数测试:")
    big_num = 2 ** 50  # 约1千万亿
    encoded_big = RadixUtil.encode_long(RadixUtil.RADIXS_59, big_num)
    decoded_big = RadixUtil.decode(RadixUtil.RADIXS_59, encoded_big)
    print(f"大数编码: {big_num} -> {encoded_big} -> {decoded_big}")

    # 4. 负数测试
    print("\n4. 负数测试:")
    negative_num = -12345
    encoded_neg = RadixUtil.encode(RadixUtil.RADIXS_34, negative_num)
    decoded_neg = RadixUtil.decode(RadixUtil.RADIXS_34, encoded_neg)
    print(f"负数编码: {negative_num} -> {encoded_neg} -> {decoded_neg}")

    # 5. 直接转换示例
    print("\n5. 直接转换示例:")
    direct_convert = RadixUtil.convert(RadixUtil.DECIMAL, RadixUtil.HEXADECIMAL, "255")
    print(f"十进制到十六进制直接转换: 255 -> {direct_convert}")

    # 6. 性能测试
    print("\n6. 性能测试:")
    start_time = time.time()
    for i in range(10000):
        RadixUtil.encode(RadixUtil.RADIXS_34, i)
    end_time = time.time()
    print(f"10000次34进制编码耗时: {(end_time - start_time) * 1000:.2f}ms")

    # 7. 错误处理示例
    print("\n7. 错误处理示例:")
    try:
        RadixUtil.encode("AAB", 10)  # 重复字符
    except ValueError as e:
        print(f"错误处理 - 重复字符: {e}")

    try:
        RadixUtil.encode("A", 10)  # 字符集太短
    except ValueError as e:
        print(f"错误处理 - 字符集太短: {e}")

    try:
        RadixUtil.decode("ABC", "AXY")  # 无效字符
    except ValueError as e:
        print(f"错误处理 - 无效字符: {e}")

    print("\n测试完成!")