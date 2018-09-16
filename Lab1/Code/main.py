import parsers
import crawlers
import sys
import getopt


def show_help():
    print(
        """
Options:
    -h,--help    Get this help.
    -u,--url     Set the target url. (Default: https://www.baidu.com)
    -o,--output  Set the output file.
    -t,--task    Specify which task to conduct.
                     1 - Parse Urls (Default)
                     2 - Parse Images
                     3 - Parse Qiushibaike
""")


def get_urls(url, output_file):
    my_crawler = crawlers.BaseCrawler()
    my_parser = parsers.BaseParser()
    html_data = my_crawler.get_html(url)
    url_set = my_parser.parse_url(html_data, url)
    with open(output_file, encoding="utf8", mode="w") as file:
        for u in url_set:
            file.write(u+"\n")


def get_imgs(url, output_file):
    my_crawler = crawlers.BaseCrawler()
    my_parser = parsers.BaseParser()
    html_data = my_crawler.get_html(url)
    img_set = my_parser.parse_img(html_data, url)
    with open(output_file, encoding="utf8", mode="w") as file:
        for i in img_set:
            file.write(i+"\n")


def get_jokes(url, output_file):
    assert url.find("www.qiushibaike.com/pic") != -1, "Invalid Qiushibaike URL!"
    my_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36",
        "Referer": "https://www.qiushibaike.com/",
    }
    my_crawler = crawlers.BaseCrawler(headers=my_headers)
    my_parser = parsers.QSBKParser()
    html_data = my_crawler.get_html(url)
    # print(html_data)
    docs, next_page = my_parser.parse_page(html_data, url)
    with open(output_file, encoding="utf8", mode="w") as file:
        file.write("Current Page\t{url}\n".format(url=url))
        for tag, post in docs.items():
            file.write("{img}\t{text}\n".format(img=post["img_url"], text=post["content"]))
        file.write("Next Page\t{url}\n".format(url=next_page))


def main(argv):
    url = "https://www.baidu.com"
    task = 0
    output_file = None
    try:
        opts, _ = getopt.getopt(argv, "u:t:o:h", ["url=", "task=", "output=", "help"])
    except getopt.GetoptError:
        print("Invalid Arguments!")
        opts = (("-h", None),)
    for opt, arg in opts:
        # print(opt, arg)
        if opt in ("-h", "--help"):
            show_help()
            exit()
        elif opt in ("-u", "--url"):
            url = arg
        elif opt in ("-t", "--task"):
            task = int(arg)
        elif opt in ("-o", "--output"):
            output_file = arg
    if task == 1:
        get_urls(url, output_file or "res1.txt")
    elif task == 2:
        get_imgs(url, output_file or "res2.txt")
    elif task == 3:
        get_jokes(url, output_file or "res3.txt")


if __name__ == '__main__':
    main(sys.argv[1:])
