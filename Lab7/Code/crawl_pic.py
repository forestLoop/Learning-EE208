import os
from my_utils.crawlers import BaseCrawler
from my_utils.parsers import QSBKParser

if __name__ == '__main__':
    next_page = "https://www.qiushibaike.com/pic/"
    data_dir = "pic_data"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    index_file = os.path.join(data_dir, "index.txt")
    data_folder = os.path.join(data_dir, "html_data")
    headers = {
        "Host": "www.qiushibaike.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.qiushibaike.com/pic/",
        "Cookie": "_xsrf=2|e1edb3d8|832b81def1106569211638bf40263909|1536828189; __cur_art_index=2506; _qqq_uuid_=2 | 1: 0 | 10: 1540125968 | 10: _qqq_uuid_ | 56: OTc3ZGU4NjE0MWFjNzAzOTMxODEzNmE3YjQzYjI5YmEzOGQzZjAwNQ == |c2e290887caef12d0a2fa99c85728fd72dd79d091779355f36eeb878d600df64",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "If-None-Match": "81d09eec532d7e4ec86ffefc9d0a418532d1fa8f",
    }
    crawler = BaseCrawler(headers=headers)
    parser = QSBKParser()
    while next_page:
        print(next_page)
        html_content = crawler.get_html(next_page)
        docs, next_page = parser.parse_page(html_content, current_url=next_page)
        with open(index_file, mode="a", encoding="utf8") as index:
            for post in docs.values():
                index.write("{img}\t{content}\n".format(img=post["img_url"],
                                                        content=post["content"]))
    print("Done!")
