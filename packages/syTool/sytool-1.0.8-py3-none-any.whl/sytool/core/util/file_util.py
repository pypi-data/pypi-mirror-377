"""
文件工具类
"""

import datetime
import fnmatch
import hashlib
import logging
import mimetypes
import mmap
import os
import re
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import (
    List, Union, Optional, Callable, Iterable,
    Generator, Tuple
)

# 配置mimetypes和日志
mimetypes.init()
logger = logging.getLogger(__name__)

# 配置常量
DEFAULT_BUFFER_SIZE = 16 * 1024 * 1024  # 16MB
DEFAULT_CHUNK_SIZE = 64 * 1024  # 64KB
MAX_PATH_LENGTH = 260  # Windows路径长度限制


class FileMode(Enum):
    """文件模式枚举"""
    READ = "r"
    WRITE = "w"
    APPEND = "a"
    READ_WRITE = "r+"
    WRITE_READ = "w+"
    APPEND_READ = "a+"
    READ_BINARY = "rb"
    WRITE_BINARY = "wb"
    APPEND_BINARY = "ab"
    READ_WRITE_BINARY = "r+b"
    WRITE_READ_BINARY = "w+b"
    APPEND_READ_BINARY = "a+b"


class LineSeparator(Enum):
    """行分隔符枚举"""
    LF = "\n"
    CR = "\r"
    CRLF = "\r\n"
    SYSTEM = os.linesep


class FileAccess(Enum):
    """文件访问模式枚举"""
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


@dataclass
class FileInfo:
    """文件信息数据类"""
    path: Path
    size: int
    modified_time: datetime.datetime
    created_time: datetime.datetime
    is_dir: bool
    is_file: bool
    is_symlink: bool
    mode: int
    owner: Optional[str] = None
    group: Optional[str] = None
    file_type: Optional[str] = None  # 新增文件类型字段


