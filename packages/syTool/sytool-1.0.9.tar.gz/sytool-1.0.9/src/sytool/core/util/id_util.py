import time
import threading
import uuid
import socket
import os
import random


class Snowflake:
    """
    Twitter的Snowflake算法实现，用于生成分布式唯一ID

    结构如下（每部分用-分开）:
    0 - 0000000000 0000000000 0000000000 0000000000 0 - 00000 - 00000 - 000000000000
    第一位为未使用（符号位表示正数），接下来的41位为毫秒级时间(41位的长度可以使用69年)
    然后是5位datacenterId和5位workerId(10位的长度最多支持部署1024个节点）
    最后12位是毫秒内的计数（12位的计数顺序号支持每个节点每毫秒产生4096个ID序号）
    """

    # 默认起始时间（2010-11-04 01:42:54 GMT）
    DEFAULT_TWEPOCH = 1288834974657
    # 默认回拨时间（2秒）
    DEFAULT_TIME_OFFSET = 2000

    # 各部分的位数
    WORKER_ID_BITS = 5
    DATA_CENTER_ID_BITS = 5
    SEQUENCE_BITS = 12

    # 最大支持的值
    MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)
    MAX_DATA_CENTER_ID = -1 ^ (-1 << DATA_CENTER_ID_BITS)

    # 移位
    WORKER_ID_SHIFT = SEQUENCE_BITS
    DATA_CENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
    TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATA_CENTER_ID_BITS

    # 序列掩码
    SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

    def __init__(self, worker_id=0, data_center_id=0, twepoch=DEFAULT_TWEPOCH, time_offset=DEFAULT_TIME_OFFSET):
        """
        初始化Snowflake

        Args:
            worker_id: 工作节点ID (0-31)
            data_center_id: 数据中心ID (0-31)
            twepoch: 起始时间戳（毫秒）
            time_offset: 允许的时间回拨（毫秒）
        """
        # 参数校验
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f"worker_id must be between 0 and {self.MAX_WORKER_ID}")
        if data_center_id > self.MAX_DATA_CENTER_ID or data_center_id < 0:
            raise ValueError(f"data_center_id must be between 0 and {self.MAX_DATA_CENTER_ID}")

        self.worker_id = worker_id
        self.data_center_id = data_center_id
        self.twepoch = twepoch
        self.time_offset = time_offset

        # 序列号和最后时间戳
        self.sequence = 0
        self.last_timestamp = -1

        # 线程锁
        self.lock = threading.Lock()

    def next_id(self):
        """生成下一个ID"""
        with self.lock:
            timestamp = self._current_time()

            # 处理时钟回拨
            if timestamp < self.last_timestamp:
                offset = self.last_timestamp - timestamp
                if offset <= self.time_offset:
                    # 在允许的回拨范围内，等待时间追赶
                    time.sleep(offset / 1000.0)
                    timestamp = self._current_time()
                else:
                    raise ValueError(f"Clock moved backwards. Refusing to generate id for {offset}ms")

            # 同一毫秒内的序列号处理
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.SEQUENCE_MASK
                if self.sequence == 0:
                    # 序列号用完，等待下一毫秒
                    timestamp = self._til_next_millis(self.last_timestamp)
            else:
                # 新的毫秒，重置序列号
                self.sequence = 0

            self.last_timestamp = timestamp

            # 生成ID
            return ((timestamp - self.twepoch) << self.TIMESTAMP_LEFT_SHIFT) | \
                (self.data_center_id << self.DATA_CENTER_ID_SHIFT) | \
                (self.worker_id << self.WORKER_ID_SHIFT) | \
                self.sequence

    def next_id_str(self):
        """生成下一个ID（字符串形式）"""
        return str(self.next_id())

    def _current_time(self):
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)

    def _til_next_millis(self, last_timestamp):
        """等待直到下一毫秒"""
        timestamp = self._current_time()
        while timestamp <= last_timestamp:
            timestamp = self._current_time()
        return timestamp

    def parse_id(self, snowflake_id):
        """解析Snowflake ID"""
        timestamp = (snowflake_id >> self.TIMESTAMP_LEFT_SHIFT) + self.twepoch
        data_center_id = (snowflake_id >> self.DATA_CENTER_ID_SHIFT) & (2 ** self.DATA_CENTER_ID_BITS - 1)
        worker_id = (snowflake_id >> self.WORKER_ID_SHIFT) & (2 ** self.WORKER_ID_BITS - 1)
        sequence = snowflake_id & (2 ** self.SEQUENCE_BITS - 1)

        return {
            'timestamp': timestamp,
            'datetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp / 1000)),
            'data_center_id': data_center_id,
            'worker_id': worker_id,
            'sequence': sequence
        }


