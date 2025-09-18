from param_server.client import AsyncParameterClient


async def main():
    async with AsyncParameterClient(host="localhost", port=8888, auto_reconnect=True) as client:
        await client.set("/store_list/numbers", [1, 2, 3, 4, 5])
        await client.set("/list_squared", [[1, 2], [3, 4]])
        numbers = await client.get("/store_list/numbers")
        lists = await client.get("/list_squared")
        print(f"Stored and retrieved list: {numbers}")
        print(f"Stored and retrieved nested list: {lists}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
