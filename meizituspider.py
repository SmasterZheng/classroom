import requests
import os
from bs4 import BeautifulSoup

#因为接下来的执行或函数都会涉及到请求，考虑代码的简洁，将共同的功能提炼出来
#接下来的三个函数都涉及到请求，这样可以进行代码复用
def get_response(url):
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    response=requests.get(url,headers=headers)#发送请求，获得响应
    return response #返回响应

#该函数主要实现图片下的链接（注意：点击每个图片，都会跳转到另一个页面，所以在这里将首页看到的图片，理解为一个包含链接的按钮）
def get_page_url(url):
    page_urls=[]#接下来需要需要将获取的链接保存到该list里面
    response=get_response(url)#发送求，并获得响应
    soup=BeautifulSoup(response.text,'lxml')#将响应体的源码信息 变成 类似lxml结构的信息
    results=soup.select('#picture p a') #获取包含链接的节点列表
    for result in results:
        page_urls.append(result.attrs['href'])#提取链接信息，并加入到page_url列表里面
    return page_urls #返回链接列表

#该函数实现的是获取图片链接
def get_img_url(urls):
    imge_urls=[]#接下来需要将获取的图片链接，插入到该列表
    for url in urls:#将传入的urls列表信息进行循环
        response=get_response(url)#发送请求，并获得响应
        soup = BeautifulSoup(response.text, 'lxml')#将响应体的源码信息 变成 类似lxml结构的信息
        imges = soup.select('#picture > p > img')#获取包含图片链接的节点列表
        for imge in imges:
            imge_urls.append(imge.attrs['src'])##提取链接信息，并加入到image_url列表里面
    return imge_urls#返回图片链接列表

#请求图片链接，并进行保存
def save_img(urls):
    for url in urls:#针对传入的图片链接列表进行循环
        img = get_response(url).content #发送请求，并获得图片的二进制流
        name = url.split('/')#将url通过‘/’进行分割成列表
        filename = name[-2]+'-'+name[-1]#在分割好的url列表里面，取后两个数据，来构建我们的图片名字，需要保证图片名字的唯一性
        with open(filename,'wb') as f:
            f.write(img)#将图片的二进制流进行写入，即保存图片

#主体函数
def download_imge(folder='D:/xxoo'):
    os.mkdir(folder)#创建文件夹
    os.chdir(folder)#切换到文件夹下面
    url='http://www.meizitu.com/'
    page_urls=get_page_url(url)#获取mm对应的url
    img_urls =get_img_url(page_urls)#获取图片的url
    save_img(img_urls)#保存图片

if __name__=='__main__':
    download_imge()