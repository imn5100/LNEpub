#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import shutil

import requests

title = 'thisisbooktitle'
creator = 'frank'
description = 'this is description'

htmllist = ['chapter1.html']  # 来自《亲爱的安德烈》中的两章

os.mkdir('tmp')

tmpfile = file('tmp/mimetype', 'w')
tmpfile.write('application/epub+zip')
tmpfile.close()

os.mkdir('tmp/META-INF')

tmpfile = file('tmp/META-INF/container.xml', 'w')
tmpfile.write('''<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
   <rootfiles> <rootfile full-path="OPS/content.opf" media-type="application/oebps-package+xml"/> </rootfiles>
</container>
''')
tmpfile.close()

os.mkdir('tmp/OPS')

if os.path.isfile('cover.jpg'):  # 如果有cover.jpg, 用来制作封面
    shutil.copyfile('cover.jpg', 'tmp/OPS/cover.jpg')
    print 'Cover.jpg found!'

opfcontent = '''<?xml version="1.0" encoding="UTF-8" ?>
<package version="2.0" unique-identifier="PrimaryID" xmlns="http://www.idpf.org/2007/opf">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
%(metadata)s
<meta name="cover" content="cover"/>
</metadata>
<manifest>
%(manifest)s
<item id="ncx" href="content.ncx" media-type="application/x-dtbncx+xml"/>
<item id="cover" href="cover.jpg" media-type="image/jpeg"/>
</manifest>
<spine toc="ncx">
%(ncx)s
</spine>
</package>
'''

dc = '<dc:%(name)s>%(value)s</dc:%(name)s>'
item = "<item id='%(id)s' href='%(url)s' media-type='application/xhtml+xml'/>"
itemref = "<itemref idref='%(id)s'/>"

metadata = '\n'.join([
    dc % {'name': 'title', 'value': title},
    dc % {'name': 'creator', 'value': creator},
    dc % {'name': 'description', 'value': description},
])

manifest = []
ncx = []

for htmlitem in htmllist:
    response = requests.get('https://www.wenku8.net/novel/2/2479/92963.htm')
    response.encoding = 'gbk'
    content = response.text.replace('gbk','utf-8')  # file(htmlitem, 'r').read()
    tmpfile = codecs.open('tmp/OPS/%s' % htmlitem, 'w', encoding='utf-8')
    tmpfile.write(content)
    tmpfile.close()
    manifest.append(item % {'id': htmlitem, 'url': htmlitem})
    ncx.append(itemref % {'id': htmlitem})

manifest = '\n'.join(manifest)
ncx = '\n'.join(ncx)

tmpfile = file('tmp/OPS/content.opf', 'w')
tmpfile.write(opfcontent % {'metadata': metadata, 'manifest': manifest, 'ncx': ncx, })
tmpfile.close()

ncx = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
<head>
  <meta name="dtb:uid" content=" "/>
  <meta name="dtb:depth" content="-1"/>
  <meta name="dtb:totalPageCount" content="0"/>
  <meta name="dtb:maxPageNumber" content="0"/>
</head>
 <docTitle><text>%(title)s</text></docTitle>
 <docAuthor><text>%(creator)s</text></docAuthor>
<navMap>
%(navpoints)s
</navMap>
</ncx>
'''

navpoint = '''<navPoint id='%s' class='level1' playOrder='%d'>
<navLabel> <text>%s</text> </navLabel>
<content src='%s'/></navPoint>'''

navpoints = []
for i, htmlitem in enumerate(htmllist):
    navpoints.append(navpoint % (htmlitem, i + 1, htmlitem, htmlitem))

tmpfile = file('tmp/OPS/content.ncx', 'w')
tmpfile.write(ncx % {
    'title': title,
    'creator': creator,
    'navpoints': '\n'.join(navpoints)})
tmpfile.close()

from zipfile import ZipFile

epubfile = ZipFile('book.epub', 'w')
os.chdir('tmp')
for d, ds, fs in os.walk('.'):
    for f in fs:
        epubfile.write(os.path.join(d, f))
epubfile.close()

shutil.rmtree("../tmp")

print ("Done")
