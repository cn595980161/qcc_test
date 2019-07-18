import asyncio
import json
import platform
import random
import time

import nest_asyncio
import pyppeteer
from flask import Flask, request, Response, jsonify
from syncer import sync

from qccweb import login_page, verify_page, mysql_task, check_verify

nest_asyncio.apply()

if platform.system() == "Linux":
    from pyvirtualdisplay import Display

app = Flask(__name__)


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


class WSGICopyBody(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        from io import BytesIO
        length = environ.get('CONTENT_LENGTH', '0')
        length = 0 if length == '' else int(length)

        body = environ['wsgi.input'].read(length)
        environ['body_copy'] = body
        environ['wsgi.input'] = BytesIO(body)

        # Call the wrapped application
        app_iter = self.application(environ, self._sr_callback(start_response))

        # Return modified response
        return app_iter

    def _sr_callback(self, start_response):
        def callback(status, headers, exc_info=None):
            # Call upstream start_response
            start_response(status, headers, exc_info)

        return callback


app.response_class = JsonResponse
app.wsgi_app = WSGICopyBody(app.wsgi_app)

max_wse = 2  # 启动几个浏览器
wse_list = []  # 存储browserWSEndpoint列表

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
        "--disable-gpu",
        # 设置UA
        # "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    ],
    # 用户数据保存目录 这个最好也自己指定一个目录
    # 如果不指定的话，chrome会自动新建一个临时目录使用，在浏览器退出的时候会自动删除临时目录
    # 在删除的时候可能会删除失败（不知道为什么会出现权限问题，我用的windows） 导致浏览器退出失败
    # 然后chrome进程就会一直没有退出 CPU就会狂飙到99%
    "userDataDir": "./userdata/tmp" + str(int(time.time())),
    "dumpio": True
    # # 'autoClose': False,
    # "handleSIGINT": False,
    # "handleSIGTERM": False,
    # "handleSIGHUP": False
}


async def init(_loop):
    for i in range(max_wse):
        print(i)
        # browser = await pyppeteer.launch(launch_kwargs)
        browser = await pyppeteer.launch(headless=False,
                                         args=[
                                             # '--disable-extensions',
                                             # '--hide-scrollbars',
                                             # '--disable-bundled-ppapi-flash',
                                             # '--mute-audio',
                                             '--disable-gpu',
                                             # '--disable-setuid-sandbox',
                                             # '--no-first-run',
                                             '--no-sandbox',
                                             # '--no-zygote',
                                         ],
                                         dumpio=True,
                                         loop=_loop,
                                         userDataDir="./userdata/tmp" + str(int(time.time())))
        browserWSEndpoint = browser.wsEndpoint
        wse_list.append(browserWSEndpoint)

    print(wse_list)


async def login(username, password):
    tmp = random.randint(0, max_wse - 1)
    browserWSEndpoint = wse_list[tmp]
    browser = await pyppeteer.connect(browserWSEndpoint=browserWSEndpoint)
    # page = await browser.newPage()
    _context = await browser.createIncognitoBrowserContext()
    # 在一个原生的上下文中创建一个新页面
    page = await _context.newPage()

    cookies = await login_page(username, password, page)

    # await page.goto('http://www.baidu.com')
    # content = await page.content()
    # print(content.replace('\n', ''))
    # await page.screenshot(path='example.png')
    await page.close()
    return cookies


async def verify(username, pwd, cookies):
    # 判断页面是否出现验证码
    if await check_verify(username, cookies):
        tmp = random.randint(0, max_wse - 1)
        browserWSEndpoint = wse_list[tmp]
        browser = await pyppeteer.connect(browserWSEndpoint=browserWSEndpoint)
        while True:
            pages = await browser.pages()
            print('页面个数:', len(pages))
            if len(pages) <= 2:

                # page = await browser.newPage()
                _context = await browser.createIncognitoBrowserContext()
                # 在一个原生的上下文中创建一个新页面
                page = await _context.newPage()

                await verify_page(username, pwd, cookies, page)

                await page.close()
                break
            else:
                await asyncio.sleep(5)


@app.route('/')
def hello_world():
    return 'Hello Flask!'


@app.route('/login', methods=['GET'])
def simulated_login():
    if request.method == 'GET':
        args = request.args.to_dict()

        username = args['username']
        password = args['password']
        try:
            loop.run_until_complete(login(username, password))
            # asyncio.ensure_future(login(username, password))
            # sync(login(username, password))
        except Exception as e:
            return str(e)
        else:
            return 'ok'


@app.route('/verify', methods=['POST'])
def simulated_verify():
    if request.method == 'POST':
        # args = request.form.to_dict()
        # cookies = args['cookies']
        body = request.environ['body_copy'].decode('utf-8', 'replace')
        body = json.loads(body)
        print(body)
        try:
            loop.run_until_complete(verify(body['username'], body['pwd'], body['cookies']))
            # asyncio.ensure_future(verify(body['username'], body['pwd'], body['cookies']))
            # sync(verify(body['username'], body['pwd'], body['cookies']))
        except Exception as e:
            return str(e)
        else:
            return 'ok'


if __name__ == '__main__':
    if platform.system() == "Linux":
        display = Display(visible=0, size=(800, 600))
        display.start()

    loop = asyncio.get_event_loop()

    # mysql开启
    asyncio.ensure_future(mysql_task(loop))

    sync(init(loop))

    app.run(host='0.0.0.0',  # 设置ip，默认127.0.0.1
            port=None,  # 设置端口，默认5000
            debug=False)  # 设置debug=True是为了让代码修改实时生效，而不用每次重启加载

    print('--------------------------------------------------------------------')
