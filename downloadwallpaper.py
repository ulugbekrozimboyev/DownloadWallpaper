# Simple wallpaper downloader from http://www.goodfon.ru

import lxml.html
import urllib
import time
from multiprocessing import Pool

URL = 'http://www.goodfon.ru/'
PAGE_NUMBER = 1
POOL_SIZE = 5


class Wallpaper:
    """Wallpaper class"""

    def __init__(self, url):
        self.__url = url
        self.__data = None
        self.__doc = None

        self.__read_webpage()

    # read web page data
    def __read_webpage(self):
        try:
            self.__data = urllib.urlopen(self.__url).read()
            self.__doc = lxml.html.document_fromstring(self.__data)
        except Exception as e:
            print 'error:', e

    # get wallpaper catalogs
    def get_catalogs(self):
        result = []
        div_catalog = self.__doc.xpath("/html/body/div[1]/div[5]/div")
        if div_catalog:
            div = div_catalog[0].find("div")
            if div is not None:
                for a in div.findall("a"):
                    result.append({
                        'url': a.attrib['href'],
                        'title': a.text_content(),
                    })

        return result

    # get number of web page
    def page_number(self):
        page_info = self.__doc.xpath("/html/body/div[1]/div[37]/div[1]")
        if page_info:
            div = page_info[0].find("div")
            if div is not None:
                return int(div.text_content())

        return 0

    # get image urls
    def get_image_urls(self):
        result = []
        div_container = self.__doc.xpath('/html/body/div[1]')

        for div in div_container:
            for d in div.findall("div"):
                div_tabl_td = d.find_class("tabl_td")
                if not div_tabl_td:
                    continue

                div_image = div_tabl_td[0].find("div")
                if div_image is None:
                    continue

                atag = div_image.find("a")
                if atag is None:
                    continue

                imgtag = atag[0]
                result.append(imgtag.attrib['src'])

        return result


# download big size image
def download_bigimage(url):
    url = url.replace('/middle/', '/big/')
    l = url.split('/')
    img_name = l[len(l) - 1]
    path = './images/%s' % img_name

    try:
        print 'start download:', url
        data = urllib.urlopen(url).read()
        with open(path, 'wb') as f:
            f.write(data)
        print 'downloaded:', url
    except Exception as e:
        print 'error on download:%s' % e


# download images from catalog
def download(catalog=''):
    global PAGE_NUMBER
    current_page = 1
    # create pool for parallelizing download
    pool = Pool(processes=POOL_SIZE)

    while current_page <= PAGE_NUMBER:
        url_page = '%s%s/index-%s.html' % (URL, catalog, current_page)
        wall = Wallpaper(url_page)
        # get all image urls from web page
        urls = wall.get_image_urls()
        # download images parallel
        pool.map(download_bigimage, urls)

        current_page += 1
        time.sleep(5)


if __name__ == '__main__':
    download()