import asyncio
from asyncua import Client, ua

async def main():
    url = "opc.tcp://192.168.50.52:4840/freeopcua/server/"
    async with Client(url=url) as client:
        print(f"Connected to {url}")
        
        var = client.get_node("ns=2;i=2")
        access_level = await var.read_attribute(ua.AttributeIds.UserAccessLevel)
        print("Raw AccessLevel bitmask:", access_level)
        
        i = 0
        while True:
            i += 1
            value = await var.read_value()
            print(f"Temperature is = {value}")
            print(f"Set temperature to {i}")
            await var.write_value(i)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
