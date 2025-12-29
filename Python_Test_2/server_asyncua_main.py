import asyncio
import argparse

##
## Import Functions
##
from functions import get_choice_YesNo, get_choices, get_choices_TureFalse

##
## Import Server
##
from OPC_UA_Server import OPCUAServer
from Lib.dependencytree import dependencytree


### paser
parser = argparse.ArgumentParser(description="Server control")
parser.add_argument(
    "--build",
    choices=["xml", "json"],
    required=False,
    default="json",
    help="Build mode for server")
parser.add_argument(
    "--export",
    required=False,
    action="store_true",
    help="Export flag to create xml file of current server")
parser.add_argument(
    "--tree",
    required=False,
    action="store_true",
    help="Tree flag print node tree of current server")
args = parser.parse_args()

async def main():
    """ Main function to run the OPC UA server. """

    # Create a OPCUAServer instance
    useSetupServerFile = True 
    opc_ua_server = OPCUAServer(_use_config_file = useSetupServerFile)    

    # Autostart the server
    await opc_ua_server.autostart(source= args.build)
    print("Server started.")

    # Print the node tree that is active in the server
    if args.tree:
        node_tree = opc_ua_server.get_server_node_tree()
        dependencytree.dependencytree_print(_tree= node_tree["node_tree"], _object_names= node_tree["server_node_information"], _add_names= True, _names_only= True)

    # Export current server model
    if args.export:
        await opc_ua_server.export_server_model()

    # Main programm loop
    print("Press Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(10)

    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print("Stopping server...")

    finally:
        await opc_ua_server.stop_server()
        print("Server stopped.")
    

if __name__ == "__main__":
    """ Run the main function. """
    asyncio.run(main())