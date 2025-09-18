import hashlib
import hmac
from pathlib import Path
from typing import Union


class DigestUtil:
    """摘要算法工具类，提供常见的消息摘要算法支持"""

    DEFAULT_CHARSET = "UTF-8"

    # -------------------------------------------------------------------- MD5

    @staticmethod
    def md5(data: Union[bytes, str], charset: str = DEFAULT_CHARSET) -> bytes:
        """
        计算32位MD5摘要值

        Args:
            data: 被摘要数据，可以是字节数组或字符串
            charset: 字符集编码（当data为字符串时使用）

        Returns:
            MD5摘要字节数组
        """
        if isinstance(data, str):
            data = data.encode(charset)
        return hashlib.md5(data).digest()

    @staticmethod
    def md5_hex(data: Union[bytes, str], charset: str = DEFAULT_CHARSET) -> str:
        """
        计算32位MD5摘要值，并转为16进制字符串

        Args:
            data: 被摘要数据，可以是字节数组或字符串
            charset: 字符集编码（当data为字符串时使用）

        Returns:
            MD5摘要的16进制表示
        """
        if isinstance(data, str):
            data = data.encode(charset)
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def md5_hex16(data: Union[bytes, str], charset: str = DEFAULT_CHARSET) -> str:
        """
        计算16位MD5摘要值，并转为16进制字符串

        Args:
            data: 被摘要数据，可以是字节数组或字符串
            charset: 字符集编码（当data为字符串时使用）

        Returns:
            16位MD5摘要的16进制表示
        """
        full_md5 = DigestUtil.md5_hex(data, charset)
        return full_md5[8:24]  # 取16位（8-24字符）

    @staticmethod
    def md5_file(file_path: Union[str, Path]) -> bytes:
        """
        计算文件的32位MD5摘要值

        Args:
            file_path: 文件路径

        Returns:
            MD5摘要字节数组
        """
        file_path = Path(file_path)
        hasher = hashlib.md5()
        with file_path.open("rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.digest()

    @staticmethod
    def md5_hex_file(file_path: Union[str, Path]) -> str:
        """
        计算文件的32位MD5摘要值，并转为16进制字符串

        Args:
            file_path: 文件路径

        Returns:
            MD5摘要的16进制表示
        """
        file_path = Path(file_path)
        hasher = hashlib.md5()
        with file_path.open("rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def md5_hex16_file(file_path: Union[str, Path]) -> str:
        """
        计算文件的16位MD5摘要值，并转为16进制字符串

        Args:
            file_path: 文件路径

        Returns:
            16位MD5摘要的16进制表示
        """
        full_md5 = DigestUtil.md5_hex_file(file_path)
        return full_md5[8:24]  # 取16位（8-24字符）

    @staticmethod
    def md5_hex_to16(md5_hex: str) -> str:
        """
        32位MD5转16位MD5

        Args:
            md5_hex: 32位MD5十六进制字符串

        Returns:
            16位MD5十六进制字符串
        """
        return md5_hex[8:24]

    # -------------------------------------------------------------------- SHA-1

    @staticmethod
    def sha1(data: Union[bytes, str], charset: str = DEFAULT_CHARSET) -> bytes:
        """
        计算SHA-1摘要值

        Args:
            data: 被摘要数据，可以是字节数组或字符串
            charset: 字符集编码（当data为字符串时使用）

        Returns:
            SHA-1摘要字节数组
        """
        if isinstance(data, str):
            data = data.encode(charset)
        return hashlib.sha1(data).digest()

    @staticmethod
    def sha1_hex(data: Union[bytes, str], charset: str = DEFAULT_CHARSET) -> str:
        """
        计算SHA-1摘要值，并转为16进制字符串

        Args:
            data: 被摘要数据，可以是字节数组或字符串
            charset: 字符集编码（当data为字符串时使用）

        Returns:
            SHA-1摘要的16进制表示
        """
        if isinstance(data, str):
            data = data.encode(charset)
        return hashlib.sha1(data).hexdigest()

    @staticmethod
    def sha1_file(file_path: Union[str, Path]) -> bytes:
        """
        计算文件的SHA-1摘要值

        Args:
            file_path: 文件路径

        Returns:
            SHA-1摘要字节数组
        """
        file_path = Path(file_path)
        hasher = hashlib.sha1()
        with file_path.open("rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.digest()

    @staticmethod
    def sha1_hex_file(file_path: Union[str, Path]) -> str:
        """
        计算文件的SHA-1摘要值，并转为16进制字符串

        Args:
            file_path: 文件路径

        Returns:
            SHA-1摘要的16进制表示
        """
        file_path = Path(file_path)
        hasher = hashlib.sha1()
        with file_path.open("rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    # -------------------------------------------------------------------- SHA-256

    @staticmethod
    def sha256(data: Union[bytes, str], charset: str = DEFAULT_CHARSET) -> bytes:
        """
        计算SHA-256摘要值

        Args:
            data: 被摘要数据，可以是字节数组或字符串
            charset: 字符集编码（当data为字符串时使用）

        Returns:
            SHA-256摘要字节数组
        """
        if isinstance(data, str):
            data = data.encode(charset)
        return hashlib.sha256(data).digest()

    @staticmethod
    def sha256_hex(data: Union[bytes, str], charset: str = DEFAULT_CHARSET) -> str:
        """
        计算SHA-256摘要值，并转为16进制字符串

        Args:
            data: 被摘要数据，可以是字节数组或字符串
            charset: 字符集编码（当data为字符串时使用）

        Returns:
            SHA-256摘要的16进制表示
        """
        if isinstance(data, str):
            data = data.encode(charset)
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha256_file(file_path: Union[str, Path]) -> bytes:
        """
        计算文件的SHA-256摘要值

        Args:
            file_path: 文件路径

        Returns:
            SHA-256摘要字节数组
        """
        file_path = Path(file_path)
        hasher = hashlib.sha256()
        with file_path.open("rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.digest()

    @staticmethod
    def sha256_hex_file(file_path: Union[str, Path]) -> str:
        """
        计算文件的SHA-256摘要值，并转为16进制字符串

        Args:
            file_path: 文件路径

        Returns:
            SHA-256摘要的16进制表示
        """
        file_path = Path(file_path)
        hasher = hashlib.sha256()
        with file_path.open("rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    # -------------------------------------------------------------------- SHA-512

    @staticmethod
    def sha512(data: Union[bytes, str], charset: str = DEFAULT_CHARSET) -> bytes:
        """
        计算SHA-512摘要值

        Args:
            data: 被摘要数据，可以是字节数组或字符串
            charset: 字符集编码（当data为字符串时使用）

        Returns:
            SHA-512摘要字节数组
        """
        if isinstance(data, str):
            data = data.encode(charset)
        return hashlib.sha512(data).digest()

    @staticmethod
    def sha512_hex(data: Union[bytes, str], charset: str = DEFAULT_CHARSET) -> str:
        """
        计算SHA-512摘要值，并转为16进制字符串

        Args:
            data: 被摘要数据，可以是字节数组或字符串
            charset: 字符集编码（当data为字符串时使用）

        Returns:
            SHA-512摘要的16进制表示
        """
        if isinstance(data, str):
            data = data.encode(charset)
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def sha512_file(file_path: Union[str, Path]) -> bytes:
        """
        计算文件的SHA-512摘要值

        Args:
            file_path: 文件路径

        Returns:
            SHA-512摘要字节数组
        """
        file_path = Path(file_path)
        hasher = hashlib.sha512()
        with file_path.open("rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.digest()

    @staticmethod
    def sha512_hex_file(file_path: Union[str, Path]) -> str:
        """
        计算文件的SHA-512摘要值，并转为16进制字符串

        Args:
            file_path: 文件路径

        Returns:
            SHA-512摘要的16进制表示
        """
        file_path = Path(file_path)
        hasher = hashlib.sha512()
        with file_path.open("rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    # -------------------------------------------------------------------- HMAC

    @staticmethod
    def hmac(algorithm: str, data: bytes, key: bytes) -> bytes:
        """
        计算HMAC摘要值

        Args:
            algorithm: 摘要算法名称（如"md5", "sha256"等）
            data: 被摘要数据
            key: HMAC密钥

        Returns:
            HMAC摘要字节数组
        """
        return hmac.new(key, data, algorithm).digest()

    @staticmethod
    def hmac_hex(algorithm: str, data: bytes, key: bytes) -> str:
        """
        计算HMAC摘要值，并转为16进制字符串

        Args:
            algorithm: 摘要算法名称（如"md5", "sha256"等）
            data: 被摘要数据
            key: HMAC密钥

        Returns:
            HMAC摘要的16进制表示
        """
        return hmac.new(key, data, algorithm).hexdigest()


if __name__ == '__main__':
    # ======================
    # MD5示例
    # ======================

    # 字符串MD5
    text = "Hello, World!"
    print(f"MD5摘要: {DigestUtil.md5_hex(text)}")  # 65a8e27d8879283831b664bd8b7f0ad4
    print(f"16位MD5: {DigestUtil.md5_hex16(text)}")  # 8879283831b664bd

    # 文件MD5
    file_path = r"D:\\Downloads\\example.txt"
    with open(file_path, "w") as f:
        f.write(text)
    print(f"文件MD5: {DigestUtil.md5_hex_file(file_path)}")

    # ======================
    # SHA系列示例
    # ======================

    # SHA-1
    print(f"SHA-1摘要: {DigestUtil.sha1_hex(text)}")  # 0a0a9f2a6772942557ab5355d76af442f8f65e01

    # SHA-256
    print(
        f"SHA-256摘要: {DigestUtil.sha256_hex(text)}")  # dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f

    # SHA-512
    print(f"SHA-512摘要: {DigestUtil.sha512_hex(text)}")  # 374d794a95cd...（64位哈希值）

    # ======================
    # HMAC示例
    # ======================

    key = b"secret-key"
    data = b"important-data"
    print(f"HMAC-SHA256: {DigestUtil.hmac_hex('sha256', data, key)}")