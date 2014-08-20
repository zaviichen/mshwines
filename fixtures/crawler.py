#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import urllib2
import codecs
from bs4 import BeautifulSoup

query_url = 'http://www.mshwines.com/%s/products_details.php?id=%d'
img_url = 'http://www.mshwines.com/ufiles/'


class WineModel(object):
    """ """
    def __init__(self, dic):
        self.Id = dic.get('Id', '0')
        self.Name = dic.get('Name', '')
        self.Code = dic.get('Code', '')
        self.Vintage = dic.get('Vintage', '')
        self.Country = dic.get('Country', '')
        self.Region = dic.get('Region', '')
        self.Type = dic.get('Type', '')
        self.Classification = dic.get('Classification', '')
        self.Size = dic.get('Size', '')
        self.Rating = dic.get('Rating', '')
        self.Price = dic.get('Price', '')
        self.Stock = dic.get('Stock', '0')
        self.Description = dic.get('Description', '')
        self.Image = dic.get('Image', '')

    def __str__(self):
        return '|'.join([str(e) for e in self.__dict__.values()])


class MshCrawler(object):
    """ """
    # def __init__(self, file):
    #     self.out = codecs.open(file, 'w', 'utf-8')

    # def __del__(self):
    #     self.out.close()

    def download(self, url):
        data = None
        try:
            conn = urllib2.urlopen(url)
            data = conn.read()
            conn.close()
        except Exception, e:
            print e
        return data

    def get_image(self, wine):
        url = img_url + urllib2.quote(wine.Image)
        img = self.download(url)
        if img:
            f = open('wineimg/' + wine.Image, 'wb')
            f.write(img)
            f.close()
        else:
            print 'Image Not Found: %s' % wine.Id

    def retrive(self, id, lang):
        url = query_url % (lang, id)
        html = self.download(url)
        if not html:
            return None
        try:
            #soup = BeautifulSoup(open("wine.html"))
            soup = BeautifulSoup(html)
            tds = soup.find(id='contentWrapper').find_all('td')
            infos = {'Id': str(id)}
            infos['Name'] = tds[1].span.string
            trs = tds[1].find_all('tr')
            for e in trs[:-2]:
                try:
                    key = e.td
                    value = key.next_sibling.next_sibling
                    infos[key.string[:-1]] = value.string
                except:
                    pass
            desc = trs[-1].td.string
            infos['Description'] = desc if desc.replace('\n', '') else ''
            if tds[0].img:
                infos['Image'] = tds[0].img['src'].split('/')[-1]
            return WineModel(infos)
        except Exception, e:
            #print '%d: %s' % (id, e)
            pass
        return None


if __name__ == '__main__':
    import sys
    if len(sys.argv) <= 2:
        print 'command error. exists.'
        sys.exit(1)
    begin_id = int(sys.argv[1])
    end_id = int(sys.argv[2])
    if end_id < begin_id:
        print 'begin_id is greater than end_id. exits.'
        sys.exit(1)

    crawler = MshCrawler()
    wines = []
    f = codecs.open('wines.dat', 'w', 'utf-8')
    #f.write('|'.join(wines[0].__dict__.keys()) + '\n')

    for id in range(begin_id, end_id):
        print '==> get %d...' % id
        wine = crawler.retrive(id, 'en')
        if not wine:
            print '    not exists'
            continue
        wines.append(wine)
        if wine.Image != '':
            print '    image: ' + wine.Image
            crawler.get_image(wine)
        f.write('%s\n' % wine)
    f.close()