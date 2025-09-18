# sytool/str_util.py
import re
from typing import Optional, List, Any, Callable, Dict, Union


class StrPool:
    """
    字符串常量池，定义常用的字符串常量
    参考 Hutool 的 StrPool 和 CharPool
    """
    # 字符常量
    C_SPACE = ' '
    C_TAB = '\t'
    C_DOT = '.'
    C_SLASH = '/'
    C_BACKSLASH = '\\'
    C_CR = '\r'
    C_LF = '\n'
    C_UNDERLINE = '_'
    C_COMMA = ','
    C_DELIM_START = '{'
    C_DELIM_END = '}'
    C_BRACKET_START = '['
    C_BRACKET_END = ']'
    C_COLON = ':'
    C_AT = '@'
    C_DASHED = '-'

    # 字符串常量
    NULL = "null"
    EMPTY = ""
    SPACE = " "
    TAB = "\t"
    DOT = "."
    DOUBLE_DOT = ".."
    SLASH = "/"
    BACKSLASH = "\\"
    CR = "\r"
    LF = "\n"
    CRLF = "\r\n"
    UNDERLINE = "_"
    DASHED = "-"
    COMMA = ","
    DELIM_START = "{"
    DELIM_END = "}"
    BRACKET_START = "["
    BRACKET_END = "]"
    COLON = ":"
    AT = "@"
    HTML_NBSP = "&nbsp;"
    HTML_AMP = "&amp;"
    HTML_QUOTE = "&quot;"
    HTML_APOS = "&apos;"
    HTML_LT = "&lt;"
    HTML_GT = "&gt;"
    EMPTY_JSON = "{}"


