import requests
import re
import pymongo

MONGO_URL='localhost'#建立连接
MONGO_DB='Maoyan'#创建数据库

client=pymongo.MongoClient(MONGO_URL)#连接数据库
db=client[MONGO_DB]#创建数据库

#获得一页的响应提信息
def get_one_page(url):
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    response = requests.get(url,headers=headers)#发送请求，获得响应
    return response.text #获得响应体信息，并返回

#解析请求的信息，并通过正则表达式提取想要的信息：电影名称、排名等
def parse_page(html):
    #通过正则表达式进行匹配
    pattern=re.compile('<dd>.*?board-index.*?>(.*?)</i>.*?data-src.*?"(.*?)".*?name.*?a.*?>(.*?)</a>.*?star.*?>(.*?)</p>.*?releasetime.*?>(.*?)</p>.*?integer.*?>(.*?)</i>.*?fraction.*?>(.*?)</i>',re.S)
    results=re.findall(pattern,html)#获得单页响应头的信息，获得的是一个列表
    #对产生的列表list进行for循环
    for result in results:
        #通过字典(dict)，组建信息
        movies={
            'rate':result[0],
            'img_url':result[1],
            'name':result[2],
            'actor':result[3].strip()[3:],
            'time':result[4][5:],
            'score':result[5]+result[6]
        }
        #保存到数据库
        save_mongo(movies)

#保存到数据库的函数
def save_mongo(info):
    if db['Movies'].insert(info):#将信息插入到数据库
        print('保存成功：',info)
    else:
        print('保存失败：',info)

#实现主流程
def main():
    #有10页，通过来获取每一页的信息
    for i in range(10):
        url='http://maoyan.com/board/4?offset='+str(i*10)#构建每一页的请求url
        html=get_one_page(url)#进行请求
        parse_page(html)#进行响应体的解析，并保存到数据库

if __name__=='__main__':
    main()#调用主体函数