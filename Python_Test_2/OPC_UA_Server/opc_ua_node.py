class OPCUANode:
    def __init__(self, _node_json: list) -> None:
        """ Initialize an OPC UA Node with given configuration. """

        """
            Attributes:        
                self           obj     self
                _node_json     list    contains node information
                
            Return value:
                int 
        """
        self.node_json = _node_json
        self.node_header = None
        self.server_assigned_header = None
        self.node = None
        self.set_Node_Header()
        self.add_information()        

    def set_Node_Header(self) -> int:
        """ Create the OPC UA node header. """
        self.node_header = {
            "ns": self.node_json.get("nodeHeader").get("nodeId").get("ns"),
            "i": self.node_json.get("nodeHeader").get("nodeId").get("i"),
            "nodeClass": self.node_json.get("nodeHeader").get("nodeClass"),
            "browseName": self.node_json.get("nodeHeader").get("browseName"),
            "displayName": self.node_json.get("nodeHeader").get("displayName"),
            "description": self.node_json.get("nodeHeader").get("description"),
            "namespaceUri": self.node_json.get("nodeHeader").get("namespaceUri"),
            "parentNodeNamespace": self.node_json.get("nodeHeader").get("parentNodeId").get("ns"),
            "parentNodeId": self.node_json.get("nodeHeader").get("parentNodeId").get("i"),
        }

    def add_information(self) -> int:
        match self.node_header["nodeClass"]:
                    case "Object":
                        ...
                    case "Variable":
                        self.data = {
                            "value": self.node_json.get("data").get("value"),
                            "dataType": self.node_json.get("data").get("dataType"),
                            "valueRank": self.node_json.get("data").get("valueRank"),
                            "arrayDimensions": self.node_json.get("data").get("arrayDimensions"),
                        }
                        self.access = {
                            "readable": self.node_json.get("access").get("readable"),
                            "writeable": self.node_json.get("access").get("writeable")
                        }
                    case "Methode":
                        ...

    def set_server_assigned_information(self, _server_node_idx: object, _server_nodeUri: str) -> int:
        self.node = _server_node_idx
        if self.node is not None:
            self.server_assigned_header = {
                "ns" : _server_node_idx.nodeid.NamespaceIndex,
                "i": _server_node_idx.nodeid.Identifier,
                "ns_consensus": None,
                "i_consensus": None
            }