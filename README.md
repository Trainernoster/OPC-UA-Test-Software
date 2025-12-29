## Licenses

This project uses the following third-party libraries:

- **asyncua** — GNU Lesser General Public License v3.0 or later (LGPL-3.0+)
- **pika** — BSD 3-Clause License
- **lxml** — BSD 3-Clause License

All third-party software remains licensed under its respective license.  
Copies of the LGPL-3.0 and BSD 3-Clause license texts are included with this project.  
If modified versions of LGPL-licensed components are distributed, the corresponding source code must be made available in accordance with the LGPL.

## OPC-UA-Test-SoftwareOPC-UA-Test-Software
This repository contains test software for OPC-UA

OPC-UA-TEST-SOFTWARE/
├── Python_Test_1/                      # PubSub testing with RabbitMQ
│   ├── recieve.py                      # AMQP subscriber implementation
│   └── send.py                         # AMQP publisher implementation
├── Python_Test_2/                      # OPC UA server–client test framework
│   ├── functions/                      # Shared helper and user interaction logic
│   │   ├── __init__.py                 # Python package marker
│   │   ├── _test_userChoice.py         # Tests for user choice handling
│   │   └── userChoice.py               # User input / selection utilities
│   ├── Lib/                            # Shared libraries
│   │   └── dependencytree/             # Dependency tree generation utilities
│   │       ├── __init__.py             # Python package marker
│   │       ├── _test_dt.py             # Dependency tree test module
│   │       └── dependencytree.py       # Dependency tree implementation
│   ├── light_weight_opcua/             # Minimal OPC UA client/server examples
│   │   ├── client.py                   # Lightweight OPC UA client
│   │   └── server.py                   # Lightweight OPC UA server
│   ├── OPC_UA_Client/                  # Full OPC UA client implementation
│   │   ├── client_config_files/        # Client configuration files
│   │   │   └── client_condif.json      # OPC UA client configuration
│   │   ├── Lib/                        # Client-specific libraries
│   │   │   └── dependencytree/         # Client dependency tree utilities
│   │   │       ├── __init__.py
│   │   │       ├── _test_dt.py
│   │   │       └── dependencytree.py
│   │   ├── __init__.py                 # Python package marker
│   │   └── asyncua_client.py           # asyncua-based OPC UA client
│   ├── OPC_UA_Server/                  # Full OPC UA server implementation
│   │   ├── design_models/              # OPC UA information model definitions
│   │   │   └── server_design_model.xml # Server node design model
│   │   ├── logs/                       # Runtime server logs
│   │   ├── server_config_files/        # Server configuration files
│   │   │   ├── __server_config.json
│   │   │   └── server_config.json
│   │   ├── __init__.py                 # Python package marker
│   │   ├── asyncua_node_container.py   # Node container abstraction
│   │   ├── asyncua_server.py           # asyncua-based OPC UA server
│   │   ├── opc_ua_namespace.py         # OPC UA namespace handling
│   │   └── opc_ua_node.py              # OPC UA node definitions
│   ├── client_asyncua_main.py          # Main entry point for OPC UA client
│   ├── clock_get.py                    # Read time from OPC UA server
│   ├── clock_set.py                    # Write time to OPC UA server
│   └── server_asyncua_main.py          # Main entry point for OPC UA server
├── Test_3/                             # Additional / experimental tests
├── .gitignore                          # Git ignore rules
└── README.md                           # Project documentation
