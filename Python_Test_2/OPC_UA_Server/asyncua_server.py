import os
import json
import asyncio
import logging

from pathlib import Path
from datetime import datetime

from asyncua import Server
from .asyncua_node_container import OPCUANodeContainer

class OPCUAServer:
    """
    Asynchronous OPC UA server wrapper.

    Provides configuration-driven initialization, namespace and node activation,
    and lifecycle management (start/stop/autostart) for an asyncua-based OPC UA server.
    """

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
        """
        Initialize the OPC UA server object.

        Args:
            _server_name: Human-readable server name.
            _endpoint: Endpoint URL (opc.tcp://host:port/…).
            _namespace_jsons: Optional list of namespace configuration JSONs.
            _node_jsons: Optional list of node configuration JSONs.
            _node_container: Existing node container, if already created.
            _server_config_path: Directory containing configuration files.
            _server_config_file: Configuration file name.
            _use_config_file: If True, load settings from the config file.
            _logger_path: Path to store log files.

        Returns:
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

        # ------------------------------------------------------------------ #
        # Logging setup
        # ------------------------------------------------------------------ #        
        # Logger Path
        self.logger_path = _logger_path
        if self.logger_path is None:
            self.logger_path = os.path.join(self.module_path, "logs")   # Default logger path
        
        # Logger file
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
    # ---------------------------------------------------------------------- #
    # Lifecycle management
    # ---------------------------------------------------------------------- #

    async def autostart(self) -> int:
        """
        Automatically initialize, start, and populate the OPC UA server.

        Steps:
            1. Initialize the server if not already done.
            2. Start the server.
            3. Create a node container if missing.
            4. Load and activate namespaces and nodes.

        Returns:
            int
        """
        # Check if server exists:
        if not self.server:
            await self.init_server()
            self.logger.info("OPC-UA server was created by autostart ...")
        
        # Check if server is running:
        if not self._running:
            await self.start_server()
            self.logger.info("OPC-UA server was started by autostart ...")
        
        # Check if node container is initialised
        if not self.node_container:
            self.logger.info("OPC-UA nodes are created by autostart ...")
            await self.init_node_container()
            self.load_namespaces_and_nodes_to_container()
            await self.activate_namespaces_and_nodes_on_server()
        

        self.logger.info("-------------------- OPC-UA server has autostarted --------------------")
        return 1

    async def init_server(self) -> int:
        """
        Create and configure the underlying asyncua.Server instance.

        Returns:
            int
        """

        self.server = Server()
        await self.server.init()
        self.server.set_endpoint(self.endpoint)
        self.server.set_server_name(self.server_name)

        self.logger.info("-------------------- OPC-UA server is initialised --------------------")
        return 1

    async def start_server(self) -> int:
        """
        Start the OPC UA server asynchronously.

        Returns:
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
        """
        Stop the OPC UA server and release resources.

        Returns:
            int
        """
        if self.server is None or not self._running:
            self.logger.warning("Trying to stop a not running server. Abort stopping server.")
            return -1

        self._running = False 
        await self.server.stop()
        self.logger.info("-------------------- OPC-UA server stoped --------------------")
        return 1
    
    # ---------------------------------------------------------------------- #
    # Node management
    # ---------------------------------------------------------------------- #

    async def init_node_container(self) -> int:
        """
        Create a local node container bound to this server.

        Returns:
            int
        """

        if self.node_container is not None :
            self.logger.warning("Trying to initialise a node container, but one is still there. Abort initialising node container.")
            return -1
        
        self.node_container = OPCUANodeContainer(
            _server= self.server,
            _namespace_jsons= self.namespace_jsons,
            _node_jsons= self.node_jsons,
            _logger= self.logger,
            _logger_active= True
        )
        self.logger.info("-------------------- OPC-UA node container initialised --------------------")
        return 1

    def load_namespaces_and_nodes_to_container(self) -> int:
        """
        Load namespace and node definitions into the node container.

        Returns:
            int
        """
        if not self.node_container:
            self.logger.warning("Trying to load namespaces and nodes to a container, but no exists. Abort adding namespaces and nodes.")
            return -1
        
        self.node_container.load_namespaces_and_nodes()
        return 1
 
    async def activate_namespaces_and_nodes_on_server(self) -> int:
        """
        Register all namespaces and nodes with the running server.

        Returns:
            int
        """
        if not self.node_container:
            self.logger.warning("Trying to activate namespaces and nodes on server, but no container exists. Abort activating namespaces and nodes.")
            return -1
        
        await self.node_container.activate_namespaces()
        await self.node_container.activate_nodes()
        return 1

    def get_server_node_tree(self) -> dict:
        """
        Return the current server node tree from the container.

        Returns:
            dict: Hierarchical node information.
        """
        return self.node_container.get_node_tree()
    
    async def export_server_model(self, savefile_path: str = None, export_values: bool = False) -> int:
        """
        Export the current OPC UA server model (all nodes) to an XML file.

        Args:
            savefile_path: File to write the XML model.
            export_values: If True, include variable values in exported XML.

        Returns:
            1 on success, -1 on failure.
        """
        if not self.server or not self._running:
            self.logger.error("Server is not running, cannot export model.")
            return -1

        nodes_to_export = []

        async def collect_nodes(node, visited=None):
            if visited is None:
                visited = set()

            nodeid = node.nodeid.to_string()
            if nodeid in visited:
                return
            visited.add(nodeid)

            nodes_to_export.append(node)

            try:
                children = await node.get_children()
                for child in children:
                    await collect_nodes(child, visited)
            except Exception as e:
                self.logger.debug(f"Error browsing {nodeid}: {e}")

        await collect_nodes(self.server.nodes.objects)

        try:
            if savefile_path == None:
                designmodel_folder = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "DesignModel"
                )
                os.makedirs(designmodel_folder, exist_ok=True)
                savefile_path = os.path.join(
                    designmodel_folder,
                    "Server_DesignModel.xml"
                )
            await self.server.export_xml(nodes_to_export, savefile_path, export_values)
            self.logger.info(f"Server model exported to {savefile_path}")
            return 1
        except Exception as e:
            self.logger.error(f"Failed to export server model: {e}")
            return -1
