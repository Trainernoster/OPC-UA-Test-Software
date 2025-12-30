cmake_minimum_required(VERSION 3.15)
project(PubSubCPP)

add_subdirectory(${CMAKE_SOURCE_DIR}/../../lib/open62541 build_open62541 EXCLUDE_FROM_ALL)

add_executable(Server main.cpp)
add_executable(ClientReader reader.cpp)
add_executable(ClientWriter writer.cpp)

target_link_libraries(Server PRIVATE open62541)
target_link_libraries(ClientReader PRIVATE open62541)
target_link_libraries(ClientWriter PRIVATE open62541)