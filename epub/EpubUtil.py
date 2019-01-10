#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import codecs
import datetime
import os
import shutil
import uuid
from zipfile import ZipFile


class MEDIA_TYPE(object):
    HTML_XML = "application/xhtml+xml"
    IMAGE_JPG = "image/jpeg"
    IMAGE_PNG = "image/png"
    FONTS = "application/x-font-ttf"
    CSS = 'text/css'
    NCX = 'application/x-dtbncx+xml'


default_info = {
    'creator': 'imn5100',
    'subject': '轻小说',
    'source': 'wenku8',
    'now': datetime.datetime.now().strftime('%Y-%m-%d'),
}
# contetn template
content_header_tem = """<?xml version="1.0" encoding="utf-8"?>
<package version="2.0" unique-identifier="BookId" xmlns="http://www.idpf.org/2007/opf">
"""
content_tail_tem = """
  <guide>
    <reference type="cover" title="Cover" href="Text/cover.xhtml"/>
  </guide>
</package>
"""
manifest_item_tem = '   <item id="%(id)s" href="%(href)s" media-type="%(type)s"/>'
spine_tem = '   <itemref idref="%(id)s"/>'

# toc template
toc_header_tem = """<?xml version="1.0" encoding="utf-8" ?>
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
    <meta content="urn:uuid:%(uuid)s" name="dtb:uid"/>
    <meta content="0" name="dtb:depth"/>
    <meta content="0" name="dtb:totalPageCount"/>
    <meta content="0" name="dtb:maxPageNumber"/>
  </head>
  <docTitle>
    <text>%(title)s</text>
  </docTitle>
  <docAuthor>
    <text>%(author)s</text>
  </docAuthor>
  <navMap>
"""

toc_tail_tem = """
  </navMap>
</ncx>
"""

toc_navPoint_tem = """
<navPoint id="%(id)s" playOrder="%(no)s">
      <navLabel>
        <text>%(title)s</text>
      </navLabel>
      <content src="%(href)s"/>
</navPoint>
"""


class DictObj(dict):
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(r"'JsonDict' object has no attribute '%s'" % attr)

    def __setattr__(self, attr, value):
        self[attr] = value


class Resource(DictObj):
    def __init__(self):
        """

        """
        # id 文件名
        super(Resource, self).__init__()
        self.id = 'chapter1.xhtml'
        # 类型
        self.type = MEDIA_TYPE.HTML_XML
        # 文件路径
        self.href = 'Text/chapter1.xhtml'
        # 排序
        self.no = 2
        self.title = '第一章'
        # 是否是内容
        self.spine = True
        # 是否是目录章
        self.toc = True


