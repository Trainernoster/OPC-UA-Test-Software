import asyncio
from asyncua import Client


async def main():
    url = "opc.tcp://192.168.50.52:4840/freeopcua/server/"
    async with Client(url=url) as client:
        print("Connected to server")

        root = client.nodes.root
        objects = client.nodes.objects

        var = await objects.get_child(["2:MyObject", "2:Temperature"])

        while True:
            value = await var.read_value()
            print(f"Read temperature: {value:.2f}")

            new_value = round(value + 0.1, 2)
            await var.write_value(new_value)
            print(f"Updated temperature to: {new_value:.2f}")

            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
