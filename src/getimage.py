from bing_image_urls import bing_image_urls
import requests
from io import BytesIO

def download_image(query):
    urls = bing_image_urls(query, limit=3)
    for url in urls:
        resp = requests.get(url, stream=True)
        if resp.status_code == 200:
            filename = url.split("/")[-1]
            if url.split(".")[-1] not in ['png', 'jpg', 'jpeg']:
                filename += ".png"
            return BytesIO(resp.content), filename
