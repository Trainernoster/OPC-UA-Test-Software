class OPCUANamespace:
    def __init__(self, _namespace_json) -> None:
        """ Initialize an OPC UA Nameapce with given configuration. """
        self.namespace_json = _namespace_json
        self.namespace_header = None
        self.server_namespace_id = None
        self.id_consensus = None
        self.set_Namespace_Header()
        
    def set_Namespace_Header(self) -> int:
        self.namespace_header ={
            "ns" : self.namespace_json.get("namespaceIndex"),
            "namespaceUri": self.namespace_json.get("namespaceUri"),
            "description": self.namespace_json.get("description")
        }

    def set_Server_Namespace_id(self, _server_namespace_id) -> int:
        self.server_namespace_id = _server_namespace_id
        if self.server_namespace_id == self.namespace_header["ns"]:
            self.id_consensus = True
        else:
            self.id_consensus = False