class EpubMaker(object):
    def __init__(self, book_info, resources):
        """
        :param book_info:dict  书信息(title 书名,description 介绍,source 来源,author 作者,creator 文件创建者作者,subject 类型,now 当前日期,uuid)
        :param resources:dict list  资源(id即文件名,type文件类型,href文件路径,title标题,spine是否是章节内容,toc是否是目录,no如果是目录需要的编号)
        """
        if book_info is None or len(book_info) == 0 or len(resources) == 0:
            raise RuntimeError("book_info is empty")
        self.book_info = book_info
        if 'uuid' not in self.book_info:
            self.uuid = uuid.uuid4()
            book_info['uuid'] = uuid
        self.uuid = book_info.get('uuid')
        self.resources = resources
        self.path = 'tmp/' + str(self.uuid)
        self.set_default()

    def set_default(self):
        for (k, v) in default_info.items():
            if k not in self.book_info:
                self.book_info[k] = v

    @staticmethod
    def template(uid):
        if not uid:
            raise RuntimeError("uid is empty")
        path = 'tmp/' + str(uid)
        shutil.copytree("template", path)
        return path

    def make(self):
        # 内容
        content_file = codecs.open(self.path + "/OEBPS/content.opf", 'w', encoding='utf-8')
        content = content_header_tem + self.metadata() + self.manifest() + self.spine() + content_tail_tem
        content_file.write(content)
        # 导航
        toc_file = codecs.open(self.path + "/OEBPS/toc.ncx", 'w', encoding='utf-8')
        toc = self.toc_header() + self.toc_nav_points() + toc_tail_tem
        toc_file.write(toc)

        epubfile = ZipFile(self.book_info['title'] + '.epub', 'w')
        os.chdir(self.path + "/")
        for d, ds, fs in os.walk('.'):
            for f in fs:
                epubfile.write(os.path.join(d, f))
        epubfile.close()

        # shutil.rmtree("../tmp")

    def metadata(self):
        meta = """<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
   <dc:title>%(title)s</dc:title>
   <dc:creator opf:role="aut" opf:file-as="%(creator)s">%(creator)s</dc:creator>
   <dc:language>zh</dc:language>
   <dc:rights>%(creator)s</dc:rights>
   <dc:subject>%(subject)s</dc:subject>
   <dc:description>%(description)s</dc:description>
   <dc:source>%(source)s</dc:source>
   <dc:publisher>%(creator)s</dc:publisher>
   <dc:date opf:event="publication">%(now)s</dc:date>
   <dc:date opf:event="modification">%(now)s</dc:date>
   <meta content="0.9.8" name="Sigil version" />
   <dc:identifier id="BookId" opf:scheme="UUID">urn:uuid:%(uuid)s</dc:identifier>
   <meta name="cover" content="cover.jpg" />
</metadata>""" % self.book_info
        return meta

    def manifest(self):
        return EpubMaker.manage_resources(self.resources, manifest_item_tem,
                                          '<manifest> <item id="ncx" href="toc.ncx" '
                                          'media-type="application/x-dtbncx+xml"/>',
                                          '</manifest>')

    def spine(self):
        return EpubMaker.manage_resources(self.resources, spine_tem, '<spine toc="ncx">', '</spine>',
                                          lambda resource: ('spine' in resource and resource.get('spine')))

    def toc_nav_points(self):
        return EpubMaker.manage_resources(self.resources, toc_navPoint_tem,
                                          res_filter=lambda resource: ('toc' in resource and resource.get('toc')))

    @staticmethod
    def manage_resources(resources, tem, head='', tail='', res_filter=None):
        res_item = []
        for res in resources:
            if res_filter:
                if res_filter(res):
                    res_item.append(tem % res)
            else:
                res_item.append(tem % res)
        return "\n" + head + "\n" + '\n'.join(res_item) + "\n" + tail

    def toc_header(self):
        return toc_header_tem % self.book_info


if __name__ == '__main__':
    res = [
        {
            'title': '封面',
            'spine': True,
            'no': 0,
            'href': 'Text/cover.xhtml',
            'toc': False,
            'type': 'application/xhtml+xml',
            'id': 'cover.xhtml'
        },
        {
            'title': 'img1',
            'spine': False,
            'no': 0,
            'href': 'Images/1.jpg',
            'toc': False,
            'type': "image/jpeg",
            'id': '1.jpg'
        },
        {
            'title': '第一章',
            'spine': True,
            'no': 1,
            'href': 'Text/chapter1.xhtml',
            'toc': True,
            'type': 'application/xhtml+xml',
            'id': 'chapter1.xhtml'
        },
        {
            'title': '第二章',
            'spine': True,
            'no': 2,
            'href': 'Text/chapter2.xhtml',
            'toc': True,
            'type': 'application/xhtml+xml',
            'id': 'chapter2.xhtml'
        },
        {
            'title': '第三章',
            'spine': True,
            'no': 3,
            'href': 'Text/chapter3.xhtml',
            'toc': True,
            'type': 'application/xhtml+xml',
            'id': 'chapter3.xhtml'
        },

    ]
    em = EpubMaker({
        'title': '阿U',
        'description': 'des',
        'source': 'wenku8.com',
        'author': 'sssg',
        'creator': 'imn5100',
        'subject': '轻小说',
        'now': datetime.datetime.now().strftime('%Y-%m-%d'),
        'uuid': uuid.uuid4()
    }, res)
    em.make()
