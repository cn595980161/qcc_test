# -*- coding: utf-8 -*-
import asyncio
import datetime
import logging
import random
import time

import aiomysql
from pyppeteer import launch
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, retry_if_result

import Config
from Logger import Logger
from Mysql import Mysql
from exe_js import js1, js3, js4, js5, js6

logger = Logger(log_file_name='log.txt', log_level=logging.DEBUG, logger_name="yongshuo").get_log()

# loop = ''
# mysql连接池
pool = ''

mysql = Mysql()


def convert_cookies_to_dict(_cookies, _domain):
    # cookies = [dict({'name': cookie.split("=", 1)[0], 'value': cookie.split("=", 1)[1]}) for cookie in _cookies.split(";")]
    cookies = []
    for cookie in _cookies.replace(' ', '').split(";"):
        if cookie != '' and cookie is not None:
            cookie_dict = {'name': cookie.split("=", 1)[0], 'value': cookie.split("=", 1)[1], 'domain': _domain}
            # cookie_dict['name'] = cookie.split("=", 1)[0]
            # cookie_dict['value'] = cookie.split("=", 1)[1]
            cookies.append(cookie_dict)
    logger.info('cookie:' + str(cookies))
    return cookies


def retry_if_result_none(result):
    return result is None


def return_last_value(retry_state):
    """return the result of the last call attempt"""
    return retry_state.outcome.result()


def input_time_random():
    return random.randint(50, 100)


async def login_page(username, pwd, page):
    logger.info('模拟登录...')
    cookies = None
    try:
        await page.goto('https://www.qichacha.com/user_login')

        await page.evaluate(js1)
        # await page.evaluate(js2)
        await page.evaluate(js3)
        await page.evaluate(js4)
        await page.evaluate(js5)
        await page.evaluate(js6)
        await page.evaluateOnNewDocument("""
                var _navigator = {};
                for (name in window.navigator) {
                    if (name != "webdriver") {
                        _navigator[name] = window.navigator[name]
                    }
                }
                Object.defineProperty(window, 'navigator', {
                    get: ()=> _navigator,
                })
            """)

        # 登录成功截图
        await page.screenshot({'path': './screenshot/example-%s.png' % time.time(), 'quality': 100, 'fullpage': True})

        logger.info("1.点击【密码登陆】")
        await page.waitForSelector('#normalLogin')
        await page.click('#normalLogin')
        page.mouse  # 模拟真实点击

        logger.info("2.输入【手机号、密码】")
        await page.type('#nameNormal', username, {'delay': input_time_random()})
        await page.type('#pwdNormal', pwd, {'delay': input_time_random()})

        logger.info("3.操作【验证码】")
        slider = await page.querySelector('#dom_id_one')

        if slider:
            logger.info('出现验证码')
            await page.screenshot({'path': './screenshot/headless-login-slide.png'})
            flag = await verify(page=page)
            logger.info('验证码结果:' + flag)
            if flag:
                # fut = asyncio.ensure_future(page.waitFor('.headface'))
                # fut.add_done_callback(lambda f: print('页面加载完成'))

                logger.info("4.点击【登录】")
                await page.click('#user_login_normal > button')
                page.mouse  # 模拟真实点击

                logger.info("5.等待页面跳转")
                try:
                    await page.waitFor('.headface', options={'timeout': 5000})
                    _cookies = await page.evaluate(
                        '() => document.cookie'
                    )
                    print(_cookies)
                    await update_account(username, _cookies)
                except Exception as e:
                    logger.error('登录失败:' + str(e))
                    await update_account(username, cookies)
                    return None
                # await fut
                # try:
                #     # await page.waitForRequest(
                #     #     'https://www.qichacha.com',
                #     #     timeout=10000,
                #     # )
                #     logger.info('登录成功!')
                # except Exception as e:
                #     logger.error(e)
                #     return None
            else:
                logger.info('滑块失败')

    except Exception as e:
        logger.error(str(e))
        await update_account(username, cookies)
    return cookies


