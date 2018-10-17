from my_utils.crawlers import MultiThreadingCrawler
import sys

if __name__ == '__main__':
    seed = "https://www.baidu.com/"
    max_page = 20
    thread_num = 4
    sleeping = 5
    session_num = 32
    index_file = "data_test1/index.txt"
    data_folder = "data_test1/html_data"
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
    my_crawler = MultiThreadingCrawler(thread_num, headers, session_num, index_file, data_folder)
    my_crawler.crawl_from(seed, max_page, thread_num, sleeping)
