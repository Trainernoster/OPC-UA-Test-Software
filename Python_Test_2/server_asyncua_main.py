import asyncio

##
## Import Functions
##
from functions import get_choice_YesNo, get_choices, get_choices_TureFalse

##
## Import Server
##
from OPC_UA_Server import OPCUAServer
from Lib.dependencytree import dependencytree

async def main():
    """ Main function to run the OPC UA server. """

    useSetupServerFile = True 
    opc_ua_server = OPCUAServer(_use_config_file = useSetupServerFile)    

    # Autostart the server
    await opc_ua_server.autostart()

    mode_tree = opc_ua_server.get_server_node_tree()
    dependencytree.dependencytree_print(_tree= mode_tree["node_tree"], _object_names= mode_tree["server_node_information"], _add_names= True, _names_only= True)

    await opc_ua_server.stop_server()

    # Iniziate the OPC-UA server
    #await opc_ua_server.setup_server()
    

    #await opc_ua_server.start_server()
    #await opc_ua_server.setup_nodes()
    #await opc_ua_server.add_device()

    #while True: #not get_choices_TureFalse(_question = "Write \"s\" to stop the server.", _delete_question = True, _choices = ["s"]):
    #    await asyncio.sleep(10)

    #print(await opc_ua_server.server.get_namespace_array())
    #print(await opc_ua_server.server.get_namespace_index("http://mynodes.local"))
    #print(await opc_ua_server.server.get_namespace_index("http://mynodes.global"))
    #await opc_ua_server.stop_server()
    

if __name__ == "__main__":
    """ Run the main function. """
    asyncio.run(main())