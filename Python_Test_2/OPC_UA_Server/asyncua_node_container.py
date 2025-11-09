import logging
from asyncua import ua
import OPC_UA_Server
from .opc_ua_node import OPCUANode
from .opc_ua_namespace import OPCUANamespace

class OPCUANodeContainer:
    def __init__(
            self,
            _server: OPC_UA_Server,
            _namespace_jsons: list,
            _node_jsons: list,
            _logger: logging = None,
            _logger_active: bool = True
        ) -> None:
        """ Initialize the OPC UA Nodes container. """

        """
            Attributes:             
                self                obj             self
                _server             OPC_UA_Server   holds OPC UA Server instanze
                _namespace_jsons    list            contains namespace jsons
                _node_jsons:        list            contains node jsons
                _logger             logging         logger from server
                _logger_active      bool            logger is active if True
                
            Return value:
                None 
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
        """ Logs infos. """

        """
            Attributes:             
                self                obj     self
                _message            str     message to log
                
            Return value:
                None 
        """
        if self.logger is not None and self.logger_active == True:
            if _type == None or _type == "info":
                self.logger.info("From OPCUANodeContainer: " + _message)
                return 1
            elif _type == "warning":
                self.logger.warning("From OPCUANodeContainer: " + _message)
                return 1
            elif _type == "error":
                self.logger.error("From OPCUANodeContainer: " + _message)
                return 1
            elif _type == "critical":
                self.logger.critical("From OPCUANodeContainer: " + _message)
                return 1
            else:
                self.logger.critical("From OPCUANodeContainer: " + _message)
                return 1
        return -1
    
    def load_namespaces_and_nodes(self) -> int:
        """ Load namespaces and nodes. """

        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """
        self.initialise_namespaces()
        self.initialise_nodes()
        self.log_message("Namespaces and nodes are initialised")
        return 1
    
    def initialise_namespaces(self) -> int:
        """ Add all namespaces from json. """

        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """
        if not self.namespace_jsons:
            self.log_message("No namespace jsons are found. Abort initialise namespaces.", "warning")
            return -1
        else:
            for namespace_json in self.namespace_jsons:
                opcua_namespace = OPCUANamespace(_namespace_json = namespace_json)             
                self.namespaces.append(opcua_namespace)
            return 1
    
    def initialise_nodes(self) -> int:
        """ Add all nodes from json. """

        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """
        
        if not self.node_jsons:
            self.log_message("No node jsons are found. Abort initialise nodes.", "warning")
            return -1
        else:

            for node_json in self.node_jsons:
                opcua_node = OPCUANode(_node_json = node_json)                
                self.nodes.append(opcua_node)
            return 1

    async def activate_namespaces(self)  -> int:
        """ Activate namespaces on server. """

        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """
        
        if not self.namespaces:
            self.log_message("Trying to activate namespaces, but no namspaces are initialised. Abort activating namespaces.", "warning")
            return -1
        else:
            for namespace in self.namespaces:
                try:
                    idx = await self.server.register_namespace(namespace.namespace_header["namespaceUri"])
                    namespace.set_server_assigned_information(_server_namespace_id= idx, _server_namespaceUri= namespace.namespace_header["namespaceUri"])
                    self.log_message(f"Namespace added to server with the following information: ID={idx}, Namespace='{namespace.namespace_header["namespaceUri"]}', Description='{namespace.namespace_header["description"]}'")
                except Exception as e:
                    self.log_message(f"Trying to activate namespace, but the server exits with an error. Abort activating namespace. {e}", "error")
            self.log_message("All namespaces are activated.")
            return 1

    async def activate_nodes(self)  -> int:
        """ Activate nodes on server. """

        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """

        async def _iterate_node(_nodes: list[OPCUANode], _level: int, _parent: OPCUANode = None, _root: object = None) -> int:
            
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
            ns = None
            found_namespace = False
            # Check if namespaces are initialized:
            if not self.namespaces:
                self.log_message("Trying to activate a node, but no namespaces are initialised. Abort activating namespace.", "error")
                return -1

            # Check if the namespace uri exists
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
                        self.log_message(f"Trying to get namespace index, but the namespaces is not activated. Abort getting namespace index. {e}", "error")
                        return -1
            if not found_namespace:
                self.log_message("Trying to activate a node, but no namespaces uri exists in the server. Abort activating node.", "warning")
                return -1
                
            # Check if parent is root
            if _node.node_header["parentNodeId"] == self.objects_node_information["i"] and _node.node_header["parentNodeNamespace"] == self.objects_node_information["ns"]:
                await _start_node(_node= _node, _parent= self.objects_node, _parent_ns= _node.node_header["parentNodeNamespace"], _level= _level)
                #idx = await self.objects_node.add_object(_node.node_header["parentNodeNamespace"], _node.node_header["browseName"])
                #_node.set_server_assigned_information(_server_node_id= idx, _server_nodeUri= _node.node_header["namespaceUri"], _server_node= idx)
            
            else:
                for parent in self.nodes:
                    if parent.server_assigned_header is not None:
                        # Check if parent is found
                        if _node.node_header["parentNodeId"] == parent.node_header["i"]  and _node.node_header["parentNodeNamespace"] == parent.node_header["ns"]:
                            await _start_node(_node= _node, _parent= parent.node, _parent_ns= _node.node_header["parentNodeNamespace"], _level= _level)
                            #idx = await parent.node.add_object(ns, _node.node_header["browseName"])
                            #_node.set_server_assigned_information(_server_node_id= idx, _server_nodeUri= _node.node_header["namespaceUri"], _server_node= idx)
            
            return 1
            
        async def _start_node(_node: OPCUANode, _parent: object, _parent_ns: OPCUANode, _level: int):
            idx = None
            match _node.node_header["nodeClass"]:
                case "Object":
                    idx = await _parent.add_object(_parent_ns, _node.node_header["browseName"])
                    #_node.set_server_assigned_information(_server_node_idx= idx, _server_nodeUri= _node.node_header["namespaceUri"])
                case "Variable":
                    idx = await _parent.add_variable(_parent_ns, _node.node_header["browseName"], _node.data["value"])

                    access = 0x00
                    if _node.access["readable"] == True and _node.access["writeable"] == True:
                        access = ua.AccessLevel.CurrentRead | ua.AccessLevel.CurrentWrite
                    elif _node.access["readable"] == True:
                        access = ua.AccessLevel.CurrentRead 
                    elif _node.access["writeable"] == True:
                        access =  ua.AccessLevel.CurrentWrite
                    await idx.write_attribute(
                        ua.AttributeIds.AccessLevel,
                        ua.DataValue(ua.Variant(access, ua.VariantType.Byte))
                    )
                    await idx.write_attribute(
                        ua.AttributeIds.UserAccessLevel,
                        ua.DataValue(ua.Variant(access, ua.VariantType.Byte))
                    )
                case "Methode":
                    
                    return -1
            _node.set_server_assigned_information(_server_node_idx= idx, _server_nodeUri= _node.node_header["namespaceUri"])
            _write_to_tree(_node= _node, _level= _level)            
            
        def _write_to_tree(_node: OPCUANode, _level: int) -> int:
            entry = [None] * _level
            entry.append(_node.node_header["i"])
            name = _node.node_header["browseName"]
            self.server_node_tree.append(entry)
            # ns: i: nodeClass: browseName
            information = ("browseName: " + _node.node_header["browseName"] + ", ns: " + str(_node.server_assigned_header["ns"]) + ", i: " + str(_node.server_assigned_header["i"]) + ", nodeClass: " + _node.node_header["nodeClass"])
            self.server_node_information.append([_node.node_header["i"], information])
            self.server_node_names.append([_node.node_header["i"], name])
        
        if not self.nodes:
            self.log_message("Trying to activate nodes, but no nodes are initialised. Abort activating nodes.", "warning")
            return -1
        else:
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
            self.server_node_tree.append([85])
            self.server_node_names.append([85, "root object"])
            await _iterate_node(_nodes= nodes_copy, _level = level, _root= self.objects_node)
            
    def get_node_tree(self) -> dict:
        return {
            "node_tree": self.server_node_tree,
            "server_node_information": self.server_node_information,
            "server_node_names": self.server_node_names
        }