from typing import List, Optional, Tuple
from asyncio import sleep, Future, wait_for, TimeoutError

from IPy import IP

from arptool.util import get_ip_mac
from arptool.arp import ARP_OP, ArpRecvTask, arp_unpack, send_simple_arp, create_noblock_raw_socket


async def live_host_scan(network_segment: str, net_interface: Optional[str], timeout: int = 10) -> List[Tuple[str, str]]:
    """
    扫描指定网段中的存活主机
    """
    scan_result = set()
    self_ip, self_mac = get_ip_mac(net_interface)
    sock = create_noblock_raw_socket(net_interface)

    def set_result_callback(msg, _):
        """
        replay包接收处理回调
        """
        arp_package = arp_unpack(msg)
        if arp_package.opcode == ARP_OP.REQUEST:
            return
        scan_result.add((arp_package.src_ip, arp_package.src_mac))

    recv_task = ArpRecvTask(raw_socket=sock, callback=set_result_callback)
    recv_task.start()

    for ip in IP(network_segment):
        send_simple_arp(
            raw_socket=sock,
            src_ip=self_ip,
            src_mac=self_mac,
            dst_ip=ip.__str__(),
        )

    await sleep(timeout)
    recv_task.cencal()
    return list(scan_result)


async def live_host_check(host_ip: str, net_interface: Optional[str], timeout: int = 3, request_num: int = 3):
    """
    探测指定ip是否存活, 如果在timeout时间内确认arp回复则立即返回, 超时返回None
    """
    future = Future()
    self_ip, self_mac = get_ip_mac(net_interface)
    sock = create_noblock_raw_socket(net_interface)

    def set_result_callback(msg, _):
        """
        replay包接收处理回调
        """
        arp_package = arp_unpack(msg)
        if arp_package.opcode == ARP_OP.REQUEST or arp_package.src_ip != host_ip:
            return
        if not future.done():
            future.set_result((arp_package.src_ip, arp_package.src_mac))

    recv_task = ArpRecvTask(raw_socket=sock, callback=set_result_callback)
    recv_task.start()

    for _ in range(request_num):
        send_simple_arp(
            raw_socket=sock,
            src_ip=self_ip,
            src_mac=self_mac,
            dst_ip=host_ip,
        )

    try:
        result = await wait_for(future, timeout)
    except TimeoutError:
        result = None
    recv_task.cencal()
    return result
