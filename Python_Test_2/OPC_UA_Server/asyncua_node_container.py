import logging
from asyncua import ua
import OPC_UA_Server
from .opc_ua_node import OPCUANode
from .opc_ua_namespace import OPCUANamespace
#from Lib.dependencytree.dependencytree import dependencytree_print


class OPCUANodeContainer:
    def __init__(
            self,
            _server: OPC_UA_Server,
            _namespace_jsons: list,
            _node_jsons: list,
            _logger: logging = None
        ) -> None:
        """ Initialize the OPC UA Nodes container. """

        """
            Attributes:             
                self                obj             self
                _server             OPC_UA_Server   holds OPC UA Server instanze
                _namespace_jsons    list            contains namespace jsons
                _node_jsons:        list            contains node jsons
                _logger             logging         logger from server
                
            Return value:
                None 
        """

        self.server: OPC_UA_Server = _server    # OPC UA Server instanze
        self.namespace_jsons = _namespace_jsons # namespace jsons
        self.node_jsons = _node_jsons           # node jsons
        self.logger = _logger                   # logger from server

        self.namespaces: list[OPCUANamespace] = []  # namespace container
        self.nodes: list[OPCUANode] = []            # nodes container
        self.objects_node = None                    # server node Objects
        self.node_tree: list = []                   # node tree
        self.node_names: list = []                  # node names
        self.node_children: list = []               # node children

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
        if self.logger is not None:
            if _type == None or _type == "info":
                self.logger.info("From OPCUANodeContainer: " + _message)
            elif _type == "warning":
                self.logger.warning("From OPCUANodeContainer: " + _message)
            elif _type == "error":
                self.logger.error("From OPCUANodeContainer: " + _message)
            elif _type == "critical":
                self.logger.critical("From OPCUANodeContainer: " + _message)
            else:
                self.logger.critical("From OPCUANodeContainer: " + _message)
    

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
        if self.namespace_jsons is None:
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
        if self.node_jsons is None:
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
        ...

    async def activate_nodes(self)  -> int:
        """ Activate nodes on server. """

        """
            Attributes:             
                self                obj     self
                
            Return value:
                int 
        """
        ...








































































    
    async def add_nodes(self) -> int:
        """ Add all nodes from json file."""
        if self.namespaces is None:
            print ("There a no namespaces, please run initialize_namespaces().")
            return -1
        elif self.nodes is None:
            print ("There a no nodes, please run initialize_nodes().")
            return -1
        else:
            self.objects_node = self.server.nodes.objects

            # Namespaces
            for namespace in self.namespaces:
                idx = await self.server.register_namespace(namespace.namespace_header["namespaceUri"])
                namespace.set_Server_Namespace_id(idx)

            def _finde_Parent(_node) -> OPCUANode:
                parent_node = None
                for par_node in self.nodes:
                    if par_node.node_header["i"] == _node.node_header["parentNodeId"]:
                        parent_node = par_node
                        break
                return parent_node

            ##
            ##  Object
            ##
            async def add_Object(_node) -> int:
                if _node.node_header["parentNodeId"] == 85:
                    object_node = await self.objects_node.add_object(_node.node_header["ns"], _node.node_header["browseName"])
                    _node.set_Node(object_node)
                else:
                    parent_node = _finde_Parent(_node)
                    if parent_node is not None:
                        object_node = await parent_node.node.add_object(_node.node_header["ns"], _node.node_header["browseName"])
                        _node.set_Node(object_node)

                return 1

            ##
            ##  Variable
            ##
            async def add_Variable(_node):
                if _node.node_header["parentNodeId"] == 85:
                    object_node = await self.objects_node.add_variable(_node.node_header["ns"], _node.node_header["browseName"], _node.data["value"])
                    _node.set_Node(object_node)
                else:
                    parent_node = _finde_Parent(_node)
                    if parent_node is not None:
                        object_node = await parent_node.node.add_variable(_node.node_header["ns"], _node.node_header["browseName"], _node.data["value"])
                        _node.set_Node(object_node)
                
                access = 0x00
                if _node.access["readable"] == True and _node.access["writeable"] == True:
                    access = ua.AccessLevel.CurrentRead | ua.AccessLevel.CurrentWrite
                elif _node.access["readable"] == True:
                    access = ua.AccessLevel.CurrentRead 
                elif _node.access["writeable"] == True:
                    access =  ua.AccessLevel.CurrentWrite
                await _node.node.write_attribute(
                    ua.AttributeIds.AccessLevel,
                    ua.DataValue(ua.Variant(access, ua.VariantType.Byte))
                )
                await _node.node.write_attribute(
                    ua.AttributeIds.UserAccessLevel,
                    ua.DataValue(ua.Variant(access, ua.VariantType.Byte))
                )

                    
            # Nodes
            for node in self.nodes:
                match node.node_header["nodeClass"]:
                    case "Object":
                        await add_Object(_node = node)
                    case "Variable":
                        await add_Variable(_node = node)
                    case "Methode":
                        ...

                print(node.node)

            return 1

  
    

















































































































    ###
    ###
    ###

    ###
    ### Not yet implemented
    ###

    ###
    ###
    ###
    
    def _set_relations(self) -> int:
        """ Changes None to right sign. """
        #print("-----------OPC UA Nodes-----------")
        #print()
        #print("Objects Node")
        vertical = "│"
        branch_middle = "├"
        branch_last = "└"
        horizontal = "─"

        self.inheritance = []
        num_rows = len(self.node_tree)

        for idx, row in enumerate(self.node_tree):
            row_len = len(row)

            if idx == 0:
                last_child = idx
                for r in range(1, num_rows):
                    if len(self.node_tree[r]) == row_len + 1:
                        last_child = r
                self.inheritance.append((idx, last_child))
            else:
                last_child = idx
                for r in range(idx + 1, num_rows):
                    if len(self.node_tree[r]) == row_len:
                        last_child = r - 1
                        break
                    else:
                        last_child = r
                self.inheritance.append((idx, last_child))
        
        #self._print_tree()
        return 1
    
    def _print_tree(self):
        """
        Print the visual tree line by line.
        """
        for row in self.node_tree:
            # Combine columns, respecting vertical lines
            line = ""
            for col in row:
                line += str(col)
            print(line)
    
    def create_node_tree(self) -> int:
        """ Print the OPC UA node tree. """
        # Reset node tree to initial state Objects with id 85
        self.node_tree = [[85]]
        # Set recursive search parameters
        current_parent_nodes = 85
        current_level = 1

        # Start recursive search for child nodes
        self._find_children(_current_parent_node = current_parent_nodes, _current_level = current_level)
        self._set_relations()
        return 1
        
    def _find_children(self, _current_parent_node: int, _current_level: int) -> int:
        """ Recursively find and add child nodes to the node tree. """
        for node in self.nodes:
            if node.node_header["parentNodeId"] == _current_parent_node:

                # Add new object to the node tree
                new_row = [None] * (_current_level + 1)
                new_row[_current_level] = node.node_header["i"]
                self.node_tree.append(new_row)
                
                # Recursively find children of the current node
                self._find_children(_current_parent_node = node.node_header["i"], _current_level = _current_level + 1)
        return 1