# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import requests
import os
import sys
from parsers import BaseParser
import chardet
from queue import Queue
from threading import Thread, Lock
from time import time
from bloom_filter import BloomFilter


def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


def get_page(page):
    content = ''
    r = requests.get(page)
    content = r.content
    # print(type(content))
    return content


def get_all_links(content, page):
    parser = BaseParser()
    url_set = parser.parse_url(content, page)
    links = [u for u in url_set]    # this is stupid
    return links


def add_page_to_folder(page, content):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = 'index.txt'  # index.txt中每行是'网址 对应的文件名'
    folder = 'html'  # 存放网页的文件夹
    filename = valid_filename(page)+".html"  # 将网址变成合法的文件名
    index = open(index_filename, 'a', encoding="utf8")
    index.write(page + '\t' + filename + '\n')
    index.close()
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w', encoding="utf8")
    encode = chardet.detect(content)
    # print(encode)
    if not encode["encoding"]:
        print("Failed to detect encoding.({url},{encode})".format(url=page, encode=encode))
    f.write(content.decode(encode["encoding"] or "utf8", errors="ignore"))  # 将网页存入文件
    f.close()


def crawl(seed, max_page, thread_num=4):

    def crawl_single_page():
        global count
        while count < max_page:
            url = url_queue.get()
            if not crawled.check(url):
                print("#{0:<4} {1}".format(count+1, url))
                content = get_page(url)
                outlinks = get_all_links(content, url)
                with lock:
                    if count >= max_page:
                        print("Drop!")
                        break
                    graph[url] = outlinks
                    for l in outlinks:
                        url_queue.put(l)
                    crawled.add(url)
                    count += 1
                add_page_to_folder(url, content)
            url_queue.task_done()
        print("I'm Done!")
    url_queue = Queue()
    lock = Lock()
    crawled = BloomFilter(max_page)
    graph = {}
    global count
    count = 0
    url_queue.put(seed)
    threads = []
    for i in range(thread_num):
        t = Thread(target=crawl_single_page)
        threads.append(t)
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
    return graph, crawled


if __name__ == '__main__':

    seed = sys.argv[1]
    max_page = sys.argv[2]
    thread_num = sys.argv[3]

    # seed = "https://tieba.baidu.com"
    # max_page = 100
    # thread_num = 8
    start_time = time()
    graph, crawled = crawl(seed, max_page, thread_num)
    end_time = time()
    print("Back Home!\n")
    print("Seed:{0}\nPage(s):{1}/{4}\nThread(s):{2}\nTime:{3}s\n".format(
        seed, len(crawled), thread_num, end_time-start_time, max_page))
