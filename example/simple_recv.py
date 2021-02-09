import asyncio

from arptool.arp import ArpRecvTask

async def main(timeout: int = 100):
    arp_recv_task = ArpRecvTask()
    arp_recv_task.start()

    await asyncio.sleep(timeout)
    arp_recv_task.cencal()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
