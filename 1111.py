import asyncio
import time

from pyppeteer import launch, connect
from syncer import sync

if __name__ == '__main__':
    loop = asyncio.new_event_loop()


    async def inner(_loop) -> None:
        browser = await launch(headless=False,
                               args=['–disable-gpu',
                                     '–disable-dev-shm-usage',
                                     '–disable-setuid-sandbox',
                                     '–no-first-run',
                                     '–no-sandbox',
                                     '–no-zygote',
                                     '–single-process'
                                     ],
                               loop=_loop)
        page = await browser.newPage()
        await page.goto('http://www.baidu.com')
        result = await page.evaluate('() => 1 + 2')
        print(result)
        await page.close()
        await browser.close()


    @sync
    async def test_connect():
        browser = await launch(headless=False, args=['--no-sandbox'], userDataDir="./userdata/tmp" + str(int(time.time())))
        browser2 = await connect(browserWSEndpoint=browser.wsEndpoint)
        page = await browser2.newPage()
        result = await page.evaluate('() => 7 * 8')
        print(result)

        await browser2.disconnect()
        page2 = await browser.newPage()
        result = await page2.evaluate('() => 7 * 6')
        print(result)
        await browser.close()


    loop.run_until_complete(inner(loop))
    # loop.run_until_complete(test_connect())
