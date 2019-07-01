import asyncio
import threading
import time
from syncer import sync

from pyppeteer import launch


class PuppeteerPool(object):
    lock = threading.Lock()
    capacity = 5
    STAT_RUNNING = 1

    STAT_CLODED = 2

    stat = STAT_RUNNING

    _browsers = ''

    inner_queue = asyncio.Queue()

    web_list = []

    async def configure(self):
        launch_kwargs = {
            # 控制是否为无头模式
            "headless": False,
            # chrome启动命令行参数
            "args": [
                # 浏览器代理 配合某些中间人代理使用
                # "--proxy-server=http://127.0.0.1:8008",
                # 最大化窗口
                # "--start-maximized",
                # 取消沙盒模式 沙盒模式下权限太小
                "--no-sandbox",
                # 不显示信息栏  比如 chrome正在受到自动测试软件的控制 ...
                "--disable-infobars",
                # log等级设置 在某些不是那么完整的系统里 如果使用默认的日志等级 可能会出现一大堆的warning信息
                "--log-level=3",
                # 设置UA
                # "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            ],
            # 用户数据保存目录 这个最好也自己指定一个目录
            # 如果不指定的话，chrome会自动新建一个临时目录使用，在浏览器退出的时候会自动删除临时目录
            # 在删除的时候可能会删除失败（不知道为什么会出现权限问题，我用的windows） 导致浏览器退出失败
            # 然后chrome进程就会一直没有退出 CPU就会狂飙到99%
            "userDataDir": "./userdata/tmp" + str(int(time.time())),
            # "handleSIGINT": False,
            # "handleSIGTERM": False,
            # "handleSIGHUP": False
        }
        self._browsers = await launch(launch_kwargs)

    async def get(self):
        await self.check_running()
        print('获取。。。', self.inner_queue)
        if not self.inner_queue.empty():
            item = self.inner_queue.get_nowait()
            print('item', item)
            if item is not None:
                return item
        if len(self.web_list) < self.capacity:
            self.lock.acquire()
            if len(self.web_list) < self.capacity:
                await self.configure()
                print('config', self._browsers)
                self.inner_queue.put_nowait(self._browsers)
                self.web_list.append(self._browsers)

            self.lock.release()

        return self.inner_queue.get_nowait()

    async def return_to_pool(self, browser):
        print('回收browser')
        await self.check_running()

        # for page in await browser.pages():
        #     await page.close()

        # await asyncio.wait([
        #     browser.disconnect(),
        #     wait_event(browser, 'disconnected')
        # ])

        self.inner_queue.put_nowait(browser)
        print(self.inner_queue)

    async def check_running(self):
        if self.stat != self.STAT_RUNNING:
            raise Exception("Already closed!");

    def wait_event(self, emitter, event_name):
        fut = asyncio.get_event_loop().create_future()

        def set_done(arg=None):
            fut.set_result(arg)

        emitter.once(event_name, set_done)
        return fut


async def test(i):
    print('test')
    browser = await PuppeteerPool().get()
    print(i, '>>', browser)
    # targets = browser.targets()
    # for target in browser.targets():
    #     print(target.type)
    # print('targets', targets)
    # _context = await browser.createIncognitoBrowserContext()
    # # 在一个原生的上下文中创建一个新页面
    # page = await _context.newPage()
    page = await browser.newPage()
    # await asyncio.sleep(10)
    # time.sleep(5)
    await page.goto('https://www.baidu.com')
    content = await page.content()
    print(content.replace('\n', ''))
    await asyncio.sleep(5)
    await PuppeteerPool().return_to_pool(browser)


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # # for i in range(10):
    # #     loop.run_until_complete(test(i + 1))
    #
    # tasks = [asyncio.ensure_future(test(i + 1)) for i in range(10)]
    #
    # tasks = asyncio.gather(*tasks)
    # # tasks = asyncio.wait(tasks)
    # loop.run_until_complete(tasks)
    sync(test(1))
    sync(test(2))
    sync(test(3))
