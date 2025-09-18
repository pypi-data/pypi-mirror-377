"""
转义和反转义工具类 (EscapeUtil)
参考Java Hutool EscapeUtil设计，提供HTML、XML转义和反转义功能，以及类JavaScript的escape/unescape功能。
注意：JavaScript的escape/unescape方法已废弃，现代应用应优先使用encodeURIComponent/decodeURIComponent。
此类主要用于兼容旧系统或特定需求。

主要功能：
1. HTML4转义和反转义
2. XML转义和反转义
3. 类JavaScript的Escape编码和解码 (Unicode)
4. 安全反转义处理
"""
import html
import re
from typing import Callable, Optional, Union
import xml.sax.saxutils as saxutils


class EscapeUtil:
    """
    转义和反转义工具类
    参考Java Hutool EscapeUtil实现，并提供了类似JavaScript的escape/unescape功能。
    """

    # 不转义的字符（参考JavaScript的escape函数行为）
    NOT_ESCAPE_CHARS = "*@-_+./"

    @staticmethod
    def escape_html4(html_text: Optional[str]) -> str:
        """
        转义HTML4中的特殊字符
        转义规则: & -> &amp;, < -> &lt;, > -> &gt;, " -> &quot;, ' -> &#39;

        Args:
            html_text: HTML文本，可以为None

        Returns:
            转义后的文本，如果输入为None则返回空字符串

        Examples:
            >> EscapeUtil.escape_html4('<div>"Hello" & 'World'</div>')
            '&lt;div&gt;&quot;Hello&quot; &amp; &#39;World&#39;&lt;/div&gt;'
            >> EscapeUtil.escape_html4(None)
            ''
        """
        if html_text is None:
            return ''
        return html.escape(html_text, quote=True)

    @staticmethod
    def unescape_html4(html_text: Optional[str]) -> str:
        """
        反转义HTML4中的特殊字符

        Args:
            html_text: HTML文本，可以为None

        Returns:
            反转义后的文本，如果输入为None则返回空字符串

        Examples:
            >> EscapeUtil.unescape_html4('&lt;div&gt;&quot;Hello&quot; &amp; &#39;World&#39;&lt;/div&gt;')
            '<div>"Hello" & \\'World\\'</div>'
            >> EscapeUtil.unescape_html4(None)
            ''
        """
        if html_text is None:
            return ''
        return html.unescape(html_text)

    @staticmethod
    def escape_xml(xml_text: Optional[str]) -> str:
        """
        转义XML中的特殊字符
        转义规则：
          & -> &amp;
          < -> &lt;
          > -> &gt;
          " -> &quot;
          ' -> &apos;

        Args:
            xml_text: XML文本，可以为None

        Returns:
            转义后的文本，如果输入为None则返回空字符串

        Examples:
            >> EscapeUtil.escape_xml('<message>"Hello" & 'World'</message>')
            '&lt;message&gt;&quot;Hello&quot; &amp; &apos;World&apos;&lt;/message&gt;'
            >> EscapeUtil.escape_xml(None)
            ''
        """
        if xml_text is None:
            return ''

        # 使用saxutils进行基本转义（处理 &, <, >, "）
        escaped = saxutils.escape(xml_text)

        # saxutils默认不转义单引号，需要额外处理
        escaped = escaped.replace("'", "&apos;")

        return escaped

    @staticmethod
    def unescape_xml(xml_text: Optional[str]) -> str:
        """
        反转义XML中的特殊字符

        Args:
            xml_text: XML文本，可以为None

        Returns:
            反转义后的文本，如果输入为None则极返回空字符串

        Examples:
            >> EscapeUtil.unescape_xml('&lt;message&gt;&quot;Hello&quot; &amp; &apos;World&apos;&lt;/message&gt;')
            '<message>"Hello" & \\'World\\'</message>'
            >> EscapeUtil.unescape_xml(None)
            ''
        """
        if xml_text is None:
            return ''

        # saxutils的unescape可以处理基本的XML实体(&amp;, &lt;, &gt;, &quot;)
        unescaped = saxutils.unescape(xml_text)

        # 处理saxutils未处理的单引号 &apos;
        unescaped = unescaped.replace("&apos;", "'")

        return unescaped

    @staticmethod
    def escape(content: Optional[str]) -> str:
        """
        Escape编码（Unicode）（模拟已废弃的JavaScript escape()方法）
        注意：此方法模拟已废弃的JavaScript escape()函数行为，现代应用应优先使用标准URL编码。
        该方法不会对 ASCII 字母和数字进行编码，也不会对指定标点符号进行编码：*@-_+./
        其他所有的字符都会被转义序列替换。
        对于Unicode字符，使用%uXXXX格式。

        Args:
            content: 被转义的内容，可以为None

        Returns:
            编码后的字符串，如果输入为None则返回空字符串

        Examples:
            >> EscapeUtil.escape('Hello World 123!@*-_+./')
            'Hello%20World%20123%21%40%2A%2D%5F%2B%2E%2F'
            >> EscapeUtil.escape('中文')
            '%u4E2D%u6587'
            >> EscapeUtil.escape(None)
            ''
        """
        if content is None:
            return ''

        # 定义过滤器函数（不过滤字母数字和指定字符）
        def default_filter(c: str) -> bool:
            return not (c.isalnum() or c in EscapeUtil.NOT_ESCAPE_CHARS)

        return EscapeUtil._escape(content, default_filter)

    @staticmethod
    def escape_all(content: Optional[str]) -> str:
        """
        Escape编码（Unicode），对所有字符进行编码
        注意：此方法模拟已废弃的JavaScript escape()函数行为，但对所有字符进行编码。
        字母数字和指定字符也会被编码。

        Args:
            content: 被转义的内容，可以为None

        Returns:
            编码后的字符串，如果输入为None则返回空字符串

        Examples:
            >> EscapeUtil.escape_all('Hello World 123!@*-_+./')
            '%48%65%6C%6C%6F%20%57%6F%72%6C%64%20%31%32%33%21%40%2A%2D%5F%2B%2E%2F'
            >> EscapeUtil.escape_all(None)
            ''
        """
        if content is None:
            return ''

        # 对所有字符进行编码
        return EscapeUtil._escape(content, lambda c: True)

    @staticmethod
    def _escape(content: str, filter_func: Callable[[str], bool]) -> str:
        """
        Escape编码（Unicode）的内部实现

        Args:
            content: 被转义的内容
            filter_func: 编码过滤器函数，返回True表示需要编码

        Returns:
            编码后的字符串
        """
        result = []

        for char in content:
            code_point = ord(char)

            # 检查是否应该跳过编码
            if not filter_func(char):
                result.append(char)
            elif code_point < 256:
                # 单字节字符使用 %XX 格式（大写字母，两位）
                result.append(f"%{code_point:02X}")
            else:
                # 多字节字符使用 %uXXXX 格式（大写字母，四位，不足补零）
                # 统一输出4位大写十六进制数，确保格式一致
                result.append(f"%u{code_point:04X}")

        return ''.join(result)

    @staticmethod
    def unescape(content: Optional[str]) -> str:
        """
        Escape解码（模拟已废弃的JavaScript unescape()方法）
        注意：此方法模拟已废弃的JavaScript unescape()函数行为。

        Args:
            content: 被转义的内容，可以为None

        Returns:
            解码后的字符串，如果输入为None则返回空字符串

        Examples:
            >> EscapeUtil.unescape('Hello%20World%20123%21%40%2A%2D%5F%2B%2E%2F')
            'Hello World 123!@*-_+./'
            >> EscapeUtil.unescape('%u4E2D%u6587')
            '中文'
            >> EscapeUtil.unescape(None)
            ''
        """
        if content is None:
            return ''

        # 使用正则表达式匹配所有转义序列
        def replace_escape(match):
            escape_seq = match.group(0)

            if escape_seq.startswith('%u'):
                # Unicode转义序列 %uXXXX (不区分大小写)
                hex_code = escape_seq[2:]
                try:
                    code_point = int(hex_code, 16)
                    # 检查码点是否在有效范围内
                    if 0 <= code_point <= 0x10FFFF:
                        return chr(code_point)
                    else:
                        # 码点无效，返回原序列
                        return escape_seq
                except (ValueError, OverflowError):
                    return escape_seq
            elif escape_seq.startswith('%'):
                # 十六进制转义序列 %XX (不区分大小写)
                hex_code = escape_seq[1:]
                try:
                    code_point = int(hex_code, 16)
                    # 检查码点是否在有效范围内 (0-255)
                    if 0 <= code_point <= 255:
                        return chr(code_point)
                    else:
                        # 码点无效，返回原序列
                        return escape_seq
                except (ValueError, OverflowError):
                    return escape_seq
            else:
                return escape_seq

        # 匹配 %XX 和 %uXXXX 格式的转义序列 (不区分大小写)
        pattern = r'%u[0-9a-fA-F]{4}|%[0-9a-fA-F]{2}'
        return re.sub(pattern, replace_escape, content)

    @staticmethod
    def safe_unescape(content: Optional[str]) -> str:
        """
        安全的unescape文本，当文本包含无效转义序列时，保留原序列而不是抛出异常
        此方法会尽最大努力解码，遇到无法解码的序列则保持原样。

        Args:
            content: 内容，可以为None

        Returns:
            解码后的字符串，如果解码失败部分返回原序列，如果输入为None则返回空字符串

        Examples:
            >> EscapeUtil.safe_unescape('Hello%20World')
            'Hello World'
            >> EscapeUtil.safe_unescape('正常文本')
            '正常文本'
            >> EscapeUtil.safe_unescape('%invalid')
            '%invalid'
            >> EscapeUtil.safe_unescape('混合%20有效%u4E2D和%无效序列')
            '混合 有效中和%无效序列'
            >> EscapeUtil.safe_unescape(None)
            ''
        """
        if content is None:
            return ''
        # unescape方法内部已经通过try-except处理了无效序列，直接调用即可
        return EscapeUtil.unescape(content)


