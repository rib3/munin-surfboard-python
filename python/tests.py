from unittest import TestCase
from surfboard import SignalData, strip_lower

__all__ = ('SignalDataTestCase', )

class SignalDataTestCase(TestCase):
    source_dir = ('..', 'testdata', )
    #source_file = 'cmSignalData.htm.1'
    source_file = 'working.htm'

    channels = [144, 141, 142, 143]

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

    def test_downstream_table(self):
        table = self.signal_data.downstream_table()
        self.assertIsNotNone(table)
        self.assertEqual('table', table.name)
        test_text = table.tbody.tr.text.lower()
        #\nDownstream \nBonding Channel Value
        self.assertTrue('downstream' in test_text)
        self.assertTrue('bonding channel' in test_text)

    def test_downstream_channel_row(self):
        row = self.signal_data.downstream_channel_row()
        self.assertIsNotNone(row)
        self.assertEqual('Channel ID'.lower(),
                         strip_lower(row.find('td').text))

    def test_downstream_channels(self):
        channels = self.signal_data.downstream_channels()
        self.assertIsNotNone(channels)
        self.assertEquals(self.channels, channels)
