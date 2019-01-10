# -*- coding: utf-8 -*-
import requests
from BeautifulSoup import BeautifulSoup


# https://www.wenku8.net/novel/2/2255/index.htm
def parse_index(html):
    if not html:
        return None
    main = BeautifulSoup(html)
    title = main.find('div', attrs={'id': 'title'}).text
    author = main.find('div', attrs={'id': 'info'}).text
    books = []
    index_data = {
        'title': title,
        'author': author,
        'books': books
    }
    book = None
    table = main.find('table', attrs={'class': 'css'})
    trs = table.findAll('tr')
    if len(trs) > 0:
        for tr in trs:
            title = tr.find('td', attrs={'class': 'vcss'})
            if title is not None:
                book = {'chapters': [], 'book_title': title.text}
                books.append(book)
            else:
                caps = tr.findAll('td', attrs={'class': 'ccss'})
                for cap in caps:
                    a = cap.find('a')
                    if a:
                        book['chapters'].append({
                            'chapters_title': a.text,
                            'link': a['href']
                        })
    return index_data


# https://www.wenku8.net/novel/0/381/13751.htm
def parse_chapter(html):
    if not html:
        return None
    main = BeautifulSoup(html)
    content = main.find('div', id='content')
    uls = content.findAll('ul', id='contentdp')
    for ul in uls:
        ul.decompose()
    chapter = {
        'title': main.find('div', id='title').text,
        'content': unicode(content),
        'imgs': [],
        'is_image': False

    }
    imgs = content.findAll('img', {'class': 'imagecontent'})
    img_urls = []
    if len(imgs) > 0:
        for img in imgs:
            img_urls.append(img['src'])
        chapter['imgs'] = img_urls
        chapter['is_image'] = True
    return chapter


if __name__ == '__main__':
    # resp = requests.get("https://www.wenku8.net/novel/1/1538/index.htm")
    # resp.encoding = 'gbk'
    # print parse_index(resp.text)
    resp = requests.get("https://www.wenku8.net/novel/0/381/25061.htm")
    resp.encoding = 'gbk'
    print (parse_chapter(resp.text))
