
import netifaces
from typing import Tuple

from arptool.errors import NetInterfaceNotExistException, UnableGetIPException, UnableGetMacException


def get_ip_mac(ifname: str) -> Tuple[str, str]:
    """
    获取网卡ip地址与mac地址
    """
    if ifname not in netifaces.interfaces():
        raise NetInterfaceNotExistException()

    infos = netifaces.ifaddresses(ifname)

    if not infos.get(netifaces.AF_PACKET):
        raise UnableGetMacException("%s not AF_PACKET" % ifname)

    if not infos.get(netifaces.AF_INET):
        raise UnableGetIPException("%s not AF_INET" % ifname)

    return infos[netifaces.AF_INET][0].get("addr"), infos[netifaces.AF_PACKET][0].get("addr")
