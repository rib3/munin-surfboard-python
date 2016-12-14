import string
from collections import OrderedDict
from parse import *

__all__ = (
    'graphs',
    'GraphPoint', 'config_graph', 'setup_graph_points',
)

# Used to label channels
GRAPH_IDS = string.ascii_uppercase

graphs = [
    {
        'graph': 'snr_power',
        'title': "Moto Surfboard Signal/Power",
        'vlabel': 'dB (down) / dBmV (up)',
        'category': 'network',
        'points': [
            ('down.snr', OrderedDict([
                ('label', 'Down {id} SnR'),
                ('vlabel', 'dB'),
            ])),
            ('up.power', OrderedDict([
                ('label', 'Up {id} Power'),
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
                ('label', 'Down {id} Power'),
                ('vlabel', 'dBmV'),
            ])),
        ],
    },
    {
        'graph': 'channels',
        'title': "Moto Surfboard Channels",
        'vlabel': 'channel',
        'category': 'network',
        'points': [
            ('down.channel', OrderedDict([
                ('label', 'Down {id} Channel'),
            ])),
            ('up.channel', OrderedDict([
                ('label', 'Up {id} Channel'),
            ])),
        ],
    },
    {
        'graph': 'frequencies',
        'title': "Moto Surfboard Frequencies",
        'vlabel': 'Hz',
        'category': 'network',
        'points': [
            ('down.freq', OrderedDict([
                ('label', 'Down {id} Frequency'),
                ('vlabel', 'Hz'),
            ])),
            ('up.freq', OrderedDict([
                ('label', 'Up {id} Frequency'),
                ('vlabel', 'Hz'),
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
