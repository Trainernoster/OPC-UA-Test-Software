import os
import json
import asyncio
import logging

from typing import Literal

from asyncua import Node
from asyncua import ua
from asyncua.ua import NodeId

from lxml import etree
import xml.etree.ElementTree as ET

from pathlib import Path
from datetime import datetime

from asyncua import Server
from .asyncua_node_container import OPCUANodeContainer

# Standard OPC UA types mapping
STANDARD_DATATYPES = {
    1: "Boolean",
    2: "SByte",
    3: "Byte",
    4: "Int16",
    5: "UInt16",
    6: "Int32",
    7: "UInt32",
    8: "Int64",
    9: "UInt64",
    10: "Float",
    11: "Double",
    12: "String",
    13: "DateTime",
    14: "Guid",
    15: "ByteString",
    16: "XmlElement",
    17: "NodeId",
    18: "ExpandedNodeId",
    19: "StatusCode",
    20: "QualifiedName",
    21: "LocalizedText",
    22: "Structure",
    23: "Number",
    24: "Integer",
    25: "UInteger",
}

# OPC UA built‑in DataType aliases (namespace 0) for NodeSet2 XML
BUILTIN_DATATYPE_ALIASES = {
    "Boolean": "ns=0;i=1",
    "SByte": "ns=0;i=2",
    "Byte": "ns=0;i=3",
    "Int16": "ns=0;i=4",
    "UInt16": "ns=0;i=5",
    "Int32": "ns=0;i=6",
    "UInt32": "ns=0;i=7",
    "Int64": "ns=0;i=8",
    "UInt64": "ns=0;i=9",
    "Float": "ns=0;i=10",
    "Double": "ns=0;i=11",
    "String": "ns=0;i=12",
    "DateTime": "ns=0;i=13",
    "Guid": "ns=0;i=14",
    "ByteString": "ns=0;i=15",
    "XmlElement": "ns=0;i=16",
    "NodeId": "ns=0;i=17",
    "ExpandedNodeId": "ns=0;i=18",
    "StatusCode": "ns=0;i=19",
    "QualifiedName": "ns=0;i=20",
    "LocalizedText": "ns=0;i=21",
    "ExtensionObject": "ns=0;i=22",
    "DataValue": "ns=0;i=23",
    "Variant": "ns=0;i=24",
    "DiagnosticInfo": "ns=0;i=25",
}

