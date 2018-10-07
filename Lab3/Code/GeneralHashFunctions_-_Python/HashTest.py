from GeneralHashFunctions import *
import mmh3
import random
import time
from string import ascii_letters as letters


def test_hash_efficiency(hash_function, test_strings):
    start_time = time.time()
    for s in test_strings:
        hash_function(s)
    finish_time = time.time()
    return finish_time - start_time


test_strings = ["".join(random.sample(letters, 32)) for i in range(100000)]
hash_functions = [hash, mmh3.hash, JSHash, PJWHash, ELFHash, BKDRHash, SDBMHash, DJBHash, DEKHash, BPHash, FNVHash, APHash]

result = []

for f in hash_functions:
    result.append((f.__name__, test_hash_efficiency(f, test_strings)))
    print("{0:<9}: {1:.8f}s".format(*result[-1]))

print("*********Result Sorted By Time**********")
result.sort(key=lambda x: x[1])
for r in result:
    print("{0:<9}: {1:.8f}s({2:.3f}x)".format(*r, r[1]/result[0][1]))


'''
hash     : 0.00897479s
hash     : 0.02493358s
JSHash   : 2.06598854s
PJWHash  : 1.63085604s
ELFHash  : 2.11861658s
BKDRHash : 0.83501196s
SDBMHash : 1.23072314s
DJBHash  : 0.88225102s
DEKHash  : 1.01107359s
BPHash   : 0.73630977s
FNVHash  : 0.99035144s
APHash   : 2.06879592s
*********Result Sorted By Time**********
hash     : 0.00897479s(1.000x)  # Built-in Hash
hash     : 0.02493358s(2.778x)  # mmh3.hash
BPHash   : 0.73630977s(82.042x)
BKDRHash : 0.83501196s(93.040x)
DJBHash  : 0.88225102s(98.303x)
FNVHash  : 0.99035144s(110.348x)
DEKHash  : 1.01107359s(112.657x)
SDBMHash : 1.23072314s(137.131x)
PJWHash  : 1.63085604s(181.715x)
JSHash   : 2.06598854s(230.199x)
APHash   : 2.06879592s(230.512x)
ELFHash  : 2.11861658s(236.063x)
'''
