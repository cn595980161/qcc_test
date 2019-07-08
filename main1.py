# -*- coding: utf-8 -*-
import asyncio
import logging
import platform
import threading

from flask import Flask, request

from login import login

if platform.system() == "Linux":
    from pyvirtualdisplay import Display

logging.basicConfig(filename='log.txt', level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)


# class JsonResponse(Response):
#     @classmethod
#     def force_type(cls, response, environ=None):
#         if isinstance(response, (dict, list)):
#             response = jsonify(response)
#
#         return super(JsonResponse, cls).force_type(response, environ)
#
#
# app.response_class = JsonResponse


@app.route('/')
def hello_world():
    return 'Hello Flask!'


@app.route('/login', methods=['GET'])
def simulated_login():
    if request.method == 'GET':
        #     print(request.form['username'])  # 获取post穿过来的参数
        #     print(request.form['password'])  # 获取post穿过来的参数
        #     dict = request.form.to_dict()  # 将请求参数解析成字典
        #     print(dict['username'])
        #     return 'POST'
        # else:
        # print(request.args['username'])  # 获取get传过来的参数
        # print(request.args['password'])  # 获取get传过来的参数
        dict = request.args.to_dict()  # 将请求参数解析成字典
        print(dict['username'])
        print(dict['password'])

        username = dict['username']
        password = dict['password']

        # asyncio.set_event_loop(asyncio.new_event_loop())
        # loop = asyncio.get_event_loop()
        # # task = asyncio.ensure_future(login1(puppeteer_manager.browser, username, password))
        # task = asyncio.ensure_future(login1(username, password))
        # result = loop.run_until_complete(task)
        asyncio.run_coroutine_threadsafe(login(username, password), thread_loop)  # 注意：run_coroutine_threadsafe 这个方法只能用在运行在线程中的循环事件使用
        # print(result)
        # thread_loop.run_until_complete(login('17155851795', '06265fda1fd8'))

        # loop.run_until_complete(asyncio.gather(asyncio.ensure_future(login(username, password), loop=loop)))
        return '1'


def start_loop(loop):
    #  运行事件循环， loop以参数的形式传递进来运行
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':

    if platform.system() == "Linux":
        display = Display(visible=0, size=(800, 600))
        display.start()

    thread_loop = asyncio.new_event_loop()  # 获取一个事件循环
    run_loop_thread = threading.Thread(target=start_loop, args=(thread_loop,))  # 将次事件循环运行在一个线程中，防止阻塞当前主线程
    run_loop_thread.start()  # 运行线程，同时协程事件循环也会运行

    # loop = asyncio.get_event_loop()

    app.run(host=None,  # 设置ip，默认127.0.0.1
            port=None,  # 设置端口，默认5000
            debug=True)  # 设置debug=True是为了让代码修改实时生效，而不用每次重启加载

    # if platform.system() == "Linux":
    #     display.stop()
