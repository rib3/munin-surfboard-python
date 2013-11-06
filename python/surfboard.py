#!/usr/bin/env python

from bs4 import BeautifulSoup
from decimal import Decimal
from functools import partial
from xml.etree import ElementTree as ET
from lxml import html as lxhtml
from pprint import pprint, pformat
from urllib import urlopen
import argparse
import sys

DEFAULT_URL = 'http://192.168.100.1/cmSignalData.htm'

parser = argparse.ArgumentParser()
parser.add_argument('mode', nargs='?')
parser.add_argument('html', nargs='?')

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
    """Convert and return a list of element's .text value with func()."""
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
    """Wrapper for convert_text with int() as conversion function."""
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

def load_data(source, parser=None):
    if hasattr(source, 'startswith') and source.startswith('http'):
        content = urlopen(source)
    else:
        content = open(source)
    return BeautifulSoup(content.read(), parser)

class SignalData(object):
    def __init__(self, html):
        self.soup = load_data(html)
        #self.soup = load_data(html, "lxml")
        self.lxml = lxhtml.fromstring(str(self.soup).lower())

    # This is used to setup class methods in setup_signal_data()
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
        },
    }


def setup_signal_data():
    """
    Setup SignalData methods by going through it's tables dict.

    This is inside of a function to avoid cluttering module namespace.
    """
    cls = SignalData
    for table, info in cls.tables.items():
        table_header = info['header']
        setattr(cls, '{}_table'.format(table), table_getter(table_header))

        rows = info.get('rows', [])
        for row in rows:
            name, row_header, sep, convert = (row + (None, None))[:4]
            args = table_header, row_header, sep, convert
            full_name = '_'.join((table, name))
            setattr(cls, '{}_row'.format(full_name), row_getter(*args[:2]))
            setattr(cls, pluralize(full_name), field_getter(*args))

        setattr(cls, '{}_by_column'.format(table),
            column_getter(table, [r[0] for r in rows]))

setup_signal_data()

def test(data):
    for section, subs in SignalData.tables.items():
        print "{}:".format(section)
        rows = [row[0] for row in subs.get('rows', [])]
        for sub in rows:
            method = pluralize('_'.join((section, sub)))
            vals = getattr(data, method)()
            print "\t{}: {}".format(sub, map(str, vals))

    pprint({
        'down': data.down_by_column(),
        'up': data.up_by_column(),
        'stats': data.stats_by_column(),
    })

graph = {
    'down': {
        'snr': {
            'label': 'Downstream {id} SnR',
            'vlabel': 'dB',
        },
    },
    'up': {
        'power': {
            'label': 'Upstream {id} Power',
            'vlabel': 'dBmV',
        },
    },
}

def config(data):
    print "graph_title Moto Surfboard Signal/Power"
    print "graph_order down_snr up_power"
    print "graph_vlabel dB / dBmV"
    print "graph_category network"

    for table, table_points in graph.items():
        columns = getattr(data, '{}_by_column'.format(table))()
        for i, column in enumerate(columns):
            id = i + 1
            for point, p_info in table_points.items():
                for field, val in p_info.items():
                    fmt = {
                        'table': table,
                        'point': point,
                        'id': id,
                        'field': field,
                    }
                    fmt['source'] = "{table}_{point}{id}".format(**fmt)
                    fmt['val'] = val.format(**fmt)
                    print "{source}.{field} {val}".format(**fmt)

def main(data):
    for table, keys in graph.items():
        columns = getattr(data, '{}_by_column'.format(table))()
        for i, info in enumerate(columns):
            id = i + 1
            for key in keys:
                source = "{}_{}{}".format(table, key, id)
                val = info.get(key)
                if val is None:
                    val = 'U' # Munin code for unavailable
                print "{}.value {}".format(source, val)

if __name__ == '__main__':
    args = parser.parse_args()
    if args.html in ('test', 'config'):
        # Need to shift...
        mode = args.html
        html = None
    else:
        mode = args.mode
        html = args.html

    if html is None:
        html = DEFAULT_URL

    data = SignalData(html)

    if mode == 'test':
        test(data)
    elif mode == 'config':
        config(data)
    else:
        main(data)
