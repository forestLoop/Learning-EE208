#!/usr/bin/env python3
import sys

damping_factor = 0.85
page_num = 0
sink_pages = set()
for line in sys.stdin:
    line = line.split()
    try:
        page_id, initial_prob = int(line[0]), float(line[1])
    except:
        continue
    else:
        page_num += 1
    if len(line) <= 2:  # for pages that link to no other pages
        sink_pages.add((page_id, initial_prob))
    else:
        links_list = line[2:]
        prob_per_link = initial_prob/(len(links_list)) * damping_factor
        for link in links_list:
            print("{page} {plus} {get_from}".format(page=link, plus=prob_per_link, get_from=page_id))

for i in range(1, page_num+1):
    print("{page} {plus}".format(page=i, plus=(1-damping_factor)/page_num))
for sink in sink_pages:
    prob_per_page = sink[1]/(page_num-1) * damping_factor
    for page in range(1, page_num+1):
        if page != sink[0]:
            print("{page} {plus}".format(page=page, plus=prob_per_page))
print("Page Num", page_num)
