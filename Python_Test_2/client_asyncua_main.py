import asyncio
from asyncua import Client

async def main():
    url = "opc.tcp://192.168.50.52:4840/freeopcua/server/"
    async with Client(url=url) as client:
        print(f"Connected to {url}")
        
        # Get the node we want to read
        var = client.get_node("ns=3;i=1")
        
        i = 1
        while True:
            i += 1
            value = await var.read_value()
            print(f"Read MyVariable = {value}")
            await var.write_value(i)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
