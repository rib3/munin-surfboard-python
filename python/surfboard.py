#!/usr/bin/env python

from bs4 import BeautifulSoup
from functools import partial
from xml.etree import ElementTree as ET
from lxml import html as lxhtml
import sys

def strip_lower(text):
    """strip() and lower() text."""
    if text is not None:
        try:
            text = text.strip().lower()
        except:
            return None
    return text

def convert_text(elems, func, split=None):
    """Take a list of elements and return their .text value as ints."""
    nums = []
    for elem in elems:
        num = elem.text
        if num is not None:
            num = strip_lower(num)
            if split is not None:
                num = num.split(split, 1)[0]
            num = func(num)
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

class SignalData(object):
    def __init__(self, html):
        self.soup = load_data(html)
        #self.soup = load_data(html, "lxml")
        self.lxml = lxhtml.fromstring(str(self.soup).lower())

    def center(self):
        return self.soup.body.center

    def downstream_table(self):
        return self.center.table.tbody

    DOWNSTREAM = 'downstream'

    downstream_table = table_getter(DOWNSTREAM)

    downstream_channel_row = row_getter(DOWNSTREAM, 'channel')
    downstream_channels = field_getter(DOWNSTREAM, 'channel')

    downstream_freq_row = row_getter(DOWNSTREAM, 'frequency')
    downstream_freqs = field_getter(DOWNSTREAM, 'frequency', ' ')

    downstream_snr_row = row_getter(DOWNSTREAM, 'signal to noise')
    downstream_snrs = field_getter(DOWNSTREAM, 'signal to noise', ' ')

    downstream_power_row = row_getter(DOWNSTREAM, 'power level')
    downstream_powers = field_getter(DOWNSTREAM, 'power level', ' ')


def load_data(source, parser=None):
    with open(source) as content:
        return BeautifulSoup(content.read(), parser)

def main():
    html = sys.argv[1]
    data = SignalData(html)

    info = (
        ('downstream', ('channel', 'freq', 'snr', 'power')),
        #('upstream', ('channel', 'freqs', 'snr', 'power')),
    )

    for section, subs in info:
        print "{}:".format(section)
        for sub in subs:
            method = '{}_{}s'.format(section, sub)
            print "\t{}: {}".format(sub, getattr(data, method)())

if __name__ == '__main__':
    main()
