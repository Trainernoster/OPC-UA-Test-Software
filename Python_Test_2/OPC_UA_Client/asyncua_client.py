import asyncio
from asyncua import Client

class OPCUAClient:
    
    def __init__(
            self, 
            _server_name: str = "OPC-UA-Server", 
            _endpoint: str = "opc.tcp://0.0.0.0:4840/freeopcua/server/",
        ) -> None:
        """ Initialize the OPC UA server with given parameters or configuration file. """
        self.server_name: str = _server_name    # Server name
        self.endpoint: str = _endpoint          # Server endpoint URL
    
    async def start_Client(self):
        self.client = Client(self.endpoint)

    async def get_First_Value(self):
        node_id = "ns=2;i=1004"
        pressure_node = self.client.get_node(node_id)

        return await pressure_node.read_value()