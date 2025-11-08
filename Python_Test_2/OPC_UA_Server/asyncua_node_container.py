import OPC_UA_Server
from asyncua import ua
from .opc_ua_node import OPCUANode
from .opc_ua_namespace import OPCUANamespace


class OPCUANodes:
    def __init__(self, _server: OPC_UA_Server,_namesspaces_json: list, _nodes_json: list) -> None:
        """ Initialize the OPC UA Nodes container. """
        self.server: OPC_UA_Server = _server
        self.objects_node = None
        self.nodes: list[OPCUANode] = []
        self.namespaces: list[OPCUANamespace] = []
        self.namespaces_json = _namesspaces_json
        self.nodes_json = _nodes_json
        self.node_tree: list = []
        self.inheritance: list = []
        self.known_objects = ["Object", "Variable", "Methode"]
    
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

            
        
    def initialize_namespaces(self) -> int:
        """ Add all loadable nodes. """
        if self.namespaces_json is None:
            print ("There a no json file for namespaces.")
            return -1
        else:
            for namespace_json in self.namespaces_json:
                opcua_namespace = OPCUANamespace(_namespace_json = namespace_json)
                
                self.namespaces.append(opcua_namespace)
            return 1
        
    def initialize_nodes(self) -> int:
        """ Add all loadable nodes. """
        if self.nodes_json is None:
            print ("There a no json file for nodes.")
            return -1
        else:
            for node_json in self.nodes_json:
                opcua_node = OPCUANode(_node_json = node_json)
                
                self.nodes.append(opcua_node)
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