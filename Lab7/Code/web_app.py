import web
import sys
import os
import lucene
import jieba
from html2text import HTML2Text

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search import BooleanQuery, TermQuery
from org.apache.lucene.search import BooleanClause
from org.apache.lucene.index import Term

HTML_INDEX_DIR = "IndexFiles.index"
IMAGE_INDEX_DIR = "IndexImages.index"


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


def search_html(query_string, limit=10):

    command_dict = parse_command(query_string)
    vm_env.attachCurrentThread()
    querys = BooleanQuery.Builder()
    cutted_query = None
    for k, v in command_dict.items():
        if k == "content":
            cutted_query = [x for x in jieba.cut_for_search(v) if x.strip()]
            v = " ".join(cutted_query)
        query = QueryParser(k, analyzer).parse(v)
        querys.add(query, BooleanClause.Occur.MUST)
    querys = querys.build()
    querys = BooleanQuery.Builder().add(query, BooleanClause.Occur.MUST).build()
    scoreDocs = searcher["html"].search(querys, limit).scoreDocs
    result = list()
    for num, scoreDoc in enumerate(scoreDocs):
        doc = searcher["html"].doc(scoreDoc.doc)
        single_result = {
            "title": doc.get("title"),
            "url": doc.get("url"),
        }
        with open(doc.get("path"), mode="r", encoding="utf8") as file:
            content = file.read()
        html2text = HTML2Text()
        html2text.ignore_links = True
        html2text.ignore_images = True
        content = html2text.handle(content)
        cutted_content = jieba.cut(content)
        flag = False
        if cutted_query:
            word_num, cnt = 20, 0
            for x in cutted_content:
                if not x.strip():
                    continue
                if not flag and x in cutted_query:
                    flag = True
                    content = ""
                if flag and cnt < word_num:
                    cnt += 1
                    content += (x if x not in cutted_query else
                                "<span class='highlight'>{0}</span>".format(x)
                                )
                elif cnt >= word_num:
                    break
        single_result["content"] = content if flag else content[:100]
        result.append(single_result)
    return result


def search_image(query_string, result_num=10):
    vm_env.attachCurrentThread()
    cutted = [x for x in jieba.cut_for_search(query_string) if x.strip()]
    command = " ".join(cutted)
    query = QueryParser("content", analyzer).parse(command)
    scoreDocs = searcher["image"].search(query, 10).scoreDocs
    result = list()
    for num, scoreDoc in enumerate(scoreDocs):
        doc = searcher["image"].doc(scoreDoc.doc)
        single_result = {
            "url": doc.get("url"),
            "description": doc.get("raw_content"),
        }
        result.append(single_result)
    return result


class Index:
    def GET(self):
        return render.index()


class IndexImage:
    def GET(self):
        return render.index_image()


class Search:
    def GET(self, search_type="html"):
        search_data = web.input()
        query_string = search_data.get("s", "")
        if not query_string:
            return render.index() if search_type == "html" else render.index_image()
        if search_type not in ("html", "image"):
            search_type = "html"
        # globals()["vm_env"].attachCurrentThread()
        search_result = search_function[search_type](query_string)
        return result_template[search_type](query_string, search_result)


urls = (
    "/", "Index",
    "/image", "IndexImage",
    "/search/(.+)", "Search",

)

render = web.template.render("templates", cache=False)
search_function = {
    "html": search_html,
    "image": search_image,
}
result_template = {
    "html": render.result,
    "image": render.result_image,
}

if __name__ == '__main__':
    vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = {
        "html": SimpleFSDirectory(Paths.get(os.path.join(base_dir, HTML_INDEX_DIR))),
        "image": SimpleFSDirectory(Paths.get(os.path.join(base_dir, IMAGE_INDEX_DIR))),
    }
    searcher = {
        "html": IndexSearcher(DirectoryReader.open(directory["html"])),
        "image": IndexSearcher(DirectoryReader.open(directory["image"])),
    }
    analyzer = StandardAnalyzer()
    app = web.application(urls, globals(), autoreload=False)
    app.run()
