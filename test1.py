import execjs.runtime_names
node = execjs.get(execjs.runtime_names.Node)
node.eval("1 + 2")
node.eval('''
    const puppeteer = require('puppeteer');
 
    (async () => {  ​
        const browser = await puppeteer.launch();  
        const page = await browser.newPage(); 
        await page.goto('http://www.baidu.com');   
        await browser.close(); 
    })();
''')