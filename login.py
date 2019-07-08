# -*- coding: utf-8 -*-
import asyncio
import logging
import platform
import random
import time
import uuid

from pyppeteer import launch
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, retry_if_result

from Mysql import Mysql
from yima import get_phone, get_message

if platform.system() == "Linux":
    pass

logging.basicConfig(filename='log.txt', level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

result = False

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
        # "--no-sandbox",
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
    "dumpio": True,
    # # 'autoClose': False,
    # "handleSIGINT": False,
    # "handleSIGTERM": False,
    # "handleSIGHUP": False
}

# exe_js.py

js1 = '''() =>{
    
           Object.defineProperties(navigator,{
             webdriver:{
               get: () => false
             }
           })
        }'''

js2 = '''() => {
        alert (
            window.navigator.webdriver
        )
    }'''

js3 = '''() => {
        window.navigator.chrome = {
    runtime: {},
    // etc.
  };
    }'''

js4 = '''() =>{
Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en']
    });
        }'''

js5 = '''() =>{
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5,6],
  });
        }'''


def screen_size():
    """使用tkinter获取屏幕大小"""
    import tkinter
    tk = tkinter.Tk()
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    return width, height


def input_time_random():
    return random.randint(10, 15)


def retry_if_result_none(result):
    print('result:', result)
    return result is None


def return_last_value(retry_state):
    """return the result of the last call attempt"""
    return retry_state.outcome.result()


@retry(retry=(retry_if_result(retry_if_result_none) | retry_if_exception_type()), retry_error_callback=return_last_value, stop=stop_after_attempt(5), wait=wait_fixed(1))
async def mouse_slide(page=None):
    # await asyncio.sleep(3)
    print('开始移动')
    try:

        await page.waitForSelector(".nc_iconfont.btn_slide")
        await page.hover('.nc_iconfont.btn_slide')
        await page.mouse.down()

        await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})
        await page.mouse.up()
        await page.screenshot({'path': './screenshot/headless-slide-result.png'})
    except Exception as e:
        print(e, '     :slide login False')
        return None
    else:
        # await page.querySelector('.nc-lang-cnt')
        await page.waitForFunction('!document.querySelector(".nc_iconfont.btn_slide")')
        # await asyncio.sleep(3)
        slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')
        if slider_again != '验证通过':
            print('没通过:', slider_again)
            if slider_again == '哎呀，出错了，点击刷新再来一次':
                await page.click('#dom_id > div > span > a')

            return None
            # raise RuntimeError(slider_again)
        else:
            await page.screenshot({'path': './screenshot/headless-slide-result.png'})
            print('验证通过')
            return slider_again


def cancel_task(p_task, type):
    global result
    print(type)
    # p_task.remove_done_callback()
    p_task.set_result(None)
    # p_task.cancel()
    result = True


async def get_cookie(page=None):
    cookies_list = await page.cookies()
    cookies = ''
    for cookie in cookies_list:
        str_cookie = '{0}={1};'
        str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'))
        cookies += str_cookie
    print(cookies)
    return cookies


async def register():
    browser = await launch(launch_kwargs)
    page = await browser.newPage()
    await page.setViewport(viewport={'width': 1000, 'height': 800})
    print('page', page)

    await page.goto('https://www.qichacha.com/user_register')

    await page.evaluate(js1)
    await page.evaluate(js3)
    await page.evaluate(js4)
    await page.evaluate(js5)

    page.waitForSelector('#dom_id')
    slider = await page.querySelector('#dom_id')

    if slider:
        print('出现滑块情况判定')
        await page.screenshot({'path': './screenshot/headless-login-slide.png'})
        print("3.操作【验证码】")
        flag = await mouse_slide(page=page)
        print(flag)
        if flag:

            # 获取手机号
            print("1.获取【手机号】")
            phone = get_phone()

            # 输账号
            print("2.输入【手机号码】{0}".format(phone))
            await page.type('#phone', phone, {'delay': input_time_random() - 50})

            print("4.点击【获取验证码】")
            await page.click('#user_regist_mobile > div:nth-child(4) > a')
            page.mouse  # 模拟真实点击

            message = get_message(phone)
            if message is not None:
                print("5.输入【验证码】{0}".format(message))
                await page.type('#vcodeNormal', message, {'delay': input_time_random() - 50})

                pwd = ''.join(str(uuid.uuid4()).split('-'))[0:12]
                print("6.输入【密码】{0}".format(pwd))
                await page.type('#pswd', pwd, {'delay': input_time_random() - 50})

                print("7.点击【注册】")
                await page.click('#register_btn')
                page.mouse  # 模拟真实点击

                print("8.获取【cookies】")
                await page.goto('https://www.qichacha.com')
                cookies = await page.evaluate(
                    '() => document.cookie'
                )
                print(cookies)
                save_account(phone, pwd, cookies)

                await page.close()
                await browser.close()


