from typing import Union, List, Optional, ClassVar
import unicodedata
from functools import lru_cache


class CharPool:
    """
    字符常量池，定义常用字符
    所有常量均为字符串类型，且长度为1
    """
    # 空格符
    SPACE: ClassVar[str] = ' '
    # 制表符
    TAB: ClassVar[str] = '\t'
    # 点
    DOT: ClassVar[str] = '.'
    # 斜杠
    SLASH: ClassVar[str] = '/'
    # 反斜杠
    BACKSLASH: ClassVar[str] = '\\'
    # 回车符
    CR: ClassVar[str] = '\r'
    # 换行符
    LF: ClassVar[str] = '\n'
    # 减号（连接符）
    DASHED: ClassVar[str] = '-'
    # 下划线
    UNDERLINE: ClassVar[str] = '_'
    # 逗号
    COMMA: ClassVar[str] = ','
    # 花括号（左）
    DELIM_START: ClassVar[str] = '{'
    # 花括号（右）
    DELIM_END: ClassVar[str] = '}'
    # 中括号（左）
    BRACKET_START: ClassVar[str] = '['
    # 中括号（右）
    BRACKET_END: ClassVar[str] = ']'
    # 双引号
    DOUBLE_QUOTES: ClassVar[str] = '"'
    # 单引号
    SINGLE_QUOTE: ClassVar[str] = "'"
    # 与符号
    AMP: ClassVar[str] = '&'
    # 冒号
    COLON: ClassVar[str] = ':'
    # 艾特符号
    AT: ClassVar[str] = '@'
    # 等号
    EQUALS: ClassVar[str] = '='
    # 问号
    QUESTION_MARK: ClassVar[str] = '?'
    # 百分号
    PERCENT: ClassVar[str] = '%'
    # 美元符号
    DOLLAR: ClassVar[str] = '$'
    # 井号
    HASH: ClassVar[str] = '#'
    # 加号
    PLUS: ClassVar[str] = '+'
    # 星号
    ASTERISK: ClassVar[str] = '*'
    # 分号
    SEMICOLON: ClassVar[str] = ';'
    # 竖线
    VERTICAL_BAR: ClassVar[str] = '|'
    # 波浪线
    TILDE: ClassVar[str] = '~'
    # 反引号
    BACKTICK: ClassVar[str] = '`'
    # 脱字符
    CARET: ClassVar[str] = '^'
    # 左括号
    PARENTHESIS_START: ClassVar[str] = '('
    # 右括号
    PARENTHESIS_END: ClassVar[str] = ')'
    # 小于号
    LESS_THAN: ClassVar[str] = '<'
    # 大于号
    GREATER_THAN: ClassVar[str] = '>'
    # 零宽空格
    ZERO_WIDTH_SPACE: ClassVar[str] = '\u200b'
    # 不间断空格
    NO_BREAK_SPACE: ClassVar[str] = '\u00a0'
    # 软连字符
    SOFT_HYPHEN: ClassVar[str] = '\u00ad'


