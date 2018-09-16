import sys
import urllib2
from bs4 import BeautifulSoup


def parseURL(content):
    urlset = set()
    ########################
    # write your code here
    ########################

	
    return urlset


def write_outputs(urls, filename):
    with open(filename, 'w') as f:
        for url in urls:
            f.write(url)
            f.write('\n')


def main():
    url = 'http://www.baidu.com'
    # url = 'http://www.sjtu.edu.cn'
    if len(sys.argv) > 1:
        url = sys.argv[1]
    content = urllib2.urlopen(url).read()
    urls = parseURL(content)
    write_outputs(urls, 'res1.txt')


if __name__ == '__main__':
    main()
