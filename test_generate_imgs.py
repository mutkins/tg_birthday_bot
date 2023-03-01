import asyncio
import aiohttp
import time


def write_image(data):
    filename = f'img/{format(int(time.time()*1000))}.png'
    with open(filename, 'wb') as file:
        file.write(data)


async def fetch_content(url,session):
    async with session.get(url, allow_redirects=True) as response:
        data = await response.read()
        write_image(data)


async def main():
    url = "https://picsum.photos/512"
    tasks = []

    async with aiohttp.ClientSession() as session:
        for i in range(400):
            task = asyncio.create_task(fetch_content(url, session))
            tasks.append(task)
        await asyncio.gather(*tasks)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
