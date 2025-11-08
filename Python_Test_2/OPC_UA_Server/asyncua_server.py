import os
import json
import asyncio
import logging

from pathlib import Path
from datetime import datetime

from asyncua import Server
from .asyncua_node_container import OPCUANodeContainer

class OPCUAServer:

    def __init__(
            self,
            _server_name: str = "OPC-UA-Server", 
            _endpoint: str = "opc.tcp://0.0.0.0:4840/freeopcua/server/",
            _namespace_jsons: list = [],
            _node_jsons: list = [],
            _node_container: OPCUANodeContainer = None,
            _server_config_path: str = "server_config_files",
            _server_config_file: str = "server_config.json",
            _use_config_file: bool = None,
            _logger_path: str = None,
        ) -> None:
        """ Initialise OPC UA server class with given parameters or configuration file. """

        """
            Attributes:                 
                self                    obj                     self          
                _server_name            str                     server name
                _endpoint               str                     holds endpoint string
                _namespace_jsons        list                    contains namespace jsons
                _node_jsons             list                    contians node jsons
                _nodes                  OPCUANodeContainer      container for node local objects
                _server_config_path     str                     path to the config file
                _server_config_file     str                     name of the config file
                _use_config_file        bool                    if Ture use a config file for the server
                _logger_path            str                     path to log file folder
            
            Return value:
                None 
        """

        self.server_name: str = _server_name                        # Server name
        self.endpoint: str = _endpoint                              # Server endpoint URL
        self.namespace_jsons: list = _namespace_jsons               # List of namespace configuration json
        self.node_jsons: list = _node_jsons                         # List of node configuration json files
        self.node_container: OPCUANodeContainer = _node_container   # OPC UA nodes container
        self.server_config_path: str = _server_config_path          # Path to server configuration files
        self.server_config_file: str = _server_config_file          # Server configuration file name
        self.use_config_file: bool = _use_config_file               # Whether to use configuration file or preconfigured parameters
        self.module_path = Path(__file__).parent                    # Get module path

        
        # Logger Path
        self.logger_path = _logger_path
        if self.logger_path is None:
            self.logger_path = os.path.join(self.module_path, "logs")   # Default logger path
        
        # Logger file
        self.logger = logging.getLogger("Server_logger")    # Logger
        os.makedirs(self.logger_path, exist_ok=True)
        self.current_logger_file = (os.path.join(self.logger_path, f"server_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"))
        
        # Server logger
        self.logger = logging.getLogger("main_logger")  # Server logger
        self.logger.setLevel(logging.DEBUG)             # Logger level
        self.logger.propagate = False                   # Block other loggers
        logging.getLogger().disabled = True             # Block other loggers

        # File handler
        self.file_handler = logging.FileHandler(self.current_logger_file)
        self.file_handler.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)        

        # Server setting
        if self.use_config_file == True:
            with open(os.path.join(self.module_path, self.server_config_path, self.server_config_file), 'r') as config_file:
                config_data = json.load(config_file)
                self.server_name = config_data.get("server_name", self.server_name)             # Get server name
                self.endpoint = config_data.get("endpoint", self.endpoint)                      # Get endpoint
                self.namespace_jsons = config_data.get("namespaces", self.namespace_jsons)      # Get namespaces json
                self.node_jsons = config_data.get("nodes", self.node_jsons)                     # Get nodes json
        
        self._running: bool = False                     # Server running state
        self.server: Server | None = None               # OPC UA Server instance
        self._server_task: asyncio.Task | None = None   # Background server task

        self.logger.info("-------------------- OPC-UA server class is created --------------------")

    async def autostart(self) -> int:
        """ Autostart and initialis OPC-UA server """

        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """

        # Check if server exists:
        if not self.server:
            self.logger.info("OPC-UA server is created by autostart ...")
            await self.init_server()
        
        # Check if server is running:
        if not self._running:
            self.logger.info("OPC-UA server is started by autostart ...")
            await self.start_server()

        # Check if node container is initialised
        if not self.node_container:
            self.logger.info("OPC-UA nodes are created by autostart ...")
            await self.init_node_container()
            self.load_namespaces_and_nodes_to_container()


        self.logger.info("-------------------- OPC-UA server has autostarted --------------------")
        return 1

    async def init_server(self) -> int:
        """ Initialise OPC UA server instance. """
        
        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """

        self.server = Server()
        await self.server.init()
        self.server.set_endpoint(self.endpoint)
        self.server.set_server_name(self.server_name)

        self.logger.info("-------------------- OPC-UA server is initialised --------------------")
        return 1

    async def start_server(self) -> int:
        """ Start OPC UA server. """
        
        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """

        if self.server is None:
            self.logger.warning("Trying to start a not initialised server. Call init_server() first.")
            return -1
        elif self._running:
            self.logger.warning("Trying to start a running server. Abort starting server.")
            return -1
        
        await self.server.start()
        self._running = True
        self.logger.info("----------------------------------------------------------------------------------")
        self.logger.info("OPC UA Server started!")
        self.logger.info(f"Endpoint URL: {self.server.endpoint}")
        self.logger.info(f"Endpoint URL: {self.endpoint}")
        self.logger.info(f"Server Name: {self.server_name}")
        self.logger.info(f"Protocol: OPC UA TCP")
        self.logger.info("----------------------------------------------------------------------------------")
        self.logger.info("-------------------- OPC-UA server has started and is running --------------------")
        return 1
    
    async def stop_server(self) -> int:
        """ Stop OPC UA server. """
        
        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """

        if self.server is None or not self._running:
            self.logger.warning("Trying to stop a not running server. Abort stopping server.")
            return -1

        self._running = False 
        await self.server.stop()
        self.logger.info("-------------------- OPC-UA server stoped --------------------")
        return 1

    async def init_node_container(self) -> int:
        """ Initialise local nodes. """
        
        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """

        if self.node_container is not None :
            self.logger.warning("Trying to initialise a node container, but one is still there. Abort initialising node container.")
            return -1
        
        self.node_container = OPCUANodeContainer(_server= self.server, _namespace_jsons= self.namespace_jsons, _node_jsons= self.node_jsons, _logger= self.logger)
        self.logger.info("-------------------- OPC-UA node container initialised --------------------")
        return 1

    def load_namespaces_and_nodes_to_container(self) -> int:
        """ Initialise local nodes. """
        
        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """

        if not self.node_container:
            self.logger.warning("Trying to load namespaces and nodes to a container, but no exists. Abort adding namespaces and nodes.")
            return -1
        
        self.node_container.load_namespaces_and_nodes()
        return 1
    
































































    
    async def activate_namespaces_and_nodes_on_server(self) -> int:
        """ Activate loaded namespaces and nodes to server. """
        
        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """
        ...





































    




























   
    
    


    
    async def add_device(self, _device_name : str = None) -> int:
        """ Set up the address space of the OPC UA server. """
        if self.server is None:
            print("Server not initialised. Call setup_server first.")
            return 0
        elif not self._running:
            print("Cannot set up address space while server is not running.")
            return 0
        
        print("Address space set up.")
        return 1
    
    async def setup_nodes(self) -> int:
        """ Set up the OPC UA nodes in the server based on the provided node JSON configurations. """
        if self.nodes is not None:
            print ("Nodes already set up.")
            return 0
        elif self.namespace_jsons == [] or self.node_jsons == []:
            print("No namespaces or node configurations provided.")
            return 0
        else:
            self.nodes = OPCUANodeContainer(_server = self.server, _namesspace_jsons = self.namespace_jsons, _nodes_json = self.node_jsons)
            self.nodes.initialize_nodes()
            self.nodes.initialize_namespaces()
            await self.nodes.add_nodes()
            self.nodes.create_node_tree()












            ####
            ###
            ###
            ###
            ###



            #logger.info(f"Number of Nodes in Objects Folder: {len(server.get_objects_node().get_children())}")