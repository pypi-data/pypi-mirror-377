"""
ZIP压缩工具类
参考Hutool的ZipUtil实现，提供ZIP文件的压缩和解压缩功能
"""
import os
import zipfile
import gzip
import zlib
import io
from typing import List, Optional, Union, Callable, BinaryIO
from pathlib import Path


class ZipUtil:
    """
    ZIP压缩工具类，提供丰富的ZIP文件操作功能
    """

    # 默认编码
    DEFAULT_ENCODING = 'utf-8'

    @staticmethod
    def zip(src_path: Union[str, Path],
            zip_path: Optional[Union[str, Path]] = None,
            encoding: str = DEFAULT_ENCODING,
            include_dir: bool = True,
            filter_func: Optional[Callable[[str], bool]] = None) -> Path:
        """
        压缩文件或目录

        :param src_path: 源文件或目录路径
        :param zip_path: 压缩文件路径，默认为源文件同目录下的[源文件名].zip
        :param encoding: 编码格式，默认为utf-8
        :param include_dir: 是否包含源目录本身
        :param filter_func: 文件过滤函数
        :return: 压缩文件路径
        """
        src_path = Path(src_path)

        # 确定压缩文件路径
        if zip_path is None:
            zip_path = src_path.parent / f"{src_path.stem}.zip"
        zip_path = Path(zip_path)

        # 验证文件
        ZipUtil._validate_files(zip_path, src_path)

        # 创建压缩文件
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6) as zf:
            if src_path.is_file():
                # 压缩单个文件
                arcname = src_path.name if include_dir else None
                ZipUtil._add_file_to_zip(zf, src_path, arcname, encoding, filter_func)
            else:
                # 压缩目录
                ZipUtil._add_directory_to_zip(zf, src_path, include_dir, encoding, filter_func)

        return zip_path

    @staticmethod
    def unzip(zip_path: Union[str, Path],
              out_path: Optional[Union[str, Path]] = None,
              encoding: str = DEFAULT_ENCODING,
              filter_func: Optional[Callable[[str], bool]] = None) -> Path:
        """
        解压ZIP文件

        :param zip_path: ZIP文件路径
        :param out_path: 解压目录路径，默认为ZIP文件同目录下的[文件名]目录
        :param encoding: 编码格式，默认为utf-8
        :param filter_func: 文件过滤函数
        :return: 解压目录路径
        """
        zip_path = Path(zip_path)

        # 确定解压目录
        if out_path is None:
            out_path = zip_path.parent / zip_path.stem
        out_path = Path(out_path)

        # 创建解压目录
        out_path.mkdir(parents=True, exist_ok=True)

        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # 首先检查所有文件是否符合过滤条件
            for file_info in zf.infolist():
                file_name = file_info.filename

                # 处理编码问题
                try:
                    file_name.encode(encoding)
                except UnicodeEncodeError:
                    # 尝试其他常见编码
                    for alt_encoding in ['gbk', 'gb2312', 'iso-8859-1']:
                        try:
                            file_name.encode(alt_encoding)
                            encoding = alt_encoding
                            break
                        except UnicodeEncodeError:
                            continue

                # 应用过滤函数
                if filter_func and not filter_func(file_name):
                    continue

                # 提取文件
                zf.extract(file_name, out_path)

        return out_path

    @staticmethod
    def zip_files(zip_path: Union[str, Path],
                  files: List[Union[str, Path]],
                  encoding: str = DEFAULT_ENCODING,
                  filter_func: Optional[Callable[[str], bool]] = None) -> Path:
        """
        压缩多个文件

        :param zip_path: 压缩文件路径
        :param files: 文件列表
        :param encoding: 编码格式
        :param filter_func: 文件过滤函数
        :return: 压缩文件路径
        """
        zip_path = Path(zip_path)

        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in files:
                file_path = Path(file_path)
                if file_path.exists():
                    if file_path.is_file():
                        ZipUtil._add_file_to_zip(zf, file_path, file_path.name, encoding, filter_func)
                    else:
                        ZipUtil._add_directory_to_zip(zf, file_path, False, encoding, filter_func)

        return zip_path

    @staticmethod
    def zip_stream(content: Union[str, bytes],
                   arcname: str,
                   encoding: str = DEFAULT_ENCODING) -> bytes:
        """
        将数据流压缩到ZIP文件中

        :param content: 要压缩的内容
        :param arcname: 在ZIP中的文件名
        :param encoding: 编码格式
        :return: ZIP文件字节数据
        """
        if isinstance(content, str):
            content = content.encode(encoding)

        with io.BytesIO() as buffer:
            with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(arcname, content)

            return buffer.getvalue()

    @staticmethod
    def unzip_stream(zip_data: bytes,
                     encoding: str = DEFAULT_ENCODING) -> dict:
        """
        从ZIP数据流中解压文件

        :param zip_data: ZIP文件字节数据
        :param encoding: 编码格式
        :return: 文件名到内容的字典
        """
        result = {}

        with io.BytesIO(zip_data) as buffer:
            with zipfile.ZipFile(buffer, 'r') as zf:
                for file_info in zf.infolist():
                    with zf.open(file_info.filename) as file:
                        content = file.read()

                        # 尝试解码文本内容
                        try:
                            content = content.decode(encoding)
                        except UnicodeDecodeError:
                            # 保持为二进制数据
                            pass

                        result[file_info.filename] = content

        return result

    @staticmethod
    def get_file_from_zip(zip_path: Union[str, Path],
                          file_path: str,
                          encoding: str = DEFAULT_ENCODING) -> Optional[Union[str, bytes]]:
        """
        从ZIP文件中获取指定文件的内容

        :param zip_path: ZIP文件路径
        :param file_path: ZIP内的文件路径
        :param encoding: 编码格式
        :return: 文件内容，如果不存在返回None
        """
        zip_path = Path(zip_path)

        if not zip_path.exists():
            return None

        with zipfile.ZipFile(zip_path, 'r') as zf:
            if file_path not in zf.namelist():
                return None

            with zf.open(file_path) as file:
                content = file.read()

                # 尝试解码文本内容
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    return content

    @staticmethod
    def gzip_compress(data: Union[str, bytes],
                      encoding: str = DEFAULT_ENCODING) -> bytes:
        """
        GZIP压缩数据

        :param data: 要压缩的数据
        :param encoding: 编码格式
        :return: 压缩后的数据
        """
        if isinstance(data, str):
            data = data.encode(encoding)

        return gzip.compress(data)

    @staticmethod
    def gzip_decompress(data: bytes,
                        encoding: str = DEFAULT_ENCODING) -> Union[str, bytes]:
        """
        GZIP解压缩数据

        :param data: 要解压的数据
        :param encoding: 编码格式
        :return: 解压后的数据
        """
        decompressed = gzip.decompress(data)

        # 尝试解码文本内容
        try:
            return decompressed.decode(encoding)
        except UnicodeDecodeError:
            return decompressed

    @staticmethod
    def zlib_compress(data: Union[str, bytes],
                      level: int = 6,
                      encoding: str = DEFAULT_ENCODING) -> bytes:
        """
        ZLIB压缩数据

        :param data: 要压缩的数据
        :param level: 压缩级别(0-9)
        :param encoding: 编码格式
        :return: 压缩后的数据
        """
        if isinstance(data, str):
            data = data.encode(encoding)

        return zlib.compress(data, level)

    @staticmethod
    def zlib_decompress(data: bytes,
                        encoding: str = DEFAULT_ENCODING) -> Union[str, bytes]:
        """
        ZLIB解压缩数据

        :param data: 要解压的数据
        :param encoding: 编码格式
        :return: 解压后的数据
        """
        decompressed = zlib.decompress(data)

        # 尝试解码文本内容
        try:
            return decompressed.decode(encoding)
        except UnicodeDecodeError:
            return decompressed

    @staticmethod
    def list_files(zip_path: Union[str, Path],
                   dir_prefix: Optional[str] = None) -> List[str]:
        """
        列出ZIP文件中的文件

        :param zip_path: ZIP文件路径
        :param dir_prefix: 目录前缀
        :return: 文件列表
        """
        zip_path = Path(zip_path)

        if not zip_path.exists():
            return []

        with zipfile.ZipFile(zip_path, 'r') as zf:
            if dir_prefix:
                # 确保目录前缀以/结尾
                if not dir_prefix.endswith('/'):
                    dir_prefix += '/'

                return [name for name in zf.namelist()
                        if name.startswith(dir_prefix) and
                        name != dir_prefix and
                        not name[len(dir_prefix):].count('/')]
            else:
                return zf.namelist()

    @staticmethod
    def _add_file_to_zip(zip_file: zipfile.ZipFile,
                         file_path: Path,
                         arcname: Optional[str],
                         encoding: str,
                         filter_func: Optional[Callable[[str], bool]] = None):
        """
        添加文件到ZIP压缩包
        """
        if filter_func and not filter_func(str(file_path)):
            return

        # 确定在ZIP中的路径
        if arcname is None:
            arcname = file_path.name

        # 写入文件
        zip_file.write(file_path, arcname)

    @staticmethod
    def _add_directory_to_zip(zip_file: zipfile.ZipFile,
                              dir_path: Path,
                              include_dir: bool,
                              encoding: str,
                              filter_func: Optional[Callable[[str], bool]] = None):
        """
        添加目录到ZIP压缩包
        """
        for root, dirs, files in os.walk(dir_path):
            root_path = Path(root)

            for file in files:
                file_path = root_path / file

                # 确定在ZIP中的路径
                if include_dir:
                    arcname = file_path.relative_to(dir_path.parent)
                else:
                    arcname = file_path.relative_to(dir_path)

                # 应用过滤函数
                if filter_func and not filter_func(str(arcname)):
                    continue

                # 写入文件
                zip_file.write(file_path, arcname)

    @staticmethod
    def _validate_files(zip_path: Path, *src_paths):
        """
        验证文件有效性
        """
        # 检查ZIP文件路径是否为目录
        if zip_path.exists() and zip_path.is_dir():
            raise ValueError(f"ZIP文件路径不能是目录: {zip_path}")

        # 检查源文件是否存在
        for src_path in src_paths:
            if src_path and not src_path.exists():
                raise ValueError(f"源文件不存在: {src_path}")

            # 检查ZIP文件是否位于源目录内（防止无限递归）
            if src_path.is_dir():
                try:
                    if zip_path.resolve().is_relative_to(src_path.resolve()):
                        raise ValueError(f"ZIP文件不能位于源目录内: {zip_path}")
                except ValueError:
                    # 在不同驱动器上时可能抛出ValueError
                    pass

