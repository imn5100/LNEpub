# -*- coding: utf-8 -*-
import os
import uuid
from zipfile import ZipFile

import requests

# 封面
# 简介
# 插图
# 章节

from epub import EpubUtil
from wenku8 import Wenku8HtmlParser, Wenku8Res2File

# epubfile = ZipFile('test' + '.epub', 'w')
# os.chdir('template' + "/")
# for d, ds, fs in os.walk('.'):
#     for f in fs:
#         epubfile.write(os.path.join(d, f))
# epubfile.close()

base_url = 'https://www.wenku8.net/novel/2/2255/'

resp = requests.get(base_url + "index.htm")
resp.encoding = 'gbk'
index_data = Wenku8HtmlParser.parse_index(resp.text)
chapters = []
print (index_data)
for book in index_data.get('books'):
    for chapter in book.get('chapters'):
        resp = requests.get(base_url + chapter.get('link'))
        resp.encoding = 'gbk'
        chapters.append(Wenku8HtmlParser.parse_chapter(resp.text))
    break

uid = str(uuid.uuid4())
index_data['uuid'] = uid
index_data['description'] = 'description'
path = EpubUtil.EpubMaker.template(uid)
epub_resource = Wenku8Res2File.res2file(path, chapters)
for res in epub_resource:
    print (res)
maker = EpubUtil.EpubMaker(index_data, epub_resource)
maker.make()
