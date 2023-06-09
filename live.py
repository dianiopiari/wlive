from fastapi import FastAPI
from playwright.async_api import async_playwright

app = FastAPI()

async def func1(pagex: str):
    url = "https://weverse.io/dreamcatcher/live/" + pagex
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        response_data = []

        async def handle_response(response):
            if "https://global.apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0" in response.url:
                json_data = await response.json()
                json_array_video = json_data['videos']['list']
                json_array_captions = json_data.get('captions', {}).get('list', [])
                data = {
                    'video': json_array_video,
                    'captions': json_array_captions
                }
                response_data.append(data)

        page.on("response", handle_response)
        await page.goto(url, wait_until="networkidle")
        await page.context.close()
        await browser.close()

    return response_data

@app.get("/{page}")
async def read_item(page: str):
    data = await func1(page)
    return data
