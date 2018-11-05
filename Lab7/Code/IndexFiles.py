#!/usr/bin/env python

HTML_INDEX_DIR = "IndexFiles.index"
IMAGE_INDEX_DIR = "IndexImages.index"

import sys
import os
import lucene
import threading
import time
import jieba
from html2text import HTML2Text
from urllib.parse import urlsplit
from datetime import datetime
from bs4 import BeautifulSoup

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory

"""
This class is loosely based on the Lucene (java implementation) demo class
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory> <doc_type>(html or image)"""

    def __init__(self, root, storeDir, analyzer, type="html"):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(Paths.get(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)
        self.load_stop_words(["CNstopwords.txt", "ENstopwords.txt", ])
        type_to_index = {
            "html": self.index_html,
            "image": self.index_image,
        }
        type_to_index[type](root, writer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def index_image(self, root, writer):

        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        with open(os.path.join(root, "index.txt"), mode="r", encoding="utf8") as index:
            count = 1
            for line in index:
                print("\r", count, end="", sep="")
                try:
                    image_url, content = line.strip().split()[:2]
                except ValueError as e:
                    print(e)
                    continue
                doc = Document()
                doc.add(Field("raw_content", content, t1))
                content = " ".join(word for word in jieba.cut_for_search(content)
                                   if word.strip() and word not in self.stop_words)

                doc.add(Field("url", image_url, t1))
                doc.add(Field("content", content, t2))
                writer.addDocument(doc)
                count += 1
            print("\n{count} image(s) added.".format(count=count))

    def index_html(self, root, writer):

        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        with open(os.path.join(root, "index.txt"), mode="r", encoding="utf8") as index:
            count = 0
            for line in index:
                try:
                    count += 1
                    url, path = line.strip().split("\t")
                    # path = os.path.join("./", path)
                    print("#{count:<4} Adding {url},{path}".format(url=url, path=path, count=count))
                    name = os.path.split(path)[-1]
                    with open(path, mode="r", encoding="utf8") as file:
                        content = file.read()
                    soup = BeautifulSoup(content, "html.parser")
                    # print(soup.title)
                    title = soup.title.text if soup.title else "No Title!"
                    site = urlsplit(url).netloc
                    html2text = HTML2Text()
                    # you'd better create a new instance everytime
                    html2text.ignore_links = True
                    html2text.ignore_images = True
                    content = html2text.handle(content)  # works better than bs4
                    content = jieba.cut_for_search(content)
                    content = " ".join(word for word in content
                                       if word.strip() and word not in self.stop_words)
                    doc = Document()
                    doc.add(Field("url", url, t1))
                    doc.add(Field("path", path, t1))
                    doc.add(Field("name", name, t1))
                    doc.add(Field("site", site, t1))
                    doc.add(Field("title", title, t1))
                    doc.add(Field("content", content, t2))
                    writer.addDocument(doc)
                except Exception as e:
                    print("Failed in indexDocs:", e)

    def load_stop_words(self, file_list):
        self.stop_words = set()
        for file in file_list:
            print("Loading stop words from", file)
            try:
                count = 0
                with open(file, mode="r", encoding="utf8") as f:
                    for line in f:
                        word = line.strip()
                        if word not in self.stop_words:
                            self.stop_words.add(word)
                            count += 1
                        print("\r", count, sep="", end="")
                print("\r{0} word(s) added.".format(count))
            except Exception as e:
                print("Error!")
                print(e)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(IndexFiles.__doc__)
        sys.exit(1)
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    start = datetime.now()
    try:
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        type_to_dir = {
            "image": IMAGE_INDEX_DIR,
            "html": HTML_INDEX_DIR
        }
        index_type = sys.argv[2].lower()
        IndexFiles(sys.argv[1], os.path.join(base_dir, type_to_dir[index_type]),
                   StandardAnalyzer(), index_type)
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e
