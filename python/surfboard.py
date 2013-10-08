#!/usr/bin/env python

from bs4 import BeautifulSoup
from functools import partial
from xml.etree import ElementTree as ET
from lxml import html as lxhtml

def strip_lower(text):
    if text is not None:
        text = text.strip().lower()
    return text

def has_text(elem, text):
    return strip_lower(elem.text) == strip_lower(text)

def intify_text(elems, split=None):
    nums = []
    for elem in elems:
        num = strip_lower(elem.text)
        if split is not None:
            num = num.split(split, 1)[0]
        nums.append(int(num))
    return nums

class SignalData(object):
    def __init__(self, html):
        self.soup = load_data(html)
        #self.soup = load_data(html, "lxml")
        self.lxml = lxhtml.fromstring(str(self.soup).lower())

    def center(self):
        return self.soup.body.center

    def downstream_table(self):
        return self.center.table.tbody

    def downstream_table(self):
        downstreams = self.lxml.xpath('//table'
            '//*[contains(text(), "downstream")]')
        if downstreams:
            tables = downstreams[0].xpath('./ancestor::table')
            if tables:
                # Return "closest" table
                return tables[-1]

    def downstream_rows(self):
        return self.downstream_table().xpath('.//tr')

    def downstream_channel_row(self):
        table = self.downstream_table()
        if table is not None:
            tds = table.xpath('.//td[contains(text(), "channel")]')
            if tds:
                return tds[0].getparent()

    def downstream_channels(self):
        row = self.downstream_channel_row()
        if row is not None:
            tds = row.xpath('.//td')[1:]
            return intify_text(tds)

    def downstream_freq_row(self):
        table = self.downstream_table()
        if table is not None:
            tds = table.xpath('.//td[contains(text(), "frequency")]')
            if tds:
                return tds[0].getparent()

    def downstream_freqs(self):
        row = self.downstream_freq_row()
        if row is not None:
            tds = row.xpath('.//td')[1:]
            return intify_text(tds, ' ')

def load_data(source, parser=None):
    with open(source) as content:
        return BeautifulSoup(content.read(), parser)
