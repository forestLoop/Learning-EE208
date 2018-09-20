# -*- coding:utf-8 -*-
import urllib2, cookielib, urllib
from bs4 import BeautifulSoup
import sys

def bbs_set(id, pw, text):
    import urllib2, cookielib, urllib
    from bs4 import BeautifulSoup

    ...

    content = urllib2.urlopen('https://bbs.sjtu.edu.cn/bbsplan').read()
    soup = BeautifulSoup(content)
    print str(soup.find('textarea').string).strip().decode('utf8')

if __name__ == '__main__':
	
    id = sys.argv[1]
    pw = sys.argv[2]
    text = sys.argv[3].decode('utf-8').encode('gbk')

    bbs_set(id, pw, text)
