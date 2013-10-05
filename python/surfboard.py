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
        return [td.text.strip() for td in tds]

    def downstream_freqs_row(self):
        try:
            return self.downstream_rows()[2]
        except IndexError:
            pass

    def downstream_freqs(self):
        tds = self.downstream_freqs_row().find_all('td')[1:]
        return [td.text.strip() for td in tds]


def load_data(source, parser=None):
    with open(source) as content:
        return BeautifulSoup(content.read(), parser)
