#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import sqlite3
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
        self.conn = sqlite3.connect('fixtures/wine.db')
        self.c = self.conn.cursor()
        self.small_categories = []
        self.small_regions = []

    def analyze_category(self):
        sql = 'select Country, count(*) as cnt from product group by Country having cnt < 10'
        self.c.execute(sql)
        self.small_categories = [cols[0] for cols in self.c.fetchall()]

        sql = 'select Region, count(*) as cnt from product group by Region having cnt < 5'
        self.c.execute(sql)
        self.small_regions = [cols[0] for cols in self.c.fetchall()]

    def handle(self, product_class_name):
        self.analyze_category()
        product_class = ProductClass.objects.get(
            name=product_class_name)

        self.c.execute('select * from product')
        for cols in self.c.fetchall():
            print cols
            try:
                self.create_product(product_class, cols)
            except Exception, e:
                print cols
                print e

    def create_product(self, product_class, cols):
        (upc, title, sku) = cols[0:3]
        description = cols[12]
        partner = 'msh'
        price = cols[8]
        stock = cols[9]

        country = cols[3]
        region = cols[4]
        if country in self.small_categories:
            category = 'Wines > Others'
        else:
            if region in self.small_regions:
                category = 'Wines > %s > Others' % country
            else:
                category = 'Wines > %s > %s' % (country, region)

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
    importer = WineSiteImporter()
    importer.handle('Wines')
