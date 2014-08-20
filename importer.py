#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import sqlite3
import sys
#
# from apps.wine.crawler import WineModel
#
#
# reload(sys)
# sys.setdefaultencoding('utf8')
#
#
# def import_dat_to_sqlite():
#     conn = sqlite3.connect('wine.db')
#     c = conn.cursor()
#
#     CREATE_TABLE = '''create table if not exists product (
#       Id integer primary key,
#       Name varchar(100),
#       Code varchar (10),
#       Country varchar(100),
#       Region varchar (100),
#       Rating varchar (20),
#       Type varchar(20),
#       Size integer null,
#       Price double null,
#       Stock integer null,
#       Classification varchar(50) null,
#       Vintage integer null,
#       Description text null,
#       Image varchar(100) null
#     )'''
#
#     INSERT = 'insert into product (%s) values (%s)'
#
#     is_header = True
#     columns = []
#     sqls = []
#
#     for line in open('wines.dat', 'r'):
#         if is_header:
#             columns = line.strip().split('|')
#             is_header = False
#             INSERT = INSERT % (','.join(columns), ','.join(['?'] * len(columns)))
#             continue
#
#         items = [unicode(e) for e in line.strip().split('|')]
#         items = [e if e != '' else None for e in items]
#         dic = dict(zip(columns, items))
#         wine = WineModel(dic)
#         try:
#             wine.Id = int(wine.Id)
#
#             if wine.Size:
#                 if wine.Size == 'Miniature':
#                     wine.Size = 10
#                 else:
#                     wine.Size = int(wine.Size[:-2])
#
#             if wine.Stock:
#                 wine.Stock = int(wine.Stock)
#
#             if wine.Vintage and wine.Vintage != 'NV':
#                 wine.Vintage = int(wine.Vintage)
#
#             if wine.Price:
#                 wine.Price = int(wine.Price[4:][:-2].replace(',', ''))
#
#             sqls.append(tuple(wine.__dict__.values()))
#         except Exception, e:
#             print e
#             print wine.__dict__
#             sys.exit(1)
#
#     c.execute(CREATE_TABLE)
#     c.execute('delete from product')
#     c.executemany(INSERT, sqls)
#     conn.commit()
#     conn.close()
#

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from decimal import Decimal as D
from datetime import datetime

from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.core.loading import get_class, get_classes


ImportingError = get_class('partner.exceptions', 'ImportingError')
Partner, StockRecord = get_classes('partner.models', ['Partner',
                                                      'StockRecord'])
ProductClass, Product, Category, ProductCategory, ProductImage = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'Category',
                         'ProductCategory', 'ProductImage'))


class WineSiteImporter(object):
    """
    Another quick and dirty catalogue product importer. Used to built the
    demo site, and most likely not useful outside of it.
    """

    def __init__(self):
        pass

    def handle(self, product_class_name):
        product_class = ProductClass.objects.get(
            name=product_class_name)

        conn = sqlite3.connect('fixtures/wine.db')
        c = conn.cursor()

        c.execute('select * from product')
        cnt = 0
        for cols in c.fetchall():
            cnt += 1
            print cols
            try:
                self.create_product(product_class, cols)
                # if cnt == 10:
                #     break
            except Exception, e:
                print cols
                print e

    def create_product(self, product_class, cols):
        (upc, title, sku) = cols[0:3]
        description = cols[12]
        partner = 'msh'
        price = cols[8]
        stock = cols[9]
        category = 'Wines > %s > %s' % (cols[3], cols[4])

        if upc:
            try:
                product = Product.objects.get(upc=upc)
            except Product.DoesNotExist:
                product = Product(upc=upc)
        else:
            product = Product()

        product.structure = Product.STANDALONE
        product.title = title
        #product.slug = upc
        product.description = description if description else ''
        product.product_class = product_class

        attr_names = ['Country', 'Region', 'Rating', 'Type', 'Size', 'Classification', 'Vintage']
        attr_values = [cols[3], cols[4], cols[5], cols[6], '%dml' % cols[7], cols[10], cols[11]]

        # Attributes
        for code, value in zip(attr_names, attr_values):
            # Need to check if the attribute requires an Option instance
            attr = product_class.attributes.get(
                code=code)
            if attr.is_option:
                value = attr.option_group.options.get(option=value)
            if attr.type == 'date':
                value = datetime.strptime(value, "%d/%m/%Y").date()
            setattr(product.attr, code, value)

        product.save()

        # Category information
        if category:
            leaf = create_from_breadcrumbs(category)
            ProductCategory.objects.get_or_create(
                product=product, category=leaf)

        # Stock record
        if partner:
            partner, __ = Partner.objects.get_or_create(name=partner)
            try:
                record = StockRecord.objects.get(product=product)
            except StockRecord.DoesNotExist:
                record = StockRecord(product=product)
            record.partner = partner
            record.partner_sku = sku
            record.price_excl_tax = D(price)
            record.price_currency = 'HKD'
            if stock != 'NULL':
                record.num_in_stock = stock
            record.save()


if __name__ == '__main__':
    print '=====> load json'
    os.system('python manage.py loaddata fixtures/wine-products.json ')

    print '=====> import wines'
    importer = WineSiteImporter()
    importer.handle('Wines')

    print '=====> import images'
    os.system('python manage.py oscar_import_catalogue_images fixtures/wineimg/')

    print '=====> update index'
    os.system('python manage.py clear_index --noinput')
    os.system('python manage.py update_index catalogue')