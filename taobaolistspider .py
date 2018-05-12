from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pymongo


MONGO_URL='localhost'#数据库的地址
MONGO_DB='Taobao'#数据库的名字
MONGO_TABLE='Food'#数据库的表单名

KEYWORD='美食'#需要搜索的关键字

client=pymongo.MongoClient(MONGO_URL)#与数据库建立连接
db=client[MONGO_DB]#创建数据库名

browser=webdriver.Chrome()#启动Chrome
wait=WebDriverWait(browser,10)#显性等待时间设置

#搜索
def search():
    try:
        browser.get('https://www.taobao.com/')#请求网址
        input=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#q')))#寻找商品搜索输入框的节点，并判断是否已经出现在元素里面
        button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))#商品搜索的确定按钮节点，并判断能否点击
        input.send_keys(KEYWORD)#输入要搜索的商品
        button.click()#点击搜索按钮
        #执行完上一步之后，会呈现商品的列表

        #判断页面是否已经加载好：主要通过等待的方式来确定，并且获取页码信息
        page=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total'))).text
        get_information(browser.page_source)#解析响应体源代码,提取信息：根据程序实现的逻辑，在这里主要获取第一页商品的信息
        return page
    except TimeoutException:#如果等待的时间超过，预设的延时等待时间，会出现TimeoutException的错误
        return search()#一旦出现超时错误，进行捕获，并重新执行search

#该函数主要实现翻页操作
def next_page(num_page):
    try:
        # 延时等待，在设置的延时等待时间里面，找到页码的输入框节点，如果超过时间，会抛出Timeout异常
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        # 延时等待，在设置的延时等待时间里面，找到页码的确定按钮节点，并且判断该节点可以点击，如果超过时间，会抛出Timeout异常
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()#页码输入框清空
        input.send_keys(num_page)#输入页码
        button.click()#点击确定按钮，完成翻页

        #完成翻页之后需要判断页面是否已经加载好，具体的做法是判断要翻页的页码是否是高亮状态
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.items .item.active'),str(num_page)))
        print('翻页：',num_page)#调试信息
        get_information(browser.page_source)#获取页面的商品信息，在这里主要获取第一页以后的信息
    except TimeoutException:#捕获超时异常
        next_page(num_page)#如果出现超时异常，重新执行翻页操作

#该函数主要实现的是：解析获取的响应体内部的商品信息
def get_information(html):
    soup=BeautifulSoup(html,'lxml')#将响应体的源码信息 变成 类似lxml结构的信息
    items = soup.select('.items .item.J_MouserOnverReq')#获取所有包含商品信息的节点，获取的是一个列表
    #用for循环对单个列表进行解析
    for item in items:
        product={
            'img': item.select('.pic img.J_ItemPic')[0].attrs['src'],#提取图片链接
            'price':item.select('.price')[0].get_text().strip(),#提取价格
            'count':item.select('.deal-cnt')[0].get_text(),#提取付款人数
            'name':item.select('.title')[0].get_text().strip(),#提取名称
            'location':item.select('.location')[0].get_text(),#提取位置
            'shop':item.select('.shop')[0].get_text().strip()#提取商店名
        }
        save_to_mongo(product)#保存到数据库

#保存到数据库的函数
def save_to_mongo(info):
    try:
        if db[MONGO_TABLE].insert(info):#插入导数据库
            print('成功保存：',info)
    except Exception:#捕获异常
        print('保存失败：',info)

#主体函数，用来
def main():
    page=search()#搜索商品，并获取页码，并获取第一页的商品信息
    pattern=re.compile('(\d+)')#
    page = int(re.search(pattern,page).group(1))#获取的页码信息含有其他信息，需要进行过滤提取，并转化为int型
    for i in range(2,page+1):#从第二页开始
        next_page(i)#进行翻页，并获取商品信息

if __name__=='__main__':
    main()
