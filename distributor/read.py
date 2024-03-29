import aiohttp

from .api_config import HEADERS, URL_TO_READ


async def check_response(code: int):
    if code == 404:
        raise FileNotFoundError(
            "Что-то пошло не так. Убедитесь, что ссылка корректна и папка доступна для просмотра по данной ссылке.")
    if code >= 500:
        raise FileNotFoundError("Проблемы со стороны Яндекс диска, попробуйте позже.")
    if code != 200:
        raise FileNotFoundError("Что-то пошло не так, попробуйте еще раз.")


async def extract_names(response):
    try:
        files = [file['name'] for file in response['_embedded']['items'] if file['type'] == 'file']
        if not len(files):
            raise FileNotFoundError()
    except Exception:
        raise FileNotFoundError(
            "Похоже, папка пуста или не содержит файлы не в том формате. Убедитесь, что файлы с билетами лежат в папке, на которую указывает ссылка.")
    return files


async def get_file_names(link: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL_TO_READ,
                               params={'public_key': link,
                                       'fields': '_embedded.items',
                                       'limit': 10000},
                               headers=HEADERS) as response:

            await check_response(response.status)
            return await extract_names(await response.json())

