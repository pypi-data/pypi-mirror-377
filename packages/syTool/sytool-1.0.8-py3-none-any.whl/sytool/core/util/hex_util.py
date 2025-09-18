"""
十六进制工具类 (HexUtil)
参考Java Hutool HexUtil设计，提供十六进制编码解码、颜色转换、数字转换等功能

主要功能：
1. 十六进制字符串判断和验证
2. 字节数组与十六进制字符串相互转换
3. 字符串与十六进制字符串相互转换
4. 颜色值与十六进制字符串相互转换
5. 数字与十六进制字符串相互转换
6. Unicode字符转换
7. 格式化输出
"""
from typing import Union, Tuple


class HexUtil:
    """
    十六进制工具类，提供十六进制相关操作
    参考Java Hutool HexUtil实现
    """

    @staticmethod
    def is_hex_number(value: str) -> bool:
        """
        判断给定字符串是否为16进制数

        :param value: 要检查的字符串
        :return: 如果是16进制数返回True

        >> HexUtil.is_hex_number("0x1A")
        True
        >> HexUtil.is_hex_number("#FF0000")
        True
        >> HexUtil.is_hex_number("Hello")
        False
        """
        if not value:
            return False

        # 处理负号（Java版本中不支持负号）
        if value.startswith('-'):
            return False

        # 检查前缀
        index = 0
        if value.startswith(('0x', '0X')):
            index += 2
        elif value.startswith('#'):
            index += 1

        # 提取纯十六进制部分
        hex_part = value[index:]
        if not hex_part:
            return False

        # 检查是否全部是十六进制字符
        try:
            int(hex_part, 16)
            return True
        except ValueError:
            return False

    # ---------------------------------------------------------------------------------------- 编码相关方法

    @staticmethod
    def encode_hex(data: bytes, to_lower: bool = True) -> str:
        """
        将字节数组转换为十六进制字符串

        :param data: 字节数组
        :param to_lower: 是否转换为小写格式
        :return: 十六进制字符串

        >> HexUtil.encode_hex(b'hello')
        '68656c6c6f'
        >> HexUtil.encode_hex(b'hello', False)
        '68656C6C6F'
        """
        if not data:
            return ''

        if not isinstance(data, bytes):
            raise TypeError(f"Expected bytes, got {type(data).__name__}")

        hex_str = data.hex()
        return hex_str.lower() if to_lower else hex_str.upper()

    @staticmethod
    def encode_hex_str(data: Union[str, bytes], encoding: str = 'utf-8',
                       to_lower: bool = True) -> str:
        """
        将字符串或字节数组转换为十六进制字符串

        :param data: 字符串或字节数组
        :param encoding: 字符串编码格式，默认为utf-8
        :param to_lower: 是否转换为小写格式
        :return: 十六进制字符串

        >> HexUtil.encode_hex_str('hello')
        '68656c6c6f'
        >> HexUtil.encode_hex_str('你好', 'utf-8')
        'e4bda0e5a5bd'
        """
        if not data:
            return ''

        if isinstance(data, str):
            data = data.encode(encoding)
        elif not isinstance(data, bytes):
            raise TypeError(f"Expected str or bytes, got {type(data).__name__}")

        return HexUtil.encode_hex(data, to_lower)

    # ---------------------------------------------------------------------------------------- 解码相关方法

    @staticmethod
    def decode_hex(hex_str: str) -> bytes:
        """
        将十六进制字符串解码为字节数组

        :param hex_str: 十六进制字符串
        :return: 字节数组

        >> HexUtil.decode_hex('68656c6c6f')
        b'hello'
        >> HexUtil.decode_hex('0x68656c6c6f')
        b'hello'
        """
        if not hex_str:
            return b''

        if not isinstance(hex_str, str):
            raise TypeError(f"Expected str, got {type(hex_str).__name__}")

        # 去除可能的前缀
        if hex_str.startswith(('0x', '0X')):
            hex_str = hex_str[2:]
        elif hex_str.startswith('#'):
            hex_str = hex_str[1:]

        # 验证十六进制字符串有效性
        if not hex_str:
            return b''

        # 确保长度为偶数
        if len(hex_str) % 2 != 0:
            hex_str = '0' + hex_str

        try:
            return bytes.fromhex(hex_str)
        except ValueError as e:
            raise ValueError(f"Invalid hex string: {hex_str}") from e

    @staticmethod
    def decode_hex_str(hex_str: str, encoding: str = 'utf-8') -> str:
        """
        将十六进制字符串解码为普通字符串

        :param hex_str: 十六进制字符串
        :param encoding: 解码使用的编码格式，默认为utf-8
        :return: 普通字符串

        >> HexUtil.decode_hex_str('68656c6c6f')
        'hello'
        >> HexUtil.decode_hex_str('e4bda0e5a5bd')
        '你好'
        """
        bytes_data = HexUtil.decode_hex(hex_str)
        return bytes_data.decode(encoding)

    # ---------------------------------------------------------------------------------------- 颜色相关方法

    @staticmethod
    def encode_color(red: int, green: int, blue: int, prefix: str = '#') -> str:
        """
        将RGB颜色值编码为十六进制形式

        :param red: 红色分量 (0-255)
        :param green: 绿色分量 (0-255)
        :param blue: 蓝色分量 (0-255)
        :param prefix: 前缀字符串，默认为'#'
        :return: 十六进制颜色字符串

        >> HexUtil.encode_color(255, 0, 0)
        '#ff0000'
        >> HexUtil.encode_color(255, 0, 0, '0x')
        '0xff0000'
        """
        # 验证颜色分量范围
        for component, name in zip([red, green, blue], ['red', 'green', 'blue']):
            if not isinstance(component, int) or not 0 <= component <= 255:
                raise ValueError(f"{name} component must be integer between 0 and 255")

        # 格式化为两位十六进制
        hex_color = f"{red:02x}{green:02x}{blue:02x}"
        return f"{prefix}{hex_color}"

    @staticmethod
    def decode_color(hex_color: str) -> Tuple[int, int, int]:
        """
        将十六进制颜色值解码为RGB分量

        :param hex_color: 十六进制颜色字符串
        :return: (red, green, blue)元组

        >> HexUtil.decode_color('#ff0000')
        (255, 0, 0)
        >> HexUtil.decode_color('0xff0000')
        (255, 0, 0)
        """
        # 去除前缀
        if hex_color.startswith(('0x', '0X')):
            hex_color = hex_color[2:]
        elif hex_color.startswith('#'):
            hex_color = hex_color[1:]

        # 验证长度
        if len(hex_color) not in [3, 6]:
            raise ValueError(f"Invalid hex color length: {hex_color}")

        # 处理3位简写形式
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])

        try:
            # 解析RGB分量
            red = int(hex_color[0:2], 16)
            green = int(hex_color[2:4], 16)
            blue = int(hex_color[4:6], 16)
            return red, green, blue
        except ValueError as e:
            raise ValueError(f"Invalid hex color: {hex_color}") from e

    # ---------------------------------------------------------------------------------------- 数字转换方法

    @staticmethod
    def to_hex(number: Union[int, float]) -> str:
        """
        将数字转换为十六进制字符串

        :param number: 要转换的数字
        :return: 十六进制字符串

        >> HexUtil.to_hex(255)
        'ff'
        >> HexUtil.to_hex(10)
        'a'
        """
        if not isinstance(number, (int, float)):
            raise TypeError("Number must be integer or float")

        # 处理浮点数
        if isinstance(number, float):
            # 将浮点数转换为十六进制表示
            return float.hex(number)

        # 处理整数
        hex_str = hex(number)
        if hex_str.startswith(('0x', '0X')):
            hex_str = hex_str[2:]

        return hex_str

    @staticmethod
    def hex_to_int(hex_str: str) -> int:
        """
        将十六进制字符串转换为整数

        :param hex_str: 十六进制字符串
        :return: 整数值

        >> HexUtil.hex_to_int('ff')
        255
        >> HexUtil.hex_to_int('a')
        10
        """
        if not hex_str:
            return 0

        if not isinstance(hex_str, str):
            raise TypeError(f"Expected str, got {type(hex_str).__name__}")

        # 去除可能的前缀
        if hex_str.startswith(('0x', '0X')):
            hex_str = hex_str[2:]
        elif hex_str.startswith('#'):
            hex_str = hex_str[1:]

        if not hex_str:
            return 0

        return int(hex_str, 16)

    @staticmethod
    def hex_to_float(hex_str: str) -> float:
        """
        将十六进制字符串转换为浮点数

        :param hex_str: 十六进制字符串
        :return: 浮点数值

        >> HexUtil.hex_to_float('0x1.fffffep+127')
        3.4028234663852886e+38
        """
        if not hex_str:
            return 0.0

        if not isinstance(hex_str, str):
            raise TypeError(f"Expected str, got {type(hex_str).__name__}")

        # 去除可能的前缀
        if hex_str.startswith(('0x', '0X')):
            hex_str = hex_str[2:]
        elif hex_str.startswith('#'):
            hex_str = hex_str[1:]

        # 添加0x前缀供float.fromhex使用
        return float.fromhex('0x' + hex_str)

    # ---------------------------------------------------------------------------------------- Unicode转换方法

    @staticmethod
    def to_unicode_hex(char: str) -> str:
        """
        将字符转换为Unicode十六进制形式

        :param char: 要转换的字符
        :return: Unicode十六进制字符串

        >> HexUtil.to_unicode_hex('你')
        '\\\\u4f60'
        >> HexUtil.to_unicode_hex('A')
        '\\\\u0041'
        """
        if not char or not isinstance(char, str) or len(char) != 1:
            raise ValueError("Input must be a single character")

        code_point = ord(char)
        hex_str = hex(code_point)[2:]  # 去除'0x'前缀

        # 对于BMP以外的字符，可能需要4位以上的十六进制
        if code_point <= 0xFFFF:
            hex_str = hex_str.zfill(4)  # 基本多文种平面字符填充到4位
        else:
            hex_str = hex_str.zfill(8)  # 补充平面字符填充到8位

        return f"\\u{hex_str}"

    @staticmethod
    def from_unicode_hex(unicode_hex: str) -> str:
        """
        将Unicode十六进制字符串转换为字符

        :param unicode_hex: Unicode十六进制字符串
        :return: 字符

        >> HexUtil.from_unicode_hex('\\\\u4f60')
        '你'
        >> HexUtil.from_unicode_hex('\\\\u0041')
        'A'
        """
        if not unicode_hex or not unicode_hex.startswith('\\u'):
            raise ValueError("Invalid Unicode hex format")

        # 提取十六进制部分
        hex_part = unicode_hex[2:]
        code_point = int(hex_part, 16)
        return chr(code_point)

    # ---------------------------------------------------------------------------------------- 格式化方法

    @staticmethod
    def format_hex(hex_str: str, separator: str = ' ', prefix: str = '') -> str:
        """
        格式化十六进制字符串，每两个字符加一个分隔符

        :param hex_str: 十六进制字符串
        :param separator: 分隔符，默认为空格
        :param prefix: 前缀字符串，如'0x'
        :return: 格式化后的十六进制字符串

        >> HexUtil.format_hex('68656c6c6f')
        '68 65 6c 6c 6f'
        >> HexUtil.format_hex('68656c6c6f', ':', '0x')
        '0x68:0x65:0x6c:0x6c:0x6f'
        """
        if not hex_str:
            return ''

        # 去除可能的前缀
        if hex_str.startswith(('0x', '0X')):
            hex_str = hex_str[2:]
        elif hex_str.startswith('#'):
            hex_str = hex_str[1:]

        # 确保长度为偶数
        if len(hex_str) % 2 != 0:
            hex_str = '0' + hex_str

        # 每两个字符分组
        groups = [hex_str[i:i + 2] for i in range(0, len(hex_str), 2)]

        # 添加前缀和分隔符
        if prefix:
            groups = [prefix + group for group in groups]

        return separator.join(groups)

    @staticmethod
    def to_big_integer(hex_str: str) -> int:
        """
        将十六进制字符串转换为大整数

        :param hex_str: 十六进制字符串
        :return: 大整数
        :raises ValueError: 如果hex_str无效

        Examples:
            >> HexUtil.to_big_integer('ffffffff')
            4294967295
            >> HexUtil.to_big_integer('10000000000000000')
            18446744073709551616
        """
        return HexUtil.hex_to_int(hex_str)

    @staticmethod
    def normalize_hex(hex_str: str, prefix: str = '', to_lower: bool = True) -> str:
        """
        标准化十六进制字符串格式

        :param hex_str: 十六进制字符串
        :param prefix: 想要的前缀，默认为空
        :param to_lower: 是否转换为小写，默认为True
        :return: 标准化后的十六进制字符串

        Examples:
            >> HexUtil.normalize_hex('0XFF', '', True)
            'ff'
            >> HexUtil.normalize_hex('#ff0000', '0x', False)
            '0xFF0000'
        """
        if not hex_str or not isinstance(hex_str, str):
            return ''

        # 去除可能的前缀
        if hex_str.startswith(('0x', '0X')):
            hex_str = hex_str[2:]
        elif hex_str.startswith('#'):
            hex_str = hex_str[1:]

        # 转换大小写
        hex_str = hex_str.lower() if to_lower else hex_str.upper()

        return f"{prefix}{hex_str}" if prefix else hex_str


