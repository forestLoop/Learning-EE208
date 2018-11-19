#!/usr/bin/env python3
import sys

current_page = None
current_prob = None
link_graph = dict()

result = dict()

for line in sys.stdin:
    line = line.split()
    page, prob = int(line[0]), float(line[1])
    if len(line) >= 3:
        get_from = int(line[2])
        link_graph.setdefault(get_from, set()).add(page)
    if page == current_page:
        current_prob += prob
    else:
        if current_page:
            result[current_page] = current_prob
        current_page, current_prob = page, prob
if current_page:
    result[current_page] = current_prob
for page, prob in result.items():
    print(page, prob, *link_graph[page])
