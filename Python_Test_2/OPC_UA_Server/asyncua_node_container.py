import logging
from asyncua import ua
import OPC_UA_Server
from .opc_ua_node import OPCUANode
from .opc_ua_namespace import OPCUANamespace

class OPCUANodeContainer:
    """
    Container class for managing OPC UA nodes and namespaces in an OPC UA server.
    
    Responsibilities:
        - Load namespaces and nodes from JSON definitions.
        - Activate namespaces on the OPC UA server.
        - Activate nodes under the server's Objects node hierarchy.
        - Maintain internal tree structures for nodes for easy reference.
        - Log relevant messages during initialization and activation.
    """
    
    def __init__(
            self,
            _server: OPC_UA_Server,
            _namespace_jsons: list,
            _node_jsons: list,
            _logger: logging = None,
            _logger_active: bool = True
        ) -> None:
        """
        Initialize the OPC UA Node Container.

        Args:
            _server (OPC_UA_Server): The OPC UA server instance.
            _namespace_jsons (list): List of namespace JSON definitions.
            _node_jsons (list): List of node JSON definitions.
            _logger (logging, optional): Logger instance from server.
            _logger_active (bool, optional): Enable or disable logging.

        Attributes:
            self.server (OPC_UA_Server): OPC UA server instance.
            self.namespace_jsons (list): JSONs for namespaces.
            self.node_jsons (list): JSONs for nodes.
            self.logger (logging): Logger object.
            self.logger_active (bool): Flag to enable logging.
            self.namespaces (list[OPCUANamespace]): List of OPCUANamespace objects.
            self.nodes (list[OPCUANode]): List of OPCUANode objects.
            self.objects_node (Node): Server Objects node reference.
            self.objects_node_information (dict): Namespace index and identifier of Objects node.
            self.node_tree (list): Hierarchical tree of node ids.
            self.node_names (list): Node names for reference.
            self.node_children (list): Node children info (future use).
            self.server_node_tree (list): Tree structure of activated nodes on server.
            self.server_node_information (list): Info about nodes on server.
            self.server_node_names (list): Node names on server.
            self.known_objects (list): Known OPC UA node classes ("Object", "Variable", "Methode").
        """
        self.server: OPC_UA_Server = _server    # OPC UA Server instanze
        self.namespace_jsons = _namespace_jsons # namespace jsons
        self.node_jsons = _node_jsons           # node jsons
        self.logger = _logger                   # logger from server
        self.logger_active = _logger_active     # activate logger

        self.namespaces: list[OPCUANamespace] = []                      # namespace container
        self.nodes: list[OPCUANode] = []                                # nodes container
        self.objects_node: bool = None                                  # server node Objects
        self.objects_node_information: list  = {"ns": None, "i": None}  # namespace index and identifier from objects node
        self.node_tree: list = []                                       # node tree
        self.node_names: list = []                                      # node names
        self.node_children: list = []                                   # node children

        self.server_node_tree: list = []
        self.server_node_information: list = []
        self.server_node_names: list = []

        self.known_objects = ["Object", "Variable", "Methode"]  # all known node classes

    def log_message(self, _message: str, _type: str = None) -> None:
        """
        Log messages using the configured logger.

        Args:
            _message (str): Message string to log.
            _type (str, optional): Type of log: "info", "warning", "error", "critical".

        Returns:
            int: 1 if message logged, -1 if logger inactive.
        """
        if self.logger is not None and self.logger_active:
            if _type is None or _type == "info":
                self.logger.info("From OPCUANodeContainer: " + _message)
            elif _type == "warning":
                self.logger.warning("From OPCUANodeContainer: " + _message)
            elif _type == "error":
                self.logger.error("From OPCUANodeContainer: " + _message)
            elif _type == "critical":
                self.logger.critical("From OPCUANodeContainer: " + _message)
            else:
                self.logger.critical("From OPCUANodeContainer: " + _message)
            return 1
        return -1
    
    def load_namespaces_and_nodes(self) -> int:
        """
        Load namespaces and nodes from the provided JSONs.

        Returns:
            int: 1 if successfully loaded, -1 if errors occurred.
        """
        self.initialise_namespaces()
        self.initialise_nodes()
        self.log_message("Namespaces and nodes are initialised")
        return 1
    
    def initialise_namespaces(self) -> int:
        """
        Create OPCUANamespace objects from namespace JSON definitions.

        Returns:
            int: 1 if successful, -1 if no namespace JSONs found.
        """
        if not self.namespace_jsons:
            self.log_message("No namespace jsons are found. Abort initialise namespaces.", "warning")
            return -1
        for namespace_json in self.namespace_jsons:
            opcua_namespace = OPCUANamespace(_namespace_json= namespace_json)
            self.namespaces.append(opcua_namespace)
        return 1
    
    def initialise_nodes(self) -> int:
        """
        Create OPCUANode objects from node JSON definitions.

        Returns:
            int: 1 if successful, -1 if no node JSONs found.
        """
        if not self.node_jsons:
            self.log_message("No node jsons are found. Abort initialise nodes.", "warning")
            return -1
        for node_json in self.node_jsons:
            opcua_node = OPCUANode(_node_json= node_json)
            self.nodes.append(opcua_node)
        return 1

    async def activate_namespaces(self)  -> int:
        """
        Register and activate namespaces on the OPC UA server.

        Returns:
            int: 1 if successful, -1 if no namespaces initialized.
        """
        if not self.namespaces:
            self.log_message("Trying to activate namespaces, but no namespaces are initialised. Abort activating namespaces.", "warning")
            return -1
        for namespace in self.namespaces:
            try:
                idx = await self.server.register_namespace(namespace.namespace_header["namespaceUri"])
                namespace.set_server_assigned_information(_server_namespace_id= idx, _server_namespaceUri= namespace.namespace_header["namespaceUri"])
                self.log_message(f"Namespace added to server with the following information: ID={idx}, Namespace='{namespace.namespace_header["namespaceUri"]}', Description='{namespace.namespace_header["description"]}'")
            except Exception as e:
                self.log_message(f"Trying to activate namespace, but the server exits with an error. Abort activating namespace. {e}", "error")
        self.log_message("All namespaces are activated.")
        return 1

    async def activate_nodes(self) -> int:
        """
        Activate nodes on the server under their respective parents.
        This includes Objects, Variables, and Methods.

        Returns:
            int: 1 if successful, -1 if no nodes initialized.
        """
        async def _iterate_node(_nodes: list[OPCUANode], _level: int, _parent: OPCUANode = None, _root: object = None) -> int:
            """
            Recursively iterate nodes to attach them under their parent nodes.

            Args:
                _nodes (list[OPCUANode]): List of nodes to activate.
                _level (int): Current tree depth.
                _parent (OPCUANode, optional): Parent node reference.
                _root (Node, optional): Root node reference for recursion.

            Returns:
                int: 1 if iteration completed, -1 otherwise.
            """
            if _root is not None:
                for node in _nodes:
                    index = 0
                    if node.node_header["parentNodeId"] == _root.nodeid.Identifier:
                        await _activate_node(_node= node, _level= _level)
                        _nodes = _nodes[:index] + _nodes[1 + index:]
                        child_level = _level + 1
                        await _iterate_node(_nodes = _nodes, _level = child_level, _parent= node)  
                    index += 1
                return 1
            elif _parent is not None:
                for node in _nodes:
                    index = 0
                    if node.node_header["parentNodeId"] == _parent.node_header["i"]:
                        await _activate_node(_node= node, _level= _level)
                        _nodes = _nodes[:index] + _nodes[1 + index:]
                        child_level = _level + 1
                        await _iterate_node(_nodes = _nodes, _level = child_level, _parent= node)  
                    index += 1
                return 1
            return -1

        async def _activate_node(_node: OPCUANode, _level: int) -> int:
            """
            Activate a single node on the server, assign it to the correct namespace and parent.

            Args:
                _node (OPCUANode): Node to activate.
                _level (int): Current depth in hierarchy.

            Returns:
                int: 1 if successful, -1 on error.
            """
            ns = None
            found_namespace = False

            # Ensure namespaces exist
            if not self.namespaces:
                self.log_message("Trying to activate a node, but no namespaces are initialised. Abort activating namespace.", "error")
                return -1

            # Find corresponding namespace
            for namespace in self.namespaces:
                if _node.node_header["namespaceUri"] in namespace.namespace_header["namespaceUri"]:
                    try:
                        namespace_server_id_array = await self.server.get_namespace_array()
                        namespace_server_id = namespace_server_id_array.index(_node.node_header["namespaceUri"])
                        _ns = namespace.server_assigned_header["ns"]
                        if namespace_server_id == _ns:
                            ns = _ns
                            found_namespace = True
                        else:
                            self.log_message("Trying to activate a node, but no namespaces has the same index. Node gets server namespace index.", "warning")
                            ns = namespace_server_id
                            found_namespace = True
                    except Exception as e:
                        self.log_message(f"Trying to get namespace index, but the namespace is not activated. Abort getting namespace index. {e}", "error")
                        return -1
            if not found_namespace:
                self.log_message("Trying to activate a node, but no matching namespaces uri exists in the server. Abort activating node.", "warning")
                return -1
            
            # Determine parent node
            if _node.node_header["parentNodeId"] == self.objects_node_information["i"] and _node.node_header["parentNodeNamespace"] == self.objects_node_information["ns"]:
                await _start_node(_node= _node, _parent= self.objects_node, _ns= ns, _level= _level)
            else:
                for parent in self.nodes:
                    if parent.server_assigned_header is not None:
                        # Check if parent was found
                        if _node.node_header["parentNodeId"] == parent.node_header["i"]  and _node.node_header["parentNodeNamespace"] == parent.node_header["ns"]:
                            await _start_node(_node= _node, _parent= parent.node, _ns= ns, _level= _level)
            return 1
            
        async def _start_node(_node: OPCUANode, _parent: object, _ns: int, _level: int):
            """
            Add a node to the server under the given parent.

            Args:
                _node (OPCUANode): Node to add.
                _parent (Node): Parent node in server.
                _ns (int): Namespace index.
                _level (int): Depth level for node tree tracking.
            """
            idx = None
            match _node.node_header["nodeClass"]:
                case "Object":
                    idx = await _parent.add_object(_ns, _node.node_header["browseName"])
                case "Variable":
                    idx = await _parent.add_variable(_ns, _node.node_header["browseName"], _node.data["value"])

                    access = 0x00
                    if _node.access["readable"] == True and _node.access["writeable"] == True:
                        #access = ua.AccessLevel.CurrentRead | ua.AccessLevel.CurrentWrite
                        access = 0x03
                        """ Set variable writeable() """
                        await idx.set_writable()
                    elif _node.access["readable"] == True:
                        #access = ua.AccessLevel.CurrentRead 
                        access = 0x01
                        """ Readable is set by default """
                    elif _node.access["writeable"] == True:
                        #access =  ua.AccessLevel.CurrentWrite
                        access = 0x02
                        """ Set variable writeable() """
                        await idx.set_writable()
                    """ Bit mask is not implemented in asyncua, Hence writeonly does not work"""
                    #await idx.write_attribute(
                    #    ua.AttributeIds.AccessLevel,
                    #    ua.DataValue(ua.Variant(access, ua.VariantType.Byte))
                    #)
                case "Methode":
                    
                    return -1
            _node.set_server_assigned_information(_server_node_idx= idx, _server_nodeUri= _node.node_header["namespaceUri"])
            _write_to_tree(_node= _node, _level= _level)
            self.log_message(f"Node: {_node.node_header["browseName"]}, was added to the server with ns: {idx.nodeid.NamespaceIndex}, i: {idx.nodeid.Identifier}.")            
            
        def _write_to_tree(_node: OPCUANode, _level: int) -> int:
            """
            Maintain internal node tree and info structures.

            Args:
                _node (OPCUANode): Node added to server.
                _level (int): Depth level in tree.

            Returns:
                int: Always 1.
            """
            entry = [None] * _level
            entry.append(_node.node_header["i"])
            name = _node.node_header["browseName"]
            self.server_node_tree.append(entry)
            # ns: i: nodeClass: browseName
            information = (f"browseName: {_node.node_header['browseName']}, ns: {_node.server_assigned_header['ns']}, "
                           f"i: {_node.server_assigned_header['i']}, nodeClass: {_node.node_header['nodeClass']}")
            self.server_node_information.append([_node.node_header["i"], information])
            self.server_node_names.append([_node.node_header["i"], name])
            return 1
        
        if not self.nodes:
            self.log_message("Trying to activate nodes, but no nodes are initialised. Abort activating nodes.", "warning")
            return -1
        
        # Get root node information
        try:
            self.objects_node = self.server.nodes.objects
            self.objects_node_information["ns"] = self.objects_node.nodeid.NamespaceIndex
            self.objects_node_information["i"] = self.objects_node.nodeid.Identifier
        except Exception as e:
            self.log_message(f"Trying to get root node, but the server exits with an error. Abort activating nodes. {e}", "error")
            return -1
        
        level = 1
        nodes_copy = self.nodes
        # Initialize tree with root object
        self.server_node_tree.append([85])
        self.server_node_information.append([85, "browseName: root object, ns: 0, i: 85, nodeClass: Objects"])
        self.server_node_names.append([85, "root object"])

        await _iterate_node(_nodes= nodes_copy, _level = level, _root= self.objects_node)
        
    def get_node_tree(self) -> dict:
        """
        Return the internal representation of the node tree and node information.

        Returns:
            dict: Contains "node_tree", "server_node_information", and "server_node_names".
        """
        return {
            "node_tree": self.server_node_tree,
            "server_node_information": self.server_node_information,
            "server_node_names": self.server_node_names
        }