# 单元测试和示例
if __name__ == "__main__":
    import doctest

    doctest.testmod()

    # 示例用法
    print("HexUtil示例:")

    # 编码解码示例
    print("\n1. 编码解码示例:")
    original_str = "Hello, 世界!"
    hex_str = HexUtil.encode_hex_str(original_str)
    decoded_str = HexUtil.decode_hex_str(hex_str)
    print(f"原始字符串: {original_str}")
    print(f"十六进制编码: {hex_str}")
    print(f"解码后字符串: {decoded_str}")

    # 颜色转换示例
    print("\n2. 颜色转换示例:")
    red, green, blue = 255, 128, 0
    color_hex = HexUtil.encode_color(red, green, blue)
    decoded_color = HexUtil.decode_color(color_hex)
    print(f"RGB颜色: ({red}, {green}, {blue})")
    print(f"十六进制颜色: {color_hex}")
    print(f"解码后RGB: {decoded_color}")

    # 数字转换示例
    print("\n3. 数字转换示例:")
    number = 255
    hex_num = HexUtil.to_hex(number)
    decoded_num = HexUtil.hex_to_int(hex_num)
    print(f"数字: {number}")
    print(f"十六进制: {hex_num}")
    print(f"解码后数字: {decoded_num}")

    # Unicode转换示例
    print("\n4. Unicode转换示例:")
    char = "你"
    unicode_hex = HexUtil.to_unicode_hex(char)
    decoded_char = HexUtil.from_unicode_hex(unicode_hex)
    print(f"字符: {char}")
    print(f"Unicode十六进制: {unicode_hex}")
    print(f"解码后字符: {decoded_char}")

    # 格式化示例
    print("\n5. 格式化示例:")
    hex_data = "68656c6c6f776f726c64"
    formatted_hex = HexUtil.format_hex(hex_data, ':', '0x')
    print(f"原始十六进制: {hex_data}")
    print(f"格式化后: {formatted_hex}")

    # 大整数示例
    print("\n6. 大整数示例:")
    big_hex = "ffffffff"
    big_int = HexUtil.to_big_integer(big_hex)
    print(f"十六进制: {big_hex}")
    print(f"大整数: {big_int}")

    # 标准化示例
    print("\n7. 标准化示例:")
    raw_hex = "0XAbCdEf"
    normalized = HexUtil.normalize_hex(raw_hex, "0x", True)
    print(f"原始: {raw_hex}")
    print(f"标准化后: {normalized}")
