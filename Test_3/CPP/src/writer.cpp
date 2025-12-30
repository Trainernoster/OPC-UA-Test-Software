#include <open62541/server.h>
#include <iostream>
#include <csignal>

UA_Boolean running = true;

void stopHandler(int sig) {
    std::cout << "\nCtrl+C detected, stopping server..." << std::endl;
    running = false;
}

int main(void) {
    std::cout << "Not implemented yet" << std::endl;
    return 0;
}