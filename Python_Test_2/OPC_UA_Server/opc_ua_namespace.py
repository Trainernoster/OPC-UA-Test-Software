class OPCUANamespace:
    """
    Represents an OPC UA Namespace definition and its mapping to a running OPC UA server.
    A namespace defines a unique URI context that identifies node identifiers, making them
    globally distinct. Each namespace can be preconfigured in JSON and later assigned a
    runtime index when registered with the server.
    """

    def __init__(self, _namespace_json: list) -> None:
        """
        Initialize an OPC UA Namespace with a given configuration JSON.

        Attributes:
            self                obj     Instance of the class.
            _namespace_json     list    JSON-like dictionary that contains
                                        predefined namespace information (URI, description, etc.)

        Example of expected JSON:
            {
                "namespaceIndex": 2,
                "namespaceUri": "urn:example:namespace",
                "description": "Example namespace for OPC UA server"
            }

        Return value:
            None
        """
        self.namespace_json = _namespace_json   # pre assigned namespace information json
        self.namespace_header = None            # pre assigned namespace header
        self.server_assigned_header = None      # automatic assigned namesapce header

        # Initialize namespace header from provided JSON data
        self.set_namespace_header()
    
    def set_namespace_header(self) -> int:
        """
        Set the pre-assigned (static) namespace information based on the configuration JSON.
        This information describes the namespace before it is registered with the server.

        Attributes:
            self    obj     Instance of the class.

        Return value:
            int     Returns 1 on success.
        """
        self.namespace_header = {
            "ns": self.namespace_json.get("namespaceIndex"),            # Predefined namespace index (if specified)
            "namespaceUri": self.namespace_json.get("namespaceUri"),    # Unique namespace URI string
            "description": self.namespace_json.get("description")       # Optional human-readable description
        }
        return 1

    def set_server_assigned_information(self, _server_namespace_id: str, _server_namespaceUri: str) -> int:
        """
        Set the namespace information as assigned by the server when registered.

        This method is typically called after the namespace has been registered
        on the OPC UA server via `server.register_namespace()`, which returns
        the assigned namespace index.

        Attributes:
            self                    obj     Instance of the class.
            _server_namespace_id     str     Namespace index assigned by the server.
            _server_namespaceUri     str     Namespace URI assigned by the server.

        Return value:
            int                     Returns 1 on success.
        """
        self.server_assigned_header = {
            "ns": _server_namespace_id,             # Actual namespace index assigned by the server
            "namespaceUri": _server_namespaceUri,   # URI as recognized by the server
            "ns_consensus": None                    # Reserved for validation or synchronization logic
        }

        # Check whether the namespace index assigned by the server matches the preconfigured one
        if self.server_assigned_header["ns"] == self.namespace_header["ns"]:
            self.server_assigned_header["id_consensus"] = True       # Indicate the indices match
        else:
            self.server_assigned_header["id_consensus"] = False      # Indicate they differ
        return 1