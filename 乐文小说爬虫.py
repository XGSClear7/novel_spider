# -*- coding: utf-8 -*-
"""
  █████▒█    ██  ▄████▄   ██ ▄█▀       ██████╗ ██╗   ██╗ ██████╗
▓██   ▒ ██  ▓██▒▒██▀ ▀█   ██▄█▒        ██╔══██╗██║   ██║██╔════╝
▒████ ░▓██  ▒██░▒▓█    ▄ ▓███▄░        ██████╔╝██║   ██║██║  ███╗
░▓█▒  ░▓▓█  ░██░▒▓▓▄ ▄██▒▓██ █▄        ██╔══██╗██║   ██║██║   ██║
░▒█░   ▒▒█████▓ ▒ ▓███▀ ░▒██▒ █▄       ██████╔╝╚██████╔╝╚██████╔╝
 ▒ ░   ░▒▓▒ ▒ ▒ ░ ░▒ ▒  ░▒ ▒▒ ▓▒       ╚═════╝  ╚═════╝  ╚═════╝
 ░     ░░▒░ ░ ░   ░  ▒   ░ ░▒ ▒░
 ░ ░    ░░░ ░ ░ ░        ░ ░░ ░
          ░     ░ ░      ░  ░
-------------------------------------------------
   File Name：     乐文小说爬虫
   Description :
   Author :       92159
   date：          2020/7/23
-------------------------------------------------
   Change Activity:
                   2020/7/23:
-------------------------------------------------
"""
__author__ = '92159'

import csv
import requests
import re
# lxml 处理html的库
from lxml import etree
import time
# 调用系统命令的库
import os
# 导入进度模块
from tqdm import tqdm
# 导入线程池
from concurrent.futures import ThreadPoolExecutor, as_completed


class PaQu():
    # 定义存放小说的目录
    csv_path = './书籍s'
    # 定义请求等待时间
    TIME_DELY = 0.2
    # 定义请求超时时间
    TIME_OUT = 5
    # 判断是否存在这个目录，不存在则创建
    if not os.path.exists(csv_path):
        os.mkdir(csv_path)

    header = {
        'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8, application / signed - exchange;v = b3',
        'Accept - Encoding': 'gzip, deflate',
        'Accept - Language': 'zh - CN, zh;q = 0.9',
        # 'Cache - Control': 'max - age = 0',
        # 'Connection': 'keep - alive',
        # 'Cookie': 'Hm_lvt_8c8b48a59e25f8cc4ba89be706b1ad27 = 1595405840;bdshare_firstime = 1595405840552;clickbids = 11098;Hm_lpvt_8c8b48a59e25f8cc4ba89be706b1ad27 = 1595405879;novelbgcolor = % 23d8e2c8;novelline = 16pt;fonttype = 16pt',
        'Referer': 'http://www.lewengu.com/',
        'User - Agent': 'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 76.0.3809.87Safari / 537.36'
    }

    def search(self, data):
        # 搜索地址
        url = 'http://www.lewengu.com/modules/article/search.php'
        # 请求参数
        data = {
            'searchkey': str(data)
        }
        res = requests.post(url, headers=self.header, data=data).content.decode()
        # 转为html格式进行处理
        res = etree.HTML(res)
        # 获取书名
        book_title = res.xpath('//div[@id="alistbox"]//div[@class="title"]/h2/a/text()')
        # 获取书的链接
        book_link = res.xpath('//div[@id="alistbox"]//div[@class="title"]/h2/a/@href')
        # 获取书的作者，方便判断
        book_author = res.xpath('//div[@id="alistbox"]//div[@class="title"]/span/text()')
        # 合并列表，将爬取的各列表合成二维列表
        book_msg = list(zip(book_title, book_author, book_link))
        return book_msg

    def get_title(self, url='/books/11/11098/'):
        url = 'http://www.lewengu.com' + url
        res = requests.get(url=url, headers=self.header).content.decode()
        res = etree.HTML(res)
        titles = res.xpath('//div[@class="dccss"]/a/text()')
        title_urls = res.xpath('//div[@class="dccss"]/a/@href')
        title_list = list(zip(titles, title_urls))  # 合并列表
        # print(title_list)
        return title_list

    def req(self, i):
        # 获取传入的元组里面呢参数
        title = i[0]  # 章节
        url = i[1]  # 章节链接
        base_url = 'http://www.lewengu.com' + url
        # 请求等待
        time.sleep(self.TIME_DELY)
        try:
            res = requests.get(url=base_url, headers=self.header, timeout=self.TIME_OUT)
            res = res.content.decode()
            res = etree.HTML(res)
        except Exception as e:
            # print(e)
            time.sleep(1.5)
            return self.req(i)
        else:
            try:
                # message = re.findall("""<P>﻿(.*?)</P>""", res)[0]
                message = res.xpath("//div[@id='content']//p/text()")
            except:
                message = '本章节暂无数据 '
            # print(message)
            result = ''
            for i in message:
                result += i.replace('\xa0\xa0\xa0\xa0', '').replace('&nbsp;', '') + '\r\n'
            return {title: result}

    def doc_w(self, data, file_name='我有药啊[系统]'):
        """
            创建md文件，并将数据写入md中，后期方便处理数据
        """
        # 拼接路径
        file_path = os.path.join(self.csv_path, file_name + '.txt')
        # 写入csv文件
        with open(file_path, 'a', encoding='utf-8-sig') as f:  # file_path:文件名, a:已追加方式写入， encoding:编码方式, newline:定义换行符
            title = list(data.keys())[0]
            txt = data[title]
            # print(title, txt)
            f.write(list(data.keys())[0] + '\r\n')
            f.writelines(txt)

    def main(self, book_name=input('请输入您要下载的小说名称：')):
        # 用户输入要爬取的小说
        # book_name = input('请输入您要下载的小说名称：')
        # book_author = input('请输入您要下载的小说作者名称：')
        # 调用函数获取搜索回的结果列表
        book_msg = self.search(book_name)
        # 建立索引方便用户选择小说
        book_index = 0
        if not book_msg:
            print('暂无书籍信息...')
        else:
            print('小说索引：\t\t小说名称：\t\t小说作者：')
            for book in book_msg:
                book_index += 1
                book_name = book[0]
                booke_author = book[1]
                print(book_index, '\t\t\t', book_name, '\t\t\t', booke_author)
            # 用索引选择小说
            index = input('请输入书籍索引选择要下载的书籍（只能选择一本）：')
            book_msg = book_msg[int(index) - 1]
            book_url = book_msg[2]
            book_name = book_msg[0].replace(r'/', '-') + '-' + book_msg[1]
            # 调用函数获取小说全部章节信息
            title_list = P.get_title(url=book_url)
            # print(title_list)
            # 创建线程池
            download_tpool = ThreadPoolExecutor(
                max_workers=64)  # 可以定义做大线程数， max_workers参数 ThreadPoolExecutor(max_workers=8)
            # 将任务加入到线程池中，大大加快下载速度
            # 使用map方法是为了阻塞线程，让结果输出的顺序与参数传入的顺序保持一致，不会章节杂乱
            for result in tqdm(download_tpool.map(self.req, title_list)):
                # print(result)
                # 将结果写入csv
                P.doc_w(result, file_name=book_name)
                # break
            print('小说下载完成！')


if __name__ == '__main__':
    # 实例化类
    P = PaQu()
    P.main()

