import base64
import re
from typing import Optional, Union, Tuple, AnyStr, BinaryIO
from pathlib import Path
import io


class Base64Util:
    """Base64工具类，提供Base64的编码和解码方案"""

    # 默认字符集
    DEFAULT_CHARSET = "UTF-8"

    # -------------------------------------------------------------------- encode

    @staticmethod
    def encode(data: bytes, line_sep: bool = False) -> bytes:
        """
        Base64编码

        Args:
            data: 被编码的数据
            line_sep: 是否添加换行符（MIME格式）

        Returns:
            编码后的字节数组
        """
        if data is None:
            return None

        if line_sep:
            # 每76个字符添加CRLF
            return base64.standard_b64encode(data)
        else:
            # 无换行符
            return base64.b64encode(data)

    @staticmethod
    def encode_url_safe(data: bytes, line_sep: bool = False) -> bytes:
        """
        URL安全的Base64编码

        Args:
            data: 被编码的数据
            line_sep: 是否添加换行符（MIME格式）

        Returns:
            编码后的字节数组
        """
        if data is None:
            return None

        # URL安全编码（去除填充）
        return base64.urlsafe_b64encode(data)

    @staticmethod
    def encode_str(source: str, charset: str = DEFAULT_CHARSET) -> str:
        """
        Base64编码字符串

        Args:
            source: 被编码的字符串
            charset: 字符集编码

        Returns:
            编码后的Base64字符串
        """
        if source is None:
            return None

        # 将字符串转换为字节数组
        data = source.encode(charset)
        return Base64Util.encode(data).decode("ASCII")

    @staticmethod
    def encode_url_safe_str(source: str, charset: str = DEFAULT_CHARSET) -> str:
        """
        URL安全的Base64编码字符串

        Args:
            source: 被编码的字符串
            charset: 字符集编码

        Returns:
            编码后的Base64字符串
        """
        if source is None:
            return None

        data = source.encode(charset)
        return Base64Util.encode_url_safe(data).decode("ASCII")

    @staticmethod
    def encode_without_padding(source: str, charset: str = DEFAULT_CHARSET) -> str:
        """
        Base64编码（不进行末尾填充）

        Args:
            source: 被编码的字符串
            charset: 字符集编码

        Returns:
            编码后的Base64字符串（无'='填充）
        """
        if source is None:
            return None

        data = source.encode(charset)
        # 编码并去除填充字符
        encoded = base64.b64encode(data).decode("ASCII")
        return encoded.rstrip('=')

    @staticmethod
    def encode_bytes(source: bytes) -> str:
        """
        Base64编码字节数组

        Args:
            source: 被编码的字节数组

        Returns:
            编码后的Base64字符串
        """
        if source is None:
            return None

        return base64.b64encode(source).decode("ASCII")

    @staticmethod
    def encode_bytes_without_padding(source: bytes) -> str:
        """
        Base64编码字节数组（不进行末尾填充）

        Args:
            source: 被编码的字节数组

        Returns:
            编码后的Base64字符串（无'='填充）
        """
        if source is None:
            return None

        encoded = base64.b64encode(source).decode("ASCII")
        return encoded.rstrip('=')

    @staticmethod
    def encode_bytes_url_safe(source: bytes) -> str:
        """
        URL安全的Base64编码字节数组

        Args:
            source: 被编码的字节数组

        Returns:
            编码后的Base64字符串
        """
        if source is None:
            return None

        return base64.urlsafe_b64encode(source).decode("ASCII")

    @staticmethod
    def encode_stream(input_stream: BinaryIO) -> str:
        """
        Base64编码输入流

        Args:
            input_stream: 被编码的输入流

        Returns:
            编码后的Base64字符串
        """
        if input_stream is None:
            return None

        # 读取所有数据
        data = input_stream.read()
        return Base64Util.encode_bytes(data)

    @staticmethod
    def encode_stream_url_safe(input_stream: BinaryIO) -> str:
        """
        URL安全的Base64编码输入流

        Args:
            input_stream: 被编码的输入流

        Returns:
            编码后的Base64字符串
        """
        if input_stream is None:
            return None

        data = input_stream.read()
        return Base64Util.encode_bytes_url_safe(data)

    @staticmethod
    def encode_file(file_path: Union[str, Path]) -> str:
        """
        Base64编码文件内容

        Args:
            file_path: 文件路径

        Returns:
            编码后的Base64字符串
        """
        file_path = Path(file_path)
        if not file_path.is_file():
            return None

        # 读取文件内容
        data = file_path.read_bytes()
        return Base64Util.encode_bytes(data)

    @staticmethod
    def encode_file_url_safe(file_path: Union[str, Path]) -> str:
        """
        URL安全的Base64编码文件内容

        Args:
            file_path: 文件路径

        Returns:
            编码后的Base64字符串
        """
        file_path = Path(file_path)
        if not file_path.is_file():
            return None

        data = file_path.read_bytes()
        return Base64Util.encode_bytes_url_safe(data)

    @staticmethod
    def encode_str_advanced(arr: bytes, is_multi_line: bool, is_url_safe: bool) -> str:
        """
        高级Base64编码

        Args:
            arr: 被编码的数据
            is_multi_line: 是否添加换行符
            is_url_safe: 是否使用URL安全编码

        Returns:
            编码后的字符串
        """
        if arr is None:
            return None

        if is_url_safe:
            # URL安全编码
            if is_multi_line:
                # URL安全编码通常不包含换行符
                return base64.urlsafe_b64encode(arr).decode("ASCII")
            else:
                return base64.urlsafe_b64encode(arr).decode("ASCII")
        else:
            # 标准Base64编码
            if is_multi_line:
                # 添加换行符
                return base64.standard_b64encode(arr).decode("ASCII")
            else:
                return base64.b64encode(arr).decode("ASCII")

    # -------------------------------------------------------------------- decode
    @staticmethod
    def decode_str(source: str, charset: str = "UTF-8", errors: str = "strict", fallback_encodings: list = None) -> str:
        """
        Base64解码为字符串，增强错误处理和编码检测

        Args:
            source: 被解码的Base64字符串
            charset: 期望的字符集编码（默认UTF-8）
            errors: 解码错误处理策略 ['strict', 'ignore', 'replace']
            fallback_encodings: 当指定编码失败时，尝试的备用编码列表

        Returns:
            解码后的字符串

        Raises:
            UnicodeDecodeError: 当所有编码尝试均失败且 errors='strict' 时
        """
        if source is None:
            return None

        # 解码字节数据
        decoded_bytes = Base64Util.decode(source)  # 这里得到的是 bytes

        # 如果用户明确知道这是二进制数据，不应转字符串，可以增加判断或直接返回 bytes
        # 但此方法设计就是转字符串，所以主要处理编码问题

        if fallback_encodings is None:
            fallback_encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'iso-8859-1']

        # 确保首要尝试用户指定的编码
        encodings_to_try = [charset] + [enc for enc in fallback_encodings if enc != charset]

        last_error = None
        for encoding in encodings_to_try:
            try:
                return decoded_bytes.decode(encoding, errors=errors)
            except UnicodeDecodeError as e:
                last_error = e
                continue  # 尝试下一个编码

        # 如果所有编码都失败了，根据 errors 策略处理
        if errors == 'ignore':
            # 尽可能忽略错误解码，但可能仍有异常
            return decoded_bytes.decode('utf-8', errors='ignore')
        elif errors == 'replace':
            # 用替换符替换无法解码的字节
            return decoded_bytes.decode('utf-8', errors='replace')
        else:
            # 'strict' 或其他未定义行为，重新抛出最后一个异常
            raise last_error

    @staticmethod
    def decode_str_gbk(source: str, errors: str = "strict") -> str:
        """
        Base64解码为GBK字符串，增强错误处理

        Args:
            source: 被解码的Base64字符串
            errors: 解码错误处理策略 ['strict', 'ignore', 'replace']

        Returns:
            解码后的GBK字符串
        """
        return Base64Util.decode_str(source, "gbk", errors, fallback_encodings=['gb18030', 'utf-8'])

    # 新增方法：自动检测编码
    @staticmethod
    def decode_str_auto(source: str, errors: str = "replace") -> str:
        """
        Base64解码为字符串，自动检测编码

        Args:
            source: 被解码的Base64字符串
            errors: 解码错误处理策略 ['strict', 'ignore', 'replace']

        Returns:
            解码后的字符串
        """
        if source is None:
            return None

        decoded_bytes = Base64Util.decode(source)

        # 使用 chardet 检测编码
        detection_result = chardet.detect(decoded_bytes)
        detected_encoding = detection_result['encoding']
        confidence = detection_result['confidence']

        # 如果置信度较低，可以回落到一些常见编码
        if confidence < 0.7:
            encodings_to_try = ['utf-8', 'gbk', 'gb18030', 'iso-8859-1']
        else:
            encodings_to_try = [detected_encoding] + ['utf-8', 'gbk', 'gb18030']  # 首选检测到的编码

        last_error = None
        for encoding in encodings_to_try:
            if encoding is None:
                continue
            try:
                return decoded_bytes.decode(encoding, errors=errors)
            except UnicodeDecodeError as e:
                last_error = e
                continue

        if errors == 'ignore':
            return decoded_bytes.decode('utf-8', errors='ignore')
        elif errors == 'replace':
            return decoded_bytes.decode('utf-8', errors='replace')
        else:
            raise last_error if last_error else UnicodeDecodeError("Failed to decode with any encoding")

    @staticmethod
    def decode_to_file(source: str, dest_file: Union[str, Path]) -> Path:
        """
        Base64解码并写入文件

        Args:
            source: 被解码的Base64字符串
            dest_file: 目标文件路径

        Returns:
            目标文件路径
        """
        if source is None:
            return None

        dest_path = Path(dest_file)
        # 解码数据
        data = Base64Util.decode(source)
        # 写入文件
        dest_path.write_bytes(data)
        return dest_path

    @staticmethod
    def decode_to_stream(source: str, output_stream: BinaryIO) -> None:
        """
        Base64解码并写入输出流

        Args:
            source: 被解码的Base64字符串
            output_stream: 输出流
        """
        if source is None:
            return

        # 解码数据
        data = Base64Util.decode(source)
        # 写入输出流
        output_stream.write(data)

    @staticmethod
    def decode(source: str) -> bytes:
        """
        Base64解码

        Args:
            source: 被解码的Base64字符串

        Returns:
            解码后的字节数组
        """
        if source is None:
            return None

        # 添加必要的填充字符
        padding_needed = len(source) % 4
        if padding_needed:
            source += '=' * (4 - padding_needed)

        try:
            return base64.b64decode(source)
        except base64.binascii.Error:
            # 尝试URL安全的Base64解码
            return base64.urlsafe_b64decode(source)

    @staticmethod
    def decode_bytes(data: bytes) -> bytes:
        """
        Base64解码字节数组

        Args:
            data: 被解码的Base64字节数组

        Returns:
            解码后的字节数组
        """
        if data is None:
            return None

        # 将字节数组转换为字符串
        base64_str = data.decode("ASCII")
        return Base64Util.decode(base64_str)

    @staticmethod
    def is_base64(source: str) -> bool:
        """
        检查字符串是否为有效的Base64格式

        Args:
            source: 待检查的字符串

        Returns:
            是否是有效的Base64格式
        """
        if source is None or len(source) < 2:
            return False

        # 检查字符串是否只包含Base64字符
        pattern = re.compile(r'^[A-Za-z0-9+/]+={0,2}$')
        if not pattern.match(source):
            return False

        # 检查填充字符位置是否正确
        if '=' in source:
            # 填充字符只能在字符串末尾
            if source.rstrip('=').find('=') != -1:
                return False

            # 填充字符数量只能是0、1或2个
            if len(source) % 4 != 0:
                return False

        try:
            # 尝试解码验证
            base64.b64decode(source, validate=True)
            return True
        except:
            # 尝试URL安全解码
            try:
                base64.urlsafe_b64decode(source)
                return True
            except:
                return False

    @staticmethod
    def is_base64_bytes(data: bytes) -> bool:
        """
        检查字节数组是否为有效的Base64格式

        Args:
            data: 待检查的字节数组

        Returns:
            是否是有效的Base64格式
        """
        if data is None or len(data) < 3:
            return False

        try:
            # 尝试转换为字符串
            source = data.decode("ASCII")
            return Base64Util.is_base64(source)
        except UnicodeDecodeError:
            return False

