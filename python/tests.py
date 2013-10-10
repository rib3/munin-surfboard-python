from decimal import Decimal
from unittest import TestCase
from surfboard import SignalData, strip_lower
from xml.etree import ElementTree as ET

__all__ = ('SignalDataTestCase', )

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

    ## Down
    test_down_table = table_tester('down',
            ['downstream', 'bonding channel'])

    test_down_channel_row = row_tester('down_channel', 'Channel Id')
    test_down_channels = val_tester('down_channels')

    test_down_freq_row = row_tester('down_freq', 'Frequency')
    test_down_freqs = val_tester('down_freqs')

    test_down_snr_row = row_tester('down_snr', 'Signal to Noise Ratio')
    test_down_snrs = val_tester('down_snrs')

    test_down_power_row = row_tester('down_power', 'Power Level')
    test_down_powers = val_tester('down_powers')

    ## Up
    test_up_table = table_tester('up', ['upstream', 'bonding channel'])

    test_up_channel_row = row_tester('up_channel', 'Channel ID')
    test_up_channels = val_tester('up_channels')

    test_up_freq_row = row_tester('up_freq', 'Frequency')
    test_up_freqs = val_tester('up_freqs')

    test_up_service_id_row = row_tester(
            'up_service_id', 'Ranging Service ID')
    test_up_service_ids = val_tester('up_service_ids')

    test_up_rate_row = row_tester('up_rate', 'Symbol Rate')
    test_up_rates = val_tester('up_rates')

    test_up_status_row = row_tester('up_status', 'Ranging Status')
    test_up_statuses = val_tester('up_statuses')

    ## Stats
    tables = {
        'stats': {
            'headers': ['signal stats (codewords)', 'bonding channel'],
            'rows': [
                ('channel', 'Channel Id'),
                ('unerrored', 'Total Unerrored Codewords'),
                ('correctable', 'Total Correctable Codewords'),
                ('uncorrectable','Total Uncorrectable Codewords'),
            ],
        },
    }

for table, info in SignalDataTestCase.tables.items():
    setattr(SignalDataTestCase, 'test_{}_table'.format(table),
        table_tester(table, info.get('headers')))
    for name, header in info.get('rows', []):
        full_name = '_'.join((table, name))
        full_plural = pluralize(full_name)
        setattr(SignalDataTestCase, 'test_{}_row'.format(full_name),
            row_tester(full_name, header))
        setattr(SignalDataTestCase, 'test_{}'.format(full_plural),
            val_tester(full_plural))
