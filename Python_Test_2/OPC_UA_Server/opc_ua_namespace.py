class OPCUANamespace:
    def __init__(self, _namespace_json: list) -> None:
        """ Initialize an OPC UA Namespace with given configuration. """

        """
            Attributes:             
                self                obj     self
                _namespace_json     list    contains namespace information
                
            Return value:
                int 
        """
        self.namespace_json = _namespace_json   # pre assigned namespace information json
        self.namespace_header = None            # pre assigned namespace header
        self.server_assigned_header = None      # automatic assigned namesapce header
        self.set_namespace_header()
    
    def set_namespace_header(self) -> int:
        """ Set pre assigned information. """

        """
            Attributes:                 
                self                    obj     self
                
            Return value:
                int 
        """
        self.namespace_header ={
            "ns" : self.namespace_json.get("namespaceIndex"),
            "namespaceUri": self.namespace_json.get("namespaceUri"),
            "description": self.namespace_json.get("description")
        }

    def set_server_assigned_information(self, _server_namespace_id: str, _server_namespaceUri: str) -> int:
        """ Set server assigned information. """

        """
            Attributes:                 
                self                    obj     self
                _server_namespace_id    str     namespace id assigned from server
                _server_namespaceUri    str     namespace uri assigned from server
                
            Return value:
                int 
        """
        self.server_assigned_header = {
            "ns" : _server_namespace_id,
            "namespaceUri": _server_namespaceUri,
            "id_consensus": None
        }

        if self.server_assigned_header["ns"] == self.namespace_header["ns"]:
            self.server_assigned_header["id_consensus"] = True
        else:
            self.server_assigned_header["id_consensus"] = False