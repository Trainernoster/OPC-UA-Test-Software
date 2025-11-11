import asyncio
import os
import json

from pathlib import Path
from asyncua import Client

class OPCUAClient:
    
    def __init__(
            self,
            _endpoint: str = "opc.tcp://192.168.50.52:4840/freeopcua/server/",
            _client_config_path: str = "client_config_files",
            _client_config_file: str = "client_config.json",
            _use_config_file: bool = None
        ) -> None:
        """ Initialise OPC UA client class with given parameters or configuration file. """

        """
            Attributes:                 
                self                    obj                     self
                _endpoint               str                     holds endpoint string
                _client_config_path     str                     path to the config file
                _client_config_file     str                     name of the config file
                _use_config_file        bool                    if Ture use a config file for the server
            
            Return value:
                None 
        """
        self.endpoint = _endpoint
        self.client_config_path = _client_config_path
        self.client_config_file = _client_config_file
        self.use_config_file = _use_config_file
        self.module_path = Path(__file__).parent                    # Get module path

        self.loadable_nodes: list = []
        self.loaded_nodes: list = []
        self.objects = None
        self.client: Client | None = None

        if self.use_config_file:
            with open(os.path.join(self.module_path, self.client_config_path, self.client_config_file), 'r') as config_file:
                config_data = json.load(config_file)
                self.endpoint = config_data.get("endpoint", self.endpoint)                      # Get endpoint
                self.loadable_nodes = config_data.get("loadable_nodes")
    
    async def start_Client(self):
        self.client = Client(self.endpoint)
        await self.client.connect()
        self.objects = self.client.nodes.objects
        if self.loadable_nodes is not None:
            i = 1
            for loadable_node in self.loadable_nodes:
                await self.add_node(_browse_name = loadable_node.get("browseName"), _identifier = loadable_node.get("i") , _namespace_index = loadable_node.get("i"))

    async def add_node(self, _browse_name: str = None , _namespace_index: int = None, _identifier: int = None) -> int:

        async def find_node_by_name(_parent_node, _name_to_find):
            children = await _parent_node.get_children()
            for child in children:
                bname = await child.read_browse_name()
                if bname.Name == _name_to_find:
                    return child
                result = await find_node_by_name(child, _name_to_find)
                if result is not None:
                    return result
            return None

        async def get_node_by_id(_ns: int, _i: int):
            node_id_str = f"ns={_ns};i={_i}"
            result = self.client.get_node(node_id_str)
            return result
        
        node = None
        if self.client is None:
            print("Client not connected.")
            return -1
        elif _browse_name is not None:
            node = await find_node_by_name(_parent_node= self.objects, _name_to_find= _browse_name)
        elif _namespace_index is not None and _identifier is not None:
            node = await get_node_by_id(_ns= _namespace_index, _i= _identifier)
        else:
            print("Information for node is wrong.")
            return -1
        
        if node:
            bname = await node.read_browse_name()
            #print(f"found node, browsename: {bname.Name}, namesapce: {node.nodeid.NamespaceIndex}, identifier: {node.nodeid.Identifier}")
            self.loaded_nodes.append([bname.Name, node.nodeid.NamespaceIndex, node.nodeid.Identifier, node])
            return 1
        else:
            print(f"Node not found, browsename: {_browse_name}, namesapce: {_namespace_index}, identifier: {_identifier}")
            return -1
    
    def get_node(self, _browse_name: str = None , _namespace_index: int = None, _identifier: int = None) -> object:
        if self.loaded_nodes == []:
            print("No nodes were loaded.")
            return -1
        for node in self.loaded_nodes:
            if _browse_name == node[0]:
                return node[3]
            elif _namespace_index == node[1] and _identifier == node[2]:
                return node[3]
        print("No loaded node was found.")
        return -1
    
    async def get_value(self, _node) -> object:
        try:
            return await _node.read_value()
        except Exception as e:
            print(f"Get value not possible: {e}")

    async def set_value(self, _node, _value) -> int:
        try:
            current_value = await _node.read_value()
            if not isinstance(_value, type(current_value)):
                print(f"Type mismatch: Node value type is {type(current_value).__name__}, "
                    f"but provided value type is {type(_value).__name__}")
                return -1
            return await _node.write_value(_value)
        except Exception as e:
            print(f"Not possible to set value: {e}")