async def verify_page(username, pwd, cookies, page):
    # logger.info('=' * 25)
    # logger.info('=', ' ' * 10, '验证码', ' ' * 10, '=')
    # logger.info('=' * 25)
    logger.info('验证码')
    await page.setViewport(viewport={'width': 1300, 'height': 800})

    # 设置cookies
    await page.setCookie(*convert_cookies_to_dict(cookies, 'www.qichacha.com'))

    await page.goto('https://www.qichacha.com/index_verify?type=companyview&back=/')

    # 1.判断是否有用户
    # 2.判断是否是验证码页面
    title = await page.title()
    logger.info('title:' + title)
    if title == '用户验证-企查查':
        await page.evaluate(js1)
        await page.evaluate(js3)
        await page.evaluate(js4)
        await page.evaluate(js5)

        # 进入验证码页面截图
        await page.screenshot({'path': './screenshot/verify-%s.png' % time.time(), 'quality': 100, 'fullpage': True})

        try:
            flag = await verify(page)

            if flag:
                await page.click('#verify')
                page.mouse  # 模拟真实点击
                await update_valid(username)

        except Exception as e:
            logger.error('验证码失败:' + str(e))
            update_valid(username)
            return None

    else:
        await update_valid(username)


@retry(retry=(retry_if_result(retry_if_result_none) | retry_if_exception_type()), retry_error_callback=return_last_value, stop=stop_after_attempt(5), wait=wait_fixed(3))
async def verify(page=None):
    try:
        await page.waitForSelector('.nc_iconfont.btn_slide')
        await page.hover('.nc_iconfont.btn_slide')
        await page.mouse.down()

        await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})
        await page.mouse.up()

        # slider_text = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')
        # print(slider_text)

        # 操作完验证码页面截图
        # await page.screenshot({'path': './screenshot/slide-result.png' % time.time(), 'quality': 100, 'fullpage': True})
    except Exception as e:
        logger.info(str(e) + '     :slide login False')
        return None
    else:
        # document.querySelector(selector)
        # await page.waitForFunction('!document.querySelector(".nc_iconfont.btn_slide")')
        # await page.querySelector('.nc-lang-cnt')
        # await asyncio.sleep(3)
        # document.querySelector(".nc-lang-cnt").textContent
        await page.waitForFunction('document.querySelector(".nc-lang-cnt").textContent!="加载中"')
        slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')
        if slider_again != '验证通过':
            logger.info('没通过:' + slider_again)
            if slider_again == '哎呀，出错了，点击刷新再来一次':
                await page.click('span.nc-lang-cnt > a:nth-child(1)')
                page.mouse  # 模拟真实点击
            if slider_again == '网络不给力，请点击刷新，或提交反馈':
                await page.click('span.nc-lang-cnt > a:nth-child(1)')
                page.mouse  # 模拟真实点击

            return None
            # raise RuntimeError(slider_again)
        else:
            await page.screenshot({'path': './screenshot/slide-result-%s.png' % time.time(), 'quality': 100, 'fullpage': True})
            logger.info('验证通过')
            return slider_again


async def update_account(username, cookies):
    logger.info('更新cookies 账号:%s' % username)
    insert_sql = """
            update user_info set cookies = %s, status = 1, locked = 0, update_time = %s where username = %s and type = 2
    """
    mysql.update(insert_sql, (cookies, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))


# async def update_valid(username):
#     logger.info('更新有效 账号:%s' % username)
#     insert_sql = """
#             update user_info set status = 1, locked = 0, update_time = %s where username = %s and type = 2
#     """
#     mysql.update(insert_sql, (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))


