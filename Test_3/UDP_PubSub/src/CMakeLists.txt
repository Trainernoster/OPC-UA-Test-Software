cmake_minimum_required(VERSION 3.15)
project(UDP_PubSub C)

add_subdirectory(${CMAKE_SOURCE_DIR}/../../lib/open62541 build_open62541 EXCLUDE_FROM_ALL)

set(CMAKE_C_STANDARD 11)

add_executable(Publisher publisher.c)
add_executable(Subscriber subscriber.c)

target_link_libraries(Publisher PRIVATE open62541)
target_link_libraries(Subscriber PRIVATE open62541)