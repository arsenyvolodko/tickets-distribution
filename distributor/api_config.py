import os

from dotenv import load_dotenv

load_dotenv()

YANDEX_DISK_API_TOKEN = os.environ.get('YANDEX_DISK_API_TOKEN')
URL_TO_CREATE_FOLDER = 'https://cloud-api.yandex.net/v1/disk/resources?path={}'
URL_TO_COPY = 'https://cloud-api.yandex.net/v1/disk/public/resources/save-to-disk'
URL_TO_GET_INFO = 'https://cloud-api.yandex.net/v1/disk/resources'
URL_TO_READ = 'https://cloud-api.yandex.net/v1/disk/public/resources'
URL_TO_PUBLISH = 'https://cloud-api.yandex.net/v1/disk/resources/publish'
HEADERS = {
    'Authorization': f'OAuth {YANDEX_DISK_API_TOKEN}',
}
