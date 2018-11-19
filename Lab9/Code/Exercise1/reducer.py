#!/usr/bin/env python3
import sys

current_letter = None
current_count = None
current_sum = None

for line in sys.stdin:
    letter, length = line.split()
    length = int(length)
    if letter == current_letter:
        current_sum += length
        current_count += 1
    else:
        if current_letter != None:
            print("{letter}\t{average}".format(letter=current_letter, average=current_sum/current_count))
        current_letter, current_count, current_sum = letter, 1, length
if current_letter:
    print("{letter}\t{average}".format(letter=current_letter, average=current_sum/current_count))
