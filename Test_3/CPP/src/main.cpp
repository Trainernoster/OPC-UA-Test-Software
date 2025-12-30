#include <open62541/server.h>
#include <iostream>
#include <csignal>

UA_Boolean running = true;

void stopHandler(int sig) {
    std::cout << "\nCtrl+C detected, stopping server..." << std::endl;
    running = false;
}

int main(void) {
    std::signal(SIGINT, stopHandler);
    std::signal(SIGTERM, stopHandler);

    UA_Server *server = UA_Server_new();
    UA_Server_runUntilInterrupt(server);
    
    std::cout << "Starting minimal OPC UA server. Press Ctrl+C to stop." << std::endl;
    
    while (running) {
        UA_Server_run_iterate(server, true);
    }
    
    UA_Server_delete(server);
    std::cout << "Server stopped." << std::endl;
    return 0;
}