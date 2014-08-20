#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import sqlite3
import sys
from fixtures.crawler import WineModel


reload(sys)
sys.setdefaultencoding('utf8')


def import_dat_to_sqlite():
    conn = sqlite3.connect('wine.db')
    c = conn.cursor()

    CREATE_TABLE = '''create table if not exists product (
      Id integer primary key,
      Name varchar(100),
      Code varchar (10),
      Country varchar(100),
      Region varchar (100),
      Rating varchar (20),
      Type varchar(20),
      Size integer null,
      Price double null,
      Stock integer null,
      Classification varchar(50) null,
      Vintage integer null,
      Description text null,
      Image varchar(100) null
    )'''

    INSERT = 'insert into product (%s) values (%s)'

    is_header = True
    columns = []
    sqls = []

    for line in open('wines.dat', 'r'):
        if is_header:
            columns = line.strip().split('|')
            is_header = False
            INSERT = INSERT % (','.join(columns), ','.join(['?'] * len(columns)))
            continue

        items = [unicode(e) for e in line.strip().split('|')]
        items = [e if e != '' else None for e in items]
        dic = dict(zip(columns, items))
        wine = WineModel(dic)
        try:
            wine.Id = int(wine.Id)

            if wine.Size:
                if wine.Size == 'Miniature':
                    wine.Size = 10
                else:
                    wine.Size = int(wine.Size[:-2])

            if wine.Stock:
                wine.Stock = int(wine.Stock)

            if wine.Vintage and wine.Vintage != 'NV':
                wine.Vintage = int(wine.Vintage)

            if wine.Price:
                wine.Price = int(wine.Price[4:][:-2].replace(',', ''))

            sqls.append(tuple(wine.__dict__.values()))
        except Exception, e:
            print e
            print wine.__dict__
            sys.exit(1)

    c.execute(CREATE_TABLE)
    c.execute('delete from product')
    c.executemany(INSERT, sqls)
    conn.commit()
    conn.close()

