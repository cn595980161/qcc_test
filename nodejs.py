#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import execjs
import json

os.environ["EXECJS_RUNTIME"] = "Node"
#os.environ["NODE_PATH"] = os.getcwd()+"/node_modules"
print(execjs.get().name)

parser = execjs.eval("""
    const puppeteer = require('puppeteer');
 
    (async () => {  ​
        const browser = await puppeteer.launch();  
        const page = await browser.newPage(); 
        await page.goto('http://www.baidu.com');   
        await browser.close(); 
    })();
""")


if __name__ == "__main__":
    obj = parser.call("parse", '<doc id=\'1\'></doc>')
    print(obj)