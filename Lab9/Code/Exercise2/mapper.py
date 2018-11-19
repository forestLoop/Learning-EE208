#!/usr/bin/env python3
import sys

damping_factor = 0.85
page_num = 4

for line in sys.stdin:
    line = line.split()
    try:
        page_id, initial_prob = int(line[0]), float(line[1])
    except:
        continue
    print("{page} {plus}".format(page=page_id, plus=(1-damping_factor)/page_num))
    if len(line) <= 2:  # for pages that link to no other pages
        prob_per_page = initial_prob/(page_num-1) * damping_factor
        for page in range(1, page_num+1):
            if page != page_id:
                print("{page} {plus}".format(page=page, plus=prob_per_page))
    else:
        links_list = line[2:]
        prob_per_link = initial_prob/(len(links_list)) * damping_factor
        for link in links_list:
            print("{page} {plus} {get_from}".format(page=link, plus=prob_per_link, get_from=page_id))
