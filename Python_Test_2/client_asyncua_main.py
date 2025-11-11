import asyncio
from asyncua import Client, ua
from OPC_UA_Client import OPCUAClient

async def main():
    
    # Create a OPCUAClient instance
    useSetupClientFile = True 
    opc_ua_client = OPCUAClient(_use_config_file = useSetupClientFile)

    await opc_ua_client.start_Client()

    clock = opc_ua_client.get_node(_browse_name= "Time1", _namespace_index= 2, _identifier= 2)
    
    print(await opc_ua_client.get_value(_node= clock))
    await opc_ua_client.set_value(_node= clock, _value= "12:00")
    print(await opc_ua_client.get_value(_node= clock))

if __name__ == "__main__":
    asyncio.run(main())