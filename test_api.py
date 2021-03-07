import unittest
from datetime import datetime
import decimal

from api import ExchangeRatesAPI


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.api = ExchangeRatesAPI()

    def test_init(self):
        self.assertEqual(self.api.BASE_URL, 'https://api.exchangeratesapi.io')
        self.assertGreater(len(self.api.currencies), 0)
        self.assertIn('USD', self.api.currencies)
        self.assertEqual(self.api.base, 'USD')

        app1 = ExchangeRatesAPI(base='EUR')
        self.assertEqual(app1.base, 'EUR')

    def test_request(self):
        resp = self.api._request('latest', 'base=USD')
        self.assertIsInstance(resp, dict)
        self.assertNotIn('error', resp)

        resp = self.api._request('latest', 'base=XXX')
        self.assertIsInstance(resp, dict)
        self.assertIn('error', resp)
    
    def test_base_validation(self):
        self.assertEqual(self.api._validate_base(None), self.api.base)
        self.assertEqual(self.api._validate_base('EUR'), 'EUR')
        self.assertIsNone(self.api._validate_base('XXX'))
        self.assertIsNone(self.api._validate_base(420))

    def test_targets_validation(self):
        target = 'EUR'
        targets = ['EUR', 'CAD']

        one_target = self.api._validate_targets(target=target)
        self.assertIsInstance(one_target, str)
        self.assertNotEqual(one_target, '')

        multi_targets = self.api._validate_targets(targets=targets)
        self.assertIsInstance(one_target, str)
        self.assertNotEqual(one_target, '')
        
        self.assertIsNone(self.api._validate_targets())
    
    def test_datetime_to_str(self):
        date1 = datetime(2020, 1, 30)
        self.assertEqual(self.api._datetime_to_valid_str(date1), '2020-01-30')

    def test_timestamps_validation(self):
        date1 = datetime(2020, 1, 30)
        date2 = datetime(2021, 1, 30)
        self.assertEqual(
            self.api._validate_timestamps(date1, date2),
            ('2020-01-30', '2021-01-30'))

        self.assertIsNone(self.api._validate_timestamps(None, None)[0])
        self.assertIsNone(self.api._validate_timestamps(None, None)[1])

    def test_latest(self):
        # Based on base currency
        latest1 = self.api.latest()
        self.assertIsInstance(latest1, dict)
        self.assertNotIn('error', latest1)

        # Based on custom base currency
        latest2 = self.api.latest('EUR')
        self.assertIsInstance(latest2, dict)
        self.assertNotIn('error', latest2)

        # None existing custom base currency
        latest3 = self.api.latest('XXX')
        self.assertIsInstance(latest3, dict)
        self.assertIn('error', latest3)

    def test_history(self):
        date1 = datetime(2020, 1, 30)
        date2 = datetime(2021, 1, 30)

        # Not include target or targets
        history1 = self.api.history(date1, date2)
        self.assertIsInstance(history1, dict)
        self.assertIn('error', history1)

        # Normal parameters
        history2 = self.api.history(date1, date2, target='EUR')
        self.assertIsInstance(history2, dict)
        self.assertNotIn('error', history2)
        self.assertNotEqual(history2['rates'], {})

        # Wrong time range
        history3 = self.api.history(date2, date1, target='EUR')
        self.assertIsInstance(history3, dict)
        self.assertIn('error', history3)

    def test_exchange(self):
        base = 'USD'
        target = 'EUR'
        money = '10'
        rate = self.api.latest(base=base)['rates'][target]
        expect = decimal.Decimal(money) * rate
        expect = str(expect) + ' ' + target

        self.assertEqual(self.api.exchange('10', base, target), expect)

        self.assertIsNone(self.api.exchange('10', 'XXX', target))
        self.assertIsNone(self.api.exchange('10', base, 'XXX'))
        self.assertIsNone(self.api.exchange('A', base, target))

if __name__ == '__main__':
    unittest.main()