class CharUtil:
    """
    字符工具类，提供字符判断和转换功能
    采用组合方式使用CharPool中的常量
    """

    # 通过类属性引用CharPool常量，避免继承
    SPACE = CharPool.SPACE
    TAB = CharPool.TAB
    DOT = CharPool.DOT
    SLASH = CharPool.SLASH
    BACKSLASH = CharPool.BACKSLASH
    CR = CharPool.CR
    LF = CharPool.LF
    DASHED = CharPool.DASHED
    UNDERLINE = CharPool.UNDERLINE
    COMMA = CharPool.COMMA
    DELIM_START = CharPool.DELIM_START
    DELIM_END = CharPool.DELIM_END
    BRACKET_START = CharPool.BRACKET_START
    BRACKET_END = CharPool.BRACKET_END
    DOUBLE_QUOTES = CharPool.DOUBLE_QUOTES
    SINGLE_QUOTE = CharPool.SINGLE_QUOTE
    AMP = CharPool.AMP
    COLON = CharPool.COLON
    AT = CharPool.AT
    EQUALS = CharPool.EQUALS
    QUESTION_MARK = CharPool.QUESTION_MARK
    PERCENT = CharPool.PERCENT
    DOLLAR = CharPool.DOLLAR
    HASH = CharPool.HASH
    PLUS = CharPool.PLUS
    ASTERISK = CharPool.ASTERISK
    SEMICOLON = CharPool.SEMICOLON
    VERTICAL_BAR = CharPool.VERTICAL_BAR
    TILDE = CharPool.TILDE
    BACKTICK = CharPool.BACKTICK
    CARET = CharPool.CARET
    PARENTHESIS_START = CharPool.PARENTHESIS_START
    PARENTHESIS_END = CharPool.PARENTHESIS_END
    LESS_THAN = CharPool.LESS_THAN
    GREATER_THAN = CharPool.GREATER_THAN
    ZERO_WIDTH_SPACE = CharPool.ZERO_WIDTH_SPACE
    NO_BREAK_SPACE = CharPool.NO_BREAK_SPACE
    SOFT_HYPHEN = CharPool.SOFT_HYPHEN

    @staticmethod
    def _validate_char_input(c: Optional[str]) -> bool:
        """
        验证输入是否为单字符且非None

        Args:
            c: 待验证的输入

        Returns:
            如果是单字符且非None返回True，否则返回False
        """
        return c is not None and len(c) == 1

    @staticmethod
    def is_ascii(c: Optional[str]) -> bool:
        """
        是否为ASCII字符，ASCII字符位于0~127之间

        Args:
            c: 被检查的字符

        Returns:
            True表示为ASCII字符，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False
        return ord(c) < 128  # type: ignore

    @staticmethod
    def is_ascii_printable(c: Optional[str]) -> bool:
        """
        是否为可见ASCII字符，可见字符位于32~126之间

        Args:
            c: 被检查的字符

        Returns:
            True表示为ASCII可见字符，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False
        return 32 <= ord(c) <= 126  # type: ignore

    @staticmethod
    def is_ascii_control(c: Optional[str]) -> bool:
        """
        是否为ASCII控制符（不可见字符），控制符位于0~31和127

        Args:
            c: 被检查的字符

        Returns:
            True表示为控制符，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False
        code = ord(c)  # type: ignore
        return code < 32 or code == 127

    @staticmethod
    def is_letter(c: Optional[str]) -> bool:
        """
        判断是否为字母（包括大写字母和小写字母）
        字母包括A~Z和a~z

        Args:
            c: 被检查的字符

        Returns:
            True表示为字母，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False
        return c.isalpha()  # type: ignore

    @staticmethod
    def is_letter_upper(c: Optional[str]) -> bool:
        """
        判断是否为大写字母，大写字母包括A~Z

        Args:
            c: 被检查的字符

        Returns:
            True表示为大写字母，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False
        return c.isupper()  # type: ignore

    @staticmethod
    def is_letter_lower(c: Optional[str]) -> bool:
        """
        检查字符是否为小写字母，小写字母指a~z

        Args:
            c: 被检查的字符

        Returns:
            True表示为小写字母，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False
        return c.islower()  # type: ignore

    @staticmethod
    def is_digit(c: Optional[str]) -> bool:
        """
        检查是否为数字字符，数字字符指0~9

        Args:
            c: 被检查的字符

        Returns:
            True表示为数字字符，输入无效返回极False
        """
        if not CharUtil._validate_char_input(c):
            return False
        return c.isdigit()  # type: ignore

    @staticmethod
    def is_hex_char(c: Optional[str]) -> bool:
        """
        是否为16进制规范的字符
        判断是否为如下字符：0~9, a~f, A~F

        Args:
            c: 字符

        Returns:
            是否为16进制规范的字符，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False
        return c in '0123456789abcdefABCDEF'  # type: ignore

    @staticmethod
    def is_letter_or_digit(c: Optional[str]) -> bool:
        """
        是否为字母或数字，包括A~Z、a~z、0~9

        Args:
            c: 被检查的字符

        Returns:
            True表示为字母或数字，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False
        return c.isalnum()  # type: ignore

    @staticmethod
    def is_whitespace(c: Optional[str]) -> bool:
        """
        是否空白符
        空白符包括空格、制表符、换行符等

        Args:
            c: 字符

        Returns:
            是否空白符，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False
        return c.isspace()  # type: ignore

    @staticmethod
    @lru_cache(maxsize=1024)  # 缓存最近判断结果，提高频繁调用性能
    def is_emoji(c: Optional[str]) -> bool:
        """
        判断是否为emoji表情符
        注意：此判断基于Unicode分类和名称，可能因Python版本和Unicode数据库版本而异

        Args:
            c: 字符

        Returns:
            是否为emoji，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False

        # 更全面的emoji判断逻辑
        try:
            # 检查Unicode分类 (Symbol, Other 可能是emoji)
            category = unicodedata.category(c)  # type: ignore
            if category in ('So', 'Sk', 'Sm', 'Sc'):
                return True

            # 检查Unicode名称
            name = unicodedata.name(c, '')  # type: ignore
            if not name:
                return False

            # 名称中包含EMOJI、FACE、HAND等关键词的认为是emoji
            emoji_keywords = ('EMOJI', 'FACE', 'HAND', 'HEART', 'SIGN', 'SYMBOL')
            return any(keyword in name for keyword in emoji_keywords)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_file_separator(c: Optional[str]) -> bool:
        """
        是否为文件分隔符
        Windows平台下分隔符为\，Linux（Unix）为/

        Args:
            c: 字符

        Returns:
            是否为文件分隔符，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False
        return c == CharUtil.SLASH or c == CharUtil.BACKSLASH  # type: ignore

    @staticmethod
    def equals(c1: Optional[str], c2: Optional[str], case_insensitive: bool = False) -> bool:
        """
        比较两个字符是否相同

        Args:
            c1: 字符1
            c2: 字符2
            case_insensitive: 是否忽略大小写

        Returns:
            是否相同，输入无效返回False
        """
        if not CharUtil._validate_char_input(c1) or not CharUtil._validate_char_input(c2):
            return False

        if case_insensitive:
            return c1.lower() == c2.lower()  # type: ignore
        return c1 == c2  # type: ignore

    @staticmethod
    def to_string(c: Optional[str]) -> Optional[str]:
        """
        字符转为字符串，实际上原样返回

        Args:
            c: 字符

        Returns:
            字符串，输入为None时返回None
        """
        return c

    @staticmethod
    def to_close_char(c: Optional[str]) -> Optional[str]:
        """
        将字母、数字转换为带圈的字符：
        '1' -> '①'
        'A' -> 'Ⓐ'
        'a' -> 'ⓐ'
        如果字符不在转换范围内，则返回原字符

        Args:
            c: 被转换的字符

        Returns:
            转换后的字符，输入无效返回None
        """
        if not CharUtil._validate_char_input(c):
            return None

        code = ord(c)  # type: ignore
        result = code

        if '1' <= c <= '9':  # type: ignore
            result = ord('①') + code - ord('1')
        elif 'A' <= c <= 'Z':  # type: ignore
            result = ord('Ⓐ') + code - ord('A')
        elif 'a' <= c <= 'z':  # type: ignore
            result = ord('ⓐ') + code - ord('a')
        else:
            # 不在转换范围内，返回原字符
            return c

        return chr(result)

    @staticmethod
    def to_close_by_number(number: int) -> str:
        """
        将[1-20]数字转换为带圈的字符：
        1 -> '①'
        12 -> '⑫'
        20 -> '⑳'

        Args:
            number: 被转换的数字

        Returns:
            转换后的字符

        Raises:
            ValueError: 如果数字不在1-20范围内
        """
        if number < 1 or number > 20:
            raise ValueError("Number must be between 1 and 20")

        return chr(ord('①') + number - 1)

    @staticmethod
    def digit16(c: Optional[str]) -> int:
        """
        获取给定字符的16进制数值

        Args:
            c: 字符

        Returns:
            16进制数值，如果不是16进制字符返回-1，输入无效返回-1
        """
        if not CharUtil._validate_char_input(c):
            return -1

        hex_digits = '0123456789abcdefABCDEF'
        if c not in hex_digits:  # type: ignore
            return -1

        return int(c, 16)  # type: ignore

    @staticmethod
    def get_type(c: Optional[str]) -> str:
        """
        获取字符的Unicode分类

        Args:
            c: 字符

        Returns:
            Unicode分类名称，输入无效返回 'Cn' (Other, not assigned)
        """
        if not CharUtil._validate_char_input(c):
            return 'Cn'  # Other, not assigned

        return unicodedata.category(c)  # type: ignore

    @staticmethod
    def is_bmp(c: Optional[str]) -> bool:
        """
        是否为BMP（基本多文种平面）字符
        BMP字符的Unicode码点位于U+0000到U+FFFF之间

        Args:
            c: 字符

        Returns:
            是否为BMP字符，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False

        return ord(c) <= 0xFFFF  # type: ignore

    @staticmethod
    def is_supplementary(c: Optional[str]) -> bool:
        """
        是否为增补字符（Supplementary Characters）
        增补字符的Unicode码点位于U+10000到U+10FFFF之间

        Args:
            c: 字符

        Returns:
            是否为增补字符，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False

        code_point = ord(c)  # type: ignore
        return 0x10000 <= code_point <= 0x10FFFF

    @staticmethod
    def to_char(value: Union[int, str, None]) -> str:
        """
        将值转换为字符
        支持整数（Unicode码点）和单字符字符串

        Args:
            value: 整数值或单字符字符串

        Returns:
            字符

        Raises:
            ValueError: 如果值无法转换为有效字符
            TypeError: 如果值类型不支持
        """
        if value is None:
            raise ValueError("Input value cannot be None")

        if isinstance(value, int):
            if value < 0 or value > 0x10FFFF:
                raise ValueError(f"Invalid code point: {value}")
            return chr(value)
        elif isinstance(value, str):
            if len(value) != 1:
                raise ValueError("String must contain exactly one character")
            return value
        else:
            raise TypeError("Value must be an integer or a single character string")

    @staticmethod
    def to_code_point(c: Optional[str]) -> int:
        """
        获取字符的Unicode码点

        Args:
            c: 字符

        Returns:
            Unicode码点

        Raises:
            ValueError: 如果不是单字符或为None
        """
        if not CharUtil._validate_char_input(c):
            raise ValueError("Input must be a single non-None character")

        return ord(c)  # type: ignore

    @staticmethod
    def is_punctuation(c: Optional[str]) -> bool:
        """
        判断字符是否为标点符号

        Args:
            c: 字符

        Returns:
            是否为标点符号，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False

        category = unicodedata.category(c)  # type: ignore
        # Unicode中标点符号的类别以P开头
        return category.startswith('P')

    @staticmethod
    def is_symbol(c: Optional[str]) -> bool:
        """
        判断字符是否为符号

        Args:
            c: 字符

        Returns:
            是否为符号，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False

        category = unicodedata.category(c)  # type: ignore
        # Unicode中符号的类别以S开头
        return category.startswith('S')

    @staticmethod
    def is_math_symbol(c: Optional[str]) -> bool:
        """
        判断字符是否为数学符号

        Args:
            c: 字符

        Returns:
            是否为数学符号，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False

        category = unicodedata.category(c)  # type: ignore
        # 数学符号的特定类别
        return category in ('Sm', 'So')

    @staticmethod
    def is_currency_symbol(c: Optional[str]) -> bool:
        """
        判断字符是否为货币符号

        Args:
            c: 字符

        Returns:
            是否为货币符号，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False

        category = unicodedata.category(c)  # type: ignore
        # 货币符号的特定类别
        return category == 'Sc'

    @staticmethod
    def is_modifier_symbol(c: Optional[str]) -> bool:
        """
        判断字符是否为修饰符号

        Args:
            c: 字符

        Returns:
            是否为修饰符号，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False

        category = unicodedata.category(c)  # type: ignore
        # 修饰符号的特定类别
        return category == 'Sk'

    @staticmethod
    def is_separator(c: Optional[str]) -> bool:
        """
        判断字符是否为分隔符

        Args:
            c: 字符

        Returns:
            是否为分隔符，输入无效返回False
        """
        if not CharUtil._validate_char_input(c):
            return False

        category = unicodedata.category(c)  # type: ignore
        # 分隔符的特定类别
        return category.startswith('Z')


