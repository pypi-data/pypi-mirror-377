import time

from param_server.client import AsyncParameterClient, ParameterClient

HOST = "localhost"
PORT = 8888
TIMEOUT = 2.0


PATH = "camera.gain"
VALUE = 2.5


async def main():
    print("Asynchronous client:")
    async with AsyncParameterClient(HOST, PORT) as client:
        async def aset_fn():
            await client.set(PATH, VALUE)

        async def aget_fn():
            await client.get(PATH)

        async def aping_fn():
            await client.ping()

        for cmd, fn in [
            ("set", aset_fn),
            ("get", aget_fn),
            ("ping", aping_fn),
        ]:
            t0 = time.perf_counter()
            for i in range(1000):
                await fn()
            t1 = time.perf_counter()
            print(f"{cmd} took {(t1-t0):.2f} ms")
            
    print("Synchronous client:")
    with ParameterClient(HOST, PORT) as client:
        def set_fn():
            client.set(PATH, VALUE)

        def get_fn():
            client.get(PATH)

        def ping_fn():
            client.ping()

        for cmd, fn in [
            ("set", set_fn),
            ("get", get_fn),
            ("ping", ping_fn),
        ]:
            t0 = time.perf_counter()
            for i in range(1000):
                fn()
            t1 = time.perf_counter()
            print(f"{cmd} took {(t1-t0):.2f} ms")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