class StrUtil:
    """
    字符串工具类，提供丰富的字符串操作方法
    参考 Hutool 的 CharSequenceUtil
    """

    # 常量定义
    INDEX_NOT_FOUND = -1

    @staticmethod
    def is_empty(s: Optional[str]) -> bool:
        """
        检查字符串是否为空（None 或空字符串）
        :param s: 待检查字符串
        :return: 是否为空
        """
        return s is None or len(s) == 0

    @staticmethod
    def is_blank(s: Optional[str]) -> bool:
        """
        检查字符串是否为空白（None、空字符串、纯空格）
        :param s: 待检查字符串
        :return: 是否为空白
        """
        return s is None or len(s.strip()) == 0

    @staticmethod
    def is_not_empty(s: Optional[str]) -> bool:
        """检查字符串是否非空"""
        return not StrUtil.is_empty(s)

    @staticmethod
    def is_not_blank(s: Optional[str]) -> bool:
        """检查字符串是否为非空白"""
        return not StrUtil.is_blank(s)

    @staticmethod
    def trim(s: Optional[str]) -> Optional[str]:
        """
        去除字符串两端空白字符
        :param s: 待处理字符串
        :return: 处理后的字符串
        """
        return s.strip() if s is not None else None

    @staticmethod
    def trim_to_empty(s: Optional[str]) -> str:
        """
        去除字符串两端空白字符，如果结果为 null 则返回空字符串
        :param s: 待处理字符串
        :return: 处理后的字符串
        """
        return StrPool.EMPTY if s is None else s.strip()

    @staticmethod
    def trim_to_null(s: Optional[str]) -> Optional[str]:
        """
        去除字符串两端空白字符，如果结果为空白则返回 None
        :param s: 待处理字符串
        :return: 处理后的字符串
        """
        if s is None:
            return None
        result = s.strip()
        return result if len(result) > 0 else None

    @staticmethod
    def trim_start(s: Optional[str]) -> Optional[str]:
        """
        去除字符串开头空白字符
        :param s: 待处理字符串
        :return: 处理后的字符串
        """
        return s.lstrip() if s is not None else None

    @staticmethod
    def trim_end(s: Optional[str]) -> Optional[str]:
        """
        去除字符串结尾空白字符
        :param s: 待处理字符串
        :return: 处理后的字符串
        """
        return s.rstrip() if s is not None else None

    @staticmethod
    def substr(s: str, start: int, end: int = None) -> str:
        """
        安全地截取子字符串，支持负数索引和越界处理
        :param s: 原始字符串
        :param start: 起始索引
        :param end: 结束索引（不包含）
        :return: 子字符串
        """
        if s is None:
            return StrPool.EMPTY

        length = len(s)

        # 处理负数索引
        start = start if start >= 0 else max(0, length + start)
        if end is None:
            end = length
        else:
            end = end if end >= 0 else max(0, length + end)

        # 确保索引在有效范围内
        start = max(0, min(start, length))
        end = max(0, min(end, length))

        # 确保 start 不大于 end
        if start > end:
            start, end = end, start

        return s[start:end]

    @staticmethod
    def camel_to_snake(s: str) -> str:
        """
        驼峰命名转下划线命名（例如：userName -> user_name）
        :param s: 驼峰命名字符串
        :return: 下划线命名字符串
        """
        if StrUtil.is_blank(s):
            return s

        # 插入下划线并转换为小写
        s = re.sub(r'(?<!^)(?=[A-Z])', '_', s)
        return s.lower()

    @staticmethod
    def snake_to_camel(s: str) -> str:
        """
        下划线命名转驼峰命名（例如：user_name -> userName）
        :param s: 下划线命名字符串
        :return: 驼峰命名字符串
        """
        if StrUtil.is_blank(s):
            return s

        parts = s.split('_')
        return parts[0] + ''.join(part.capitalize() for part in parts[1:])

    @staticmethod
    def reverse(s: str) -> str:
        """
        反转字符串
        :param s: 原始字符串
        :return: 反转后的字符串
        """
        return s[::-1] if s is not None else None

    @staticmethod
    def format(template: str, *args, **kwargs) -> str:
        """
        字符串格式化（支持位置参数和关键字参数）
        :param template: 模板字符串
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 格式化后的字符串
        """
        if template is None:
            return None

        if kwargs:
            return template.format(**kwargs)
        else:
            return template.format(*args)

    @staticmethod
    def contains(s: str, sub: str) -> bool:
        """
        检查字符串是否包含子串
        :param s: 原始字符串
        :param sub: 子串
        :return: 是否包含
        """
        if s is None or sub is None:
            return False
        return sub in s

    @staticmethod
    def contains_any(s: str, *substrings) -> bool:
        """
        检查字符串是否包含任意一个子串
        :param s: 原始字符串
        :param substrings: 子串列表
        :return: 是否包含任意一个子串
        """
        if s is None:
            return False
        return any(sub in s for sub in substrings if sub is not None)

    @staticmethod
    def contains_all(s: str, *substrings) -> bool:
        """
        检查字符串是否包含所有子串
        :param s: 原始字符串
        :param substrings: 子串列表
        :return: 是否包含所有子串
        """
        if s is None:
            return False
        return all(sub in s for sub in substrings if sub is not None)

    @staticmethod
    def remove(s: str, char: str) -> str:
        """
        移除字符串中所有指定字符
        :param s: 原始字符串
        :param char: 要移除的字符
        :return: 处理后的字符串
        """
        if s is None or char is None:
            return s
        return s.replace(char, StrPool.EMPTY)

    @staticmethod
    def remove_all(s: str, *chars) -> str:
        """
        移除字符串中所有指定字符
        :param s: 原始字符串
        :param chars: 要移除的字符列表
        :return: 处理后的字符串
        """
        if s is None:
            return None

        result = s
        for char in chars:
            if char is not None:
                result = result.replace(char, StrPool.EMPTY)
        return result

    @staticmethod
    def split(s: str, delimiter: str, limit: int = -1) -> List[str]:
        """
        分割字符串，可限制分割次数
        :param s: 原始字符串
        :param delimiter: 分隔符
        :param limit: 分割次数限制
        :return: 分割后的字符串列表
        """
        if s is None:
            return []

        if delimiter is None:
            return [s]

        return s.split(delimiter, limit) if limit >= 0 else s.split(delimiter)

    @staticmethod
    def join(delimiter: str, elements: List[Any]) -> str:
        """
        将元素列表连接为字符串
        :param delimiter: 分隔符
        :param elements: 元素列表
        :return: 连接后的字符串
        """
        if elements is None:
            return StrPool.EMPTY

        return delimiter.join(str(e) for e in elements)

    @staticmethod
    def start_with(s: str, prefix: str, ignore_case: bool = False) -> bool:
        """
        检查字符串是否以指定前缀开头
        :param s: 原始字符串
        :param prefix: 前缀
        :param ignore_case: 是否忽略大小写
        :return: 是否以指定前缀开头
        """
        if s is None or prefix is None:
            return False

        if ignore_case:
            return s.lower().startswith(prefix.lower())
        return s.startswith(prefix)

    @staticmethod
    def end_with(s: str, suffix: str, ignore_case: bool = False) -> bool:
        """
        检查字符串是否以指定后缀结尾
        :param s: 原始字符串
        :param suffix: 后缀
        :param ignore_case: 是否忽略大小写
        :return: 是否以指定后缀结尾
        """
        if s is None or suffix is None:
            return False

        if ignore_case:
            return s.lower().endswith(suffix.lower())
        return s.endswith(suffix)

    @staticmethod
    def repeat(s: str, count: int) -> str:
        """
        重复字符串指定次数
        :param s: 原始字符串
        :param count: 重复次数
        :return: 重复后的字符串
        """
        if s is None or count <= 0:
            return StrPool.EMPTY
        return s * count

    @staticmethod
    def default_if_empty(s: Optional[str], default: str) -> str:
        """
        如果字符串为空或 None，返回默认值
        :param s: 原始字符串
        :param default: 默认值
        :return: 处理后的字符串
        """
        return default if StrUtil.is_empty(s) else s

    @staticmethod
    def default_if_blank(s: Optional[str], default: str) -> str:
        """
        如果字符串为空白，返回默认值
        :param s: 原始字符串
        :param default: 默认值
        :return: 处理后的字符串
        """
        return default if StrUtil.is_blank(s) else s

    @staticmethod
    def has_text(s: Optional[str]) -> bool:
        """
        检查字符串是否包含非空白字符
        :param s: 原始字符串
        :return: 是否包含非空白字符
        """
        return not StrUtil.is_blank(s)

    @staticmethod
    def count_matches(s: str, sub: str) -> int:
        """
        计算子串在字符串中出现的次数
        :param s: 原始字符串
        :param sub: 子串
        :return: 出现次数
        """
        if StrUtil.is_empty(s) or StrUtil.is_empty(sub):
            return 0
        return s.count(sub)

    @staticmethod
    def equals(s1: Optional[str], s2: Optional[str], ignore_case: bool = False) -> bool:
        """
        比较两个字符串是否相等
        :param s1: 字符串1
        :param s2: 字符串2
        :param ignore_case: 是否忽略大小写
        :return: 是否相等
        """
        if s1 is None and s2 is None:
            return True
        if s1 is None or s2 is None:
            return False

        if ignore_case:
            return s1.lower() == s2.lower()
        return s1 == s2

    @staticmethod
    def index_of(s: str, sub: str, start: int = 0) -> int:
        """
        查找子串在字符串中的位置
        :param s: 原始字符串
        :param sub: 子串
        :param start: 起始位置
        :return: 子串位置，未找到返回 -1
        """
        if s is None or sub is None:
            return StrUtil.INDEX_NOT_FOUND
        return s.find(sub, start)

    @staticmethod
    def last_index_of(s: str, sub: str, start: int = 0) -> int:
        """
        查找子串在字符串中最后出现的位置
        :param s: 原始字符串
        :param sub: 子串
        :param start: 起始位置
        :return: 子串位置，未找到返回 -1
        """
        if s is None or sub is None:
            return StrUtil.INDEX_NOT_FOUND
        return s.rfind(sub, start)

    @staticmethod
    def substring_before(s: str, separator: str) -> str:
        """
        获取分隔符之前的子串
        :param s: 原始字符串
        :param separator: 分隔符
        :return: 分隔符之前的子串
        """
        if s is None or separator is None:
            return s or StrPool.EMPTY

        index = s.find(separator)
        if index == StrUtil.INDEX_NOT_FOUND:
            return s
        return s[:index]

    @staticmethod
    def substring_after(s: str, separator: str) -> str:
        """
        获取分隔符之后的子串
        :param s: 原始字符串
        :param separator: 分隔符
        :return: 分隔符之后的子串
        """
        if s is None or separator is None:
            return s or StrPool.EMPTY

        index = s.find(separator)
        if index == StrUtil.INDEX_NOT_FOUND:
            return StrPool.EMPTY
        return s[index + len(separator):]

    @staticmethod
    def remove_prefix(s: str, prefix: str) -> str:
        """
        移除字符串前缀
        :param s: 原始字符串
        :param prefix: 前缀
        :return: 移除前缀后的字符串
        """
        if s is None or prefix is None:
            return s or StrPool.EMPTY

        if s.startswith(prefix):
            return s[len(prefix):]
        return s

    @staticmethod
    def remove_suffix(s: str, suffix: str) -> str:
        """
        移除字符串后缀
        :param s: 原始字符串
        :param suffix: 后缀
        :return: 移除后缀后的字符串
        """
        if s is None or suffix is None:
            return s or StrPool.EMPTY

        if s.endswith(suffix):
            return s[:-len(suffix)]
        return s

    @staticmethod
    def capitalize(s: str) -> str:
        """
        将字符串首字母大写
        :param s: 原始字符串
        :return: 首字母大写后的字符串
        """
        if StrUtil.is_empty(s):
            return s or StrPool.EMPTY
        return s[0].upper() + s[1:]

    @staticmethod
    def uncapitalize(s: str) -> str:
        """
        将字符串首字母小写
        :param s: 原始字符串
        :return: 首字母小写后的字符串
        """
        if StrUtil.is_empty(s):
            return s or StrPool.EMPTY
        return s[0].lower() + s[1:]

    @staticmethod
    def wrap(s: str, wrap_with: str) -> str:
        """
        用指定字符包裹字符串
        :param s: 原始字符串
        :param wrap_with: 包裹字符
        :return: 包裹后的字符串
        """
        if s is None or wrap_with is None:
            return s or StrPool.EMPTY
        return wrap_with + s + wrap_with

    @staticmethod
    def unwrap(s: str, wrap_char: str) -> str:
        """
        移除字符串两端的指定字符
        :param s: 原始字符串
        :param wrap_char: 包裹字符
        :return: 移除包裹字符后的字符串
        """
        if s is None or wrap_char is None:
            return s or StrPool.EMPTY

        if s.startswith(wrap_char) and s.endswith(wrap_char):
            return s[1:-1]
        return s

    @staticmethod
    def is_numeric(s: str) -> bool:
        """
        检查字符串是否只包含数字
        :param s: 原始字符串
        :return: 是否只包含数字
        """
        if StrUtil.is_empty(s):
            return False
        return s.isdigit()

    @staticmethod
    def is_alpha(s: str) -> bool:
        """
        检查字符串是否只包含字母
        :param s: 原始字符串
        :return: 是否只包含字母
        """
        if StrUtil.is_empty(s):
            return False
        return s.isalpha()

    @staticmethod
    def is_alphanumeric(s: str) -> bool:
        """
        检查字符串是否只包含字母和数字
        :param s: 原始字符串
        :return: 是否只包含字母和数字
        """
        if StrUtil.is_empty(s):
            return False
        return s.isalnum()

    @staticmethod
    def has_empty(*strs) -> bool:
        """
        检查多个字符串中是否包含空字符串
        :param strs: 字符串列表
        :return: 是否包含空字符串
        """
        return any(StrUtil.is_empty(s) for s in strs)

    @staticmethod
    def has_blank(*strs) -> bool:
        """
        检查多个字符串中是否包含空白字符串
        :param strs: 字符串列表
        :return: 是否包含空白字符串
        """
        return any(StrUtil.is_blank(s) for s in strs)

    @staticmethod
    def is_all_empty(*strs) -> bool:
        """
        检查所有字符串是否都为空
        :param strs: 字符串列表
        :return: 是否都为空
        """
        return all(StrUtil.is_empty(s) for s in strs)

    @staticmethod
    def is_all_blank(*strs) -> bool:
        """
        检查所有字符串是否都为空白
        :param strs: 字符串列表
        :return: 是否都为空白
        """
        return all(StrUtil.is_blank(s) for s in strs)

    @staticmethod
    def is_all_not_empty(*strs) -> bool:
        """
        检查所有字符串是否都不为空
        :param strs: 字符串列表
        :return: 是否都不为空
        """
        return all(StrUtil.is_not_empty(s) for s in strs)

    @staticmethod
    def is_all_not_blank(*strs) -> bool:
        """
        检查所有字符串是否都不为空白
        :param strs: 字符串列表
        :return: 是否都不为空白
        """
        return all(StrUtil.is_not_blank(s) for s in strs)

    @staticmethod
    def null_to_empty(s: Optional[str]) -> str:
        """
        如果字符串为 None，返回空字符串
        :param s: 原始字符串
        :return: 处理后的字符串
        """
        return StrPool.EMPTY if s is None else s

    @staticmethod
    def empty_to_null(s: Optional[str]) -> Optional[str]:
        """
        如果字符串为空字符串，返回 None
        :param s: 原始字符串
        :return: 处理后的字符串
        """
        return None if StrUtil.is_empty(s) else s

    @staticmethod
    def blank_to_null(s: Optional[str]) -> Optional[str]:
        """
        如果字符串为空白，返回 None
        :param s: 原始字符串
        :return: 处理后的字符串
        """
        return None if StrUtil.is_blank(s) else s

    @staticmethod
    def null_to_default(s: Optional[str], default: str) -> str:
        """
        如果字符串为 None，返回默认值
        :param s: 原始字符串
        :param default: 默认值
        :return: 处理后的字符串
        """
        return default if s is None else s

    @staticmethod
    def empty_to_default(s: Optional[str], default: str) -> str:
        """
        如果字符串为空，返回默认值
        :param s: 原始字符串
        :param default: 默认值
        :return: 处理后的字符串
        """
        return default if StrUtil.is_empty(s) else s

    @staticmethod
    def blank_to_default(s: Optional[str], default: str) -> str:
        """
        如果字符串为空白，返回默认值
        :param s: 原始字符串
        :param default: 默认值
        :return: 处理后的字符串
        """
        return default if StrUtil.is_blank(s) else s

    @staticmethod
    def first_not_empty(*strs) -> Optional[str]:
        """
        返回第一个非空字符串
        :param strs: 字符串列表
        :return: 第一个非空字符串，如果没有则返回 None
        """
        for s in strs:
            if StrUtil.is_not_empty(s):
                return s
        return None

    @staticmethod
    def first_not_blank(*strs) -> Optional[str]:
        """
        返回第一个非空白字符串
        :param strs: 字符串列表
        :return: 第一个非空白字符串，如果没有则返回 None
        """
        for s in strs:
            if StrUtil.is_not_blank(s):
                return s
        return None

    @staticmethod
    def pad_start(s: str, length: int, pad_char: str = ' ') -> str:
        """
        在字符串开头填充指定字符，直到达到指定长度
        :param s: 原始字符串
        :param length: 目标长度
        :param pad_char: 填充字符
        :return: 填充后的字符串
        """
        if s is None:
            s = StrPool.EMPTY

        if pad_char is None or len(pad_char) == 0:
            pad_char = StrPool.SPACE

        pad_length = length - len(s)
        if pad_length <= 0:
            return s

        return StrUtil.repeat(pad_char, pad_length) + s

    @staticmethod
    def pad_end(s: str, length: int, pad_char: str = ' ') -> str:
        """
        在字符串结尾填充指定字符，直到达到指定长度
        :param s: 原始字符串
        :param length: 目标长度
        :param pad_char: 填充字符
        :return: 填充后的字符串
        """
        if s is None:
            s = StrPool.EMPTY

        if pad_char is None or len(pad_char) == 0:
            pad_char = StrPool.SPACE

        pad_length = length - len(s)
        if pad_length <= 0:
            return s

        return s + StrUtil.repeat(pad_char, pad_length)

    @staticmethod
    def center(s: str, length: int, pad_char: str = ' ') -> str:
        """
        在字符串两边填充指定字符，使其居中
        :param s: 原始字符串
        :param length: 目标长度
        :param pad_char: 填充字符
        :return: 居中后的字符串
        """
        if s is None:
            s = StrPool.EMPTY

        if pad_char is None or len(pad_char) == 0:
            pad_char = StrPool.SPACE

        pad_length = length - len(s)
        if pad_length <= 0:
            return s

        left_pad = pad_length // 2
        right_pad = pad_length - left_pad

        return StrUtil.repeat(pad_char, left_pad) + s + StrUtil.repeat(pad_char, right_pad)

    @staticmethod
    def is_wrapped(s: str, wrap_char: str) -> bool:
        """
        检查字符串是否被指定字符包裹
        :param s: 原始字符串
        :param wrap_char: 包裹字符
        :return: 是否被包裹
        """
        if s is None or wrap_char is None or len(s) < 2:
            return False

        return s.startswith(wrap_char) and s.endswith(wrap_char)

    @staticmethod
    def replace(s: str, old: str, new: str, count: int = -1) -> str:
        """
        替换字符串中的子串
        :param s: 原始字符串
        :param old: 要替换的子串
        :param new: 替换为的子串
        :param count: 替换次数，-1 表示全部替换
        :return: 替换后的字符串
        """
        if s is None or old is None or new is None:
            return s

        return s.replace(old, new, count)

    @staticmethod
    def replace_first(s: str, old: str, new: str) -> str:
        """
        替换字符串中第一次出现的子串
        :param s: 原始字符串
        :param old: 要替换的子串
        :param new: 替换为的子串
        :return: 替换后的字符串
        """
        if s is None or old is None or new is None:
            return s

        return s.replace(old, new, 1)

    @staticmethod
    def replace_last(s: str, old: str, new: str) -> str:
        """
        替换字符串中最后一次出现的子串
        :param s: 原始字符串
        :param old: 要替换的子串
        :param new: 替换为的子串
        :return: 替换后的字符串
        """
        if s is None or old is None or new is None:
            return s

        # 找到最后一次出现的位置
        last_index = s.rfind(old)
        if last_index == StrUtil.INDEX_NOT_FOUND:
            return s

        return s[:last_index] + new + s[last_index + len(old):]