# 单元测试和示例
if __name__ == "__main__":
    import doctest

    doctest.testmod()

    # 示例用法
    print("CharPool常量示例:")
    print(f"空格: '{CharPool.SPACE}'")
    print(f"制表符: '{CharPool.TAB}'")
    print(f"换行符: '{CharPool.LF}'")
    print(f"逗号: '{CharPool.COMMA}'")
    print(f"不间断空格: '{CharPool.NO_BREAK_SPACE}'")

    print("\nCharUtil方法示例:")
    print(f"is_ascii('a'): {CharUtil.is_ascii('a')}")
    print(f"is_letter('A'): {CharUtil.is_letter('A')}")
    print(f"is_digit('5'): {CharUtil.is_digit('5')}")
    print(f"to_close_char('1'): {CharUtil.to_close_char('1')}")
    print(f"to_close_by_number(15): {CharUtil.to_close_by_number(15)}")
    print(f"equals('a', 'A', True): {CharUtil.equals('a', 'A', True)}")

    # 测试None输入
    print(f"is_ascii(None): {CharUtil.is_ascii(None)}")
    print(f"is_ascii('ab'): {CharUtil.is_ascii('ab')}")

    # 测试新功能
    print(f"is_punctuation('.'): {CharUtil.is_punctuation('.')}")
    print(f"is_symbol('$'): {CharUtil.is_symbol('$')}")
    print(f"is_currency_symbol('¥'): {CharUtil.is_currency_symbol('¥')}")