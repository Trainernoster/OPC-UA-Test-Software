used packages:
o asyncua
o nympy

Python_Test_2/
│
├── client_asyncua_main.py              # Main client-side entry point using asyncua to connect to an OPC UA server
├── server_asyncua_main.py              # Main server-side entry point for starting the OPC UA server
├── clock_get.py                        # Script to read time values from the OPC UA server
├── clock_set.py                        # Script to write time values to the OPC UA server
├── RAEDME.md
│
├── functions/                          # General-purpose function library
│   ├── userChoice.py                   # Handles user input/selection logic
│   ├── _test_userChoice.py             # Unit tests for userChoice functions
│   └── __init__.py
│
├── Lib/                                # Shared libraries or modules
│   └── dependencytree/                 
│       ├── dependencytree.py           # Implements dependency tree management or visualization
│       ├── _test_dt.py                 # Unit tests for dependency tree module
│       └── __init__.py
│
├── light_weight_opcua/                 # Lightweight, minimal OPC UA implementations
│   ├── client.py                       # Simple OPC UA client logic (non-async version)
│   └── server.py                       # Lightweight OPC UA server logic
│
├── OPC_UA_Client/                      # Full-featured OPC UA client implementation
│   ├── asyncua_client.py               # Asynchronous OPC UA client with node management and read/write methods
│   ├── client_config_files/
│   │   └── client_config.json          # Client configuration (endpoint, loadable nodes)
│   ├── Lib/                            # Client-side dependency tree utilities
│   │   └── dependencytree/
│   │       ├── dependencytree.py       # Implements dependency tree management or visualization
│   │       ├── _test_dt.py             # Unit tests for dependency tree module
│   │       └── __init__.py
│   └── __init__.py
│
└── OPC_UA_Server/                      # Full-featured OPC UA server implementation
    ├── asyncua_server.py               # Main server class for asyncua, handles lifecycle and logging
    ├── asyncua_node_container.py       # Container class managing all namespaces and nodes
    ├── opc_ua_namespace.py             # Handles namespace creation and linking
    ├── opc_ua_node.py                  # Defines and configures OPC UA nodes and their data
    ├── server_config_files/
    │   ├── server_config.json          # Default server configuration
    │   └── __server_config.json        # Possibly backup or test configuration
    ├── logs/                           # Server log files
    └── __init__.py
