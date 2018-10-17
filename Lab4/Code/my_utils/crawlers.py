import requests
import random
import chardet
import os
from time import sleep
from queue import Queue
from threading import Thread, Lock
from .bloom_filter import BloomFilter
from .parsers import BaseParser


class BaseCrawler(object):

    def __init__(self, headers=None):
        self.new_session()
        self.headers = headers

    def get_html(self, url, headers=None):
        assert self.session != None
        headers = headers or self.headers  # if headers are not specified for this single request, use the global headers
        content = self.session.get(url, headers=headers).content
        decoded_content = content.decode("utf8")  # maybe not utf-8 for some sites?
        return decoded_content

    def new_session(self):
        self.session = requests.Session()


class MultiThreadingCrawler(BaseCrawler):

    def __init__(self, thread_num=4, headers=None, session_num=10,
                 index_file=None, data_folder=None):
        super(MultiThreadingCrawler, self).__init__(headers)
        self.thread_num = thread_num
        self.index_file = index_file or "index.txt"
        self.data_folder = data_folder or "html_data"
        self.my_parser = BaseParser()
        self.sessions = list()
        for i in range(session_num):
            self.sessions.append(requests.Session())

    def get_html(self, url, headers=None):
        assert len(self.sessions) != 0, "There's no Session available!"
        headers = headers or self.headers
        current_session = random.choice(self.sessions)
        raw_html = current_session.get(url, headers=headers).content
        decoded_html = self.__decode_html(raw_html)
        return decoded_html

    def __decode_html(self, raw_html):
        encoding_info = chardet.detect(raw_html)
        try:
            return raw_html.decode(encoding_info["encoding"] or "utf8")
        except Exception as e:
            print("Failed to decode:", e)
            return raw_html.decode("utf8")

    def __get_links(self, html_content, current_url):
        return self.my_parser.parse_url(html_content, current_url)

    def __wirte_data(self, url, content):
        filename = os.path.join(self.data_folder, self.__valid_filename(url))
        with open(self.index_file, mode="a", encoding="utf8") as index:
            index.write("{url}\t{filename}\n".format(url=url, filename=filename))
        if not os.path.exists(self.data_folder):
            os.mkdir(self.data_folder)
        with open(filename, mode="w", encoding="utf8") as file:
            file.write(content)

    def __valid_filename(self, s):
        import string
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        s = ''.join(c for c in s if c in valid_chars)
        s += ".html"
        return s

    def crawl_from(self, seed, max_page, thread_num=None, sleeping=None):

        def crawl_single_page():
            print("I'm working!")
            while count[0] < max_page:
                url = url_queue.get(timeout=10)
                if not crawled.check(url):
                    print("#{0:<4} {1}".format(count[0]+1, url))
                    try:
                        content = self.get_html(url)
                        outlinks = self.__get_links(content, url)
                        self.__wirte_data(url, content)
                    except Exception as e:
                        print(e)
                        continue
                    with lock:
                        if count[0] >= max_page:
                            print("Drop!")
                            break
                        graph[url] = outlinks
                        for l in outlinks:
                            url_queue.put(l)
                        crawled.add(url)
                        count[0] += 1
                    sleep(sleeping)
                url_queue.task_done()
            print("Done!")
        url_queue = Queue()
        lock = Lock()
        crawled = BloomFilter(max_page)
        graph = {}
        count = [0, ]
        url_queue.put(seed)
        threads = []
        sleeping = sleeping or 5
        print("Thread:", thread_num or self.thread_num)
        for i in range(thread_num or self.thread_num):
            t = Thread(target=crawl_single_page)
            threads.append(t)
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()
        return graph, crawled


def unit_test():
    print("Unit Test Begins.")
    test_crawler = BaseCrawler()
    print("Try to get the content of https://keithnull.top/")
    html = test_crawler.get_html("https://keithnull.top/")
    assert html.find("Keith") != -1
    print("Success")


def debugging():
    crawler = MultiThreadingCrawler()
    seed = "https://www.baidu.com"
    max_page = 10
    thread_num = 4
    crawler.crawl_from(seed, max_page, thread_num)


if __name__ == '__main__':
    # unit_test()
    debugging()
