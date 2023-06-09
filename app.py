import multiprocessing as mp
from fastapi import FastAPI
from playwright.sync_api import Locator, sync_playwright

app = FastAPI()

def func1(pagex: str, q: mp.Queue):
    url = "https://weverse.io/dreamcatcher/live/"+pagex
    with sync_playwright() as p:
        def handle_response(response):
            if "https://global.apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0" in response.url:
                json_data = response.json()
                json_array_video = json_data['videos']['list']
                json_array_captions = json_data.get('captions', {}).get('list', [])
                data = {
                    'video': json_array_video,
                    'captions': json_array_captions
                }
                q.put(data)
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("response", handle_response)
        page.goto(url, wait_until="networkidle")
        page.context.close()
        browser.close()
    return None

@app.get("/{page}")
def read_item(page: str):
    q = mp.Queue()
    process = mp.Process(target=func1, args=(page, q))
    process.start()
    response = q.get()
    process.join
    return response
