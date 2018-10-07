# -*- coding: gbk -*-
import time
import copy


def make_hashtable(b):
    return [[], ]*b


def hashtable_get_bucket(table, keyword):
    return table[hash_string(keyword, len(table))]


def hash_string(keyword, buckets):
    h = 0
    for char in keyword:
        h = 31 * h + ord(char)
    return h % buckets


def hashtable_add(table, keyword):
    hashtable_get_bucket(table, keyword).append(keyword)


def hashtable_lookup(table, keyword):
    return keyword in hashtable_get_bucket(table, keyword)


def get_random_string():
    import random
    return ''.join(random.sample([chr(i) for i in range(48, 123)], 6))


tocrawl = [get_random_string() for i in range(10**4)]
tocrawl_copy = copy.deepcopy(tocrawl)
# tocrawl.pop()�Ὣtocrawl�е�Ԫ��ȫ��ȥ������Ҫ�ิ��һ��


def time_execution(code):
    start = time.time()
    result = eval(code)
    run_time = time.time() - start
    return run_time, result


def crawl(tocrawl):
    crawled = []
    while tocrawl:
        page = tocrawl.pop()
        if page not in crawled:
            # crawl page
            crawled.append(page)
    return crawled


def crawl_hashtable(tocrawl):
    table = make_hashtable(100)
    while tocrawl:
        page = tocrawl.pop()
        if not hashtable_lookup(table, page):
            # crawl page
            hashtable_add(table, page)
    return table


[time_crawl, crawled] = time_execution('crawl(tocrawl)')
[time_crawl_hashtable, table] = time_execution('crawl_hashtable(tocrawl_copy)')
print(time_crawl)
print(time_crawl_hashtable)