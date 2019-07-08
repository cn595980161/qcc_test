#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyppeteer import launch
from syncer import sync


async def test(browser):
    print('连接:', browser)
    # browser = await connect(browserWSEndpoint=endpoint)
    print(browser)
    page = await browser.newPage()
    await page.goto('http://www.baidu.com')
    content = await page.content()
    print(content.replace('\n', ''))
    # await page.close()


async def main() -> None:
    browsers = []
    for i in range(3):
        browser = await launch(headless=False, args=['--no-sandbox'])
        # print(browser.wsEndpoint, flush=True)
        # endpoint = browser.wsEndpoint
        # browser1 = await connect(browserWSEndpoint=endpoint)
        browsers.append(browser)

    # loop = asyncio.get_event_loop()
    for browser in browsers:
        sync(test(browser))

    # print(browsers)
    # for browser in browsers:
    #     print('连接:', browser)
    #     # browser = await connect(browserWSEndpoint=endpoint)
    #     print(browser)
    #     page = await browser.newPage()
    #     await page.goto('http://www.baidu.com')
    #     content = await page.content()
    #     print(content.replace('\n', ''))
    #     await page.close()
    #     # await browser.close()
    #     # await browser.disconnect()

    # print(browsers)
    # for browser in browsers:
    #     print('连接:', browser)
    #     # browser = await connect(browserWSEndpoint=endpoint)
    #     print(browser)
    #     page = await browser.newPage()
    #     await page.goto('http://www.baidu.com')
    #     content = await page.content()
    #     print(content.replace('\n', ''))
    #     await page.close()
    #     # await browser.close()
    #     # await browser.disconnect()


# asyncio.get_event_loop().run_until_complete(main())
sync(main())
