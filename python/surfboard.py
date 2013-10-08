#!/usr/bin/env python

from bs4 import BeautifulSoup
from functools import partial
from xml.etree import ElementTree as ET
from lxml import html as lxhtml

def strip_lower(text):
    """strip() and lower() text."""
    if text is not None:
        try:
            text = text.strip().lower()
        except:
            return None
    return text

def intify_text(elems, split=None):
    """Take a list of elements and return their .text value as ints."""
    nums = []
    for elem in elems:
        num = elem.text
        if num is not None:
            num = strip_lower(num)
            if split is not None:
                num = num.split(split, 1)[0]
            num = int(num)
        nums.append(num)
    return nums

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

def row_getter(table_getter, header):
    def func(self):
        table = getattr(self, table_getter)()
        return get_row(table, header)
    return func

def get_fields(table, header, split=None):
    """Get a fields for a row specified by their header text."""
    row = get_row(table, header)
    if row is not None:
        tds = row.xpath('./td')[1:]
        return intify_text(tds, split)

def field_getter(table_getter, header, split=None):
    def func(self):
        table = getattr(self, table_getter)()
        return get_fields(table, header, split)
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

    downstream_table = table_getter('downstream')

    downstream_channel_row = row_getter('downstream_table', 'channel')
    downstream_channels = field_getter('downstream_table', 'channel')

    downstream_freq_row = row_getter('downstream_table', 'frequency')
    downstream_freqs = field_getter('downstream_table', 'frequency', ' ')

    downstream_snr_row = row_getter('downstream_table', 'signal to noise')
    downstream_snrs = field_getter('downstream_table', 'signal to noise', ' ')

    downstream_power_row = row_getter('downstream_table', 'power level')
    downstream_powers = field_getter('downstream_table', 'power level', ' ')

def load_data(source, parser=None):
    with open(source) as content:
        return BeautifulSoup(content.read(), parser)
