from my_utils.crawlers import MultiThreadingCrawler
import sys
import os

if __name__ == '__main__':
    seed = "https://www.hao123.com/"
    max_page = 5000
    thread_num = 16
    sleeping = 1
    session_num = 32
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    index_file = os.path.join(data_dir, "index.txt")
    data_folder = os.path.join(data_dir, "html_data")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    my_crawler = MultiThreadingCrawler(thread_num, headers, session_num,
                                       index_file, data_folder, debug=False, verbose=False)
    my_crawler.crawl_from(seed, max_page, thread_num, sleeping)
