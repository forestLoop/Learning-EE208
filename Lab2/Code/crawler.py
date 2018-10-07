# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import requests
import os
import sys
from parsers import BaseParser
import chardet


def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


def get_page(page):
    content = ''
    try:
        r = requests.get(page, timeout=10)
    except:
        return None
    content = r.content
    # print(type(content))
    return content


def get_all_links(content, page):
    parser = BaseParser()
    url_set = parser.parse_url(content, page)
    links = [u for u in url_set]    # this is stupid
    return links


def union_dfs(a, b):
    for e in b:
        if e not in a:
            a.append(e)


def union_bfs(a, b):
    for e in b:
        if e not in a:
            a.insert(0, e)


def add_page_to_folder(page, content):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = 'index.txt'  # index.txt中每行是'网址 对应的文件名'
    folder = 'html'  # 存放网页的文件夹
    filename = valid_filename(page)  # 将网址变成合法的文件名
    index = open(index_filename, 'a', encoding="utf8")
    index.write(page + '\t' + filename + '\n')
    index.close()
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w', encoding="utf8")
    encode = chardet.detect(content)
    print(encode)
    f.write(content.decode(encode["encoding"], errors="ignore"))  # 将网页存入文件
    f.close()


def crawl(seed, method, max_page):
    tocrawl = [seed]
    crawled = []
    graph = {}
    count = 0

    while tocrawl and count < max_page:
        page = tocrawl.pop()
        if page not in crawled:
            print(page)
            content = get_page(page)
            if not content:
                print("Failed to get {0}.".format(page))
                continue
            add_page_to_folder(page, content)
            outlinks = get_all_links(content, page)
            graph[page] = outlinks
            globals()['union_%s' % method](tocrawl, outlinks)
            crawled.append(page)
            count += 1
    return graph, crawled


if __name__ == '__main__':

    seed = sys.argv[1]
    method = sys.argv[2]
    max_page = sys.argv[3]
    # seed = "https://www.sjtu.edu.cn"
    # method = "bfs"
    # max_page = 100
    graph, crawled = crawl(seed, method, max_page)
