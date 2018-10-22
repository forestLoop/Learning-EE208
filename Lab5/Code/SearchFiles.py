#!/usr/bin/env python

INDEX_DIR = "IndexFiles.index"

import sys
import os
import lucene
import jieba

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search import BooleanQuery, TermQuery
from org.apache.lucene.search import BooleanClause
from org.apache.lucene.index import Term
"""
This script is loosely based on the Lucene (java implementation) demo class
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""


def parse_command(command):
    allowed_opts = ["site", ]
    command_dict = dict()
    opt = "content"
    for s in command.split():
        if ":" in s:
            opt, value = s.split(":")[:2]
            opt = opt.lower()
            if opt in allowed_opts and value:
                command_dict[opt] = value
        else:
            command_dict[opt] = command_dict.get(opt, "") + " " + s
    return command_dict


def run(searcher, analyzer):
    while True:
        print("Hit enter with no input to quit.")
        command = input("Query:")
        import os
        os.system("clear")
        if command == "":
            return
        print("Searching for:", command)
        command_dict = parse_command(command)
        querys = BooleanQuery.Builder()
        for k, v in command_dict.items():
            if k == "content":
                cutted = [x for x in jieba.cut_for_search(v) if x.strip()]
                v = " ".join(cutted)
                print("After segmentation:", v)
            query = QueryParser(k, analyzer).parse(v)
            querys.add(query, BooleanClause.Occur.MUST)
        # query = QueryParser("content", analyzer).parse(command)
        querys = querys.build()
        # query = QueryParser("content", analyzer).parse("美好")
        # query = TermQuery(Term("content", "美好"))
        querys = BooleanQuery.Builder().add(query, BooleanClause.Occur.MUST).build()
        scoreDocs = searcher.search(querys, 10).scoreDocs
        print("{} total matching documents.".format(len(scoreDocs)))
        for num, scoreDoc in enumerate(scoreDocs):
            doc = searcher.doc(scoreDoc.doc)
            print("\n#{num}:\nTitle:{title}\nURL:{url}\nSite:{site}\nPath:{path}\nFile Name:{name}\n".format(
                num=num + 1, title=doc.get("title"), url=doc.get("url"),
                path=doc.get("path"), name=doc.get("name"), site=doc.get("site")))


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(Paths.get(os.path.join(base_dir, INDEX_DIR)))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = StandardAnalyzer()
    run(searcher, analyzer)
    del searcher