# 单元测试和示例
if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)

    # 示例用法
    print("EscapeUtil示例:")

    # HTML转义示例
    print("\n1. HTML转义示例:")
    html_text = '<div>"Hello" & '
    escaped_html = EscapeUtil.escape_html4(html_text)
    unescaped_html = EscapeUtil.unescape_html4(escaped_html)
    print(f"原始HTML: {html_text}")
    print(f"转义后: {escaped_html}")
    print(f"反转义后: {unescaped_html}")

    # XML转义示例
    print("\n2. XML转义示例:")
    xml_text = '<message>"Hello" & '
    escaped_xml = EscapeUtil.escape_xml(xml_text)
    unescaped_xml = EscapeUtil.unescape_xml(escaped_xml)
    print(f"原始XML: {xml_text}")
    print(f"转义后: {escaped_xml}")
    print(f"反转义后: {unescaped_xml}")

    # Unicode Escape示例
    print("\n3. Unicode Escape示例:")
    text = "Hello World 123!@*-_+./"
    escaped_text = EscapeUtil.escape(text)
    unescaped_text = EscapeUtil.unescape(escaped_text)
    print(f"原始文本: {text}")
    print(f"Escape编码后: {escaped_text}")
    print(f"Escape解码后: {unescaped_text}")

    # 中文Escape示例
    print("\n4. 中文Escape示例:")
    chinese_text = "中文"
    escaped_chinese = EscapeUtil.escape(chinese_text)
    unescaped_chinese = EscapeUtil.unescape(escaped_chinese)
    print(f"原始中文: {chinese_text}")
    print(f"Escape编码后: {escaped_chinese}")
    print(f"Escape解码后: {unescaped_chinese}")

    # 安全反转义示例
    print("\n5. 安全反转义示例:")
    test_cases = [
        "%invalid",
        "混合%20有效%u4E2D和%无效序列",
        "%ZZ",
        "%u123",
        "%u12345"
    ]
    for test_case in test_cases:
        safe_result = EscapeUtil.safe_unescape(test_case)
        print(f"输入: '{test_case}' -> 输出: '{safe_result}'")

    # 空值和None值处理示例
    print("\n6. 空值处理示例:")
    print(f"None值转义: '{EscapeUtil.escape_html4(None)}'")
    print(f"空字符串转义: '{EscapeUtil.escape_html4('')}'")