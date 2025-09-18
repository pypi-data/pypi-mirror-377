"""
下载工具相关
"""
import hashlib
import os
import sys
from pathlib import Path
from typing import Optional, Callable, Union, Iterator


def get_root_path(relative_path: str = "") -> Path:
    """动态获取项目根目录（兼容开发/Nuitka/PyInstaller单双文件模式）"""
    # 环境变量覆盖
    if env_root := os.getenv("APP_ROOT"):
        return Path(env_root).resolve()

    is_pyinstaller = getattr(sys, 'frozen', False) or getattr(sys, '_MEIPASS', False)
    is_nuitka = "__compiled__" in globals()

    base_path = None
    executable_path = Path(sys.executable).resolve()
    if is_pyinstaller:
        # PyInstaller打包时会设置sys.frozen=True和sys._MEIPASS=True,此时使用Path(sys.executable)和Path(sys.argv[0])效果相同
        # sys.argv[0] 是 sys 模块提供的命令行参数列表的第一个元素，表示被执行的脚本名称.如果程序启动时显式传递了额外参数，sys.argv[0] 会被替换为第一个参数,所以优先使用sys.executable更稳定
        base_path = executable_path.parent
    elif is_nuitka:
        base_path = executable_path.parent
    else:
        if relative_path:
            # 如果没有传递基准路径,则获取调用者的文件路径，从该路径开始查找根目录
            current_path = Path(relative_path).resolve()
        else:
            # 如果传递基准路径,则直接使用该路径
            current_path = Path(__file__).resolve()

        # 开发环境检测,获取所有父级目录,判断其下是否包含root_markers任一文件,包含则认为是项目根目录
        root_markers = [
            'requirements.txt', 'deploy.py', 'setup.py', '.git', '.svn', '.gitignore', 'app', 'main.py'
        ]
        max_depth = 10
        for i, parent in enumerate(current_path.parents):
            if i > max_depth:
                raise RuntimeError(f"开发环境查找目录时超过最大搜索层级:{max_depth}")
            if any((parent / marker).resolve().exists() for marker in root_markers):
                base_path = parent.resolve()
                break

    # 判断路径是否存在
    if not base_path or not base_path.exists():
        raise FileNotFoundError(f"未找到项目根目录:{base_path}")
    return base_path


def count_files(folder_path, extension, recursive=True, pattern_fn=None):
    """统计目录下指定格式的文件数量（支持递归、自定义匹配）"""
    path = Path(folder_path)
    if not path.is_dir():
        return 0

    # 默认匹配规则：后缀严格等于 extension（支持多扩展名）
    pattern_fn = pattern_fn or (lambda f, ext: f.suffix == ext)
    pattern = f"**/*{extension}" if recursive else f"*{extension}"

    try:
        files = path.rglob(pattern) if recursive else path.glob(pattern)
        return sum(1 for file in files if file.is_file() and pattern_fn(file, extension))
    except PermissionError:
        return 0  # 或抛出警告

def count_files_scandir(
        folder_path: Union[str, Path],
        extension: Optional[str] = None,  # 允许 extension 为 None，匹配所有文件
        recursive: bool = True,
        pattern_fn: Optional[Callable[[os.DirEntry, Optional[str]], bool]] = None, # pattern_fn 现在也接收 Optional[str]
) -> int:
    """
    使用 os.scandir() 高效递归统计目录下指定格式的文件数量。默认不跟踪符号链接以防止无限递归。
    若不指定扩展名（extension=None）且无自定义匹配函数，则统计所有文件。

    Args:
        folder_path: 要统计的目标目录路径。
        extension: 要匹配的文件扩展名（如 ".txt"）。默认为 None，表示匹配任何扩展名或无条件匹配。
                   匹配逻辑最终由 pattern_fn 决定，若 pattern_fn 未提供，则使用内置的基于扩展名的匹配。
        recursive: 是否递归统计子目录中的文件。默认为 True。
        pattern_fn: 自定义匹配函数，接收一个 DirEntry 对象和可选的 extension 字符串作为参数，
                    返回布尔值表示是否匹配。默认为 None，使用内置的匹配逻辑。

    Returns:
        匹配到的文件数量。
    """
    path = Path(folder_path)
    if not path.is_dir():
        return 0

    # 优化默认匹配规则：
    # 1. 如果提供了 pattern_fn，则优先使用它，并且传入 extension（可能为 None）
    # 2. 如果未提供 pattern_fn，则根据 extension 的情况决定匹配方式
    if pattern_fn is None:
        if extension is not None:
            # 如果给了 extension，则进行精确后缀匹配（忽略大小写）
            pattern_fn = lambda entry, ext: os.path.splitext(entry.name)[1].lower() == ext.lower()
        else:
            # 如果 extension 也为 None，则匹配所有文件
            pattern_fn = lambda entry, ext: True
    # 如果 pattern_fn 不为 None，则直接使用用户提供的函数，extension 参数会原样传入

    count = 0
    try:
        with os.scandir(folder_path) as entries:
            for entry in entries:
                try:
                    # 使用 follow_symlinks=False 避免跟踪符号链接，防止无限递归
                    if entry.is_file(follow_symlinks=False):
                        # 调用 pattern_fn，并传入 extension (可能是 None)
                        if pattern_fn(entry, extension):
                            count += 1
                    elif recursive and entry.is_dir(follow_symlinks=False):
                        # 递归进入子目录
                        count += count_files_scandir(entry.path, extension, recursive, pattern_fn)
                except OSError as e:
                    # 处理单个条目时的错误（如损坏的符号链接、无权限访问单个文件等），记录并继续
                    print(f"警告：跳过条目 '{entry.path}'：{e}")
                    continue
    except PermissionError:
        print(f"错误：无权限访问目录 '{folder_path}'")
        raise
    except OSError as e:
        print(f"错误：无法扫描目录 '{folder_path}'：{e}")
        raise
    return count


