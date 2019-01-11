# -*- coding: utf-8 -*-
import codecs
import os
import shutil

import requests

text_xhtml_tem = u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:xml="http://www.w3.org/XML/1998/namespace">
<head>
<link href="../Styles/style.css" rel="stylesheet" type="text/css"/>

<title>%(title)s</title>
</head>

<body>
%(content)s
</body>
</html>
"""

img_xhtml_tem = u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:xml="http://www.w3.org/XML/1998/namespace">
<head>
  <link href="../Styles/style.css" rel="stylesheet" type="text/css"/>
  <title>%(title)s</title>
</head>
<body>
  <div>
<div class="center duokan-image-single"><img alt="003" src="../Images/%(id)s"/></div>
    </div>
</body>
</html>
"""

cover_xhtml_tem = u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:xml="http://www.w3.org/XML/1998/namespace">
<head>
  <link href="../Styles/style.css" rel="stylesheet" type="text/css"/>

  <title>封面</title>
</head>

<body>
  <div>
  <div class="cover duokan-image-single"><img alt="" class="bb" src="../Images/%(id)s"/></div>
 </div>
</body>
</html>
"""


# chapter = {
#     'title': main.find('div', id='title').text,
#     'content': str(content),
#     'imgs': [],
#     'is_image': False
#
# }
# id 文件名
# self.id = 'chapter1.xhtml'
# # 类型
# self.type = MEDIA_TYPE.HTML_XML
# # 文件路径
# self.href = 'Text/chapter1.xhtml'
# # 排序
# self.no = 2
# self.title = '第一章'
# # 是否是内容
# self.spine = True
# # 是否是目录章
# self.toc = True

def download(url, prefix='', path=None, override=False):
    if not path:
        path = prefix + os.path.basename(url)
    if os.path.exists(path) and not override:
        return path
    response = requests.get(url, timeout=60, stream=True)
    with open(path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    return path


def manage_img(path, res):
    epub_resource = []
    urls = res['imgs']
    is_first = True
    for url in urls:
        epub_resource.extend(img2xhtml(res, path, url, is_first))
        is_first = False
    return epub_resource


def cover(path, url):
    is_jpg = not str(url).endswith('.png')
    file_name = "cover" + ('.png' if not is_jpg else '.jpg')
    download(url, path=path + "/OEBPS/Images/" + file_name, override=True)
    return {'id': file_name, 'type': ('image/png' if not is_jpg else 'image/jpeg'),
            'href': 'Images/' + file_name,
            'title': u'封面',
            'spine': False, 'toc': False}


def img2xhtml(res, path, url, toc=False):
    epub_resources = []
    download(url, prefix=path + "/OEBPS/Images/")
    file_name = os.path.basename(url)
    is_jpg = not str(url).endswith('.png')
    epub_resources.append(
        {'id': file_name, 'type': ('image/png' if not is_jpg else 'image/jpeg'),
         'href': 'Images/' + file_name,
         'title': res['title'],
         'spine': False, 'toc': False})

    name = file_name + '.xhtml'
    file_content = img_xhtml_tem % {'id': file_name, 'title': file_name}
    content_file = codecs.open(path + "/OEBPS/Text/" + name, 'w', encoding='utf-8')
    content_file.write(file_content)
    epub_resources.append(
        {'id': name, 'type': 'application/xhtml+xml', 'href': 'Text/' + name, 'title': res['title'],
         'spine': True, 'toc': toc})
    return epub_resources


def res2file(path, resources, cover_url=None):
    epub_resource = []
    img_res = None
    if cover_url:
        epub_resource.insert(0, cover(path, cover_url))
    for res in resources:
        if 'is_image' in res and res.get('is_image'):
            if cover_url is None:
                epub_resource.insert(0, cover(path, res['imgs'][0]))
            img_res = manage_img(path, res)
        else:
            file_content = text_xhtml_tem % res
            name = res['title'] + '.xhtml'
            content_file = codecs.open(path + "/OEBPS/Text/" + name, 'w', encoding='utf-8')
            content_file.write(file_content)
            epub_resource.append(
                {'id': name, 'type': 'application/xhtml+xml', 'href': 'Text/' + name, 'title': res['title'],
                 'spine': True, 'toc': True})
    if img_res:
        epub_resource.extend(img_res)
    no = 0
    for res in epub_resource:
        if 'toc' in res and res['toc']:
            res['no'] = no
            no += 1
    return epub_resource
