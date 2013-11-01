#!/usr/bin/env python

from bs4 import BeautifulSoup
from decimal import Decimal
from functools import partial
from xml.etree import ElementTree as ET
from lxml import html as lxhtml
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('mode', nargs='?')
parser.add_argument('html')

def pluralize(word):
    """HORRIBLE WAY TO PLURALIZE A WORD!!!"""
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

    DOWN = 'downstream'
    down_table = table_getter(DOWN)

    DOWN_CHANNEL = 'channel'
    down_channel_row = row_getter(DOWN, DOWN_CHANNEL)
    down_channels = field_getter(DOWN, DOWN_CHANNEL)

    DOWN_FREQ = 'frequency'
    down_freq_row = row_getter(DOWN, DOWN_FREQ)
    down_freqs = field_getter(DOWN, DOWN_FREQ, ' ')

    DOWN_SNR = 'signal to noise'
    down_snr_row = row_getter(DOWN, DOWN_SNR)
    down_snrs = field_getter(DOWN, DOWN_SNR, ' ')

    DOWN_POWER = 'power level'
    down_power_row = row_getter(DOWN, DOWN_POWER)
    down_powers = field_getter(DOWN, DOWN_POWER, ' ')

    down_by_column = column_getter('down',
            ('channel', 'freq', 'snr', 'power'))

    UP = 'upstream'
    up_table = table_getter(UP)

    UP_CHANNEL = 'channel'
    up_channel_row = row_getter(UP, UP_CHANNEL)
    up_channels = field_getter(UP, UP_CHANNEL)

    UP_FREQ = 'frequency'
    up_freq_row = row_getter(UP, UP_FREQ)
    up_freqs = field_getter(UP, UP_FREQ, ' ')

    UP_SERVICE_ID = 'service id'
    up_service_id_row = row_getter(UP, UP_SERVICE_ID)
    up_service_ids = field_getter(UP, UP_SERVICE_ID)

    UP_RATE = 'symbol rate'
    up_rate_row = row_getter(UP, UP_RATE)
    up_rates = field_getter(UP, UP_RATE, ' ', Decimal)

    UP_POWER = 'power level'
    up_power_row = row_getter(UP, UP_POWER)
    up_powers = field_getter(UP, UP_POWER, ' ')

    UP_STATUS = 'ranging status'
    up_status_row = row_getter(UP, UP_STATUS)
    up_statuses = field_getter(UP, UP_STATUS, None, str)

    up_by_column = column_getter('up',
            ('channel', 'freq', 'service_id', 'rate', 'power', 'status'))

    STATS = 'signal stats (codewords)'
    stats_table = table_getter(STATS)

    STATS_CHANNEL = 'channel id'
    stats_channel_row = row_getter(STATS, STATS_CHANNEL)
    stats_channels = field_getter(STATS, STATS_CHANNEL)

    STATS_UNERRORED = 'total unerrored'
    stats_unerrored_row = row_getter(STATS, STATS_UNERRORED)
    stats_unerroreds = field_getter(STATS, STATS_UNERRORED)

    STATS_CORRECTABLE = 'total correctable'
    stats_correctable_row = row_getter(STATS, STATS_CORRECTABLE)
    stats_correctables = field_getter(STATS, STATS_CORRECTABLE)

    STATS_UNCORRECTABLE = 'total uncorrectable'
    stats_uncorrectable_row = row_getter(STATS, STATS_UNCORRECTABLE)
    stats_uncorrectables = field_getter(STATS, STATS_UNCORRECTABLE)

    stats_by_column = column_getter('stats',
            ('channel', 'unerrored', 'correctable', 'uncorrectable'))


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
    print "down_by: {}".format(data.down_by_column())

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
