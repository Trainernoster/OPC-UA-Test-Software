import asyncio
from asyncua import Server

async def run_server():
    server = Server()

    # 1. Initialize the server (MUST be done first!)
    await server.init()

    # 2. Set endpoint and server name
    server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")
    server.set_server_name("Test OPC UA Server")

    # 3. Register custom namespace
    ns_idx = await server.register_namespace("http://mynodes.local")
    print("Namespace index:", ns_idx)

    # 4. Add an object and a variable
    device_node = await server.nodes.objects.add_object(ns_idx, "Device1")
    pressure_node = await device_node.add_variable(ns_idx, "Pressure", 1)
    await pressure_node.set_writable()  # make it readable and writable
    print("Pressure node NodeId:", pressure_node.nodeid)

    # 5. Start the server
    await server.start()
    print("Server running at opc.tcp://localhost:4840/freeopcua/server/")

    try:
        # 6. Keep server alive
        while True:
            await asyncio.sleep(1)
    finally:
        # Stop server cleanly on exit
        await server.stop()
        print("Server stopped")

if __name__ == "__main__":
    asyncio.run(run_server())
