## OPC-UA-Test-SoftwareOPC-UA-Test-Software
This repository contains test software for OPC-UA

```
OPC-UA-TEST-SOFTWARE/
├── Python_Test_1/                      # PubSub testing with RabbitMQ
│   ├── recieve.py                      # AMQP subscriber implementation
│   └── send.py                         # AMQP publisher implementation
|
├── Python_Test_2/                      # OPC UA server–client test framework
│   ├── functions/                      # Shared helper and user interaction logic
│   │   ├── __init__.py                 # Python package marker
│   │   ├── _test_userChoice.py         # Tests for user choice handling
│   │   └── userChoice.py               # User input / selection utilities
|   |
│   ├── Lib/                            # Shared libraries
│   │   └── dependencytree/             # Dependency tree generation utilities
│   │       ├── __init__.py             # Python package marker
│   │       ├── _test_dt.py             # Dependency tree test module
│   │       └── dependencytree.py       # Dependency tree implementation
|   | 
│   ├── light_weight_opcua/             # Minimal OPC UA client/server examples
│   │   ├── client.py                   # Lightweight OPC UA client
│   │   └── server.py                   # Lightweight OPC UA server
|   |
│   ├── OPC_UA_Client/                  # Full OPC UA client implementation
│   │   ├── client_config_files/        # Client configuration files
│   │   │   └── client_condif.json      # OPC UA client configuration
|   |   |
│   │   ├── Lib/                        # Client-specific libraries
│   │   │   └── dependencytree/         # Client dependency tree utilities
│   │   │       ├── __init__.py
│   │   │       ├── _test_dt.py
│   │   │       └── dependencytree.py
|   |   |
│   │   ├── __init__.py                 # Python package marker
│   │   └── asyncua_client.py           # asyncua-based OPC UA client
|   |
│   ├── OPC_UA_Server/                  # Full OPC UA server implementation
│   │   ├── design_models/              # OPC UA information model definitions
│   │   │   └── server_design_model.xml # Server node design model
|   |   |
│   │   ├── logs/                       # Runtime server logs
|   |   |
│   │   ├── server_config_files/        # Server configuration files
│   │   │   ├── __server_config.json    # Default / template server configuration
│   │   │   └── server_config.json      # Active OPC UA server configuration
|   |   |
│   │   ├── __init__.py                 # Python package marker
│   │   ├── asyncua_node_container.py   # OPC UA node container abstraction
│   │   ├── asyncua_server.py           # asyncua-based OPC UA server
│   │   ├── opc_ua_namespace.py         # OPC UA namespace handling
│   │   └── opc_ua_node.py              # OPC UA node definitions
|   |
│   ├── client_asyncua_main.py          # Main entry point for OPC UA client
│   ├── clock_get.py                    # Read time from OPC UA server
│   ├── clock_set.py                    # Write time to OPC UA server
│   └── server_asyncua_main.py          # Main entry point for OPC UA server
|
├── Test_3/                             # Additional / experimental tests
│   ├── asyncua_Compiler/               # Tools for compiling models into asyncua code
│   │   ├── DesignModels/               # High-level OPC UA design model definitions
│   │   |   └── DesignModel.json        # JSON-based OPC UA design model
|   |   |
│   │   ├── XML_Models/                 # OPC UA NodeSet XML definitions
│   │   |   └── custom.NodeSet2.xml     # Custom OPC UA NodeSet2 model
|   |   |
│   │   └── asyncua_compiler.py         # Compiler converting models to asyncua code
|   |
│   ├── asyncua_PubSub/                 # Experimental test from unreleased asyncua
│   │   ├── publisher_simple.py         # Publisher test script from asyncua
│   │   └── subscriber_simple.py        # Subscriber test script from asyncua
|   |
│   ├── builder/                        # Build configuration and automation utilities
│   │   ├── builder.py                  # Build orchestration script
│   │   ├── builds.json                 # Build definitions
│   │   └── test_builds.json            # Test build configurations
|   |
│   ├── CPP/                            # Native C++ OPC UA experiments
│   │   ├── build/                      # C++ build output directory
│   │   └── src/                        # C++ source files
│   │       ├── CMakeLists.tex          # CMake build configuration
│   │       ├── main.cpp                # C++ application entry point
│   │       ├── reader.cpp              # OPC UA data reader implementation
│   │       └── writer.cpp              # OPC UA data writer implementation
|   |
│   ├── Lib/                            # Third-party native libraries
│   │   └── open62541/                  # open62541 OPC UA C library
|   |
│   ├── PythonCPP/                      # Python ↔ C++ interoperability tests
│   │   ├── CPP/                        # C++ side of Python-C++ integration
│   │   │   ├── build/                  # C++ build output directory
│   │   │   └── src/                    # C++ source files
│   │   │       ├── CMakeLists.tex      # CMake build configuration
│   │   │       └── main.cpp            # C++ entry point for Python calls
|   |   |
│   │   └── Python/                     # Python interface to C++ code
│   │       └── Call_Cpp.py             # Python wrapper calling C++ binaries
|   |
│   └── UDP_PubSub/                     # UDP-based OPC UA PubSub experiments
│       ├── build/                      # UDP PubSub build output directory
│       └── src/                        # UDP PubSub source files
│           ├── CMakeLists.tex          # CMake build configuration
│           ├── publisher.c             # UDP PubSub publisher implementation
│           └── subscriber.c            # UDP PubSub subscriber implementation
|
├── .gitignore                          # Git ignore rules
├── .gitmodules                         # Git submodule configuration
├── LICENSE                             # Project license information
└── README.md                           # Project documentation

```