async def login(username, pwd):
    cookies = None
    # browser = await launch(headless=False, args=[f'--window-size={width},{height}', '--disable-infobars'])
    # headless参数设为False，则变成有头模式
    try:
        browser = await launch(launch_kwargs)
        # browser1 = await launch(launch_kwargs)
        # _context = await browser.createIncognitoBrowserContext()
        # # 在一个原生的上下文中创建一个新页面
        # page = await _context.newPage()
        page = await browser.newPage()
        print('page', page)
        # 设置页面视图大小
        # width, height = screen_size()
        # await page.setViewport(viewport={'width': width, 'height': height})
        # page.evaluateOnNewDocument("""
        #         var _navigator = {};
        #         for (name in window.navigator) {
        #             if (name != "webdriver") {
        #                 _navigator[name] = window.navigator[name]
        #             }
        #         }
        #         Object.defineProperty(window, 'navigator', {
        #             get: ()=> _navigator,
        #         })
        #     """)
        await page.goto('https://www.qichacha.com/user_login')

        await page.evaluate(js1)
        await page.evaluate(js3)
        await page.evaluate(js4)
        await page.evaluate(js5)
        # await page.evaluate(
        #     '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
        # 登录成功截图
        await page.screenshot({'path': './screenshot/example-%s.png' % time.time(), 'quality': 100, 'fullpage': True})

        logging.info("1.点击【密码登陆】")
        page.waitForSelector('#normalLogin')
        await page.click('#normalLogin')
        page.mouse  # 模拟真实点击

        logging.info("2.输入【手机号、密码】")
        await page.type('#nameNormal', username, {'delay': input_time_random() - 50})
        await page.type('#pwdNormal', pwd, {'delay': input_time_random()})

        slider = await page.querySelector('#dom_id_one')

        if slider:
            print('出现滑块情况判定')
            await page.screenshot({'path': './screenshot/headless-login-slide.png'})
            flag = await mouse_slide(page=page)
            print(flag)
            if flag:
                await page.click('#user_login_normal > button')
                page.mouse  # 模拟真实点击

                # await page.waitForRequest('https://www.qichacha.com', options={
                #     'timeout': 3000
                # })
                # waitFor = asyncio.ensure_future(page.waitForSelector(
                #     '.toast-message',
                #     options={
                #         'timeout': 30000
                #     }))
                # waitForNavigation = asyncio.ensure_future(page.waitForNavigation(
                #     options={
                #         'timeout': 30000,
                #         'waitUntil': 'load'
                #     }
                # ))

                # waitFor.add_done_callback(lambda fut: cancel_task(waitForNavigation, 1))
                # waitForNavigation.add_done_callback(lambda fut: cancel_task(waitFor, 2))
                # await waitFor
                # await waitForNavigation

                try:
                    await page.waitForNavigation(
                        options={
                            'timeout': 3000,
                            # 'waitUntil': 'load'
                        }
                    )
                except Exception as e:
                    logging.error(e)
                    print(e)
                    return

                cookies = await get_cookie(page)
            else:
                print('滑块失败')

    except Exception:
        await browser.close()

    await browser.close()
    return cookies