if __name__ == '__main__':

    # 1. 压缩单个文件
    zip_path = ZipUtil.zip(r"D:\\Downloads\\example.txt")
    print(f"压缩文件已创建: {zip_path}")

    test_dir = "D:\\Downloads\\temp"

    # 2. 压缩目录（不包含目录本身）
    zip_path = ZipUtil.zip(test_dir, include_dir=False)

    # 3. 压缩目录（包含目录本身）
    zip_path = ZipUtil.zip(test_dir, include_dir=True)

    # 4. 解压ZIP文件
    extracted_dir = ZipUtil.unzip(zip_path)
    print(f"文件解压到: {extracted_dir}")

    # 5. 压缩多个文件
    files = ["file1.txt", "file2.txt", "image.jpg"]
    zip_path = ZipUtil.zip_files("bundle.zip", files)


    # 6. 使用过滤函数（只压缩.txt文件）
    def only_txt_files(filename):
        return filename.endswith('.txt')


    zip_path = ZipUtil.zip(test_dir, filter_func=only_txt_files)

    # 7. 流压缩
    content = "这是要压缩的文本内容"
    zip_data = ZipUtil.zip_stream(content, "example.txt")
    with open("stream.zip", "wb") as f:
        f.write(zip_data)

    # 8. 流解压
    with open("stream.zip", "rb") as f:
        zip_data = f.read()
    contents = ZipUtil.unzip_stream(zip_data)
    print(contents)

    # 9. 从ZIP中获取特定文件
    content = ZipUtil.get_file_from_zip("archive.zip", "example.txt")
    if content:
        print(content)

    # 10. GZIP压缩/解压缩
    compressed = ZipUtil.gzip_compress("要压缩的文本")
    decompressed = ZipUtil.gzip_decompress(compressed)
    print(decompressed)

    # 11. 列出ZIP中的文件
    files = ZipUtil.list_files(zip_path, "documents/")
    print(files)