import asyncio
from arptool.scan import live_host_scan

async def main():
    result = await live_host_scan("192.168.140.0/24", "ens33", 3)
    print(result)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
