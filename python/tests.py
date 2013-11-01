from decimal import Decimal
from unittest import TestCase
from surfboard import SignalData, strip_lower
from xml.etree import ElementTree as ET

__all__ = (
    'SignalDataTestCase', 'SignalDataTestCaseTwo',
    'SDOneDownOnlyTestCase',
)

def pluralize(word):
    """HORRIBLE WAY TO PLURALIZE A WORD!!!"""
    if word.endswith('s'):
        suffix = 'es'
    else:
        suffix = 's'
    return ''.join((word, suffix))

def ts_lower(elem):
    return ET.tostring(elem).lower()

def table_tester(name, headers=None):
    def func(self):
        table = getattr(self.signal_data, '{}_table'.format(name))()
        self.assertIsNotNone(table)
        self.assertEqual('table', table.tag)
        header_text = ts_lower(table.xpath('./tbody/tr')[0])
        for header in headers or []:
            self.assertTrue(header in header_text)
    return func

def row_tester(name, header):
    def func(self):
        row = getattr(self.signal_data, '{}_row'.format(name))()
        self.assertIsNotNone(row)
        self.assertEqual(strip_lower(header),
                         strip_lower(row.find('td').text))
    return func

def val_tester(name):
    def func(self):
        vals = getattr(self.signal_data, name)()
        self.assertIsNotNone(vals)
        self.assertEquals(getattr(self, name), vals)
    return func

def column_tester(table, fields):
    def func(self):
        column_method = '{}_by_column'.format(table)
        columns = getattr(self.signal_data, column_method)()
        self.assertIsNotNone(columns)

        for i, column in enumerate(columns):
            for key, val in column.items():
                val_name = '_'.join((table, key))
                val_name = pluralize(val_name)
                vals = getattr(self, val_name)
                #print 'val, val[{}]'.format(i), val, vals[i]
                #self.assertEquals(vals[i], val)

        columns = []
        for field in fields:
            method = '_'.join((table, field)) +'s'
            columns.append(getattr(self, method))

        columns = zip(*columns)
        columns = map(lambda c: dict(zip(fields, c)), columns)
        self.assertEquals(columns,
            getattr(self.signal_data, column_method)())

    return func

class SignalDataTestCase(TestCase):
    source_dir = ('..', 'testdata', )
    #source_file = 'cmSignalData.htm.1'
    source_file = 'working.htm'

    down_channels = [144, 141, 142, 143]
    down_freqs = [699000000, 681000000, 687000000, 693000000]
    down_snrs = [34, 35, 35, 34]
    down_powers = [-11, -9, -9, -10]

    up_channels = [2, 1, 3]
    up_freqs = [29000000, 36000000, 23000000]
    up_service_ids = [49, 49, 49]
    up_rates = [Decimal('5.120'), Decimal('5.120'), Decimal('2.560')]
    up_powers = [51, 51, 51]
    up_statuses = ['continue', 'aborted', 'aborted']

    stats_channels = [144, 141, 142, 143]
    stats_unerroreds = [1454013, 813636, 813638, 813641]
    stats_correctables = [27, 47, 13, 10]
    stats_uncorrectables = [1354, 664, 698, 701]

    @classmethod
    def setUpClass(cls):
        super(SignalDataTestCase, cls).setUpClass()

        cls._source_parts = cls.source_dir + (cls.source_file, )
        cls._source_path = '/'.join(cls._source_parts)
        cls._signal_data = SignalData(cls._source_path)

    def setUp(self):
        super(SignalDataTestCase, self).setUp()
        self.signal_data = self.__class__._signal_data

    def test_signal_data(self):
        self.assertIsNotNone(self.signal_data)

    tables = {
        'down': {
            'headers': ['downstream', 'bonding channel'],
            'rows': [
                ('channel', 'Channel ID'),
                ('freq', 'Frequency'),
                ('snr', 'Signal to Noise Ratio'),
                ('power', 'Power Level'),
            ],
        },
        'up': {
            'headers': ['upstream', 'bonding channel'],
            'rows': [
                ('channel', 'Channel ID'),
                ('freq', 'Frequency'),
                ('service_id', 'Ranging Service ID'),
                ('rate', 'Symbol Rate'),
                ('power', 'Power Level'),
                ('status', 'Ranging Status'),
            ],
        },
        'stats': {
            'headers': ['signal stats (codewords)', 'bonding channel'],
            'rows': [
                ('channel', 'Channel ID'),
                ('unerrored', 'Total Unerrored Codewords'),
                ('correctable', 'Total Correctable Codewords'),
                ('uncorrectable','Total Uncorrectable Codewords'),
            ],
        },
    }

cls = SignalDataTestCase
for table, info in SignalDataTestCase.tables.items():
    setattr(cls, 'test_{}_table'.format(table),
        table_tester(table, info.get('headers')))

    rows = info.get('rows', [])
    for name, header in rows:
        full_name = '_'.join((table, name))
        full_plural = pluralize(full_name)
        setattr(cls, 'test_{}_row'.format(full_name),
            row_tester(full_name, header))
        setattr(cls, 'test_{}'.format(full_plural),
            val_tester(full_plural))

    fields = [name for name, _ in rows]
    if table == 'down':
        setattr(cls, 'test_{}_columns'.format(table),
            column_tester(table, fields))

# Delete, or var will be found in module and added to testcases
del cls


class SignalDataTestCaseTwo(SignalDataTestCase):
    source_file = 'working-2.htm'

    up_service_ids = [49, 49, 49]
    up_statuses = ['continue', 'aborted', 'aborted']
    stats_unerroreds = [828766, 828769, 828771, 828773]
    stats_correctables = [17, 16, 21, 15]
    stats_uncorrectables = [641, 642, 637, 643]


class SDOneDownOnlyTestCase(SignalDataTestCase):
    source_dir = ('..', 'testdata', )
    source_file = 'one_down_only.htm'

    down_channels = [144]
    down_freqs = [699000000]
    down_snrs = [34]
    down_powers = [-11]

    up_channels = []
    up_freqs = []
    up_service_ids = []
    up_rates = []
    up_powers = []
    up_statuses = []

    stats_channels = [144]
    stats_unerroreds = [183209]
    stats_correctables = [11]
    stats_uncorrectables = [658]