async def login_page(username, pwd, page):
    print('模拟登录')
    cookies = None
    try:
        # browser, page = await PuppeteerManager().get_browser(_loop)
        # page = await Singleton().instance().get_page();
        # browser, page = await PuppeteerManager().get_browser(_loop)
        # page = await browser.newPage()
        # 设置页面视图大小
        # width, height = screen_size()
        # await page.setViewport(viewport={'width': width, 'height': height})
        # page.evaluateOnNewDocument("""
        #         var _navigator = {};
        #         for (name in window.navigator) {
        #             if (name != "webdriver") {
        #                 _navigator[name] = window.navigator[name]
        #             }
        #         }
        #         Object.defineProperty(window, 'navigator', {
        #             get: ()=> _navigator,
        #         })
        #     """)
        await page.goto('https://www.qichacha.com/user_login')

        await page.evaluate(js1)
        await page.evaluate(js3)
        await page.evaluate(js4)
        await page.evaluate(js5)
        # await page.evaluate(
        #     '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
        # 登录成功截图
        await page.screenshot({'path': './screenshot/example-%s.png' % time.time(), 'quality': 100, 'fullpage': True})

        logging.info("1.点击【密码登陆】")
        page.waitForSelector('#normalLogin')
        await page.click('#normalLogin')
        page.mouse  # 模拟真实点击

        logging.info("2.输入【手机号、密码】")
        await page.type('#nameNormal', username, {'delay': input_time_random() - 50})
        await page.type('#pwdNormal', pwd, {'delay': input_time_random()})

        slider = await page.querySelector('#dom_id_one')
        print(slider)

        if slider:
            print('出现滑块情况判定')
            await page.screenshot({'path': './screenshot/headless-login-slide.png'})
            flag = await mouse_slide(page=page)
            print(flag)
            if flag:
                ##user_login_normal > button
                await page.click('#user_login_normal > button')
                page.mouse  # 模拟真实点击

                # await page.waitForRequest('https://www.qichacha.com', options={
                #     'timeout': 3000
                # })
                # waitFor = asyncio.ensure_future(page.waitForSelector(
                #     '.toast-message',
                #     options={
                #         'timeout': 30000
                #     }))
                # waitForNavigation = asyncio.ensure_future(page.waitForNavigation(
                #     options={
                #         'timeout': 30000,
                #         'waitUntil': 'load'
                #     }
                # ))

                # waitFor.add_done_callback(lambda fut: cancel_task(waitForNavigation, 1))
                # waitForNavigation.add_done_callback(lambda fut: cancel_task(waitFor, 2))
                # await waitFor
                # await waitForNavigation

                try:
                    await page.waitForNavigation(
                        options={
                            'timeout': 10000,
                            'waitUntil': ['load', 'domcontentloaded']
                        }
                    )
                except Exception as e:
                    logging.error(e)
                    print(e)
                    return None

                cookies = await get_cookie(page)
            else:
                print('滑块失败')

    except Exception as e:
        print(e)
    return cookies


def start_loop(loop):
    #  运行事件循环， loop以参数的形式传递进来运行
    asyncio.set_event_loop(loop)
    loop.run_forever()


def save_account(username, pwd, cookies):
    insert_sql = """
            insert into user_info(USERNAME, PASSWORD, COOKIES, STATUS, USED, LOCKED, TYPE)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    id = mysql.insertOne(insert_sql, (username, pwd, cookies, 1, 0, 0, 2))
    print(id)


loop = ''
mysql = Mysql()
# mysql连接池
pool = ''
if __name__ == '__main__':
    # if platform.system() == "Linux":
    #     display = Display(visible=0, size=(800, 600))
    #     display.start()

    # thread_loop = asyncio.new_event_loop()  # 获取一个事件循环
    # run_loop_thread = threading.Thread(target=start_loop, args=(thread_loop,))  # 将次事件循环运行在一个线程中，防止阻塞当前主线程
    # run_loop_thread.start()  # 运行线程，同时协程事件循环也会运行

    loop = asyncio.get_event_loop()

    for i in range(10):
        # loop.run_until_complete(login('17155851795', '06265fda1fd8'))
        loop.run_until_complete(register())
    # asyncio.ensure_future(test(loop))

    # if platform.system() == "Linux":
    #     display.stop()
