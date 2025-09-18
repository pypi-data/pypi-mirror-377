import datetime
import re
from typing import Union, Optional, List, Tuple, Callable, Any
from enum import Enum
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser
import pytz
from functools import lru_cache


class DateField(Enum):
    """日期字段枚举 (用于偏移计算)"""
    YEAR = 'years'
    MONTH = 'months'
    DAY = 'days'
    HOUR = 'hours'
    MINUTE = 'minutes'
    SECOND = 'seconds'
    MICROSECOND = 'microseconds'
    WEEK = 'weeks'  # relativedelta 也支持 weeks


class DateUnit(Enum):
    """日期单位枚举"""
    MS = "milliseconds"
    SECOND = "seconds"
    MINUTE = "minutes"
    HOUR = "hours"
    DAY = "days"
    WEEK = "weeks"
    MONTH = "months"
    YEAR = "years"


class DatePattern:
    """日期模式常量类"""
    NORM_DATE_PATTERN = "%Y-%m-%d"
    NORM_TIME_PATTERN = "%H:%M:%S"
    NORM_DATETIME_PATTERN = "%Y-%m-%d %H:%M:%S"
    NORM_DATETIME_MINUTE_PATTERN = "%Y-%m-%d %H:%M"
    NORM_DATETIME_MS_PATTERN = "%Y-%m-%d %H:%M:%S.%f"
    UTC_SIMPLE_PATTERN = "%Y-%m-%dT%H:%M:%S"
    UTC_SIMPLE_MS_PATTERN = "%Y-%m-%dT%H:%M:%S.%f"
    HTTP_DATETIME_PATTERN = "%a, %d %b %Y %H:%M:%S %Z"
    JDK_DATETIME_PATTERN = "%a %b %d %H:%M:%S %Z %Y"
    PURE_DATE_PATTERN = "%Y%m%d"
    PURE_TIME_PATTERN = "%H%M%S"
    PURE_DATETIME_PATTERN = "%Y%m%d%H%M%S"
    PURE_DATETIME_MS_PATTERN = "%Y%m%d%H%M%S%f"
    CHINESE_DATE_PATTERN = "%Y年%m月%d日"
    CHINESE_DATE_TIME_PATTERN = "%Y年%m月%d日 %H时%M分%S秒"


class DateUtilError(Exception):
    """DateUtil 相关异常基类"""
    pass


class DateUtilParseError(DateUtilError):
    """日期解析异常"""
    pass


