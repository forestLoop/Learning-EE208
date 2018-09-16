import requests


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


def unit_test():
    print("Unit Test Begins.")
    test_crawler = BaseCrawler()
    print("Try to get the content of https://keithnull.top/")
    html = test_crawler.get_html("https://keithnull.top/")
    assert html.find("Keith") != -1
    print("Success")


if __name__ == '__main__':
    unit_test()