if __name__ == '__main__':
    # ======================
    # 编码示例
    # ======================

    # 1. 基本字符串编码
    text = "Hello, World!"
    encoded = Base64Util.encode_str(text)
    print(f"Base64编码: {encoded}")  # SGVsbG8sIFdvcmxkIQ==

    # 2. URL安全编码
    url_safe = Base64Util.encode_url_safe_str("https://example.com/data?q=测试")
    print(f"URL安全编码: {url_safe}")  # aHR0cHM6Ly9leGFtcGxlLmNvbS9kYXRhP3E95rWL6K-V

    # 3. 无填充编码
    no_padding = Base64Util.encode_without_padding("Hello")
    print(f"无填充编码: {no_padding}")  # SGVsbG8

    # 4. 文件编码
    file_path = "example.jpg"
    encoded_file = Base64Util.encode_file(file_path)
    print(f"文件编码长度: {len(encoded_file) if encoded_file else 0}")

    # 5. 流编码
    with open(r"D:\\Downloads\\example.txt", "rb") as f:
        encoded_stream = Base64Util.encode_stream(f)
        print(f"流编码: {encoded_stream[:30]}...")

    # ======================
    # 解码示例
    # ======================

    # 1. 基本解码
    decoded = Base64Util.decode_str("SGVsbG8sIFdvcmxkIQ==")
    print(f"解码结果: {decoded}")  # Hello, World!

    # 2. GBK解码
    decoded_gbk = Base64Util.decode_str_gbk("5Lit5paH")
    print(f"GBK解码: {decoded_gbk}")  # 你好

    # 3. 解码到文件
    Base64Util.decode_to_file(encoded_file, "decoded.jpg")
    print("文件解码完成")

    # 4. 解码到流
    output = io.BytesIO()
    Base64Util.decode_to_stream(encoded, output)
    print(f"流解码结果: {output.getvalue().decode()}")

    # ======================
    # 格式验证
    # ======================

    # 1. 验证Base64字符串
    print(f"是否有效Base64: {Base64Util.is_base64('SGVsbG8sIFdvcmxkIQ==')}")  # True
    print(f"是否有效Base64: {Base64Util.is_base64('Invalid@Base64')}")  # False

    # 2. 验证字节数组
    data = b'SGVsbG8sIFdvcmxkIQ=='
    print(f"是否有效Base64字节: {Base64Util.is_base64_bytes(data)}")  # True