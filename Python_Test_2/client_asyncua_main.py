import asyncio
from OPC_UA_Client import OPCUAClient

async def main():
    opc_ua_client = OPCUAClient()
    await opc_ua_client.start_Client()
    print(await opc_ua_client.get_First_Value())

if __name__ == "__main__":
    """ Run the main function. """
    asyncio.run(main())