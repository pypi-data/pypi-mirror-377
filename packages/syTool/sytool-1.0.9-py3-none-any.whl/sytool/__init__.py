"""
Sawyer Tools
======================
工具包集

:copyright: (c) 2025 by laishaoya.
:license: GPLv3 for non-commercial project, see README for more details.
"""

__version__ = "1.0.9"
__author__ = "Sawyerlsy"


def show_banner():
    """显示艺术字标识"""
    banner = r"""
    ███████╗██╗   ██╗████████╗ ██████╗  ██████╗ ██╗     
    ██╔════╝╚██╗ ██╔╝╚══██╔══╝██╔═══██╗██╔═══██╗██║     
    ███████╗ ╚████╔╝    ██║   ██║   ██║██║   ██║██║     
    ╚════██║  ╚██╔╝     ██║   ██║   ██║██║   ██║██║     
    ███████║   ██║      ██║   ╚██████╔╝╚██████╔╝███████╗
    ╚══════╝   ╚═╝      ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
    """
    print(banner)
    print(f"📢 Version: {__version__} | Author: {__author__}")
show_banner()

# 仅导入不需要额外依赖的模块
from .core.util.char_util import CharPool, CharUtil
from .core.util.date_util import DateField,DateUnit,DatePattern,DateUtil
from .core.util.escape_util import EscapeUtil
from .core.util.file_util import FileMode,PathUtil,FileUtil
from .core.util.hex_util import HexUtil
from .core.util.id_util import Snowflake,IdUtil
from .core.util.number_util import NumberUtil
from .core.util.object_util import ObjectUtil
from .core.util.radix_util import RadixUtil
from .core.util.random_util import RandomUtil
from .core.util.str_util import StrPool,StrUtil
from .core.util.zip_util import ZipUtil
from .core.singleton import SingletonMeta

from .cypto.base64_util import Base64Util
from .cypto.digest_util import DigestUtil

from .db.sqlbuilder import SQLBuilder
from .json.json_util import JSONUtil

from .core.debounce_timer import DebounceTimer
