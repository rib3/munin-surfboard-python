from bs4 import BeautifulSoup
from collections import OrderedDict
from functools import partial
from pprint import pprint

from parse import *

import argparse
import string

__all__ = (
    'DEFAULT_URL',
    # Re-expored from parse (for tests)
    'pluralize', 'strip_lower', 'zip_and_dict', 'SignalData',

    'GraphPoint', 'config_graph', 'config', 'values',
    'handle_args',
)

DEFAULT_URL = 'http://192.168.100.1/cmSignalData.htm'

# Used to label channels
GRAPH_IDS = string.uppercase

graphs = [
    {
        'graph': 'snr_power',
        'title': "Moto Surfboard Signal/Power",
        'vlabel': 'dB (down) / dBmV (up)',
        'category': 'network',
        'points': [
            ('down.snr', OrderedDict([
                ('label', 'Downstream {id} SnR'),
                ('vlabel', 'dB'),
            ])),
            ('up.power', OrderedDict([
                ('label', 'Upstream {id} Power'),
                ('vlabel', 'dBmV'),
            ])),
        ],
    },
    {
        'graph': 'down_power',
        'title': "Moto Surfboard Downstream Power Level",
        'vlabel': 'dBmV',
        'category': 'network',
        'points': [
            ('down.power', OrderedDict([
                ('label', 'Downstream {id} Power'),
                ('vlabel', 'dBmV'),
            ])),
        ],
    },
    {
        'graph': 'stats',
        'title': "Moto Surfboard Stats",
        'vlabel': 'codewords',
        'category': 'network',
        'points': [
            ('stats.unerrored', OrderedDict([
                ('label', 'Unerrored {id}'),
                ('vlabel', 'unerrored'),
                ('type', 'DERIVE'),
                ('min', '0'),
            ])),
            ('stats.correctable', OrderedDict([
                ('label', 'Correctable Errors {id}'),
                ('vlabel', 'correctable'),
                ('type', 'DERIVE'),
                ('min', '0'),
            ])),
            ('stats.uncorrectable', OrderedDict([
                ('label', 'Uncorrectable Errors {id}'),
                ('vlabel', 'uncorrectable'),
                ('type', 'DERIVE'),
                ('min', '0'),
            ])),
        ],
    },
    {
        'graph': 'errors',
        'title': "Moto Surfboard Errors",
        'vlabel': 'codewords',
        'category': 'network',
        'points': [
            ('stats.correctable', OrderedDict([
                ('label', 'Correctable Errors {id}'),
                ('vlabel', 'correctable'),
                ('type', 'DERIVE'),
                ('min', '0'),
            ])),
            ('stats.uncorrectable', OrderedDict([
                ('label', 'Uncorrectable Errors {id}'),
                ('vlabel', 'uncorrectable'),
                ('type', 'DERIVE'),
                ('min', '0'),
            ])),
        ],
    },
]

parser = argparse.ArgumentParser()
parser.add_argument('mode', nargs='?')
parser.add_argument('html', nargs='?')

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


class GraphPoint(object):
    """GraphPoint object, can be used to generate configs or values"""
    def __init__(self, table, point, id, extra, value=None):
        self.table = table
        self.point = point
        self.id = id
        self.extra = extra
        self._value = value

    def __repr__(self):
        return ('GraphPoint(table={self.table!r}'
                ', point={self.point!r}'
                ', id={self.id!r})').format(self=self)

    @property
    def source(self):
        return "{table}_{point}{id}".format(**self.__dict__)

    def config(self):
        config = []
        for field, val in self.extra:
            val = val.format(**self.__dict__)
            config.append("{}.{} {}".format(self.source, field, val))

        return '\n'.join(config)

    @property
    def value(self):
        if self._value is None:
            return 'U' # Munin code for unavailable
        return self._value

    def value_line(self):
        return "{}.value {}".format(self.source, self.value)


def setup_graph_points(data, graph):
    points = []
    for point, p_info in graph.get('points', []):
        table, p_name = point.split('.')
        columns = getattr(data, '{}_by_column'.format(table))()
        for i, column in enumerate(columns):
            id = GRAPH_IDS[i]
            point = GraphPoint(table, p_name, id, p_info.items(),
                               column.get(p_name))
            points.append(point)
    return points

def config_graph(data, graph):
    config = []
    for key in 'graph', 'title', 'category', 'vlabel':
        val = graph.get(key)
        if val is not None:
            if key == 'graph':
                config.append("multigraph surfboard_{}".format(val))
            else:
                config.append("graph_{} {}".format(key, val))

    p_config, order = [], ['graph_order']
    for point in setup_graph_points(data, graph):
        order.append(point.source)
        p_config.append(point.config())

    config.append(' '.join(order))
    config.append('') # blank line

    config.extend(p_config)
    return '\n'.join(config)

def config(data):
    return '\n\n'.join(map(partial(config_graph, data), graphs))

def values(data):
    values = []
    for graph in graphs:
        if values:
            values.append('') # blank line spacer
        graph_name = graph.get('graph')
        values.append("multigraph surfboard_{}".format(graph_name))
        for point in setup_graph_points(data, graph):
            values.append(point.value_line())
    return '\n'.join(values)

def handle_args(args=None):
    MODES = 'test', 'config'
    args = parser.parse_args(args)

    if not args.mode in MODES:
        # Maybe it's html
        args.html = args.mode
        args.mode = None

    if args.html is None:
        args.html = DEFAULT_URL

    return args

def main():
    args = handle_args()
    data = SignalData(args.html)
    if args.mode == 'test':
        test(data)
    elif args.mode == 'config':
        print config(data)
    else:
        print values(data)
