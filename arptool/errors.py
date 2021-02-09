class UnableGetIPException(Exception):
    """
    无法获取ip异常
    """
    pass


class UnableGetMacException(Exception):
    """
    无法获取mac地址异常
    """
    pass

class NetInterfaceNotExistException(Exception):
    """
    指定网卡不存在异常
    """
    pass
