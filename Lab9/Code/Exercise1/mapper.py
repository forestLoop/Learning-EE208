#!/usr/bin/env python3
import sys
from string import ascii_letters

valid_chars = ascii_letters
for line in sys.stdin:
    stripped_line = "".join([x if x in valid_chars else " " for x in line])
    words_list = stripped_line.split()
    for word in words_list:
        print("{letter}\t{length}".format(letter=word[0].lower(), length=len(word)))
