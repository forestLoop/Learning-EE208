# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import sys


def bbs_set(id, pw, text):

    s = requests.Session()
    login_data = {
        "id": id,
        "pw": pw,
        "submit": "login",
    }
    login_url = "https://bbs.sjtu.edu.cn/bbslogin"
    login_request = s.post(login_url, login_data)
    assert login_request.status_code == 200, "Failed to log in."
    update_data = {
        "text": text,
        "type": "update",
    }
    update_url = "https://bbs.sjtu.edu.cn/bbsplan"
    update_request = s.post(update_url, update_data)
    content = s.get('https://bbs.sjtu.edu.cn/bbsplan').content
    soup = BeautifulSoup(content, features="html.parser")
    print(str(soup.find('textarea').string).strip())


if __name__ == '__main__':

    id = sys.argv[1]
    pw = sys.argv[2]
    text = sys.argv[3].encode('gbk')

    bbs_set(id, pw, text)
