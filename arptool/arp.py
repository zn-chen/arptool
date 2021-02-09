"""
arp Python原始套接字实现
"""
import errno
import socket
import socket
import binascii
from enum import Enum
from re import findall
from struct import pack, unpack
from dataclasses import dataclass
from typing import Callable, Optional

from tornado.ioloop import IOLoop

BROADCAST_ADDRESS = pack('!6B', *(0xFF,) * 6)  # 广播地址
ZERO_MAC = pack('!6B', *(0x00,) * 6)  # 0地址
ARP_OP_REQUEST = pack('!H', 0x0001)  # ARP请求类型:请求
ARP_OP_REPLY = pack('!H', 0x0002)  # ARP请求类型: 通知
ARP_PROTOCOL_TYPE_ETHERNET_IP = pack(
    '!HHBB', 0x0001, 0x0800, 0x0006, 0x0004)  # ARP首部
ETHERNET_PROTOCOL_TYPE_ARP = pack('!H', 0x0806)  # 数据帧类型
ARP_PROTOCOL_TYPE = b"\x08\x06"  # ARP 协议类型


class ARP_OP(Enum):
    REQUEST = 1  # arp请求类型
    REPLY = 2  # arp相应类型


@dataclass
class EthernetFrame:
    destination: str
    source: str
    Type: int


@dataclass
class ArpPackage:
    ethernet_frame: EthernetFrame
    hardware_type: str
    protocol_type: str
    hardware_size: int
    protocol_size: int
    opcode: ARP_OP
    src_mac: str
    src_ip: str
    dst_mac: str
    dst_ip: str


def is_arp(msg: bytes) -> bool:
    """
    判断是否为arp报文
    """
    return True if len(msg) >= 42 and msg[12:12+2] == ARP_PROTOCOL_TYPE else False


def arp_master_pack(arp_package: ArpPackage) -> bytes:
    """
    由ArpPackage 打包arp数据包, 可自定义每一个字段
    """
    src_ip = pack('!4B', *[int(x)
                           for x in arp_package.src_ip.split('.')])  # 发送方IP
    src_mac = pack('!6B', *[int(x, 16)
                            for x in arp_package.src_mac.split(':')])  # 发送方mac
    dst_ip = pack('!4B', *[int(x)
                           for x in arp_package.dst_ip.split('.')])  # 目标ip
    dst_mac = pack('!6B', *[int(x, 16)
                            for x in arp_package.dst_mac.split(':')])  # 目的mac
    target_mac_ethernet = pack(
        '!6B', *[int(x, 16) for x in arp_package.ethernet_frame.destination.split(':')])  # 以太帧目标mac地址
    src_mac_ethernet = pack(
        '!6B', *[int(x, 16) for x in arp_package.ethernet_frame.source.split(':')])  # 以太帧源mac地址

    ethernet_frame_msg = pack(
        "!6s6sh", target_mac_ethernet, src_mac_ethernet, arp_package.ethernet_frame.Type)
    arp_frame_msg = pack("!2s2s1s1sH6s4s6s4s", arp_package.hardware_type, arp_package.protocol_type, arp_package.hardware_size, arp_package.protocol_size,
                         arp_package.opcode, src_mac, src_ip, dst_mac, dst_ip)


    return ethernet_frame_msg + arp_frame_msg


def arp_simple_pack(src_ip: str, src_mac: str, dst_ip: str, dst_mac: str = None, op: ARP_OP = ARP_OP.REQUEST) -> bytes:
    """
    arp报文快速打包
    """
    src_ip = pack('!4B', *[int(x)
                           for x in src_ip.split('.')])  # 发送方IP
    src_mac = pack('!6B', *[int(x, 16)
                            for x in src_mac.split(':')])  # 发送方mac
    dst_ip = pack('!4B', *[int(x)
                           for x in dst_ip.split('.')])  # 目标ip

    # 目标mac
    if dst_mac is None:
        target_mac_ethernet = BROADCAST_ADDRESS
        target_mac_arp = ZERO_MAC
    else:
        target_mac_ethernet = pack(
            '!6B', *[int(x, 16) for x in dst_mac.split(':')])
        target_mac_arp = target_mac_ethernet

    # arp报文类型
    if op == ARP_OP.REQUEST:
        op = ARP_OP_REQUEST
    else:
        op = ARP_OP_REPLY

    return b''.join([
        # Ethernet
        target_mac_ethernet,
        src_mac,
        ETHERNET_PROTOCOL_TYPE_ARP,
        # ARP
        ARP_PROTOCOL_TYPE_ETHERNET_IP,
        op,
        src_mac,
        src_ip,
        target_mac_arp,
        dst_ip,
    ])


