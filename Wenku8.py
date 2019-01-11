# -*- coding: utf-8 -*-
import time
import uuid
import requests
from epub import EpubUtil
from wenku8 import Wenku8HtmlParser, Wenku8Res2File


def req(url):
    retry_count = 3
    while retry_count > 0:
        try:
            print ('req:' + url)
            response = requests.get(url)
            if response.ok:
                response.encoding = 'gbk'
                return response.text
            else:
                retry_count -= 1
        except Exception as e:
            retry_count -= 1
            print (e)
            time.sleep(2)
    raise RuntimeError("request fail")


# 简介
# 章节
# 插图

# book_info https://www.wenku8.net/book/2255.htm
# index_info https://www.wenku8.net/novel/2/2255/index.htm
# chapter https://www.wenku8.net/novel/2/2255/82491.htm


base_url = 'https://www.wenku8.net/book/2255.htm'
print ('Get book info...')
book_info = Wenku8HtmlParser.parse_book_htm(req(base_url))
print (book_info)

index_url = book_info['index_url']
chapter_base_url = index_url.replace('index.htm', '')

print ('Get book index...')
index_data = Wenku8HtmlParser.parse_index(req(index_url))

uid = str(uuid.uuid4())
book_info.update(index_data)
book_info['uuid'] = uid
book_info['creator'] = index_data['author']
book_info['source'] = 'www.wenku8.net'

chapters = []
print ('Get book chapters...')
for book in index_data.get('books'):
    for chapter in book.get('chapters'):
        chapters.append(Wenku8HtmlParser.parse_chapter(req(chapter_base_url + chapter.get('link'))))

    path = EpubUtil.EpubMaker.template(uid)
    print ('html to epub resources...')
    epub_resource = Wenku8Res2File.res2file(path, chapters, None)
    print ('build epub resources success:' + str(len(epub_resource)))
    print ("making")
    book_info['title'] = book_info['title'] + " " + book['book_title']
    maker = EpubUtil.EpubMaker(book_info, epub_resource)
    maker.make()
    break