class PathUtil:
    """
    路径工具类 - 提供基础高效的路径操作和文件遍历方法
    所有方法都是静态方法，可以直接调用
    """

    # 定义跨平台路径长度限制
    if sys.platform == "win32":
        MAX_PATH = 260
        PREFIX = "\\\\?\\"  # Windows长路径前缀
    else:
        MAX_PATH = 4096  # 典型Linux/Unix路径限制
        PREFIX = ""

    @staticmethod
    def safe_path(path: Union[str, Path]) -> Path:
        """
        创建安全路径对象，处理长路径问题（特别是Windows）

        Args:
            path: 路径字符串或Path对象

        Returns:
            安全Path对象
        """
        path_str = str(path)
        if sys.platform == "win32" and len(path_str) > 248:
            # Windows长路径处理
            if not path_str.startswith(PathUtil.PREFIX):
                if path_str.startswith("\\\\"):
                    # UNC路径
                    path_str = "\\\\?\\UNC\\" + path_str[2:]
                else:
                    path_str = PathUtil.PREFIX + path_str
        return Path(path_str)

    @staticmethod
    def is_dir_empty(dir_path: Union[str, Path]) -> bool:
        """高效判断目录是否为空"""
        try:
            dir_path = PathUtil.safe_path(dir_path)
            if not dir_path.exists() or not dir_path.is_dir():
                return False

            # 使用scandir高效检查
            with os.scandir(dir_path) as it:
                return next(it, None) is None
        except (OSError, PermissionError, ValueError) as e:
            logger.warning(f"检查目录是否为空时出错: {dir_path}, 错误: {e}")
            return False

    @staticmethod
    def scan_entries(
            path: Union[str, Path],
            recursive: bool = True,
            follow_symlinks: bool = False,
            include_files: bool = True,
            include_dirs: bool = False,
            entry_filter: Optional[Callable[[os.DirEntry], bool]] = None
    ) -> Generator[os.DirEntry, None, None]:
        """
        高效扫描目录条目（使用os.scandir）

        Args:
            path: 要扫描的路径
            recursive: 是否递归扫描子目录
            follow_symlinks: 是否跟随符号链接
            include_files: 是否包含文件
            include_dirs: 是否包含目录
            entry_filter: 条目过滤函数

        Yields:
            os.DirEntry对象

        Raises:
            FileNotFoundError: 如果路径不存在
            NotADirectoryError: 如果路径不是目录
        """
        path = PathUtil.safe_path(path)
        if not path.exists():
            raise FileNotFoundError(f"路径不存在: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"路径不是目录: {path}")

        try:
            with os.scandir(path) as it:
                for entry in it:
                    try:
                        # 检查是否匹配过滤条件
                        matches_filter = entry_filter is None or entry_filter(entry)

                        # 处理文件
                        if include_files and entry.is_file(follow_symlinks=follow_symlinks) and matches_filter:
                            yield entry

                        # 处理目录
                        if include_dirs and entry.is_dir(follow_symlinks=follow_symlinks) and matches_filter:
                            yield entry
                            # 递归处理子目录
                            if recursive:
                                yield from PathUtil.scan_entries(
                                    entry.path,
                                    recursive=True,
                                    follow_symlinks=follow_symlinks,
                                    include_files=include_files,
                                    include_dirs=include_dirs,
                                    entry_filter=entry_filter
                                )
                    except (OSError, PermissionError) as e:
                        logger.debug(f"无法访问条目: {entry.path}, 错误: {e}")
                        continue
        except (PermissionError, FileNotFoundError, NotADirectoryError) as e:
            logger.error(f"扫描目录时出错: {path}, 错误: {e}")
            raise

    @staticmethod
    def get_file_info(path: Union[str, Path]) -> Optional[FileInfo]:
        """
        获取文件的详细信息

        Args:
            path: 文件路径

        Returns:
            FileInfo对象或None（如果文件不存在）
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists():
                return None

            stat = path_obj.stat()

            # 获取所有者和组信息（跨平台兼容）
            owner = group = None
            try:
                if hasattr(os, 'getuid'):
                    import pwd
                    import grp
                    owner = pwd.getpwuid(stat.st_uid).pw_name
                    group = grp.getgrgid(stat.st_gid).gr_name
            except (ImportError, KeyError, AttributeError):
                # Windows平台或不支持的系统，静默失败
                pass

            # 获取文件类型
            file_type = None
            if path_obj.is_file():
                file_type = mimetypes.guess_type(path_obj)[0] or 'application/octet-stream'
            elif path_obj.is_dir():
                file_type = 'inode/directory'
            elif path_obj.is_symlink():
                file_type = 'inode/symlink'

            return FileInfo(
                path=path_obj,
                size=stat.st_size,
                modified_time=datetime.datetime.fromtimestamp(stat.st_mtime),
                created_time=datetime.datetime.fromtimestamp(stat.st_ctime),
                is_dir=path_obj.is_dir(),
                is_file=path_obj.is_file(),
                is_symlink=path_obj.is_symlink(),
                mode=stat.st_mode,
                owner=owner,
                group=group,
                file_type=file_type
            )
        except (OSError, ValueError) as e:
            logger.warning(f"获取文件信息失败: {path}, 错误: {e}")
            return None

    @staticmethod
    def count_entries(
            path: Union[str, Path],
            recursive: bool = True,
            follow_symlinks: bool = False,
            include_files: bool = True,
            include_dirs: bool = False,
            entry_filter: Optional[Callable[[os.DirEntry], bool]] = None
    ) -> int:
        """
        高效统计目录条目数量

        Args:
            path: 要统计的路径
            recursive: 是否递归统计子目录
            follow_symlinks: 是否跟随符号链接
            include_files: 是否包含文件
            include_dirs: 是否包含目录
            entry_filter: 条目过滤函数

        Returns:
            符合条件的条目数量
        """
        count = 0
        for _ in PathUtil.scan_entries(
                path,
                recursive=recursive,
                follow_symlinks=follow_symlinks,
                include_files=include_files,
                include_dirs=include_dirs,
                entry_filter=entry_filter
        ):
            count += 1
        return count

    @staticmethod
    def walk_files(
            path: Union[str, Path],
            recursive: bool = True,
            follow_symlinks: bool = False,
            file_filter: Optional[Callable[[os.DirEntry], bool]] = None
    ) -> Generator[os.DirEntry, None, None]:
        """
        高效遍历文件（返回DirEntry对象）

        Args:
            path: 要遍历的路径
            recursive: 是否递归遍历
            follow_symlinks: 是否跟随符号链接
            file_filter: 文件过滤函数

        Yields:
            符合条件的文件DirEntry对象
        """
        yield from PathUtil.scan_entries(
            path,
            recursive=recursive,
            follow_symlinks=follow_symlinks,
            include_files=True,
            include_dirs=False,
            entry_filter=file_filter
        )

    @staticmethod
    def walk_dirs(
            path: Union[str, Path],
            recursive: bool = True,
            follow_symlinks: bool = False,
            dir_filter: Optional[Callable[[os.DirEntry], bool]] = None
    ) -> Generator[os.DirEntry, None, None]:
        """
        高效遍历目录（返回DirEntry对象）

        Args:
            path: 要遍历的路径
            recursive: 是否递归遍历
            follow_symlinks: 是否跟随符号链接
            dir_filter: 目录过滤函数

        Yields:
            符合条件的目录DirEntry对象
        """
        yield from PathUtil.scan_entries(
            path,
            recursive=recursive,
            follow_symlinks=follow_symlinks,
            include_files=False,
            include_dirs=True,
            entry_filter=dir_filter
        )

    @staticmethod
    def delete_path(path: Union[str, Path], force: bool = False) -> bool:
        """
        安全删除文件或目录

        Args:
            path: 要删除的路径
            force: 是否强制删除（忽略错误）

        Returns:
            删除是否成功
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists():
                return True

            # 文件或符号链接直接删除
            if path_obj.is_file() or path_obj.is_symlink():
                path_obj.unlink()
                return True

            # 目录使用shutil.rmtree删除
            if path_obj.is_dir():
                if force:
                    shutil.rmtree(path_obj, ignore_errors=True)
                else:
                    shutil.rmtree(path_obj)
                return True

            return False
        except (OSError, PermissionError, ValueError) as e:
            logger.error(f"删除路径失败: {path}, 错误: {e}")
            if not force:
                raise
            return False

    @staticmethod
    def copy_file(
            src: Union[str, Path],
            dest: Union[str, Path],
            overwrite: bool = False,
            preserve_metadata: bool = True,
            buffer_size: int = DEFAULT_BUFFER_SIZE
    ) -> Path:
        """
        高效拷贝文件

        Args:
            src: 源文件路径
            dest: 目标文件路径
            overwrite: 是否覆盖已存在文件
            preserve_metadata: 是否保留元数据
            buffer_size: 缓冲区大小

        Returns:
            目标文件路径

        Raises:
            FileNotFoundError: 源文件不存在
            FileExistsError: 目标文件已存在且overwrite为False
        """
        src_path = PathUtil.safe_path(src)
        dest_path = PathUtil.safe_path(dest)

        if not src_path.exists():
            raise FileNotFoundError(f"源文件不存在: {src_path}")

        if not src_path.is_file():
            raise ValueError(f"源路径不是文件: {src_path}")

        # 如果目标是目录，则使用相同文件名
        if dest_path.exists() and dest_path.is_dir():
            dest_path = dest_path / src_path.name

        # 检查目标文件是否存在
        if dest_path.exists():
            if not overwrite:
                raise FileExistsError(f"目标文件已存在: {dest_path}")
            # 删除已存在的文件
            PathUtil.delete_path(dest_path, force=True)

        # 创建目标目录
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # 使用优化的拷贝方法
        if preserve_metadata:
            # 使用copy2保留元数据
            shutil.copy2(src_path, dest_path)
        else:
            # 只拷贝内容，使用大缓冲区
            with open(src_path, 'rb') as src_file:
                with open(dest_path, 'wb', buffering=buffer_size) as dest_file:
                    shutil.copyfileobj(src_file, dest_file, length=buffer_size)

        return dest_path

    @staticmethod
    def copy_dir(
            src: Union[str, Path],
            dest: Union[str, Path],
            overwrite: bool = False,
            preserve_metadata: bool = True
    ) -> Path:
        """
        高效拷贝目录

        Args:
            src: 源目录路径
            dest: 目标目录路径
            overwrite: 是否覆盖已存在目录
            preserve_metadata: 是否保留元数据

        Returns:
            目标目录路径

        Raises:
            FileNotFoundError: 源目录不存在
            NotADirectoryError: 源或目标不是目录
        """
        src_path = PathUtil.safe_path(src)
        dest_path = PathUtil.safe_path(dest)

        if not src_path.exists() or not src_path.is_dir():
            raise NotADirectoryError(f"源目录不存在: {src_path}")

        if dest_path.exists() and not dest_path.is_dir():
            raise NotADirectoryError(f"目标不是目录: {dest_path}")

        # 如果目标目录已存在且需要覆盖，先删除
        if dest_path.exists():
            if not overwrite:
                raise FileExistsError(f"目标目录已存在: {dest_path}")
            PathUtil.delete_path(dest_path, force=True)

        # 创建目标目录
        dest_path.mkdir(parents=True, exist_ok=True)

        # 使用scandir高效遍历和拷贝
        for entry in os.scandir(src_path):
            item_dest = dest_path / entry.name
            if entry.is_dir():
                PathUtil.copy_dir(
                    entry.path,
                    item_dest,
                    overwrite,
                    preserve_metadata
                )
            elif entry.is_file():
                PathUtil.copy_file(
                    entry.path,
                    item_dest,
                    overwrite,
                    preserve_metadata
                )

        return dest_path

    @staticmethod
    def move_path(
            src: Union[str, Path],
            dest: Union[str, Path],
            overwrite: bool = False
    ) -> Path:
        """
        移动文件或目录

        Args:
            src: 源路径
            dest: 目标路径
            overwrite: 是否覆盖已存在目标

        Returns:
            目标路径

        Raises:
            FileNotFoundError: 源路径不存在
            FileExistsError: 目标路径已存在且overwrite为False
        """
        src_path = PathUtil.safe_path(src)
        dest_path = PathUtil.safe_path(dest)

        if not src_path.exists():
            raise FileNotFoundError(f"源不存在: {src_path}")

        # 如果目标是目录，则使用相同名称
        if dest_path.exists() and dest_path.is_dir():
            dest_path = dest_path / src_path.name

        # 检查目标是否存在
        if dest_path.exists():
            if not overwrite:
                raise FileExistsError(f"目标已存在: {dest_path}")
            # 删除已存在的目标
            PathUtil.delete_path(dest_path, force=True)

        # 创建目标目录
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 尝试原子操作
            src_path.rename(dest_path)
        except OSError:
            # 跨设备移动需要拷贝+删除
            if src_path.is_dir():
                PathUtil.copy_dir(src_path, dest_path, overwrite=True)
                PathUtil.delete_path(src_path, force=True)
            else:
                PathUtil.copy_file(src_path, dest_path, overwrite=True)
                PathUtil.delete_path(src_path, force=True)

        return dest_path

    @staticmethod
    def get_file_size(path: Union[str, Path]) -> int:
        """
        获取文件大小（字节）

        Args:
            path: 文件路径

        Returns:
            文件大小（字节），如果文件不存在则返回0
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists() or not path_obj.is_file():
                return 0
            return path_obj.stat().st_size
        except (OSError, ValueError) as e:
            logger.debug(f"获取文件大小失败: {path}, 错误: {e}")
            return 0

    @staticmethod
    def get_dir_size(
            path: Union[str, Path],
            include_self: bool = False
    ) -> int:
        """
        获取目录大小（字节）

        Args:
            path: 目录路径
            include_self: 是否包含目录自身的大小

        Returns:
            目录大小（字节），如果目录不存在则返回0
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists() or not path_obj.is_dir():
                return 0

            total_size = path_obj.stat().st_size if include_self else 0

            # 使用scandir高效遍历
            for entry in os.scandir(path_obj):
                if entry.is_file(follow_symlinks=False):
                    total_size += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total_size += PathUtil.get_dir_size(entry.path, include_self=True)

            return total_size
        except (OSError, ValueError) as e:
            logger.debug(f"获取目录大小失败: {path}, 错误: {e}")
            return 0

    @staticmethod
    def get_mime_type(path: Union[str, Path]) -> str:
        """
        获取MIME类型

        Args:
            path: 文件路径

        Returns:
            MIME类型字符串
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists():
                return 'application/octet-stream'

            mime_type, _ = mimetypes.guess_type(path_obj)
            return mime_type or 'application/octet-stream'
        except (OSError, ValueError) as e:
            logger.debug(f"获取MIME类型失败: {path}, 错误: {e}")
            return 'application/octet-stream'

    @staticmethod
    def create_temp_file(
            prefix: str = "tmp",
            suffix: str = ".tmp",
            directory: Optional[Union[str, Path]] = None,
            delete_on_close: bool = False
    ) -> Path:
        """
        创建临时文件

        Args:
            prefix: 文件名前缀
            suffix: 文件名后缀
            directory: 临时文件目录
            delete_on_close: 是否在关闭时删除

        Returns:
            临时文件路径
        """
        if directory is not None:
            directory = PathUtil.safe_path(directory)
            directory.mkdir(parents=True, exist_ok=True)

        if delete_on_close:
            fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=directory)
            os.close(fd)
            return Path(path)
        else:
            temp_file = tempfile.NamedTemporaryFile(
                prefix=prefix,
                suffix=suffix,
                dir=directory,
                delete=False
            )
            temp_file.close()
            return Path(temp_file.name)

    @staticmethod
    def get_last_modified(path: Union[str, Path]) -> Optional[datetime.datetime]:
        """
        获取最后修改时间

        Args:
            path: 文件路径

        Returns:
            最后修改时间，如果文件不存在则返回None
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists():
                return None
            return datetime.datetime.fromtimestamp(path_obj.stat().st_mtime)
        except (OSError, ValueError) as e:
            logger.debug(f"获取最后修改时间失败: {path}, 错误: {e}")
            return None

    @staticmethod
    def is_newer_than(
            path: Union[str, Path],
            reference: Union[str, Path, float, datetime.datetime]
    ) -> bool:
        """
        判断文件是否比参照文件新

        Args:
            path: 文件路径
            reference: 参照文件路径或时间戳

        Returns:
            文件是否比参照新
        """
        path_time = PathUtil.get_last_modified(path)
        if path_time is None:
            return False

        path_timestamp = path_time.timestamp()

        if isinstance(reference, (int, float)):
            return path_timestamp > reference
        elif isinstance(reference, datetime.datetime):
            return path_timestamp > reference.timestamp()

        ref_time = PathUtil.get_last_modified(reference)
        if ref_time is None:
            return True

        return path_timestamp > ref_time.timestamp()

    @staticmethod
    def get_file_hash(
            path: Union[str, Path],
            algorithm: str = "md5",
            chunk_size: int = DEFAULT_CHUNK_SIZE
    ) -> Optional[str]:
        """
        计算文件哈希值

        Args:
            path: 文件路径
            algorithm: 哈希算法（md5, sha1, sha256等）
            chunk_size: 分块大小

        Returns:
            哈希字符串，如果文件不存在则返回None
        """
        path_obj = PathUtil.safe_path(path)
        if not path_obj.exists() or not path_obj.is_file():
            return None

        try:
            hash_func = hashlib.new(algorithm)
            with open(path_obj, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except (IOError, ValueError) as e:
            logger.warning(f"计算文件哈希失败: {path}, 错误: {e}")
            return None

    @staticmethod
    def set_file_permissions(path: Union[str, Path], mode: int) -> bool:
        """
        设置文件权限

        Args:
            path: 文件路径
            mode: 权限模式（八进制，如0o755）

        Returns:
            是否成功
        """
        try:
            path_obj = PathUtil.safe_path(path)
            path_obj.chmod(mode)
            return True
        except (OSError, ValueError) as e:
            logger.warning(f"设置文件权限失败: {path}, 错误: {e}")
            return False

    @staticmethod
    def validate_path(path: Union[str, Path], check_exists: bool = True) -> Tuple[bool, str]:
        """
        验证路径是否有效

        Args:
            path: 要验证的路径
            check_exists: 是否检查路径存在性

        Returns:
            (是否有效, 错误消息)
        """
        try:
            path_obj = Path(path)
            path_str = str(path_obj)

            # 检查路径长度
            if len(path_str) > PathUtil.MAX_PATH:
                return False, f"路径长度超过系统限制: {len(path_str)} > {PathUtil.MAX_PATH}"

            # 检查非法字符
            illegal_chars = {'\\', '/', ':', '*', '?', '"', '<', '>', '|'} if sys.platform == "win32" else {'/', '\0'}
            if any(char in path_str for char in illegal_chars):
                return False, "路径包含非法字符"

            # 检查路径存在性
            if check_exists and not path_obj.exists():
                return False, "路径不存在"

            return True, "路径有效"
        except Exception as e:
            return False, f"路径验证失败: {e}"


class FileUtil(PathUtil):
    """
    文件工具类 - 提供高级文件操作
    继承自PathUtil，可以使用所有PathUtil的方法
    """

    @staticmethod
    def is_windows() -> bool:
        """是否为Windows环境"""
        return os.name == 'nt'

    @staticmethod
    def ls(path: Union[str, Path]) -> List[Path]:
        """
        列出目录内容

        Args:
            path: 目录路径

        Returns:
            目录内容路径列表

        Raises:
            ValueError: 路径不是目录
        """
        path_obj = PathUtil.safe_path(path)
        if not path_obj.exists() or not path_obj.is_dir():
            raise ValueError(f"路径不是目录: {path_obj}")

        return [Path(entry.path) for entry in os.scandir(path_obj)]

    @staticmethod
    def is_empty(path: Union[str, Path]) -> bool:
        """
        判断文件或目录是否为空

        Args:
            path: 路径

        Returns:
            是否为空
        """
        path_obj = PathUtil.safe_path(path)

        if not path_obj.exists():
            return True

        if path_obj.is_file():
            return path_obj.stat().st_size <= 0

        return PathUtil.is_dir_empty(path_obj)

    @staticmethod
    def find_files(
            path: Union[str, Path],
            pattern: Optional[str] = None,
            recursive: bool = True,
            case_sensitive: bool = False
    ) -> List[Path]:
        """
        查找匹配模式的文件

        Args:
            path: 搜索路径
            pattern: 匹配模式（如"*.txt"）
            recursive: 是否递归搜索
            case_sensitive: 是否区分大小写

        Returns:
            匹配的文件路径列表
        """

        def filter_func(entry: os.DirEntry) -> bool:
            if pattern is None:
                return True

            if case_sensitive:
                return fnmatch.fnmatch(entry.name, pattern)
            else:
                return fnmatch.fnmatchcase(entry.name.lower(), pattern.lower())

        return [
            Path(entry.path)
            for entry in PathUtil.walk_files(path, recursive=recursive, file_filter=filter_func)
        ]

    @staticmethod
    def count_files(
            path: Union[str, Path],
            pattern: Optional[str] = None,
            recursive: bool = True
    ) -> int:
        """
        统计匹配模式的文件数量

        Args:
            path: 搜索路径
            pattern: 匹配模式（如"*.txt"）
            recursive: 是否递归搜索

        Returns:
            匹配的文件数量
        """

        def filter_func(entry: os.DirEntry) -> bool:
            if pattern is None:
                return True
            return fnmatch.fnmatch(entry.name, pattern)

        return PathUtil.count_entries(
            path,
            recursive=recursive,
            include_files=True,
            include_dirs=False,
            entry_filter=filter_func
        )

    @staticmethod
    def get_total_lines(
            path: Union[str, Path],
            encoding: str = 'utf-8',
            buffer_size: int = DEFAULT_CHUNK_SIZE
    ) -> int:
        """
        高效计算文件行数

        Args:
            path: 文件路径
            encoding: 文件编码
            buffer_size: 缓冲区大小

        Returns:
            文件行数
        """
        path_obj = PathUtil.safe_path(path)
        if not path_obj.exists() or not path_obj.is_file():
            return 0

        count = 0
        try:
            with path_obj.open('r', encoding=encoding, buffering=buffer_size) as f:
                # 高效计数（不加载整个文件）
                for _ in f:
                    count += 1
        except Exception as e:
            logger.warning(f"计算文件行数失败: {path}, 错误: {e}")
            return 0

        return count

    @staticmethod
    def read_bytes(path: Union[str, Path]) -> Optional[bytes]:
        """
        读取文件内容为字节

        Args:
            path: 文件路径

        Returns:
            文件内容字节，如果文件不存在则返回None
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists() or not path_obj.is_file():
                return None
            with path_obj.open('rb') as f:
                return f.read()
        except (IOError, OSError) as e:
            logger.warning(f"读取文件字节失败: {path}, 错误: {e}")
            return None

    @staticmethod
    def read_text(
            path: Union[str, Path],
            encoding: str = 'utf-8',
            errors: str = 'strict'
    ) -> Optional[str]:
        """
        读取文件内容为文本

        Args:
            path: 文件路径
            encoding: 文件编码
            errors: 错误处理策略

        Returns:
            文件内容文本，如果文件不存在则返回None
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists() or not path_obj.is_file():
                return None
            with path_obj.open('r', encoding=encoding, errors=errors) as f:
                return f.read()
        except (IOError, OSError, UnicodeDecodeError) as e:
            logger.warning(f"读取文件文本失败: {path}, 错误: {e}")
            return None

    @staticmethod
    def read_lines(
            path: Union[str, Path],
            encoding: str = 'utf-8',
            keep_ends: bool = False,
            errors: str = 'strict'
    ) -> Optional[List[str]]:
        """
        读取文件所有行

        Args:
            path: 文件路径
            encoding: 文件编码
            keep_ends: 是否保留行结束符
            errors: 错误处理策略

        Returns:
            文件行列表，如果文件不存在则返回None
        """
        text = FileUtil.read_text(path, encoding, errors)
        if text is None:
            return None

        lines = text.splitlines()
        if keep_ends:
            return [line + '\n' for line in lines]
        return lines

    @staticmethod
    def read_chunks(
            path: Union[str, Path],
            chunk_size: int = DEFAULT_CHUNK_SIZE
    ) -> Generator[bytes, None, None]:
        """
        分块读取文件内容

        Args:
            path: 文件路径
            chunk_size: 块大小（字节）

        Yields:
            文件数据块

        Raises:
            FileNotFoundError: 文件不存在
        """
        path_obj = PathUtil.safe_path(path)
        if not path_obj.exists() or not path_obj.is_file():
            raise FileNotFoundError(f"文件不存在: {path_obj}")

        with path_obj.open('rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    @staticmethod
    def write_bytes(
            path: Union[str, Path],
            data: bytes,
            append: bool = False,
            buffer_size: int = DEFAULT_BUFFER_SIZE
    ) -> bool:
        """
        写入字节到文件

        Args:
            path: 文件路径
            data: 要写入的数据
            append: 是否追加模式
            buffer_size: 缓冲区大小

        Returns:
            是否成功
        """
        try:
            path_obj = PathUtil.safe_path(path)
            mode = 'ab' if append else 'wb'
            with path_obj.open(mode, buffering=buffer_size) as f:
                f.write(data)
            return True
        except (IOError, OSError) as e:
            logger.error(f"写入字节到文件失败: {path}, 错误: {e}")
            return False

    @staticmethod
    def write_text(
            path: Union[str, Path],
            content: str,
            encoding: str = 'utf-8',
            append: bool = False
    ) -> bool:
        """
        写入文本到文件

        Args:
            path: 文件路径
            content: 要写入的内容
            encoding: 文件编码
            append: 是否追加模式

        Returns:
            是否成功
        """
        try:
            path_obj = PathUtil.safe_path(path)
            mode = 'a' if append else 'w'
            with path_obj.open(mode, encoding=encoding) as f:
                f.write(content)
            return True
        except (IOError, OSError) as e:
            logger.error(f"写入文本到文件失败: {path}, 错误: {e}")
            return False

    @staticmethod
    def write_lines(
            path: Union[str, Path],
            lines: Iterable[str],
            encoding: str = 'utf-8',
            append: bool = False,
            line_separator: LineSeparator = LineSeparator.SYSTEM
    ) -> bool:
        """
        写入多行到文件

        Args:
            path:
            lines: 要写入的行
            encoding: 文件编码
            append: 是否追加模式
            line_separator: 行分隔符

        Returns:
            是否成功
        """
        content = line_separator.value.join(lines)
        return FileUtil.write_text(path, content, encoding, append)

    @staticmethod
    def touch(path: Union[str, Path], create_parents: bool = True) -> bool:
        """
        创建空文件（如果不存在）或更新修改时间

        Args:
            path: 文件路径
            create_parents:

        Returns:
            是否成功
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if create_parents:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
            path_obj.touch(exist_ok=True)
            return True
        except (IOError, OSError) as e:
            logger.error(f"创建文件失败: {path}, 错误: {e}")
            return False

    @staticmethod
    def copy(
            src: Union[str, Path],
            dest: Union[str, Path],
            overwrite: bool = False,
            preserve_metadata: bool = True
    ) -> Optional[Path]:
        """
        复制文件或目录

        Args:
            src: 源路径
            dest: 目标路径
            overwrite: 是否覆盖已存在目标
            preserve_metadata: 是否保留元数据

        Returns:
            目标路径，如果失败则返回None
        """
        try:
            src_path = PathUtil.safe_path(src)
            dest_path = PathUtil.safe_path(dest)

            if not src_path.exists():
                return None

            if src_path.is_file():
                return PathUtil.copy_file(
                    src_path, dest_path, overwrite, preserve_metadata
                )
            elif src_path.is_dir():
                return PathUtil.copy_dir(
                    src_path, dest_path, overwrite, preserve_metadata
                )
            else:
                return None
        except (IOError, OSError, ValueError) as e:
            logger.error(f"复制路径失败: {src} -> {dest}, 错误: {e}")
            return None

    @staticmethod
    def move(
            src: Union[str, Path],
            dest: Union[str, Path],
            overwrite: bool = False
    ) -> Optional[Path]:
        """
        移动文件或目录

        Args:
            src: 源路径
            dest: 目标路径
            overwrite: 是否覆盖已存在目标

        Returns:
            目标路径，如果失败则返回None
        """
        try:
            return PathUtil.move_path(src, dest, overwrite)
        except (IOError, OSError, ValueError) as e:
            logger.error(f"移动路径失败: {src} -> {dest}, 错误: {e}")
            return None

    @staticmethod
    def rename(
            path: Union[str, Path],
            new_name: str,
            overwrite: bool = False
    ) -> Optional[Path]:
        """
        重命名文件或目录

        Args:
            path: 路径
            new_name: 新名称
            overwrite: 是否覆盖已存在目标

        Returns:
            新路径，如果失败则返回None
        """
        try:
            path_obj = PathUtil.safe_path(path)
            new_path = path_obj.parent / new_name
            return PathUtil.move_path(path_obj, new_path, overwrite)
        except (IOError, OSError, ValueError) as e:
            logger.error(f"重命名失败: {path} -> {new_name}, 错误: {e}")
            return None

    @staticmethod
    def clean_invalid_chars(file_name: str) -> str:
        """清除文件名中的非法字符"""
        return re.sub(r'[\\/*?:"<>|]', '', file_name)

    @staticmethod
    def contains_invalid_chars(file_name: str) -> bool:
        """检查文件名是否包含非法字符"""
        return bool(re.search(r'[\\/*?:"<>|]', file_name))

    @staticmethod
    def calculate_crc32(
            path: Union[str, Path],
            chunk_size: int = DEFAULT_CHUNK_SIZE
    ) -> Optional[int]:
        """
        计算文件CRC32校验码

        Args:
            path: 文件路径
            chunk_size: 分块大小

        Returns:
            CRC32校验码，如果文件不存在则返回None
        """
        try:
            import zlib
            crc = 0
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists() or not path_obj.is_file():
                return None

            with path_obj.open('rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    crc = zlib.crc32(chunk, crc)
            return crc & 0xFFFFFFFF
        except (IOError, OSError, ImportError) as e:
            logger.warning(f"计算CRC32失败: {path}, 错误: {e}")
            return None

    @staticmethod
    def tail(
            path: Union[str, Path],
            callback: Callable[[str], None],
            encoding: str = 'utf-8',
            interval: float = 0.1,
            lines: int = 10
    ) -> None:
        """
        监控文件尾部变化（类似tail -f）

        Args:
            path: 文件路径
            callback: 新行回调函数
            encoding: 文件编码
            interval: 检查间隔（秒）
            lines: 初始读取行数

        Raises:
            FileNotFoundError: 文件不存在
        """
        path_obj = PathUtil.safe_path(path)
        if not path_obj.exists() or not path_obj.is_file():
            raise FileNotFoundError(f"文件不存在: {path_obj}")

        # 读取最后几行
        try:
            with path_obj.open('r', encoding=encoding) as f:
                # 高效读取最后几行
                from collections import deque
                lines_deque = deque(f, lines)
                for line in lines_deque:
                    callback(line.rstrip('\n\r'))
        except IOError:
            pass  # 文件可能正在被写入

        # 获取初始文件大小
        last_size = path_obj.stat().st_size
        last_position = last_size

        try:
            while True:
                current_size = path_obj.stat().st_size

                # 文件被截断或清空
                if current_size < last_position:
                    last_position = 0

                # 有新增内容
                if current_size > last_position:
                    with path_obj.open('r', encoding=encoding) as f:
                        f.seek(last_position)
                        for line in f:
                            callback(line.rstrip('\n\r'))
                        last_position = f.tell()

                last_size = current_size
                time.sleep(interval)
        except (FileNotFoundError, PermissionError):
            # 文件可能被删除或权限变更
            return
        except Exception as e:
            logger.error(f"文件监控失败: {path}, 错误: {e}")
            return

    @staticmethod
    def memory_map(
            path: Union[str, Path],
            access: int = mmap.ACCESS_READ,
            offset: int = 0,
            size: int = 0
    ) -> Optional[mmap.mmap]:
        """
        内存映射文件

        Args:
            path: 文件路径
            access: 访问模式
            offset: 偏移量
            size: 映射大小（0表示整个文件）

        Returns:
            内存映射对象，如果失败则返回None
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists() or not path_obj.is_file():
                return None

            with open(path_obj, 'rb' if access == mmap.ACCESS_READ else 'r+b') as f:
                return mmap.mmap(f.fileno(), size, access=access, offset=offset)
        except (IOError, OSError) as e:
            logger.error(f"内存映射文件失败: {path}, 错误: {e}")
            return None

    @staticmethod
    def root_dir(relative_path: str = "") -> Path:
        """动态获取项目根目录（兼容开发/Nuitka/PyInstaller单双文件模式）"""
        # 环境变量覆盖
        if env_root := os.getenv("APP_ROOT"):
            return Path(env_root).resolve()

        is_pyinstaller = getattr(sys, 'frozen', False) or getattr(sys, '_MEIPASS', False)
        is_nuitka = "__compiled__" in globals()

        base_path = None
        executable_path = Path(sys.executable).resolve()
        if is_pyinstaller:
            base_path = executable_path.parent
        elif is_nuitka:
            base_path = executable_path.parent
        else:
            if relative_path:
                current_path = Path(relative_path).resolve()
            else:
                current_path = Path(__file__).resolve()

            # 开发环境检测
            root_markers = [
                'requirements.txt', 'deploy.py', 'setup.py', '.git',
                '.svn', '.gitignore', 'app', 'main.py'
            ]
            max_depth = 10
            for i, parent in enumerate(current_path.parents):
                if i > max_depth:
                    raise RuntimeError(f"开发环境查找目录时超过最大搜索层级:{max_depth}")
                if any((parent / marker).resolve().exists() for marker in root_markers):
                    base_path = parent.resolve()
                    break

        if not base_path or not base_path.exists():
            raise FileNotFoundError(f"未找到项目根目录:{base_path}")
        return base_path

    @staticmethod
    def calculate_file_md5(file_path: Union[str, Path]) -> str:
        """分块计算文件MD5，避免内存溢出"""
        path_obj = PathUtil.safe_path(file_path)
        hash_md5 = hashlib.md5()
        with path_obj.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def get_file_encoding(file_path: Union[str, Path]) -> Optional[str]:
        """
        检测文件编码

        Args:
            file_path: 文件路径

        Returns:
            编码名称或None（如果无法检测）
        """
        try:
            import chardet

            path_obj = PathUtil.safe_path(file_path)
            if not path_obj.exists() or not path_obj.is_file():
                return None

            with path_obj.open('rb') as f:
                raw_data = f.read(1024)  # 读取前1KB用于检测

            result = chardet.detect(raw_data)
            return result['encoding'] if result['confidence'] > 0.7 else None
        except Exception as e:
            logger.warning(f"检测文件编码失败: {file_path}, 错误: {e}")
            return None

    @staticmethod
    def backup_file(
            path: Union[str, Path],
            backup_dir: Optional[Union[str, Path]] = None,
            suffix: str = ".bak"
    ) -> Optional[Path]:
        """
        创建文件备份

        Args:
            path: 要备份的文件路径
            backup_dir: 备份目录（默认为原文件所在目录）
            suffix: 备份文件后缀

        Returns:
            备份文件路径，如果备份失败则返回None
        """
        try:
            path_obj = PathUtil.safe_path(path)
            if not path_obj.exists() or not path_obj.is_file():
                return None

            if backup_dir is None:
                backup_dir = path_obj.parent

            backup_dir = PathUtil.safe_path(backup_dir)
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{path_obj.stem}_{timestamp}{suffix}"
            backup_path = backup_dir / backup_name

            PathUtil.copy_file(path_obj, backup_path, overwrite=False)
            return backup_path
        except Exception as e:
            logger.error(f"文件备份失败: {path}, 错误: {e}")
            return None

    @staticmethod
    def atomic_write(
            path: Union[str, Path],
            content: Union[str, bytes],
            encoding: str = 'utf-8',
            mode: str = 'w'
    ) -> bool:
        """
        原子写入文件（避免写入过程中出现部分内容）

        Args:
            path: 文件路径
            content: 要写入的内容
            encoding: 文件编码（文本模式时有效）
            mode: 写入模式（'w'或'wb'）

        Returns:
            是否成功
        """
        path_obj = PathUtil.safe_path(path)
        temp_path = path_obj.with_suffix('.tmp')

        try:
            # 写入临时文件
            if 'b' in mode:
                with open(temp_path, 'wb') as f:
                    if isinstance(content, str):
                        content = content.encode(encoding)
                    f.write(content)
            else:
                with open(temp_path, 'w', encoding=encoding) as f:
                    f.write(content)

            # 原子替换原文件
            if sys.platform == 'win32':
                # Windows需要先删除原文件
                if path_obj.exists():
                    path_obj.unlink()
                temp_path.rename(path_obj)
            else:
                # Unix系统可以直接原子替换
                temp_path.rename(path_obj)

            return True
        except Exception as e:
            logger.error(f"原子写入失败: {path}, 错误: {e}")
            # 清理临时文件
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            return False


# 使用示例和测试代码
if __name__ == '__main__':
    # 配置日志:不调用basicConfig或者调用了basicConfig但是不配置filename参数，日志将输出到控制台
    logging.basicConfig(level=logging.INFO)

    # ======================
    # 使用PathUtil基础功能
    # ======================

    test_dir = PathUtil.safe_path("D:\\Downloads")

    # 1. 检查目录是否为空
    print(f"当前目录是否为空: {PathUtil.is_dir_empty('')}")

    # 2. 统计目录下文件数量
    file_count = PathUtil.count_entries(
        test_dir,
        include_dirs=False,
        entry_filter=lambda e: e.name.endswith('.py')
    )
    print(f"Python文件数量: {file_count}")

    # 3. 遍历文件
    for entry in PathUtil.walk_files(test_dir, recursive=True):
        print(f"文件: {entry.path}, 大小: {entry.stat().st_size}字节")

    # 4. 复制文件
    try:
        copied_file = PathUtil.copy_file(test_dir / 'source.txt', test_dir / 'backup.txt', overwrite=True)
        print(f"文件已复制到: {copied_file}")
    except (FileNotFoundError, FileExistsError) as e:
        print(f"复制文件失败: {e}")

    # 5. 获取文件MIME类型
    mime_type = PathUtil.get_mime_type('image.jpg')
    print(f"文件MIME类型: {mime_type}")

    # ======================
    # 使用FileUtil高级功能
    # ======================

    # 1. 列出目录内容
    print(f"当前目录内容: {FileUtil.ls('')}")

    # 2. 查找所有文本文件
    text_files = FileUtil.find_files(test_dir, '*.txt')
    print(f"找到的文本文件: {text_files}")

    # 3. 统计所有图片文件数量
    image_count = FileUtil.count_files(test_dir, '*.jpg')
    print(f"JPG图片数量: {image_count}")

    # 4. 读取文件内容
    try:
        content = FileUtil.read_text(test_dir / 'example.txt')
        print(f"文件内容: {content[:100]}...")
    except Exception as e:
        print(f"读取文件失败: {e}")

    # 5. 写入文件
    try:
        FileUtil.write_text(test_dir / 'output.txt', 'Hello, World!')
        print("文件已写入")
    except Exception as e:
        print(f"写入文件失败: {e}")

    # 6. 复制目录
    try:
        FileUtil.copy(test_dir / 'temp', test_dir / 'backupDir', overwrite=True)
        print("目录已复制")
    except Exception as e:
        print(f"复制目录失败: {e}")

    # 7. 获取项目根目录
    try:
        root_dir = FileUtil.root_dir()
        print('项目根目录:', root_dir)
    except Exception as e:
        print(f"获取根目录失败: {e}")

    # 8. 计算文件哈希
    try:
        md5_hash = FileUtil.calculate_file_md5(test_dir / 'example.txt')
        print(f"文件MD5哈希: {md5_hash}")
    except Exception as e:
        print(f"计算哈希失败: {e}")

    # 9. 文件备份
    try:
        backup_path = FileUtil.backup_file(test_dir / 'example.txt')
        if backup_path:
            print(f"文件已备份到: {backup_path}")
    except Exception as e:
        print(f"文件备份失败: {e}")

    # 10. 原子写入
    try:
        success = FileUtil.atomic_write(test_dir / 'atomic.txt', '重要数据')
        print(f"原子写入成功: {success}")
    except Exception as e:
        print(f"原子写入失败: {e}")
