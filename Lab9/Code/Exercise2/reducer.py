#!/usr/bin/env python3
import sys

current_page = None
current_prob = None
current_links = None

for line in sys.stdin:
    line = line.split()
    page, operation_type = int(line[0]), line[1]
    if page != current_page:
        if current_page:
            print(current_page, current_prob, *current_links)
        current_page, current_prob, current_links = page, 0, None
    if operation_type == "links":
        current_links = line[2:]  # note here we don't convert page_id to int
    elif operation_type == "plus":
        current_prob += float(line[2])
if current_page:
    print(current_page, current_prob, *current_links)
