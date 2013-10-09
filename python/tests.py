from unittest import TestCase
from surfboard import SignalData, strip_lower
from xml.etree import ElementTree as ET

__all__ = ('SignalDataTestCase', )

def ts_lower(elem):
    return ET.tostring(elem).lower()

class SignalDataTestCase(TestCase):
    source_dir = ('..', 'testdata', )
    #source_file = 'cmSignalData.htm.1'
    source_file = 'working.htm'

    down_channels = [144, 141, 142, 143]
    down_freqs = [699000000, 681000000, 687000000, 693000000]
    down_snrs = [34, 35, 35, 34]
    down_powers = [-11, -9, -9, -10]

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