class OPCUAServer:
    """
    Asynchronous OPC UA server wrapper.

    Provides configuration-driven initialization, namespace and node activation,
    and lifecycle management (start/stop/autostart) for an asyncua-based OPC UA server.
    """

    def __init__(
            self,
            _server_name: str = "OPC-UA-Server", 
            _endpoint: str = "opc.tcp://0.0.0.0:4840/freeopcua/server/",
            _namespace_jsons: list = [],
            _node_jsons: list = [],
            _node_container: OPCUANodeContainer = None,
            _server_config_path: str = "server_config_files",
            _server_config_file: str = "server_config.json",
            _server_xml_path: str = "design_models",
            _server_xml_file: str = "server_design_model.xml",
            _use_config_file: bool = None,
            _logger_path: str = None,
        ) -> None:
        """
        Initialize the OPC UA server object.

        Args:
            _server_name: Human-readable server name.
            _endpoint: Endpoint URL (opc.tcp://host:port/…).
            _namespace_jsons: Optional list of namespace configuration JSONs.
            _node_jsons: Optional list of node configuration JSONs.
            _node_container: Existing node container, if already created.
            _server_config_path: Directory containing configuration files.
            _server_config_file: Configuration file name.
            _server_xml_path: Directory containing server design models files.
            _server_xml_file: Design model file name.
            _use_config_file: If True, load settings from the config file.
            _logger_path: Path to store log files.

        Returns:
            None
        """
        self.server_name: str = _server_name                        # Server name
        self.endpoint: str = _endpoint                              # Server endpoint URL
        self.namespace_jsons: list = _namespace_jsons               # List of namespace configuration json
        self.node_jsons: list = _node_jsons                         # List of node configuration json files
        self.node_container: OPCUANodeContainer = _node_container   # OPC UA nodes container
        self.server_config_path: str = _server_config_path          # Path to server configuration files
        self.server_config_file: str = _server_config_file          # Server configuration file name
        self.server_xml_path: str = _server_xml_path                # Path to server design model files
        self.server_xml_file: str = _server_xml_file                # Server design model file name
        self.loaded_by_xml: bool = False                            # True if loaded by xml file
        self.use_config_file: bool = _use_config_file               # Whether to use configuration file or preconfigured parameters
        self.module_path = Path(__file__).parent                    # Get module path

        # ------------------------------------------------------------------ #
        # Logging setup
        # ------------------------------------------------------------------ #        
        # Logger Path
        self.logger_path = _logger_path
        if self.logger_path is None:
            self.logger_path = os.path.join(self.module_path, "logs")   # Default logger path
        
        # Logger file
        os.makedirs(self.logger_path, exist_ok=True)
        self.current_logger_file = (os.path.join(self.logger_path, f"server_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"))
        
        # Server logger
        self.logger = logging.getLogger("main_logger")  # Server logger
        self.logger.setLevel(logging.DEBUG)             # Logger level
        self.logger.propagate = False                   # Block other loggers
        logging.getLogger().disabled = True             # Block other loggers

        # File handler
        self.file_handler = logging.FileHandler(self.current_logger_file)
        self.file_handler.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)        

        # Server setting
        if self.use_config_file == True:
            with open(os.path.join(self.module_path, self.server_config_path, self.server_config_file), 'r') as config_file:
                config_data = json.load(config_file)
                self.server_name = config_data.get("server_name", self.server_name)             # Get server name
                self.endpoint = config_data.get("endpoint", self.endpoint)                      # Get endpoint
                self.namespace_jsons = config_data.get("namespaces", self.namespace_jsons)      # Get namespaces json
                self.node_jsons = config_data.get("nodes", self.node_jsons)                     # Get nodes json
        
        self._running: bool = False                     # Server running state
        self.server: Server | None = None               # OPC UA Server instance
        self._server_task: asyncio.Task | None = None   # Background server task

        self.logger.info("-------------------- OPC-UA server class is created --------------------")
    # ---------------------------------------------------------------------- #
    # Lifecycle management
    # ---------------------------------------------------------------------- #

    async def autostart(self, source: Literal ["json", "xml"] = "json") -> int:
        """
        Automatically initialize, start, and populate the OPC UA server.

        Steps:
            1. Initialize the server if not already done.
            2. Start the server.
            3. Create a node container if missing.
            4. Load and activate namespaces and nodes.

        Returns:
            int
        """
        match source:
            case "json":
                # Check if server exists:
                if not self.server:
                    await self.init_server()
                    self.logger.info("OPC-UA server was created by autostart ...")
                
                # Check if server is running:
                if not self._running:
                    await self.start_server()
                    self.logger.info("OPC-UA server was started by autostart ...")
                
                # Check if node container is initialised
                if not self.node_container:
                    self.logger.info("OPC-UA nodes are created by autostart ...")
                    await self.init_node_container()
                    self.load_namespaces_and_nodes_to_container()
                    await self.activate_namespaces_and_nodes_on_server()
            case "xml":
                await self.start_xml_server()
                self.loaded_by_xml = True
            case _:
                self.logger.error(f"{source} not found, server has not started!")
                return -1        

        self.logger.info("-------------------- OPC-UA server has autostarted --------------------")
        return 1

    async def start_xml_server(self) -> int:
        """
        Initialize and start the OPC UA server using a NodeSet2 XML design model.

        Returns:
            int:
        """
        # Check if server exists:
        if not self.server:
            await self.init_server()
            self.logger.info("OPC-UA server was created by autostart ...")

        # Load namespaces from XML automatically
        xml_file = os.path.join(
            self.module_path,
            self.server_xml_path,
            self.server_xml_file
        )
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Namespace for NodeSet XML
        ns = {"ua": "http://opcfoundation.org/UA/2011/03/UANodeSet.xsd"}

        for uri_elem in root.findall("ua:NamespaceUris/ua:Uri", ns):
            uri = uri_elem.text
            if uri:
                await self.server.register_namespace(uri)

        # Import all nodes from XML
        await self.server.import_xml(xml_file)

        # Check if server is running:
        if not self._running:
            await self.start_server()
            self.logger.info("OPC-UA server was started by autostart ...")

    async def init_server(self) -> int:
        """
        Create and configure the underlying asyncua.Server instance.

        Returns:
            int
        """

        self.server = Server()
        await self.server.init()
        self.server.set_endpoint(self.endpoint)
        self.server.set_server_name(self.server_name)

        self.logger.info("-------------------- OPC-UA server is initialised --------------------")
        return 1

    async def start_server(self) -> int:
        """
        Start the OPC UA server asynchronously.

        Returns:
            int
        """
        if self.server is None:
            self.logger.warning("Trying to start a not initialised server. Call init_server() first.")
            return -1
        elif self._running:
            self.logger.warning("Trying to start a running server. Abort starting server.")
            return -1
        
        await self.server.start()
        self._running = True
        self.logger.info("----------------------------------------------------------------------------------")
        self.logger.info("OPC UA Server started!")
        self.logger.info(f"Endpoint URL: {self.server.endpoint}")
        self.logger.info(f"Endpoint URL: {self.endpoint}")
        self.logger.info(f"Server Name: {self.server_name}")
        self.logger.info(f"Protocol: OPC UA TCP")
        self.logger.info("----------------------------------------------------------------------------------")
        self.logger.info("-------------------- OPC-UA server has started and is running --------------------")
        return 1
    
    async def stop_server(self) -> int:
        """
        Stop the OPC UA server and release resources.

        Returns:
            int
        """
        if self.server is None or not self._running:
            self.logger.warning("Trying to stop a not running server. Abort stopping server.")
            return -1

        self._running = False 
        await self.server.stop()
        self.logger.info("-------------------- OPC-UA server stoped --------------------")
        return 1
    
    # ---------------------------------------------------------------------- #
    # Node management
    # ---------------------------------------------------------------------- #

    async def init_node_container(self) -> int:
        """
        Create a local node container bound to this server.

        Returns:
            int
        """

        if self.node_container is not None :
            self.logger.warning("Trying to initialise a node container, but one is still there. Abort initialising node container.")
            return -1
        
        self.node_container = OPCUANodeContainer(
            _server= self.server,
            _namespace_jsons= self.namespace_jsons,
            _node_jsons= self.node_jsons,
            _logger= self.logger,
            _logger_active= True
        )
        self.logger.info("-------------------- OPC-UA node container initialised --------------------")
        return 1

    def load_namespaces_and_nodes_to_container(self) -> int:
        """
        Load namespace and node definitions into the node container.

        Returns:
            int
        """
        if not self.node_container:
            self.logger.warning("Trying to load namespaces and nodes to a container, but no exists. Abort adding namespaces and nodes.")
            return -1
        
        self.node_container.load_namespaces_and_nodes()
        return 1
 
    async def activate_namespaces_and_nodes_on_server(self) -> int:
        """
        Register all namespaces and nodes with the running server.

        Returns:
            int
        """
        if not self.node_container:
            self.logger.warning("Trying to activate namespaces and nodes on server, but no container exists. Abort activating namespaces and nodes.")
            return -1
        
        await self.node_container.activate_namespaces()
        await self.node_container.activate_nodes()
        return 1

    def get_server_node_tree(self) -> dict:
        """
        Return the current server node tree from the container.

        Returns:
            dict: Hierarchical node information.
        """
        if not self.loaded_by_xml:
            return self.node_container.get_node_tree()
        else:
            return {'node_tree': [[404]], 'server_node_information': [[404, 'Node-tree is not printable']]}
                
    async def export_server_model(self, output_file: str = None) -> int:
        """
        Export the current server address space to a NodeSet2 XML file
        using datatype aliases for built-in types.

        Args:
            output_file: Optional path to the output XML file.

        Returns:
            int: 1 on success, -1 on failure.
        """
        if not self.server or not self._running:
            self.logger.error("Server is not running, cannot export model.")
            return -1

        # Get all namespaces
        namespaces = await self.server.get_namespace_array()
        self.logger.info(f"Namespaces: {namespaces}")

        # Identify custom URIs (exclude standard OPC UA URIs)
        standard_ns = [
            "http://opcfoundation.org/UA/",
            "http://opcfoundation.org/UA/DI/",
            "http://opcfoundation.org/UA/ADI/",
            "http://opcfoundation.org/UA/MDIS/"
        ]
        custom_ns_indices = [i for i, ns in enumerate(namespaces) if ns not in standard_ns]
        self.logger.info(f"Custom namespace indices: {custom_ns_indices}")

        # Recursively collect all custom nodes under Objects
        root_node = self.server.nodes.objects

        async def collect_nodes(node: Node):
            nodes = []
            for child in await node.get_children():
                if child.nodeid.NamespaceIndex in custom_ns_indices:
                    nodes.append(child)
                    nodes.extend(await collect_nodes(child))
            return nodes

        custom_nodes = await collect_nodes(root_node)
        self.logger.info(f"Found {len(custom_nodes)} custom nodes.")

        # Build XML with NodeSet2 namespace
        nsmap = {
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "uax": "http://opcfoundation.org/UA/2008/02/Types.xsd",
            "xsd": "http://www.w3.org/2001/XMLSchema",
            None: "http://opcfoundation.org/UA/2011/03/UANodeSet.xsd"
        }
        root_elem = etree.Element("UANodeSet", nsmap=nsmap)

        # NamespaceUris block
        ns_uris_elem = etree.SubElement(root_elem, "NamespaceUris")
        for i in custom_ns_indices:
            uri_elem = etree.SubElement(ns_uris_elem, "Uri")
            uri_elem.text = namespaces[i]

        # Aliases block (datatype aliases only)
        aliases_elem = etree.SubElement(root_elem, "Aliases")
        for alias, nodeid in BUILTIN_DATATYPE_ALIASES.items():
            alias_elem = etree.SubElement(aliases_elem, "Alias", Alias=alias)
            # Only identifier, omit ns=0 for aliases
            alias_elem.text = nodeid

        # Write each node
        for node in custom_nodes:
            nc = await node.read_node_class()
            browse_name = await node.read_browse_name()
            display_name = await node.read_display_name()

            # Only export objects and variables
            tag = None
            if nc.name == "Object":
                tag = "UAObject"
            elif nc.name == "Variable":
                tag = "UAVariable"
            else:
                continue

            node_elem = etree.SubElement(root_elem, tag)
            node_elem.set("NodeId", f"ns={node.nodeid.NamespaceIndex};i={node.nodeid.Identifier}")
            node_elem.set("BrowseName", f"{browse_name.NamespaceIndex}:{browse_name.Name}")

            # DisplayName
            dn_elem = etree.SubElement(node_elem, "DisplayName")
            dn_elem.text = display_name.Text or browse_name.Name

            # ParentNodeId if present
            try:
                parent = await node.get_parent()
                if parent is not None:
                    node_elem.set("ParentNodeId", f"ns={parent.nodeid.NamespaceIndex};i={parent.nodeid.Identifier}")
            except Exception:
                pass

            # References block
            refs_elem = etree.SubElement(node_elem, "References")
            refs = await node.get_references()
            for ref in refs:
                ref_type_node = self.server.get_node(ref.ReferenceTypeId)
                ref_type_browse = await ref_type_node.read_browse_name()
                try:
                    target_nodeid = ref.NodeId
                except AttributeError:
                    continue

                ref_elem = etree.SubElement(
                    refs_elem,
                    "Reference",
                    ReferenceType=str(ref_type_browse.Name),
                    IsForward=str(ref.IsForward).lower()
                )
                ref_elem.text = f"ns={target_nodeid.NamespaceIndex};i={target_nodeid.Identifier}"

            # Set DataType for variables only
            if tag == "UAVariable":
                try:
                    dtype = await node.read_data_type()
                    dtype_node = self.server.get_node(dtype)
                    dtype_browse = await dtype_node.read_browse_name()
                    if dtype_browse.Name in BUILTIN_DATATYPE_ALIASES:
                        node_elem.set("DataType", dtype_browse.Name)
                except Exception:
                    # fallback: do nothing if datatype can't be read
                    pass

        # Determine output path
        if output_file is None:
            out_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "design_models")
            os.makedirs(out_folder, exist_ok=True)
            output_file = os.path.join(out_folder, "server_design_model.xml")

        tree = etree.ElementTree(root_elem)
        tree.write(output_file, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        self.logger.info(f"Exported NodeSet2 XML to {output_file}")
        return 1