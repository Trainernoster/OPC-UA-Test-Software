class OPCUANode:
    """
    Represents a single OPC UA Node that is defined using a JSON configuration.
    Each node can be an Object, Variable, or Method and contains metadata, access levels,
    and server-assigned information once registered with an OPC UA server.
    """

    def __init__(self, _node_json: list) -> None:
        """
        Initialize an OPC UA Node with the given configuration JSON.

        Attributes:
            self            obj     Instance of the class itself.
            _node_json      list    JSON-like dictionary containing all node information
                                    such as nodeId, namespace, browseName, access rights, etc.

        Return value:
            None
        """
        self.node_json = _node_json                     # JSON configuration for this node.
        self.node_header = None                         # Contains base metadata (namespace, browseName, etc.).
        self.server_assigned_header = None              # Holds information assigned by the server when node is created.
        self.node = None                                # Actual server node object (after activation on server).

        # Initialize the node by extracting all its static configuration
        self.set_Node_Header()
        self.add_information()        

    def set_Node_Header(self) -> int:
        """
        Parse and set up the OPC UA node header from the provided JSON.
        The header holds the main descriptive and structural information
        of the node (such as identifiers, class, and parent relationship).

        Attributes:
            self        obj     Instance of the class.

        Return value:
            int         Always returns 1 on success (could be extended to return status).
        """
        # Extract the node header information from the JSON.
        self.node_header = {
            "ns": self.node_json.get("nodeHeader").get("nodeId").get("ns"),                         # Namespace index
            "i": self.node_json.get("nodeHeader").get("nodeId").get("i"),                           # Identifier (integer or string)
            "nodeClass": self.node_json.get("nodeHeader").get("nodeClass"),                         # Node class (Object, Variable, Method)
            "browseName": self.node_json.get("nodeHeader").get("browseName"),                       # Browse name used for client navigation
            "displayName": self.node_json.get("nodeHeader").get("displayName"),                     # Human-readable display name
            "description": self.node_json.get("nodeHeader").get("description"),                     # Optional text description
            "namespaceUri": self.node_json.get("nodeHeader").get("namespaceUri"),                   # Namespace URI for the node
            "parentNodeNamespace": self.node_json.get("nodeHeader").get("parentNodeId").get("ns"),  # Namespace index of parent
            "parentNodeId": self.node_json.get("nodeHeader").get("parentNodeId").get("i"),          # Identifier of parent node
        }
        return 1

    def add_information(self) -> int:
        """
        Add node-specific attributes and metadata based on its nodeClass type.
        This includes data types, access control, and initial values for Variables.

        Attributes:
            self        obj     Instance of the class.

        Return value:
            int         Returns 1 if additional information is added successfully.
        """
        match self.node_header["nodeClass"]:
            case "Object":
                ...
            case "Variable":
        # Variable nodes hold a data value and have defined access levels.
                self.data = {
                    "value": self.node_json.get("data").get("value"),                       # Initial value for the variable
                    "dataType": self.node_json.get("data").get("dataType"),                 # Data type (e.g., Double, String)
                    "valueRank": self.node_json.get("data").get("valueRank"),               # Value rank (-1 = scalar, >0 = array)
                    "arrayDimensions": self.node_json.get("data").get("arrayDimensions"),   # Array dimensions if applicable
                }
                self.access = {
                    "readable": self.node_json.get("access").get("readable"),               # True if the value can be read by clients
                    "writeable": self.node_json.get("access").get("writeable")              # True if the value can be modified by clients
                }

            case "Methode":
                ...
        return 1

    def set_server_assigned_information(self, _server_node_idx: object, _server_nodeUri: str) -> int:
        """
        Store information assigned by the server once the node is created.
        This typically happens after the node has been added to the server address space.

        Attributes:
            self                obj         Instance of the class.
            _server_node_idx    object      Reference to the created node object in the server.
            _server_nodeUri     str         Namespace URI assigned to this node by the server.

        Return value:
            int                 Returns 1 on success.
        """
        self.node = _server_node_idx
        if self.node is not None:
            # Store the server-assigned namespace and identifier
            self.server_assigned_header = {
                "ns": _server_node_idx.nodeid.NamespaceIndex,    # Namespace index assigned by the server
                "i": _server_node_idx.nodeid.Identifier,         # Identifier assigned by the server
                "ns_consensus": None,                            # Reserved for namespace verification (future use)
                "i_consensus": None                              # Reserved for identifier verification (future use)
            }
            return 1
        return -1