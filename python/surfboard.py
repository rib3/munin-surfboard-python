#!/usr/bin/env python

from bs4 import BeautifulSoup
from functools import partial
from xml.etree import ElementTree as ET

def strip_lower(text):
    if text is not None:
        text = text.strip().lower()
    return text

def has_text(elem, text):
    return strip_lower(elem.text) == strip_lower(text)

def intify_text(elems, split=None):
    nums = [strip_lower(elem.text) for elem in elems]
    return map(int, nums)

class SignalData(object):
    def __init__(self, html):
        self.soup = load_data(html)
        #self.soup = load_data(html, "lxml")

    def center(self):
        return self.soup.body.center

    def downstream_table(self):
        return self.center.table.tbody

    def downstream_table(self):
        header = self.soup.find(partial(has_text, text='Downstream'))
        return header.parent.parent.parent

    def downstream_rows(self):
        return self.downstream_table().find_all('tr')

    def downstream_channel_row(self):
        try:
            return self.downstream_rows()[1]
        except IndexError:
            pass

    def downstream_channels(self):
        tds = self.downstream_channel_row().find_all('td')[1:]
        return intify_text(tds)

    def downstream_freq_row(self):
        try:
            return self.downstream_rows()[2]
        except IndexError:
            pass

    def downstream_freqs(self):
        tds = self.downstream_freq_row().find_all('td')[1:]
        freqs = [strip_lower(td.text.split(' ')[0]) for td in tds]
        return map(int, freqs)


def load_data(source, parser=None):
    with open(source) as content:
        return BeautifulSoup(content.read(), parser)