if __name__ == '__main__':
    # 使用示例

    # 常量使用
    print(StrPool.EMPTY)  # ""
    print(StrPool.SPACE)  # " "

    # 字符串判空
    print(StrUtil.is_empty(""))  # True
    print(StrUtil.is_blank("  "))  # True

    # 字符串转换
    print(StrUtil.camel_to_snake("userName"))  # "user_name"
    print(StrUtil.snake_to_camel("user_name"))  # "userName"

    # 字符串处理
    print(StrUtil.trim("  hello  "))  # "hello"
    print(StrUtil.substr("hello world", 0, 5))  # "hello"
    print(StrUtil.reverse("hello"))  # "olleh"

    # 字符串检查
    print(StrUtil.start_with("hello world", "hello"))  # True
    print(StrUtil.end_with("hello world", "world"))  # True
    print(StrUtil.contains_any("hello world", "world", "test"))  # True

    # 字符串替换
    print(StrUtil.replace("hello world", "world", "python"))  # "hello python"
    print(StrUtil.remove("hello world", "o"))  # "hell wrld"

    # 默认值处理
    print(StrUtil.default_if_empty(None, "default"))  # "default"
    print(StrUtil.first_not_blank("", "  ", "hello"))  # "hello"

    # 字符串填充
    print(StrUtil.pad_start("5", 3, "0"))  # "005"
    print(StrUtil.pad_end("5", 3, "0"))  # "500"
    print(StrUtil.center("5", 3, "0"))  # "050"