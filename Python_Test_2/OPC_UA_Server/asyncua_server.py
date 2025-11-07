import os
import json
import asyncio

from pathlib import Path

from asyncua import Server
from .asyncua_nodes import OPCUANodes

class OPCUAServer:

    def __init__(
            self, 
            _server_name: str = "OPC-UA-Server", 
            _endpoint: str = "opc.tcp://0.0.0.0:4840/freeopcua/server/",
            _namespaces_json: list = [],
            _node_jsons: list = [],
            _nodes: OPCUANodes = None,
            _server_config_path: str = "server_config_files",
            _server_config_file: str = "server_config.json",
            _use_config_file: bool = None
        ) -> None:
        """ Initialize the OPC UA server with given parameters or configuration file. """
        self.server_name: str = _server_name    # Server name
        self.endpoint: str = _endpoint          # Server endpoint URL
        self.namespaces_json: list = _namespaces_json  # List of namespace configuration JSON
        self.node_jsons: list = _node_jsons     # List of node configuration JSON files
        self.nodes: OPCUANodes = _nodes        # OPC UA Nodes container
        self.server_config_path: str = _server_config_path  # Path to server configuration files
        self.server_config_file: str = _server_config_file  # Server configuration file name
        self.use_config_file: bool = _use_config_file   # Whether to use configuration file or preconfigured parameters

        if self.use_config_file == True:
            with open(os.path.join(Path(__file__).parent, self.server_config_path, self.server_config_file), 'r') as config_file:
                config_data = json.load(config_file)
                self.server_name = config_data.get("server_name", self.server_name)
                self.endpoint = config_data.get("endpoint", self.endpoint)
                self.namespaces_json = config_data.get("namespaces", self.namespaces_json)
                self.node_jsons = config_data.get("nodes", self.node_jsons)
        
        self._running: bool = False #Server running state
        self.server: Server | None = None   #OPC UA Server instance
        self._server_task: asyncio.Task | None = None  # Background server task
    

    
    async def setup_server(self) -> int:
        """ Initialize the OPC UA server instance. """
        self.server = Server()
        await self.server.init()
        self.server.set_endpoint(self.endpoint)
        self.server.set_server_name(self.server_name)
        print(f"OPC UA Server initialized at {self.endpoint} with name {self.server_name}")

        return 1
    
    async def start_server(self) -> int:
        """ Start the OPC UA server. """
        if self.server is None:
            print("Server not initialized. Call setup_server first.")
            return 0
        elif self._running:
            print("Server already running")
            return 0
        
        print(f"Starting server at {self.endpoint}")
        await self.server.start()
        self._running = True
        #print("Server is running")
        return 1

    async def stop_server(self) -> int:
        """ Stop the OPC UA server. """
        if self.server is None or not self._running:
            print("Server wasn´t running or initialized")
            return 0

        self._running = False  # exit the server loop
        #print("Stopping server...")
        await self.server.stop()
        #print("Server stopped")
        return 1
    
    async def add_device(self, _device_name : str = None) -> int:
        """ Set up the address space of the OPC UA server. """
        if self.server is None:
            print("Server not initialized. Call setup_server first.")
            return 0
        elif not self._running:
            print("Cannot set up address space while server is not running.")
            return 0
        
        #print("Address space set up.")
        return 1
    
    async def setup_nodes(self) -> int:
        """ Set up the OPC UA nodes in the server based on the provided node JSON configurations. """
        if self.nodes is not None:
            print ("Nodes already set up.")
            return 0
        elif self.namespaces_json == [] or self.node_jsons == []:
            print("No namespaces or node configurations provided.")
            return 0
        else:
            self.nodes = OPCUANodes(_server = self.server, _namesspaces_json = self.namespaces_json, _nodes_json = self.node_jsons)
            self.nodes.initialize_nodes()
            self.nodes.initialize_namespaces()
            await self.nodes.add_nodes()
            self.nodes.create_node_tree()