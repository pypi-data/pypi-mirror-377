import socket
import re
import subprocess
import platform
import ipaddress
import netifaces
from typing import List, Tuple, Dict, Optional, Set, Union


class NetUtil:
    """网络工具类，提供丰富的网络操作方法"""

    # 本地IPv4地址
    LOCAL_IP = "127.0.0.1"

    # 默认最小端口，1024
    PORT_RANGE_MIN = 1024
    # 默认最大端口，65535
    PORT_RANGE_MAX = 65535

    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        验证IP地址是否有效

        Args:
            ip: IP地址字符串

        Returns:
            是否有效
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_ipv4(ip: str) -> bool:
        """
        验证是否为IPv4地址

        Args:
            ip: IP地址字符串

        Returns:
            是否为IPv4地址
        """
        try:
            return isinstance(ipaddress.ip_address(ip), ipaddress.IPv4Address)
        except ValueError:
            return False

    @staticmethod
    def is_ipv6(ip: str) -> bool:
        """
        验证是否为IPv6地址

        Args:
            ip: IP地址字符串

        Returns:
            是否为IPv6地址
        """
        try:
            return isinstance(ipaddress.ip_address(ip), ipaddress.IPv6Address)
        except ValueError:
            return False

    @staticmethod
    def is_usable_local_port(port: int) -> bool:
        """
        检测本地端口是否可用

        Args:
            port: 端口号

        Returns:
            是否可用
        """
        if not NetUtil.is_valid_port(port):
            return False

        try:
            # 尝试创建TCP套接字
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            return False

    @staticmethod
    def is_valid_port(port: int) -> bool:
        """
        验证端口号是否有效

        Args:
            port: 端口号

        Returns:
            是否有效
        """
        return NetUtil.PORT_RANGE_MIN <= port <= NetUtil.PORT_RANGE_MAX

    @staticmethod
    def get_usable_local_port(min_port: int = PORT_RANGE_MIN, max_port: int = PORT_RANGE_MAX) -> int:
        """
        获取一个可用的本地端口

        Args:
            min_port: 最小端口号
            max_port: 最大端口号

        Returns:
            可用的端口号
        """
        for port in range(min_port, max_port + 1):
            if NetUtil.is_usable_local_port(port):
                return port
        raise RuntimeError(f"Could not find an available port in range [{min_port}, {max_port}]")

    @staticmethod
    def is_inner_ip(ip: str) -> bool:
        """
        判断是否为内网IP地址

        Args:
            ip: IP地址

        Returns:
            是否为内网IP
        """
        if not NetUtil.is_ipv4(ip):
            return False

        # 内网IP段
        inner_ip_ranges = [
            ("10.0.0.0", "10.255.255.255"),
            ("172.16.0.0", "172.31.255.255"),
            ("192.168.0.0", "192.168.255.255"),
            ("127.0.0.0", "127.255.255.255")
        ]

        ip_int = int(ipaddress.IPv4Address(ip))
        for start, end in inner_ip_ranges:
            start_int = int(ipaddress.IPv4Address(start))
            end_int = int(ipaddress.IPv4Address(end))
            if start_int <= ip_int <= end_int:
                return True
        return False

    @staticmethod
    def get_ip_by_host(hostname: str) -> str:
        """
        通过域名获取IP地址

        Args:
            hostname: 域名

        Returns:
            IP地址
        """
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return hostname

    @staticmethod
    def get_localhost() -> str:
        """
        获取本机IP地址

        Returns:
            本机IP地址
        """
        try:
            # 创建一个UDP套接字连接到公共DNS
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            try:
                return socket.gethostbyname(socket.gethostname())
            except socket.gaierror:
                return NetUtil.LOCAL_IP

    @staticmethod
    def get_mac_address(ip: str = None) -> str:
        """
        获取MAC地址

        Args:
            ip: 目标IP地址（默认为本机）

        Returns:
            MAC地址
        """
        if ip is None or ip == NetUtil.get_localhost():
            # 获取本机MAC地址
            for interface in netifaces.interfaces():
                ifaddrs = netifaces.ifaddresses(interface)
                if netifaces.AF_LINK in ifaddrs:
                    mac = ifaddrs[netifaces.AF_LINK][0]['addr']
                    if mac != '00:00:00:00:00:00':
                        return mac
            return ""

        # 获取远程主机MAC地址（需要ARP协议）
        if platform.system() == "Windows":
            cmd = f"arp -a {ip}"
        else:
            cmd = f"arp -n {ip}"

        try:
            output = subprocess.check_output(cmd, shell=True).decode()
            # 解析ARP输出获取MAC地址
            match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", output)
            if match:
                return match.group(0)
        except Exception:
            pass
        return ""

    @staticmethod
    def get_host_name() -> str:
        """
        获取主机名

        Returns:
            主机名
        """
        return socket.gethostname()

    @staticmethod
    def get_network_interfaces() -> List[Dict]:
        """
        获取所有网络接口信息

        Returns:
            网络接口信息列表
        """
        interfaces = []
        for interface in netifaces.interfaces():
            ifaddrs = netifaces.ifaddresses(interface)
            interfaces.append({
                'name': interface,
                'addresses': ifaddrs
            })
        return interfaces

    @staticmethod
    def local_ipv4s() -> Set[str]:
        """
        获取本机所有IPv4地址

        Returns:
            IPv4地址集合
        """
        ips = set()
        for interface in netifaces.interfaces():
            ifaddrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in ifaddrs:
                for addr_info in ifaddrs[netifaces.AF_INET]:
                    ips.add(addr_info['addr'])
        return ips

    @staticmethod
    def local_ipv6s() -> Set[str]:
        """
        获取本机所有IPv6地址

        Returns:
            IPv6地址集合
        """
        ips = set()
        for interface in netifaces.interfaces():
            ifaddrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET6 in ifaddrs:
                for addr_info in ifaddrs[netifaces.AF_INET6]:
                    ips.add(addr_info['addr'])
        return ips

    @staticmethod
    def ping(host: str, timeout: int = 200) -> bool:
        """
        Ping检测主机是否可达

        Args:
            host: 主机地址
            timeout: 超时时间（毫秒）

        Returns:
            是否可达
        """
        # 根据操作系统选择不同的ping命令
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        count = '1'
        timeout_sec = timeout / 1000.0

        # 构建ping命令
        command = ['ping', param, count, '-W', str(timeout_sec), host]

        try:
            # 执行ping命令
            subprocess.check_output(command, stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
        """
        检查远程端口是否开启

        Args:
            host: 主机地址
            port: 端口号
            timeout: 超时时间（秒）

        Returns:
            端口是否开启
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((host, port))
                return True
        except (socket.timeout, ConnectionRefusedError):
            return False

    @staticmethod
    def get_dns_info(hostname: str, record_type: str = "A") -> List[str]:
        """
        获取DNS信息

        Args:
            hostname: 域名
            record_type: DNS记录类型（如A、AAAA、TXT等）

        Returns:
            DNS记录列表
        """
        try:
            import dns.resolver
            answers = dns.resolver.resolve(hostname, record_type)
            return [str(r) for r in answers]
        except ImportError:
            raise RuntimeError("dnspython module is required for DNS operations")
        except Exception:
            return []

    @staticmethod
    def hide_ip_part(ip: str) -> str:
        """
        隐藏IP地址的最后一部分

        Args:
            ip: IP地址

        Returns:
            隐藏后的IP地址
        """
        if not NetUtil.is_valid_ip(ip):
            return ip

        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.*"
        return ip

    @staticmethod
    def get_local_mac_address() -> str:
        """
        获取本机MAC地址

        Returns:
            MAC地址
        """
        return NetUtil.get_mac_address()

    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """
        判断是否为私有IP地址

        Args:
            ip: IP地址

        Returns:
            是否为私有IP
        """
        try:
            ip_addr = ipaddress.ip_address(ip)
            return ip_addr.is_private
        except ValueError:
            return False

    @staticmethod
    def get_public_ip() -> str:
        """
        获取本机公网IP地址

        Returns:
            公网IP地址
        """
        try:
            # 使用第三方服务获取公网IP
            import requests
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            if response.status_code == 200:
                return response.json()['ip']
        except Exception:
            pass
        return ""

    @staticmethod
    def get_network_info() -> Dict[str, Dict]:
        """
        获取详细的网络信息

        Returns:
            网络信息字典
        """
        info = {}
        for interface in netifaces.interfaces():
            ifaddrs = netifaces.ifaddresses(interface)
            info[interface] = {
                'mac': ifaddrs.get(netifaces.AF_LINK, [{}])[0].get('addr', ''),
                'ipv4': [addr['addr'] for addr in ifaddrs.get(netifaces.AF_INET, [])],
                'ipv6': [addr['addr'] for addr in ifaddrs.get(netifaces.AF_INET6, [])],
                'netmask': [addr.get('netmask', '') for addr in ifaddrs.get(netifaces.AF_INET, [])],
                'broadcast': [addr.get('broadcast', '') for addr in ifaddrs.get(netifaces.AF_INET, [])]
            }
        return info

    @staticmethod
    def get_default_gateway() -> str:
        """
        获取默认网关

        Returns:
            默认网关IP地址
        """
        gateways = netifaces.gateways()
        default_gateway = gateways.get('default', {})
        if netifaces.AF_INET in default_gateway:
            return default_gateway[netifaces.AF_INET][0]
        return ""

    @staticmethod
    def get_dns_servers() -> List[str]:
        """
        获取系统DNS服务器

        Returns:
            DNS服务器列表
        """
        try:
            # 不同操作系统的获取方式不同
            if platform.system() == 'Windows':
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters") as key:
                    nameservers = winreg.QueryValueEx(key, "NameServer")[0]
                    return nameservers.split(',') if nameservers else []
            elif platform.system() == 'Darwin':  # macOS
                import plistlib
                output = subprocess.check_output(['scutil', '--dns']).decode()
                dns_servers = []
                for line in output.splitlines():
                    if 'nameserver' in line:
                        parts = line.split()
                        if len(parts) > 1:
                            dns_servers.append(parts[1])
                return dns_servers
            else:  # Linux
                with open('/etc/resolv.conf') as f:
                    content = f.read()
                    return re.findall(r'nameserver\s+(\S+)', content)
        except Exception:
            return []

    @staticmethod
    def port_scan(host: str, start_port: int = 1, end_port: int = 1024, timeout: float = 0.5) -> Dict[int, bool]:
        """
        端口扫描

        Args:
            host: 主机地址
            start_port: 起始端口
            end_port: 结束端口
            timeout: 超时时间（秒）

        Returns:
            端口状态字典
        """
        results = {}
        for port in range(start_port, end_port + 1):
            results[port] = NetUtil.is_port_open(host, port, timeout)
        return results

    @staticmethod
    def get_http_response(url: str, timeout: int = 5) -> str:
        """
        获取HTTP响应内容

        Args:
            url: URL地址
            timeout: 超时时间（秒）

        Returns:
            HTTP响应内容
        """
        try:
            import requests
            response = requests.get(url, timeout=timeout)
            return response.text
        except Exception:
            return ""

    @staticmethod
    def get_host_by_ip(ip: str) -> str:
        """
        通过IP地址获取主机名

        Args:
            ip: IP地址

        Returns:
            主机名
        """
        try:
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            return ip

    @staticmethod
    def is_loopback_ip(ip: str) -> bool:
        """
        判断是否为回环地址

        Args:
            ip: IP地址

        Returns:
            是否为回环地址
        """
        try:
            ip_addr = ipaddress.ip_address(ip)
            return ip_addr.is_loopback
        except ValueError:
            return False

    @staticmethod
    def get_network_cidr(ip: str, netmask: str) -> str:
        """
        获取网络CIDR表示

        Args:
            ip: IP地址
            netmask: 子网掩码

        Returns:
            CIDR表示
        """
        try:
            network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
            return str(network)
        except ValueError:
            return ""

    @staticmethod
    def get_ip_range(ip: str, netmask: str) -> Tuple[str, str]:
        """
        获取IP地址范围

        Args:
            ip: IP地址
            netmask: 子网掩码

        Returns:
            (起始IP, 结束IP)
        """
        try:
            network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
            return str(network[0]), str(network[-1])
        except ValueError:
            return "", ""

    @staticmethod
    def is_same_network(ip1: str, ip2: str, netmask: str) -> bool:
        """
        判断两个IP是否在同一子网

        Args:
            ip1: 第一个IP地址
            ip2: 第二个IP地址
            netmask: 子网掩码

        Returns:
            是否在同一子网
        """
        try:
            network1 = ipaddress.IPv4Network(f"{ip1}/{netmask}", strict=False)
            network2 = ipaddress.IPv4Network(f"{ip2}/{netmask}", strict=False)
            return network1 == network2
        except ValueError:
            return False


if __name__ == '__main__':
    # ======================
    # IP地址操作
    # ======================

    # 验证IP地址
    print(f"127.0.0.1 是否有效: {NetUtil.is_valid_ip('127.0.0.1')}")
    print(f"192.168.1.300 是否有效: {NetUtil.is_valid_ip('192.168.1.300')}")

    # 判断内网IP
    print(f"192.168.1.1 是否为内网IP: {NetUtil.is_inner_ip('192.168.1.1')}")
    print(f"8.8.8.8 是否为内网IP: {NetUtil.is_inner_ip('8.8.8.8')}")

    # 隐藏IP部分
    print(f"隐藏IP: {NetUtil.hide_ip_part('192.168.1.100')}")

    # ======================
    # 端口操作
    # ======================

    # 检测端口是否可用
    port = 8080
    print(f"端口 {port} 是否可用: {NetUtil.is_usable_local_port(port)}")

    # 获取可用端口
    available_port = NetUtil.get_usable_local_port()
    print(f"获取到可用端口: {available_port}")

    # 端口扫描
    scan_results = NetUtil.port_scan("localhost", 80, 85)
    for port, is_open in scan_results.items():
        print(f"端口 {port}: {'开放' if is_open else '关闭'}")

    # ======================
    # 网络信息获取
    # ======================

    # 获取本机IP
    print(f"本机IP: {NetUtil.get_localhost()}")

    # 获取公网IP
    print(f"公网IP: {NetUtil.get_public_ip()}")

    # 获取MAC地址
    print(f"本机MAC地址: {NetUtil.get_local_mac_address()}")

    # 获取主机名
    print(f"主机名: {NetUtil.get_host_name()}")

    # 获取网络接口信息
    interfaces = NetUtil.get_network_interfaces()
    for item in interfaces:
        print(f"接口 {item['name']}: {item['addresses']}")

    # ======================
    # 网络检测
    # ======================

    # Ping检测
    host = "www.google.com"
    print(f"Ping {host}: {'成功' if NetUtil.ping(host) else '失败'}")

    # 检测端口开放
    port = 80
    print(f"端口 {port} 是否开放: {NetUtil.is_port_open(host, port)}")

    # ======================
    # DNS操作
    # ======================

    # 域名解析
    domain = "www.example.com"
    print(f"{domain} 的IP地址: {NetUtil.get_ip_by_host(domain)}")

    # 获取DNS记录
    dns_records = NetUtil.get_dns_info(domain, "A")
    print(f"{domain} 的A记录: {dns_records}")

    # ======================
    # 其他功能
    # ======================

    # 获取HTTP响应
    url = "http://www.example.com"
    print(f"{url} 的响应内容: {NetUtil.get_http_response(url)[:100]}...")

    # 获取网络CIDR
    ip = "192.168.1.100"
    netmask = "255.255.255.0"
    print(f"网络CIDR: {NetUtil.get_network_cidr(ip, netmask)}")

    # 判断同一子网
    ip1 = "192.168.1.100"
    ip2 = "192.168.1.200"
    print(f"{ip1} 和 {ip2} 是否同一子网: {NetUtil.is_same_network(ip1, ip2, netmask)}")