def arp_unpack(msg: bytes) -> ArpPackage:
    """
    arp报文解包
    """
    # 解析以太帧
    ethernet_frame_msg = unpack("!6s6sh", msg[0:14])
    ethernet_frame = EthernetFrame(
        destination=bytes_turn_hex_mac(ethernet_frame_msg[0]),
        source=bytes_turn_hex_mac(ethernet_frame_msg[1]),
        Type=ethernet_frame_msg[2]
    )

    # 解析arp数据帧
    arp_frame_msg = unpack("!2s2s1s1sH6s4s6s4s", msg[14:42])
    arp_package = ArpPackage(
        ethernet_frame=ethernet_frame,
        hardware_type=bytes_turn_hex(arp_frame_msg[0]),
        protocol_type=bytes_turn_hex(arp_frame_msg[1]),
        hardware_size=bytes_turn_hex(arp_frame_msg[2]),
        protocol_size=bytes_turn_hex(arp_frame_msg[3]),
        opcode=arp_frame_msg[4],
        src_mac=bytes_turn_hex_mac(arp_frame_msg[5]),
        src_ip=socket.inet_ntoa(arp_frame_msg[6]),
        dst_mac=bytes_turn_hex_mac(arp_frame_msg[7]),
        dst_ip=socket.inet_ntoa(arp_frame_msg[8])
    )

    return arp_package


def bytes_turn_hex(data):
    return binascii.hexlify(data).decode('utf-8')


def bytes_turn_hex_mac(data):
    return ':'.join(findall(r'.{2}', bytes_turn_hex(data)))


def send_simple_arp(raw_socket: socket.socket, src_ip: str, src_mac: str, dst_ip: str, dst_mac="ff:ff:ff:ff:ff:ff", op: ARP_OP = ARP_OP.REQUEST):
    """
    发送一个ARP包
    """
    arp_package = arp_simple_pack(
        src_ip=src_ip,
        src_mac=src_mac,
        dst_ip=dst_ip,
        dst_mac=dst_mac,
    )
    raw_socket.send(arp_package)


class ArpRecvTask:
    """
    Arp接收处理任务
    """

    def __init__(self, raw_socket: Optional[socket.socket] = None, callback: Optional[Callable[[bytes, int], None]] = None,
                 loop: Optional[IOLoop] = None) -> None:
        self._raw_socket = raw_socket or create_noblock_raw_socket()
        self._callback = callback or self._example_callback
        self._loop = loop or IOLoop.instance()
        self._is_close = True

    def start(self):
        """
        开始接收arp数据包并交由回调函数处理
        """
        if not self._is_close:
            return
        self._is_close = False
        self._loop.add_handler(self._raw_socket.fileno(),
                               self._accept_handler, IOLoop.READ)

    def cencal(self):
        """
        取消接收任务
        """
        if self._is_close:
            return
        self._is_close = True
        self._loop.remove_handler(self._raw_socket.fileno())

    def _accept_handler(self, fd, events):
        while not self._is_close:
            try:
                msg = self._raw_socket.recvfrom(2048)[0]
            except socket.error as e:
                if e.args[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    return
                raise
            if is_arp(msg):
                self._callback(msg, fd)

    @staticmethod
    def _example_callback(msg: bytes, _):
        """
        演示用的回调callback, 用于打印收到的arp报文
        """
        arp_package = arp_unpack(msg)
        print(arp_package)

    def __del__(self):
        self.cencal()


def create_noblock_raw_socket(net_interface: str = None, htons=0x0003) -> socket.socket:
    """
    创建一个非阻塞的原始套接字
    """
    raw_socket = socket.socket(
        socket.AF_PACKET,
        socket.SOCK_RAW,
        socket.htons(htons),
    )
    raw_socket.setblocking(0)
    if net_interface:
        raw_socket.bind((net_interface, socket.SOCK_RAW))
    return raw_socket
