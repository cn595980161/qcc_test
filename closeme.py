#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

from pyppeteer import launch, connect


async def main() -> None:
    wsEndpoints = []
    for i in range(10):
        browser = await launch(headless=False, args=['--no-sandbox'])
        # print(browser.wsEndpoint, flush=True)
        endpoint = browser.wsEndpoint
        # browser1 = await connect(browserWSEndpoint=endpoint)
        wsEndpoints.append(endpoint)

    print(wsEndpoints)
    for endpoint in wsEndpoints:
        print('连接:', endpoint)
        browser = await connect(browserWSEndpoint=endpoint)
        print(browser)
        page = await browser.newPage()
        await page.goto('http://www.baidu.com')
        await page.close()
        await browser.close()



asyncio.get_event_loop().run_until_complete(main())
