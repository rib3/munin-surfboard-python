import argparse
from functools import partial
from pprint import pprint
from parse import *
from graph import *

__all__ = (
    'DEFAULT_URL', 'handle_args', 'config', 'values',
    # Re-expored from parse (for tests)
    'pluralize', 'strip_lower', 'zip_and_dict', 'SignalData',
    # Re-expored from config (for tests)
    'GraphPoint', 'config_graph',
)

DEFAULT_URL = 'http://192.168.100.1/cmSignalData.htm'

parser = argparse.ArgumentParser()
parser.add_argument('mode', nargs='?')
parser.add_argument('html', nargs='?', default=DEFAULT_URL)

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
    args = parser.parse_args(args)
    munge_args(args)
    return args

def munge_args(args):
    MODES = 'test', 'config'
    if args.mode is not None:
        if args.mode not in MODES:
            # Maybe it's the html argument
            args.html = args.mode
            args.mode = None

def main():
    args = handle_args()
    data = SignalData(args.html)
    if args.mode == 'test':
        test(data)
    elif args.mode == 'config':
        print config(data)
    else:
        print values(data)
