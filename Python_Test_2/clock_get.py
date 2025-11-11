import asyncio
import sys
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
            now = await opc_ua_client.get_value(_node= clock)
            print("The current date and time is:")
            print(now)
            await asyncio.sleep(1)
            sys.stdout.write("\033[F\033[K")  # Move up 1 line + clear line
            sys.stdout.write("\033[F\033[K")  # Move up 1 more line + clear line
            sys.stdout.flush()

    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print("Stopping clock...")

    finally:
        print("Clock stopped.")

if __name__ == "__main__":
    asyncio.run(main())