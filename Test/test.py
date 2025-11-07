import asyncio
from asyncua import Client

async def main():
    url = "opc.tcp://192.168.50.52:4840/freeopcua/server/"
    
    async with Client(url) as client:
        client.set_security_string("None")


asyncio.run(main())