class IdUtil:
    """ID生成工具类"""

    # Snowflake单例字典
    _snowflake_instances = {}
    _snowflake_lock = threading.Lock()

    @staticmethod
    def random_uuid():
        """生成随机UUID"""
        return str(uuid.uuid4())

    @staticmethod
    def simple_uuid():
        """生成简化的UUID（去掉横线）"""
        return uuid.uuid4().hex

    @staticmethod
    def fast_uuid():
        """生成随机UUID（性能优化版本）"""
        return str(uuid.uuid4())

    @staticmethod
    def fast_simple_uuid():
        """生成简化的UUID（去掉横线，性能优化版本）"""
        return uuid.uuid4().hex

    @staticmethod
    def get_snowflake(worker_id=None, data_center_id=None):
        """
        获取Snowflake单例

        Args:
            worker_id: 工作节点ID
            data_center_id: 数据中心ID

        Returns:
            Snowflake实例
        """
        # 如果没有提供参数，使用默认值0
        worker_id = worker_id if worker_id is not None else 0
        data_center_id = data_center_id if data_center_id is not None else 0

        key = (worker_id, data_center_id)

        with IdUtil._snowflake_lock:
            if key not in IdUtil._snowflake_instances:
                IdUtil._snowflake_instances[key] = Snowflake(worker_id, data_center_id)
            return IdUtil._snowflake_instances[key]

    @staticmethod
    def get_data_center_id(max_data_center_id=31):
        """
        获取数据中心ID（基于MAC地址）

        Args:
            max_data_center_id: 最大数据中心ID

        Returns:
            数据中心ID
        """
        try:
            # 获取MAC地址
            mac = uuid.getnode()
            # 转换为整数并取模
            return mac % (max_data_center_id + 1)
        except:
            return random.randint(0, max_data_center_id)

    @staticmethod
    def get_worker_id(data_center_id, max_worker_id=31):
        """
        获取工作节点ID（基于进程ID）

        Args:
            data_center_id: 数据中心ID
            max_worker_id: 最大工作节点ID

        Returns:
            工作节点ID
        """
        try:
            # 获取进程ID
            pid = os.getpid()
            # 结合数据中心ID生成工作节点ID
            return (data_center_id + pid) % (max_worker_id + 1)
        except:
            return random.randint(0, max_worker_id)

    @staticmethod
    def nano_id(size=21):
        """
        生成NanoID

        Args:
            size: ID长度

        Returns:
            NanoID
        """
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return ''.join(random.choices(alphabet, k=size))

    @staticmethod
    def get_snowflake_next_id():
        """获取下一个Snowflake ID"""
        return IdUtil.get_snowflake().next_id()

    @staticmethod
    def get_snowflake_next_id_str():
        """获取下一个Snowflake ID（字符串形式）"""
        return str(IdUtil.get_snowflake().next_id())


if __name__ == "__main__":

    # 1. 生成UUID
    print("随机UUID:", IdUtil.random_uuid())
    print("简单UUID(无横线):", IdUtil.simple_uuid())

    # 3. 生成Snowflake ID
    snowflake = IdUtil.get_snowflake(1, 1)  # 指定worker_id和datacenter_id
    print("Snowflake ID:", snowflake.next_id())
    print("Snowflake ID字符串:", str(snowflake.next_id()))

    # 4. 简单获取Snowflake ID
    print("简单Snowflake ID:", IdUtil.get_snowflake_next_id())
    print("简单Snowflake ID字符串:", IdUtil.get_snowflake_next_id_str())

    # 5. 生成NanoId
    print("NanoId:", IdUtil.nano_id())
    print("自定义长度NanoId:", IdUtil.nano_id(10))

    # 6. 自动生成worker_id和datacenter_id
    datacenter_id = IdUtil.get_data_center_id(31)
    worker_id = IdUtil.get_worker_id(datacenter_id, 31)
    print(f"自动生成的数据中心ID: {datacenter_id}, 工作机器ID: {worker_id}")
