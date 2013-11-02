#!/usr/bin/env python

from bs4 import BeautifulSoup
from decimal import Decimal
from functools import partial
from xml.etree import ElementTree as ET
from lxml import html as lxhtml
from pprint import pprint, pformat
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('mode', nargs='?')
parser.add_argument('html')

def pluralize(word):
    """HORRIBLE WAY TO PLURALIZE A WORD!!!

    Will modify (if needed) in future, otherwise it works ok for now.
    """
    if word.endswith('s'):
        suffix = 'es'
    else:
        suffix = 's'
    return ''.join((word, suffix))

def strip_lower(text):
    """strip() and lower() text."""
    if text is not None:
        try:
            text = text.strip().lower()
        except:
            return None
    return text

def zip_and_dict(lists, keys):
    """Helper to convert value lists to keyed dicts.

    Sample: (should this just be a doc test??)
      lists: [['red', 'blue'], [0, 1]]
      keys: ['color', 'status']
    Returns:
      [{'color': 'red', 'status': 0],
       {'color': 'blue', 'status': 1]]
    """
    lists = zip(*lists)
    lists = map(lambda list: dict(zip(keys, list)), lists)
    return lists

def convert_text(elems, func, split=None):
    """Take a list of elements and return their .text value as ints."""
    nums = []
    for elem in elems:
        num = elem.text
        if num is not None:
            num = strip_lower(num)
            if split is not None:
                num = num.split(split, 1)[0]
            try:
                num = func(num)
            except:
                num = None
        nums.append(num)
    return nums

def intify_text(elems, split=None):
    return convert_text(elems, int, split)

def contains(text):
    """Generate an xpath contains() for text."""
    return 'contains(text(), "{}")'.format(text)

def get_table(lxml, header):
    """Get a table via header text."""
    headers = lxml.xpath('//table//*[{}]'.format(contains(header)))
    if headers:
        tables = headers[0].xpath('./ancestor::table')
        if tables:
            # Return "closest" table
            return tables[-1]

def table_getter(header):
    def func(self):
        return get_table(self.lxml, header)
    return func

def get_row(table, header):
    """Get a row via it's header text."""
    if table is not None:
        xpath = './tbody/tr/td[{}]'.format(contains(header))
        tds = table.xpath(xpath)
        if tds:
            return tds[0].getparent()

def row_getter(table, header):
    def func(self):
        return get_row(get_table(self.lxml, table), header)
    return func

def get_fields(table, header, split=None, convert=None):
    """Get a fields for a row specified by their header text."""
    row = get_row(table, header)
    if row is not None:
        tds = row.xpath('./td')[1:]
        if convert is not None:
            return convert_text(tds, convert, split)
        else:
            return intify_text(tds, split)

def field_getter(table, header, split=None, convert=None):
    def func(self):
        t = get_table(self.lxml, table)
        return get_fields(t, header, split, convert)
    return func

def column_getter(table, fields):
    def func(self):
        columns = []
        for field in fields:
            method = '_'.join((table, field))
            method = pluralize(method)
            columns.append(getattr(self, method)())
        columns = zip_and_dict(columns, fields)
        return columns
    return func

class SignalData(object):
    def __init__(self, html):
        self.soup = load_data(html)
        #self.soup = load_data(html, "lxml")
        self.lxml = lxhtml.fromstring(str(self.soup).lower())

    def center(self):
        return self.soup.body.center

    def downstream_table(self):
        return self.center.table.tbody

    tables = {
        'down': {
            'header': 'downstream',
            'rows': [
                ('channel', 'channel'),
                ('freq', 'frequency', ' '),
                ('snr', 'signal to noise', ' '),
                ('power', 'power level', ' '),
            ],
        },
        'up': {
            'header': 'upstream',
            'rows': [
                ('channel', 'channel'),
                ('freq', 'frequency', ' '),
                ('service_id', 'service id'),
                ('rate', 'symbol rate', ' ', Decimal),
                ('power', 'power level', ' '),
                ('status', 'ranging status', None, str),
            ],
        },
        'stats': {
            'header': 'signal stats (codewords)',
            'rows': [
                ('channel', 'channel id'),
                ('unerrored', 'total unerrored'),
                ('correctable', 'total correctable'),
                ('uncorrectable','total uncorrectable'),
            ],
        }
    }


cls = SignalData
for table, info in cls.tables.items():
    table_header = info['header']
    setattr(cls, '{}_table'.format(table), table_getter(table_header))

    rows = info.get('rows', [])
    for row in rows:
        name, row_header, sep, convert = (row + (None, None))[:4]
        if convert is not None:
            print 'convert', convert
        full_name = '_'.join((table, name))
        full_plural = pluralize(full_name)
        row_name = '{}_row'.format(full_name)
        setattr(cls, '{}_row'.format(full_name),
                row_getter(table_header, row_header))
        setattr(cls, full_plural,
                field_getter(table_header, row_header, sep, convert))

    setattr(cls, '{}_by_column'.format(table),
        column_getter(table, [r[0] for r in rows]))

def load_data(source, parser=None):
    with open(source) as content:
        return BeautifulSoup(content.read(), parser)

def test(data):
    print "Test: {}".format(data)
    info = (
        ('down', ('channels', 'freqs', 'snrs', 'powers')),
        ('up',
            ('channels', 'service_ids', 'rates', 'powers', 'statuses')),
    )

    for section, subs in info:
        print "{}:".format(section)
        for sub in subs:
            method = '_'.join((section, sub))
            vals = getattr(data, method)()
            print "\t{}: {}".format(sub, map(str, vals))
    pprint({
        'down': data.down_by_column(),
        'up': data.up_by_column(),
        'stats': data.stats_by_column(),
    })

def config(data):
    print "graph_title Moto Surfboard Signal/Power"
    print "graph_order down_snr up_power"
    print "graph_vlabel dB / dBmV"
    #print "graph_category network"
    for i, v in enumerate(data.down_snrs()):
        id = i + 1
        print "down_snr{}.label Downstream {} SnR".format(id, id)
        #print "down_snr{}.value {}".format(id, v)
        #print "down_freqs{}.value {}".format(id, v)
    for i, v in enumerate(data.up_powers()):
        id = i + 1
        print "up_power{}.label Upstream {} Power".format(id, id)
        #print "up_power{}.value {}".format(id, v)

def main(data):
    for i, v in enumerate(data.down_snrs()):
        id = i + 1
        print "down_snr{}.value {}".format(id, v)
        #print "down_freqs{}.value {}".format(id, v)
    for i, v in enumerate(data.up_powers()):
        id = i + 1
        print "up_power{}.value {}".format(id, v)

if __name__ == '__main__':
    args = parser.parse_args()
    if args.html in ('test', 'config'):
        # Need to shift...
        mode = args.html
        html = none
    else:
        mode = args.mode
        html = args.html

    data = SignalData(html)

    if mode == 'test':
        test(data)
    elif mode == 'config':
        config(data)
    else:
        main(data)
