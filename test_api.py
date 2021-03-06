import unittest
from datetime import datetime

from api import ExchangeRatesAPI


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = ExchangeRatesAPI()

    def test_init(self):
        self.assertEqual(self.app.BASE_URL, 'https://api.exchangeratesapi.io')
        self.assertGreater(len(self.app.currencies), 0)
        self.assertIn('USD', self.app.currencies)
        self.assertEqual(self.app.base, 'USD')

        app1 = ExchangeRatesAPI(base='EUR')
        self.assertEqual(app1.base, 'EUR')

    def test_request(self):
        resp = self.app._request('latest', 'base=USD')
        self.assertIsInstance(resp, dict)
        self.assertNotIn('error', resp)

        resp = self.app._request('latest', 'base=XXX')
        self.assertIsInstance(resp, dict)
        self.assertIn('error', resp)
    
    def test_base_validation(self):
        self.assertEqual(self.app._validate_base(None), self.app.base)
        self.assertEqual(self.app._validate_base('EUR'), 'EUR')
        self.assertIsNone(self.app._validate_base('XXX'))
        self.assertIsNone(self.app._validate_base(420))

    def test_targets_validation(self):
        target = 'EUR'
        targets = ['EUR', 'CAD']

        one_target = self.app._validate_targets(target=target)
        self.assertIsInstance(one_target, str)
        self.assertNotEqual(one_target, '')

        multi_targets = self.app._validate_targets(targets=targets)
        self.assertIsInstance(one_target, str)
        self.assertNotEqual(one_target, '')
        
        self.assertIsNone(self.app._validate_targets())
    
    def test_datetime_to_str(self):
        date1 = datetime(2020, 1, 30)
        self.assertEqual(self.app._datetime_to_valid_str(date1), '2020-01-30')

    def test_timestamps_validation(self):
        date1 = datetime(2020, 1, 30)
        date2 = datetime(2021, 1, 30)
        self.assertEqual(
            self.app._validate_timestamps(date1, date2),
            ('2020-01-30', '2021-01-30'))

        self.assertIsNone(self.app._validate_timestamps(None, None)[0])
        self.assertIsNone(self.app._validate_timestamps(None, None)[1])

    def test_latest(self):
        # Based on base currency
        latest1 = self.app.latest()
        self.assertIsInstance(latest1, dict)
        self.assertNotIn('error', latest1)

        # Based on custom base currency
        latest2 = self.app.latest('EUR')
        self.assertIsInstance(latest2, dict)
        self.assertNotIn('error', latest2)

        # None existing custom base currency
        latest3 = self.app.latest('XXX')
        self.assertIsInstance(latest3, dict)
        self.assertIn('error', latest3)

    def test_history(self):
        date1 = datetime(2020, 1, 30)
        date2 = datetime(2021, 1, 30)

        # Not include target or targets
        history1 = self.app.history(date1, date2)
        self.assertIsInstance(history1, dict)
        self.assertIn('error', history1)

        # Normal parameters
        history2 = self.app.history(date1, date2, target='EUR')
        self.assertIsInstance(history2, dict)
        self.assertNotIn('error', history2)
        self.assertNotEqual(history2['rates'], {})

        # Wrong time range
        history3 = self.app.history(date2, date1, target='EUR')
        self.assertIsInstance(history3, dict)
        self.assertNotIn('error', history3)
        self.assertEqual(history3['rates'], {})


if __name__ == '__main__':
    unittest.main()
