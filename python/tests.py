from decimal import Decimal
from unittest import TestCase
from surfboard import SignalData, strip_lower
from xml.etree import ElementTree as ET

__all__ = ('SignalDataTestCase', )

def ts_lower(elem):
    return ET.tostring(elem).lower()

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

    def test_down_table(self):
        table = self.signal_data.down_table()
        self.assertIsNotNone(table)
        self.assertEqual('table', table.tag)
        test_text = ts_lower(table.xpath('./tbody/tr')[0])
        #\nDownstream \nBonding Channel Value
        self.assertTrue('downstream' in test_text)
        self.assertTrue('bonding channel' in test_text)

    def test_down_channel_row(self):
        row = self.signal_data.down_channel_row()
        self.assertIsNotNone(row)
        self.assertEqual('Channel ID'.lower(),
                         strip_lower(row.find('td').text))

    def test_down_channels(self):
        channels = self.signal_data.down_channels()
        self.assertIsNotNone(channels)
        self.assertEquals(self.down_channels, channels)

    def test_down_freq_row(self):
        row = self.signal_data.down_freq_row()
        self.assertIsNotNone(row)
        self.assertEqual('Frequency'.lower(),
                         strip_lower(row.find('td').text))

    def test_down_freqs(self):
        freqs = self.signal_data.down_freqs()
        self.assertIsNotNone(freqs)
        self.assertEquals(self.down_freqs, freqs)

    def test_down_snr_row(self):
        row = self.signal_data.down_snr_row()
        self.assertIsNotNone(row)
        self.assertEqual(strip_lower('Signal to Noise Ratio'),
                         strip_lower(row.find('td').text))

    def test_down_snrs(self):
        snrs = self.signal_data.down_snrs()
        self.assertIsNotNone(snrs)
        self.assertEquals(self.down_snrs, snrs)

    def test_down_power_row(self):
        row = self.signal_data.down_power_row()
        self.assertIsNotNone(row)
        self.assertEqual('Power Level'.lower(),
                         strip_lower(row.find('td').text))

    def test_down_powers(self):
        powers = self.signal_data.down_powers()
        self.assertIsNotNone(powers)
        self.assertEquals(self.down_powers, powers)

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

    #########
    # STATS #
    #########
    def test_stats_table(self):
        table = self.signal_data.stats_table()
        self.assertIsNotNone(table)
        self.assertEqual('table', table.tag)
        test_text = ts_lower(table.xpath('./tbody/tr')[0])
        # check for table (header) text
        self.assertTrue('signal stats (codewords)' in test_text)
        self.assertTrue('bonding channel' in test_text)

    test_stats_channel_row = row_tester('stats_channel', 'Channel ID')
    test_stats_channels = val_tester('stats_channels')

    test_stats_unerrored_row = row_tester(
            'stats_unerrored', 'Total Unerrored Codewords')
    test_stats_unerroreds = val_tester('stats_unerroreds')

    test_stats_correctable_row = row_tester(
            'stats_correctable', 'Total Correctable Codewords')
    test_stats_correctables = val_tester('stats_correctables')

    test_stats_uncorrectable_row = row_tester(
            'stats_uncorrectable', 'Total Uncorrectable Codewords')
    test_stats_uncorrectables = val_tester('stats_uncorrectables')