async def update_valid(username):
    """
    使用异步IO方式保存数据到mysql中
    :param items:
    :param pool:
    :return:
    """
    logger.info('更新有效 账号:%s' % username)

    sql = """
            update user_info set status = 1, locked = 0, update_time = %s where username = %s and type = 2
    """
    # print('_insertMany:' + sql)

    # 异步IO方式插入数据库
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(sql, (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
                logger.debug('修改数据成功')
            except aiomysql.Error as e:
                # traceback.print_exc()
                logger.debug('mysql error %d: %s' % (e.args[0], e.args[1]))


async def mysql_task(loop):
    logger.debug('mysql获取连接池...')
    global pool
    pool = await aiomysql.create_pool(
        host=Config.DBHOST,
        port=Config.DBPORT,
        user=Config.DBUSER,
        password=Config.DBPWD,
        db=Config.DBNAME,
        loop=loop,
        charset='utf8',
        autocommit=True)
    logger.info('mysql连接池 %s' % pool)


async def main():
    browser = await launch(headless=False,
                           args=[
                               '--disable-extensions',
                               '--hide-scrollbars',
                               '--disable-bundled-ppapi-flash',
                               '--mute-audio',
                               '--disable-gpu',
                               # '--disable-dev-shm-usage',
                               '--disable-setuid-sandbox',
                               '--no-first-run',
                               '--no-sandbox',
                               '--no-zygote',
                               # '--single-process'
                           ],
                           dumpio=True,
                           userDataDir="./userdata/tmp" + str(int(time.time())))
    t1 = time.time()
    context = await browser.createIncognitoBrowserContext()
    # 在一个原生的上下文中创建一个新页面
    page = await context.newPage()
    # await page.setViewport(viewport={'width': 1300, 'height': 800})
    # page = await browser.newPage()
    await verify_page('13766112146', '3108acbffbf6',
                      '_uab_collina=156241894220300269109003; UM_distinctid=16bc76d12ee327-02c8837df77e05-605d7520-1fa400-16bc76d12ef60b; CNZZDATA1254842228=1438966448-1562415348-%7C1562415348; zg_did=%7B%22did%22%3A%20%2216bc76d13b56e4-0c820aba8d038a-605d7520-1fa400-16bc76d13b6ba3%22%7D; hasShow=1; QCCSESSID=agv6na7rmvoot7jfpgnid3jra5; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201562418942905%2C%22updated%22%3A%201562419062530%2C%22info%22%3A%201562418942922%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22%22%2C%22cuid%22%3A%20%22f836e1268f35fa99030de583a9544692%22%7D; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1562418948,1562418979,1562419001,1562419063; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1562419063;acw_sc__v2=5d21a7c747efa31c92481c5115b9c56d71aad0a1;',
                      page)
    # await login_page('17155851795', '06265fda1fd8', page)
    await page.screenshot({'path': 'example.png'})
    await page.close()

    # context = await browser.createIncognitoBrowserContext()
    # # 在一个原生的上下文中创建一个新页面
    # page = await context.newPage()
    # # await verify_page(
    # #     'zg_did=%7B%22did%22%3A%20%2216bc2e6b298350-0464444a42919f-605d7520-1fa400-16bc2e6b299f%22%7D; _uab_collina=156234302819541716686775; UM_distinctid=16bc2e6b7575a8-0b8346429b6716-605d7520-1fa400-16bc2e6b7583eb; CNZZDATA1254842228=1240806025-1562338833-%7C1562338833; hasShow=1; QCCSESSID=jjahpr0o94j3vh60ngvgmc0bi7; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1562343029,1562343059,1562343088; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201562343027356%2C%22updated%22%3A%201562343108089%2C%22info%22%3A%201562343027360%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22%22%7D; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1562343108;acw_sc__v2=5d1f7859ef0a6ceab913c8764fd80e22ebf3a31d;',
    # #     page)
    # await login_page('17155851795', '06265fda1fd8', page)
    # await page.screenshot({'path': 'example.png'})
    # await page.close()

    await browser.close()
    t2 = time.time()
    logger.debug('总共耗时：%s' % (t2 - t1))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # mysql开启
    asyncio.ensure_future(mysql_task(loop))

    loop.run_until_complete(main())