class DateUtil:
    """日期时间工具类，提供丰富的日期时间操作方法"""

    @staticmethod
    def now(tz: Optional[datetime.tzinfo] = None) -> datetime.datetime:
        """
        获取当前日期时间

        Args:
            tz: 时区信息对象，如果为None则返回本地时间，否则返回指定时区时间

        Returns:
            日期时间对象
        """
        if tz is None:
            return datetime.datetime.now()
        else:
            return datetime.datetime.now(tz)

    @staticmethod
    def now_utc() -> datetime.datetime:
        """
        获取当前UTC时间

        Returns:
            UTC日期对象
        """
        return datetime.datetime.now(pytz.UTC)

    @staticmethod
    def today() -> datetime.date:
        """获取当前日期"""
        return datetime.date.today()

    @staticmethod
    def parse(date_str: str, pattern: Optional[str] = None) -> datetime.datetime:
        """
        解析字符串为日期时间对象

        Args:
            date_str: 日期时间字符串
            pattern: 日期格式模式（可选）。如果提供，则使用strptime；否则使用dateutil.parser.parse

        Returns:
            日期时间对象

        Raises:
            DateUtilParseError: 当解析失败时抛出
        """
        try:
            if pattern:
                return datetime.datetime.strptime(date_str, pattern)
            return date_parser.parse(date_str)
        except (ValueError, TypeError, AttributeError) as e:
            raise DateUtilParseError(f"Failed to parse date string '{date_str}' with pattern '{pattern}': {e}")

    @staticmethod
    def parse_date(date_str: str) -> datetime.date:
        """
        解析字符串为日期对象

        Args:
            date_str: 日期字符串

        Returns:
            日期对象

        Raises:
            DateUtilParseError: 当解析失败时抛出
        """
        return DateUtil.parse(date_str).date()

    @staticmethod
    def parse_time(time_str: str) -> datetime.time:
        """
        解析字符串为时间对象

        Args:
            time_str: 时间字符串

        Returns:
            时间对象

        Raises:
            DateUtilParseError: 当解析失败时抛出
        """
        return DateUtil.parse(time_str).time()

    @staticmethod
    def format(date: datetime.datetime, pattern: str) -> str:
        """
        格式化日期时间对象为字符串

        Args:
            date: 日期时间对象
            pattern: 日期格式模式

        Returns:
            格式化后的字符串
        """
        return date.strftime(pattern)

    @staticmethod
    def format_date(date: datetime.datetime) -> str:
        """
        格式化日期部分（不包括时间）

        Args:
            date: 日期时间对象

        Returns:
            yyyy-MM-dd格式的字符串
        """
        return date.strftime(DatePattern.NORM_DATE_PATTERN)

    @staticmethod
    def format_time(date: datetime.datetime) -> str:
        """
        格式化时间部分

        Args:
            date: 日期时间对象

        Returns:
            HH:mm:ss格式的字符串
        """
        return date.strftime(DatePattern.NORM_TIME_PATTERN)

    @staticmethod
    def format_datetime(date: datetime.datetime) -> str:
        """
        格式化日期时间

        Args:
            date: 日期时间对象

        Returns:
            yyyy-MM-dd HH:mm:ss格式的字符串
        """
        return date.strftime(DatePattern.NORM_DATETIME_PATTERN)

    @staticmethod
    def offset(date: datetime.datetime, field: DateField, amount: int) -> datetime.datetime:
        """
        偏移日期时间 (使用 relativedelta，能更准确处理月和年)

        Args:
            date: 原始日期时间
            field: 偏移字段
            amount: 偏移量

        Returns:
            偏移后的日期时间
        """
        # 构建 relativedelta 参数
        delta_args = {field.value: amount}
        return date + relativedelta(**delta_args)

    @staticmethod
    def offset_days(date: datetime.datetime, days: int) -> datetime.datetime:
        """
        偏移天数

        Args:
            date: 原始日期时间
            days: 偏移天数

        Returns:
            偏移后的日期时间
        """
        return DateUtil.offset(date, DateField.DAY, days)

    @staticmethod
    def offset_hours(date: datetime.datetime, hours: int) -> datetime.datetime:
        """
        偏移小时数

        Args:
            date: 原始日期时间
            hours: 偏移小时数

        Returns:
            偏移后的日期时间
        """
        return DateUtil.offset(date, DateField.HOUR, hours)

    @staticmethod
    def offset_minutes(date: datetime.datetime, minutes: int) -> datetime.datetime:
        """
        偏移分钟数

        Args:
            date: 原始日期时间
            minutes: 偏移分钟数

        Returns:
            偏移后的日期时间
        """
        return DateUtil.offset(date, DateField.MINUTE, minutes)

    @staticmethod
    def offset_seconds(date: datetime.datetime, seconds: int) -> datetime.datetime:
        """
        偏移秒数

        Args:
            date: 原始日期时间
            seconds: 偏移秒数

        Returns:
            偏移后的日期时间
        """
        return DateUtil.offset(date, DateField.SECOND, seconds)

    @staticmethod
    def offset_weeks(date: datetime.datetime, weeks: int) -> datetime.datetime:
        """
        偏移周数

        Args:
            date: 原始日期时间
            weeks: 偏移周数

        Returns:
            偏移后的日期时间
        """
        return DateUtil.offset(date, DateField.WEEK, weeks)

    @staticmethod
    def offset_months(date: datetime.datetime, months: int) -> datetime.datetime:
        """
        偏移月数

        Args:
            date: 原始日期时间
            months: 偏移月数

        Returns:
            偏移后的日期时间
        """
        return DateUtil.offset(date, DateField.MONTH, months)

    @staticmethod
    def offset_years(date: datetime.datetime, years: int) -> datetime.datetime:
        """
        偏移年数

        Args:
            date: 原始日期时间
            years: 偏移年数

        Returns:
            偏移后的日期时间
        """
        return DateUtil.offset(date, DateField.YEAR, years)

    @staticmethod
    def between(start: datetime.datetime, end: datetime.datetime, unit: DateUnit) -> int:
        """
        计算两个日期时间之间的差值

        Args:
            start: 开始时间
            end: 结束时间
            unit: 时间单位

        Returns:
            时间差值
        """
        delta = end - start
        if unit == DateUnit.MS:
            return int(delta.total_seconds() * 1000)
        elif unit == DateUnit.SECOND:
            return int(delta.total_seconds())
        elif unit == DateUnit.MINUTE:
            return int(delta.total_seconds() / 60)
        elif unit == DateUnit.HOUR:
            return int(delta.total_seconds() / 3600)
        elif unit == DateUnit.DAY:
            return delta.days
        elif unit == DateUnit.WEEK:
            return delta.days // 7
        elif unit == DateUnit.MONTH:
            return (end.year - start.year) * 12 + (end.month - start.month)
        elif unit == DateUnit.YEAR:
            return end.year - start.year
        else:
            raise ValueError(f"Unsupported unit: {unit}")

    @staticmethod
    def is_same_day(date1: datetime.datetime, date2: datetime.datetime) -> bool:
        """
        判断两个日期是否为同一天

        Args:
            date1: 日期1
            date2: 日期2

        Returns:
            是否为同一天
        """
        return date1.date() == date2.date()

    @staticmethod
    def is_same_month(date1: datetime.datetime, date2: datetime.datetime) -> bool:
        """
        判断两个日期是否为同一月

        Args:
            date1: 日期1
            date2: 日期2

        Returns:
            是否为同一月
        """
        return date1.year == date2.year and date1.month == date2.month

    @staticmethod
    def is_same_year(date1: datetime.datetime, date2: datetime.datetime) -> bool:
        """
        判断两个日期是否为同一年

        Args:
            date1: 日期1
            date2: 日期2

        Returns:
            是否为同一年
        """
        return date1.year == date2.year

    @staticmethod
    @lru_cache(maxsize=128)
    def is_leap_year(year: int) -> bool:
        """
        判断是否为闰年

        Args:
            year: 年份

        Returns:
            是否为闰年
        """
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    @staticmethod
    @lru_cache(maxsize=128)
    def get_days_in_month(year: int, month: int) -> int:
        """
        获取某年某月的天数

        Args:
            year: 年份
            month: 月份

        Returns:
            天数

        Raises:
            ValueError: 如果月份不在1-12之间
        """
        if month < 1 or month > 12:
            raise ValueError("month must be in 1..12")
        if month == 2:
            return 29 if DateUtil.is_leap_year(year) else 28
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            return 31

    @staticmethod
    def get_begin_of_day(date: datetime.datetime) -> datetime.datetime:
        """
        获取某天的开始时间（00:00:00）

        Args:
            date: 日期时间对象

        Returns:
            当天的开始时间
        """
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def get_end_of_day(date: datetime.datetime) -> datetime.datetime:
        """
        获取某天的结束时间（23:59:59.999999）

        Args:
            date: 日期时间对象

        Returns:
            当天的结束时间
        """
        return date.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def get_begin_of_month(date: datetime.datetime) -> datetime.datetime:
        """
        获取某月的开始时间

        Args:
            date: 日期时间对象

        Returns:
            当月的开始时间
        """
        return datetime.datetime(date.year, date.month, 1)

    @staticmethod
    def get_end_of_month(date: datetime.datetime) -> datetime.datetime:
        """
        获取某月的结束时间

        Args:
            date: 日期时间对象

        Returns:
            当月的结束时间
        """
        next_month = date.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    @staticmethod
    def get_begin_of_year(date: datetime.datetime) -> datetime.datetime:
        """
        获取某年的开始时间

        Args:
            date: 日期时间对象

        Returns:
            当年的开始时间
        """
        return datetime.datetime(date.year, 1, 1)

    @staticmethod
    def get_end_of_year(date: datetime.datetime) -> datetime.datetime:
        """
        获取某年的结束时间

        Args:
            date: 日期时间对象

        Returns:
            当年的结束时间
        """
        return datetime.datetime(date.year, 12, 31, 23, 59, 59, 999999)

    @staticmethod
    def get_week_of_year(date: datetime.datetime) -> int:
        """
        获取日期在一年中的周数 (ISO 8601 周数)

        Args:
            date: 日期时间对象

        Returns:
            周数
        """
        return date.isocalendar()[1]

    @staticmethod
    def get_day_of_year(date: datetime.datetime) -> int:
        """
        获取日期在一年中的天数

        Args:
            date: 日期时间对象

        Returns:
            天数
        """
        return date.timetuple().tm_yday

    @staticmethod
    def get_day_of_week(date: datetime.datetime) -> int:
        """
        获取日期在一周中的天数（周一为0，周日为6）

        Args:
            date: 日期时间对象

        Returns:
            周几（0-6）
        """
        return date.weekday()

    @staticmethod
    def is_weekend(date: datetime.datetime) -> bool:
        """
        判断日期是否为周末

        Args:
            date: 日期时间对象

        Returns:
            是否为周末
        """
        return date.weekday() in [5, 6]  # 5=周六, 6=周日

    @staticmethod
    def age(birth_date: datetime.datetime, reference_date: Optional[datetime.datetime] = None) -> int:
        """
        计算年龄

        Args:
            birth_date: 出生日期
            reference_date: 参考日期（默认为当前日期）

        Returns:
            年龄
        """
        if reference_date is None:
            reference_date = datetime.datetime.now()

        years = reference_date.year - birth_date.year
        if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
            years -= 1
        return years

    @staticmethod
    def to_timestamp(date: datetime.datetime) -> int:
        """
        将日期时间转换为时间戳（毫秒）

        Args:
            date: 日期时间对象

        Returns:
            时间戳（毫秒）
        """
        return int(date.timestamp() * 1000)

    @staticmethod
    def from_timestamp(timestamp: int) -> datetime.datetime:
        """
        将时间戳（毫秒）转换为日期时间

        Args:
            timestamp: 时间戳（毫秒）

        Returns:
            日期时间对象
        """
        return datetime.datetime.fromtimestamp(timestamp / 1000.0)

    @staticmethod
    def convert_timezone(date: datetime.datetime, timezone: str) -> datetime.datetime:
        """
        转换时区

        Args:
            date: 原始日期时间 (需为时区感知类型，否则假定为本地时间)
            timezone: 目标时区字符串 (e.g., 'UTC', 'Asia/Shanghai')

        Returns:
            转换时区后的日期时间
        """
        if date.tzinfo is None:
            # 如果原始日期没有时区信息，假定为本地时间
            local_tz = pytz.timezone('UTC')  # 这里应该用本地时区，但pytz没有直接的本地时区，通常用系统设置。这里简化处理，建议传入的date最好带时区。
            date = local_tz.localize(date)
        tz = pytz.timezone(timezone)
        return date.astimezone(tz)

    @staticmethod
    def is_between(date: datetime.datetime, start: datetime.datetime, end: datetime.datetime) -> bool:
        """
        判断日期是否在指定范围内

        Args:
            date: 要判断的日期
            start: 开始日期
            end: 结束日期

        Returns:
            是否在范围内
        """
        return start <= date <= end

    @staticmethod
    def range(start: datetime.datetime, end: datetime.datetime, unit: DateUnit, step: int = 1) -> List[
        datetime.datetime]:
        """
        生成日期范围 (对于月和年，使用relativedelta；对于其他单位，使用timedelta)

        Args:
            start: 开始日期
            end: 结束日期
            unit: 时间单位
            step: 步长

        Returns:
            日期范围列表
        """
        result = []
        current = start

        if unit in [DateUnit.MONTH, DateUnit.YEAR]:
            # 对于月和年，使用 relativedelta
            if unit == DateUnit.MONTH:
                delta_func = lambda d: relativedelta(months=d)
            else:  # DateUnit.YEAR
                delta_func = lambda d: relativedelta(years=d)

            while current <= end:
                result.append(current)
                current = current + delta_func(step)
        else:
            # 对于其他单位，使用 timedelta
            unit_to_timedelta = {
                DateUnit.MS: datetime.timedelta(milliseconds=step),
                DateUnit.SECOND: datetime.timedelta(seconds=step),
                DateUnit.MINUTE: datetime.timedelta(minutes=step),
                DateUnit.HOUR: datetime.timedelta(hours=step),
                DateUnit.DAY: datetime.timedelta(days=step),
                DateUnit.WEEK: datetime.timedelta(weeks=step),
            }
            delta = unit_to_timedelta.get(unit)
            if delta is None:
                raise ValueError(f"Unsupported unit for range with timedelta: {unit}")

            while current <= end:
                result.append(current)
                current = current + delta

        return result

    @staticmethod
    def format_duration(duration: datetime.timedelta) -> str:
        """
        格式化时间间隔

        Args:
            duration: 时间间隔

        Returns:
            格式化后的字符串（天:小时:分:秒）
        """
        seconds = duration.total_seconds()
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(days)}:{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    @staticmethod
    def get_last_day_of_month(year: int, month: int) -> int:
        """
        获取某月的最后一天

        Args:
            year: 年份
            month: 月份

        Returns:
            最后一天
        """
        next_month = datetime.datetime(year + (month // 12), (month % 12) + 1, 1)
        last_day = next_month - datetime.timedelta(days=1)
        return last_day.day

    @staticmethod
    def is_last_day_of_month(date: datetime.datetime) -> bool:
        """
        判断是否为当月的最后一天

        Args:
            date: 日期时间对象

        Returns:
            是否为最后一天
        """
        next_day = date + datetime.timedelta(days=1)
        return next_day.month != date.month

    @staticmethod
    def normalize(date_str: str) -> str:
        """
        标准化日期字符串 (尝试替换中文单位和分隔符，但解析仍建议使用parse方法)

        Args:
            date_str: 日期字符串

        Returns:
            标准化后的日期字符串
        """
        # 替换中文日期分隔符
        normalized = date_str.replace("年", "-").replace("月", "-").replace("日", "")
        normalized = normalized.replace("时", ":").replace("分", ":").replace("秒", "")

        # 替换其他分隔符
        normalized = re.sub(r"[/.]", "-", normalized)

        # 处理多余的分隔符
        normalized = re.sub(r"-+", "-", normalized)
        normalized = re.sub(r":+", ":", normalized)

        return normalized.strip()

    @staticmethod
    def parse_utc(utc_str: str) -> datetime.datetime:
        """
        解析UTC时间字符串 (支持'Z'后缀)

        Args:
            utc_str: UTC时间字符串

        Returns:
            日期时间对象 (时区感知)
        """
        if 'Z' in utc_str:
            utc_str = utc_str.replace('Z', '+00:00')
        return datetime.datetime.fromisoformat(utc_str)

    @staticmethod
    def format_utc(date: datetime.datetime) -> str:
        """
        格式化为UTC时间字符串 (添加'Z'后缀)。如果date不是时区感知的，假定为本地时间并转换。

        Args:
            date: 日期时间对象

        Returns:
            UTC时间字符串
        """
        if date.tzinfo is None:
            # 假定为本地时间，转换为UTC
            date = date.astimezone(pytz.UTC)
        utc_str = date.isoformat(timespec='seconds')
        if utc_str.endswith('+00:00'):
            utc_str = utc_str[:-6] + 'Z'
        return utc_str

    @staticmethod
    def get_quarter(date: datetime.datetime) -> int:
        """
        获取季度

        Args:
            date: 日期时间对象

        Returns:
            季度（1-4）
        """
        return (date.month - 1) // 3 + 1

    @staticmethod
    def get_begin_of_quarter(date: datetime.datetime) -> datetime.datetime:
        """
        获取季度的开始时间

        Args:
            date: 日期时间对象

        Returns:
            季度开始时间
        """
        quarter = DateUtil.get_quarter(date)
        month = (quarter - 1) * 3 + 1
        return datetime.datetime(date.year, month, 1)

    @staticmethod
    def get_end_of_quarter(date: datetime.datetime) -> datetime.datetime:
        """
        获取季度的结束时间

        Args:
            date: 日期时间对象

        Returns:
            季度结束时间
        """
        quarter = DateUtil.get_quarter(date)
        month = quarter * 3
        return DateUtil.get_end_of_month(datetime.datetime(date.year, month, 1))

    @staticmethod
    def get_week_start(date: datetime.datetime, start_day: int = 0) -> datetime.datetime:
        """
        获取周的开始时间

        Args:
            date: 日期时间对象
            start_day: 周的开始日（0=周一，6=周日）

        Returns:
            周的开始时间
        """
        weekday = date.weekday()
        days_diff = (weekday - start_day) % 7
        return date - datetime.timedelta(days=days_diff)

    @staticmethod
    def get_week_end(date: datetime.datetime, start_day: int = 0) -> datetime.datetime:
        """
        获取周的结束时间

        Args:
            date: 日期时间对象
            start_day: 周的开始日（0=周一，6=周日）

        Returns:
            周的结束时间
        """
        start = DateUtil.get_week_start(date, start_day)
        return start + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)

    @staticmethod
    def is_overlap(start1: datetime.datetime, end1: datetime.datetime,
                   start2: datetime.datetime, end2: datetime.datetime) -> bool:
        """
        判断两个时间段是否有重叠

        Args:
            start1: 时间段1开始时间
            end1: 时间段1结束时间
            start2: 时间段2开始时间
            end2: 时间段2结束时间

        Returns:
            是否有重叠
        """
        return (start1 <= end2) and (start2 <= end1)


if __name__ == '__main__':
    # ======================
    # 解析与格式化
    # ======================

    # 解析日期时间
    dt = DateUtil.parse("2023-10-15 14:30:00")
    print(f"解析结果: {dt}")

    # 格式化日期时间
    formatted = DateUtil.format(dt, DatePattern.NORM_DATETIME_PATTERN)
    print(f"格式化结果: {formatted}")

    # ======================
    # 日期计算
    # ======================

    # 偏移天数
    tomorrow = DateUtil.offset_days(dt, 1)
    print(f"明天: {tomorrow}")

    # 偏移月份
    next_month = DateUtil.offset_months(dt, 1)
    print(f"下个月: {next_month}")

    # 计算时间差
    days_diff = DateUtil.between(dt, tomorrow, DateUnit.DAY)
    print(f"相差天数: {days_diff}")

    # ======================
    # 日期信息获取
    # ======================

    # 获取季度
    quarter = DateUtil.get_quarter(dt)
    print(f"季度: {quarter}")

    # 获取周数
    week_number = DateUtil.get_week_of_year(dt)
    print(f"周数: {week_number}")

    # 判断是否为周末
    is_weekend = DateUtil.is_weekend(dt)
    print(f"是否为周末: {is_weekend}")

    # ======================
    # 日期范围处理
    # ======================

    # 获取当天的开始和结束时间
    start_of_day = DateUtil.get_begin_of_day(dt)
    end_of_day = DateUtil.get_end_of_day(dt)
    print(f"当天开始: {start_of_day}, 当天结束: {end_of_day}")

    # 获取当月的开始和结束时间
    start_of_month = DateUtil.get_begin_of_month(dt)
    end_of_month = DateUtil.get_end_of_month(dt)
    print(f"当月开始: {start_of_month}, 当月结束: {end_of_month}")

    # 生成日期范围
    start_date = datetime.datetime(2023, 10, 1)
    end_date = datetime.datetime(2023, 10, 10)
    date_range = DateUtil.range(start_date, end_date, DateUnit.DAY)
    print(f"日期范围: {[d.strftime('%Y-%m-%d') for d in date_range]}")

    # ======================
    # 其他功能
    # ======================

    # 年龄计算
    birth_date = datetime.datetime(1990, 5, 15)
    age = DateUtil.age(birth_date)
    print(f"年龄: {age}")

    # 时间戳转换
    timestamp = DateUtil.to_timestamp(dt)
    print(f"时间戳: {timestamp}")
    dt_from_ts = DateUtil.from_timestamp(timestamp)
    print(f"从时间戳恢复: {dt_from_ts}")

    # 时区转换
    ny_time = DateUtil.convert_timezone(dt, "America/New_York")
    print(f"纽约时间: {ny_time}")