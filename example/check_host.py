import asyncio
from arptool.scan import live_host_check

async def main():
    result = await live_host_check("192.168.140.1", "ens33")
    print(result)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