def walk_files_scandir(
        folder_path: Union[str, Path],
        extension: Optional[str] = None,  # 允许 extension 为 None，匹配所有文件
        recursive: bool = True,
        pattern_fn: Optional[Callable[[os.DirEntry, Optional[str]], bool]] = None, # pattern_fn 现在也接收 Optional[str]
) -> Iterator[os.DirEntry]:
    """
    使用 os.scandir() 递归遍历目录下指定格式的文件，返回一个生成 DirEntry 对象的迭代器。
    默认不跟踪符号链接以防止无限递归。适用于需要逐个处理文件或节省内存的场景。
    若不指定扩展名（extension=None）且无自定义匹配函数，则遍历所有文件。

    Args:
        folder_path: 要遍历的目标目录路径。
        extension: 要匹配的文件扩展名（如 ".txt"）。默认为 None，表示匹配任何扩展名或无条件匹配。
                   匹配逻辑最终由 pattern_fn 决定，若 pattern_fn 未提供，则使用内置的基于扩展名的匹配。
        recursive: 是否递归遍历子目录中的文件。默认为 True。
        pattern_fn: 自定义匹配函数，接收一个 DirEntry 对象和可选的 extension 字符串作为参数，
                    返回布尔值表示是否匹配。默认为 None，使用内置的匹配逻辑。

    Yields:
        os.DirEntry: 匹配到的文件对应的 DirEntry 对象。

    Raises:
        PermissionError: 当没有权限访问初始目录时。
        OSError: 当发生其他操作系统错误时（如路径不存在）。
    """
    path = Path(folder_path)
    if not path.is_dir():
        return

    # 优化默认匹配规则，逻辑同 count_files_scandir
    if pattern_fn is None:
        if extension is not None:
            pattern_fn = lambda entry, ext: os.path.splitext(entry.name)[1].lower() == ext.lower()
        else:
            pattern_fn = lambda entry, ext: True

    try:
        with os.scandir(folder_path) as entries:
            for entry in entries:
                try:
                    # 使用 follow_symlinks=False 避免跟踪符号链接，防止无限递归
                    if entry.is_file(follow_symlinks=False):
                        if pattern_fn(entry, extension):
                            yield entry
                    elif recursive and entry.is_dir(follow_symlinks=False):
                        # 递归进入子目录，并 yield 所有匹配的文件
                        yield from walk_files_scandir(entry.path, extension, recursive, pattern_fn)
                except OSError as e:
                    # 处理单个条目时的错误（如损坏的符号链接、无权限访问单个文件等），记录并继续
                    print(f"警告：跳过条目 '{entry.path}'：{e}")
                    continue
    except PermissionError as e:
        print(f"错误：无权限访问目录 '{folder_path}'")
        raise
    except OSError as e:
        print(f"错误：无法扫描目录 '{folder_path}'：{e}")
        raise

def calculate_file_md5(file_path: str) -> str:
    """分块计算文件MD5，避免内存溢出"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()



# 使用示例
if __name__ == "__main__":
    sample_dir = r"D:\Downloads"  # 替换为你的目录路径

    print("=== 示例1：统计所有文件（extension=None） ===")
    try:
        all_files_count = count_files_scandir(sample_dir, extension=None, recursive=True)
        print(f"找到 {all_files_count} 个文件。")
    except Exception as e:
        print(f"统计文件时发生错误: {e}")

    print("\n=== 示例2：统计 .jpg 文件 ===")
    try:
        txt_count = count_files_scandir(sample_dir, ".jpg", recursive=True)
        print(f"找到 {txt_count} 个 .jpg 文件。")
    except Exception as e:
        print(f"统计文件时发生错误: {e}")

    print("\n=== 示例3：使用自定义匹配函数（查找大于1MB的文件） ===")
    def large_file_filter(entry: os.DirEntry, ext: Optional[str]) -> bool:
        """自定义过滤函数：文件大小大于1MB则返回True，忽略扩展名"""
        try:
            return entry.stat().st_size > 1024 * 1024 # 1MB
        except OSError:
            return False

    try:
        large_files_count = count_files_scandir(sample_dir, extension=None, recursive=True, pattern_fn=large_file_filter)
        print(f"找到 {large_files_count} 个大于1MB的文件。")
    except Exception as e:
        print(f"统计大文件时发生错误: {e}")

    print("\n" + "="*50 + "\n")

    print("=== 示例4：遍历所有文件（extension=None） ===")
    try:
        for file_entry in walk_files_scandir(sample_dir, extension=None, recursive=True):
            file_stat = file_entry.stat()
            print(f"文件: {file_entry.path}, 大小: {file_stat.st_size} 字节")
    except Exception as e:
        print(f"遍历文件时发生错误: {e}")

    print("\n=== 示例5：遍历 .jpg 文件 ===")
    try:
        for file_entry in walk_files_scandir(sample_dir, ".jpg", recursive=True):
            file_stat = file_entry.stat()
            print(f"图片: {file_entry.path}, 大小: {file_stat.st_size} 字节")
    except Exception as e:
        print(f"遍历图片时发生错误: {e}")
