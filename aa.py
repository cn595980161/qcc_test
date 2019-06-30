# import asyncio
# import threading
# import time
#
# from pyppeteer import launch, connect
#
#
# class Singleton(object):
#     launch_kwargs = {
#         # 控制是否为无头模式
#         "headless": False,
#         # chrome启动命令行参数
#         "args": [
#             # 浏览器代理 配合某些中间人代理使用
#             # "--proxy-server=http://127.0.0.1:8008",
#             # 最大化窗口
#             # "--start-maximized",
#             # 取消沙盒模式 沙盒模式下权限太小
#             "--no-sandbox",
#             # 不显示信息栏  比如 chrome正在受到自动测试软件的控制 ...
#             "--disable-infobars",
#             # log等级设置 在某些不是那么完整的系统里 如果使用默认的日志等级 可能会出现一大堆的warning信息
#             "--log-level=3",
#             # 设置UA
#             # "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
#         ],
#         # 用户数据保存目录 这个最好也自己指定一个目录
#         # 如果不指定的话，chrome会自动新建一个临时目录使用，在浏览器退出的时候会自动删除临时目录
#         # 在删除的时候可能会删除失败（不知道为什么会出现权限问题，我用的windows） 导致浏览器退出失败
#         # 然后chrome进程就会一直没有退出 CPU就会狂飙到99%
#         "userDataDir": "./userdata/tmp" + str(int(time.time())),
#         # "handleSIGINT": False,
#         # "handleSIGTERM": False,
#         # "handleSIGHUP": False
#     }
#     _instance_lock = threading.Lock()
#     # _browser = None
#     _wsEndpoint = None
#
#     def __init__(self):
#         # time.sleep(1)
#         print('init')
#
#     async def get_browser(self):
#         _browser = await launch(self.launch_kwargs)
#         # await _browser.newPage()
#         self._wsEndpoint = _browser.wsEndpoint
#
#     async def get_page(self):
#         _browser = await connect({'browserWSEndpoint': self._wsEndpoint})
#         # 创建一个匿名的浏览器上下文
#         _context = await _browser.createIncognitoBrowserContext()
#         # 在一个原生的上下文中创建一个新页面
#         return await _context.newPage()
#
#     @classmethod
#     def instance(cls, *args, **kwargs):
#         if not hasattr(Singleton, "_instance"):
#             with Singleton._instance_lock:
#                 if not hasattr(Singleton, "_instance"):
#                     Singleton._instance = Singleton(*args, **kwargs)
#
#                     asyncio.set_event_loop(asyncio.new_event_loop())
#                     loop = asyncio.get_event_loop()
#                     loop.run_until_complete(cls.get_browser(cls))
#
#         return Singleton._instance
#
#
# def task(arg):
#     obj = Singleton.instance()
#     print(obj)
#
#
# for i in range(2):
#     t = threading.Thread(target=task, args=[i, ])
#     t.start()
# time.sleep(20)
# # obj = Singleton.instance()
# # print(obj)
