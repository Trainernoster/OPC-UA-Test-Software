import asyncio
from asyncua import Server
from asyncua import ua


async def main():
    server = Server()

    await server.init()
    server.set_endpoint("opc.tcp://192.168.50.52:4840/freeopcua/server/")

    uri = "http://example.org/asyncua"
    idx = await server.register_namespace(uri)

    myobj = await server.nodes.objects.add_object(idx, "MyObject")

    temp_var = await myobj.add_variable(idx, "Temperature", 25.0)
    await temp_var.set_writable()

    print("Server started at opc.tcp://localhost:4840/freeopcua/server/")
    print("Variable: MyObject.Temperature")

    async with server:
        while True:
            temp_value = await temp_var.read_value()
            print(f"Current temperature: {temp_value:.2f}")
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
