import aiohttp
from .api_config import URL_TO_COPY, HEADERS, URL_TO_CREATE_FOLDER, URL_TO_PUBLISH, URL_TO_GET_INFO


async def create_folder(path):
    async with aiohttp.ClientSession() as session:
        async with session.put(URL_TO_CREATE_FOLDER.format(path), headers=HEADERS) as response:
            if response.status != 201:
                if response.status == 409:
                    res = await response.json()
                    if res['error'] == 'DiskPathPointsToExistentDirectoryError':
                        return
                    raise AssertionError(f"Cannot create folder, status code: {response.status}")
                raise AssertionError(f"Cannot create folder, status code: {response.status}")


async def create_folder_path(path):
    folders = path.split('/')
    cur = ""
    for folder in folders:
        cur += f"%2F{folder}"
        await create_folder(cur)


async def copy_file(public_key: str, file_name: str, new_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url=URL_TO_COPY,
                params={
                    "public_key": public_key,
                    "path": f'/{file_name}',
                    "save_path": f'/{new_path}',
                    "force_async": str(True)
                },
                headers=HEADERS
        ) as response:
            if not (response.status == 202 or response.status == 201):
                raise AssertionError(f"Cannot copy file, status code: {response.status}")


async def open_dir(path: str):
    async with aiohttp.ClientSession() as session:
        async with session.put(URL_TO_PUBLISH, headers=HEADERS, params={"path": path}) as response:
            if response.status != 200:
                raise AssertionError(f"Cannot open folder, status code: {response.status}")


async def get_public_url(path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL_TO_GET_INFO,
                               headers=HEADERS,
                               params={
                                   "path": path,
                                   'fields': 'public_url'
                               }) as response:
            if response.status != 200:
                raise AssertionError(f"Cannot get public url, status code: {response.status}")
            return (await response.json())['public_url']


async def create_and_open_folder(path: str) -> str:
    await create_folder_path(path)
    await open_dir(path)
    new_url = await get_public_url(path)
    return new_url
