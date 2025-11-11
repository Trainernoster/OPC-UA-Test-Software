import asyncio
from asyncua import Client, ua
from OPC_UA_Client import OPCUAClient
from datetime import datetime

async def main():
    
    # Create a OPCUAClient instance
    useSetupClientFile = True 
    opc_ua_client = OPCUAClient(_use_config_file = useSetupClientFile)

    await opc_ua_client.start_Client()

    clock = opc_ua_client.get_node(_browse_name= "Time1", _namespace_index= 2, _identifier= 2)
    
    # Main programm loop
    print(" Press Ctrl+C to stop the clock.")
    try:
        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await opc_ua_client.set_value(_node= clock, _value= now)
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print("Stopping clock...")

    finally:
        print("Clock stopped.")

if __name__ == "__main__":
    asyncio.run(main())