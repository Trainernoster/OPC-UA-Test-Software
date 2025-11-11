import asyncio
import os
import json

from pathlib import Path
from asyncua import Client

class OPCUAClient:
    """
    Asynchronous OPC UA client for connecting to and interacting with an OPC UA server.

    This class handles connection management, node discovery (by browse name or node ID),
    value reading/writing, and optional configuration loading from JSON files.
    """
    
    def __init__(
            self,
            _endpoint: str = "opc.tcp://192.168.50.52:4840/freeopcua/server/",
            _client_config_path: str = "client_config_files",
            _client_config_file: str = "client_config.json",
            _use_config_file: bool = None
        ) -> None:
        """
        Initialize the OPC UA client with optional configuration file.

        Args:
            _endpoint: The OPC UA client endpoint URL.
            _client_config_path: Directory where configuration files are stored.
            _client_config_file: JSON file name containing client configuration.
            _use_config_file: If True, load configuration from file instead of arguments.
        """
        # Core configuration
        self.endpoint = _endpoint
        self.client_config_path = _client_config_path
        self.client_config_file = _client_config_file
        self.use_config_file = _use_config_file
        self.module_path = Path(__file__).parent                    # Get module path

        # Node tracking
        self.loadable_nodes: list = []      # Nodes defined in config file
        self.loaded_nodes: list = []        # Nodes successfully connected to
        self.objects = None                 # Root 'Objects' node reference
        self.client: Client | None = None   # asyncua Client instance

        # Load from configuration file if enabled
        if self.use_config_file:
            config_path = os.path.join(self.module_path, self.client_config_path, self.client_config_file)
            with open(config_path, "r") as config_file:
                config_data = json.load(config_file)
                self.endpoint = config_data.get("endpoint", self.endpoint)                      # Get endpoint
                self.loadable_nodes = config_data.get("loadable_nodes", [])

    # ---------------------------------------------------------------------- #
    # Connection management
    # ---------------------------------------------------------------------- #
    
    async def start_Client(self):
        """
        Connect to the OPC UA server and automatically load predefined nodes.

        Returns:
            None
        """
        self.client = Client(self.endpoint)
        await self.client.connect()
        self.objects = self.client.nodes.objects
        if self.loadable_nodes is not None:
            i = 1
            for loadable_node in self.loadable_nodes:
                await self.add_node(_browse_name = loadable_node.get("browseName"), _identifier = loadable_node.get("i") , _namespace_index = loadable_node.get("i"))

    # ---------------------------------------------------------------------- #
    # Node handling
    # ---------------------------------------------------------------------- #

    async def add_node(
        self,
        _browse_name: str = None,
        _namespace_index: int = None,
        _identifier: int = None
    ) -> int:
        """
        Add a node reference to the client, by either browse name or node ID.

        Args:
            _browse_name: The browse name of the target node.
            _namespace_index: Namespace index of the node.
            _identifier: Node identifier (numeric).

        Returns:
            int: 1 if node found and added, -1 otherwise.
        """

        async def find_node_by_name(_parent_node, _name_to_find):
            """
            Recursively search for a node by its browse name.

            Args:
                _parent_node: Parent node to search under.
                _name_to_find: Target browse name.

            Returns:
                Node object if found, else None.
            """
            children = await _parent_node.get_children()
            for child in children:
                bname = await child.read_browse_name()
                if bname.Name == _name_to_find:
                    return child
                result = await find_node_by_name(child, _name_to_find)
                if result is not None:
                    return result
            return None

        async def get_node_by_id(_ns: int, _i: int):
            """
            Retrieve a node directly by its NodeId (namespace + identifier).

            Args:
                _ns: Namespace index.
                _i: Identifier.

            Returns:
                Node object.
            """
            node_id_str = f"ns={_ns};i={_i}"
            return self.client.get_node(node_id_str)
        
        # ------------------------------------------------------------------ #
        # Main logic for adding node
        # ------------------------------------------------------------------ #
        
        if self.client is None:
            print("Client not connected.")
            return -1
        
        node = None
        if _browse_name is not None:
            node = await find_node_by_name(_parent_node= self.objects, _name_to_find= _browse_name)
        elif _namespace_index is not None and _identifier is not None:
            node = await get_node_by_id(_ns= _namespace_index, _i= _identifier)
        else:
            print("Invalid node information provided.")
            return -1
        
        if node:
            bname = await node.read_browse_name()
            #print(f"found node, browsename: {bname.Name}, namesapce: {node.nodeid.NamespaceIndex}, identifier: {node.nodeid.Identifier}")
            self.loaded_nodes.append(
                [bname.Name, node.nodeid.NamespaceIndex, node.nodeid.Identifier, node]
            )
            return 1
        else:
            print(
                f"Node not found: browseName='{_browse_name}', "
                f"namespace={_namespace_index}, identifier={_identifier}"
            )
            return -1
    
    def get_node(
        self,
        _browse_name: str = None,
        _namespace_index: int = None,
        _identifier: int = None
    ) -> object:
        """
        Retrieve a previously loaded node by browse name or node ID.

        Args:
            _browse_name: Node browse name.
            _namespace_index: Namespace index.
            _identifier: Node identifier.

        Returns:
            Node object if found, else -1.
        """
        if self.loaded_nodes == []:
            print("No nodes have been loaded.")
            return -1
        for node in self.loaded_nodes:
            if _browse_name == node[0]:
                return node[3]
            elif _namespace_index == node[1] and _identifier == node[2]:
                return node[3]
        print("No loaded node found matching given parameters.")
        return -1

    # ---------------------------------------------------------------------- #
    # Node value operations
    # ---------------------------------------------------------------------- #

    async def get_value(self, _node) -> object:
        """
        Read the current value from a given OPC UA node.

        Args:
            _node: Target node object.

        Returns:
            The current node value, or None if reading fails.
        """
        try:
            return await _node.read_value()
        except Exception as e:
            print(f"Get value not possible: {e}")
            return None

    async def set_value(self, _node, _value) -> object:
        """
        Write a value to an OPC UA node after verifying type compatibility.

        Args:
            _node: Target node object.
            _value: New value to write.

        Returns:
            int: 1 if successful, -1 on type mismatch or error.
        """
        try:
            current_value = await _node.read_value()
            if not isinstance(_value, type(current_value)):
                print(
                    f"Type mismatch: Node expects {type(current_value).__name__}, "
                    f"but got {type(_value).__name__}"
                )
                return -1
            await _node.write_value(_value)
            return 1
        except Exception as e:
            print(f"Unable to write value to node: {e}")
            return -1