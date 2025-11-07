import asyncio

##
## Import Functions
##
from functions import get_choice_YesNo, get_choices, get_choices_TureFalse

##
## Import Server
##
from OPC_UA_Server import OPCUAServer

async def main():
    """ Main function to run the OPC UA server. """

    useSetupServerFile = True #get_choice_YesNo(_question = "Use server configuration file?", _delete_question = True)
    opc_ua_server = OPCUAServer(_use_config_file = useSetupServerFile)    

    await opc_ua_server.setup_server()
    

    await opc_ua_server.start_server()
    await opc_ua_server.setup_nodes()
    #await opc_ua_server.add_device()

    while True: #not get_choices_TureFalse(_question = "Write \"s\" to stop the server.", _delete_question = True, _choices = ["s"]):
        ...

    print(await opc_ua_server.server.get_namespace_array())
    print(await opc_ua_server.server.get_namespace_index("http://mynodes.local"))
    print(await opc_ua_server.server.get_namespace_index("http://mynodes.global"))
    await opc_ua_server.stop_server()
    

if __name__ == "__main__":
    """ Run the main function. """
    asyncio.run(main())