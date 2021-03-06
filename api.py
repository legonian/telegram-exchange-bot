import requests
import json
import decimal
from datetime import datetime, timedelta

from plotter import Plotter
from cache import Cache


class ExchangeRatesAPI:
    BASE_URL = 'https://api.exchangeratesapi.io'
    currencies = None

    def __init__(self, base='USD'):
        """Set base and supported currencies list.
        
        Args:
            param1 (obj): self
            param2 (str): currency code
        """
        self.cache = Cache()
        self.plotter = Plotter()

        self.base = base

        rates = self.latest()['rates']
        self.currencies = [cur for cur in rates]

    def _datetime_to_valid_str(self, date1):
        """
        Args:
            param1 (datetime.datetime): time to convert
        
        Returns:
            (str): string of valid date representation
        """
        return date1.strftime('%Y-%m-%d')

    def _request(self, path, query=''):
        """
        Args:
            param1 (obj): self
            param2 (str): URL path
            param3 (str): URL query parameters

        Returns:
            (obj): response from API
        """
        url = '{}/{}?{}'.format(self.BASE_URL, path, query)
        resp = requests.get(url)
        return json.loads(resp.text)

    def _validate_base(self, base):
        """
        Args:
            param1 (obj): self
            param2 (str): base currency

        Returns:
            (str): validated base currency
        """
        if base is None:
            return self.base
        elif not isinstance(base, str):
            return None
        elif base.upper() not in self.currencies:
            return None

        return base.upper()
    
    def _validate_timestamps(self, start, end):
        """
        Args:
            param1 (obj): self
            param2 (datetime.datetime): start timestamps
            param3 (datetime.datetime): end timestamps

        Returns:
            start (str): validated start timestamps
            end (str): validated end timestamps
        """
        if isinstance(start, datetime) and isinstance(end, datetime):
            start = self._datetime_to_valid_str(start)
            end = self._datetime_to_valid_str(end)
        if not (isinstance(start, str) and isinstance(end, str)):
            return None, None
        return start, end

    def _validate_targets(self, target=None, targets=[]):
        """
        Args:
            param1 (obj): self
            param2 (str): target currency
            param3 (list): list of multiple targets

        Returns:
            (str): validated target or targets
        """
        if (target is None) and isinstance(targets, list):
            if len(targets) == 0:
                return None
            targets = ','.join([self._validate_targets(t)for t in targets])
            
            if any(t is None for t in targets):
                return None
            targets = ','.join(targets)
        else:
            if ((not isinstance(target, str)) and
                    (target.upper() not in self.currencies)):
                return None
            targets = target.upper()
        return targets

    def _validate_exchange(self, amount, cur_from, cur_to):
        if not isinstance(cur_from, str) or not isinstance(cur_to, str):
            return None, None, None
        elif cur_from.upper() not in self.currencies:
            return None, None, None
        elif cur_to.upper() not in self.currencies:
            return None, None, None
        
        try:
            amount = decimal.Decimal(amount)
            return amount, cur_from.upper(), cur_to.upper()
        except:
            return None, None, None

    def latest(self, base=None):
        """
        Args:
            param1 (obj): self
            param2 (str): base currency

        Returns:
            (dict): response
        """
        api_path='latest'

        base = self._validate_base(base)
        if base is None:
            return {'error': 'Invalid base currency'}
        
        query = 'base={}'.format(base)

        cached_data = self.cache.rates(base)
        if cached_data is None:
            data = self._request(api_path, query)
            self.cache.save_rates(data, base)
        else:
            data = cached_data

        if 'error' not in data:
          for rate in data['rates']:
            data['rates'][rate] = round(
                decimal.Decimal(data['rates'][rate]), 2)
        return data
    
    def history(self, start, end, base=None, target=None, targets=[]):
        """
        Args:
            param1 (obj): self
            param2 (datetime.datetime): start timestamps
            param3 (datetime.datetime): end timestamps
            param4 (str): base currency
            param5 (str): target currency
            param6 (list): list of multiple targets

        Returns:
            (dict): response
        """
        api_path = 'history'

        base =        self._validate_base(base)
        start, end =  self._validate_timestamps(start, end)
        targets =     self._validate_targets(target, targets)

        if any(arg is None for arg in [base, start, end, targets]):
            return {'error': 'Invalid parameters'}

        query = 'start_at={}&end_at={}&base={}&symbols={}'
        query = query.format(start, end, base, targets)

        res = self._request(api_path, query)
        if 'error' in res:
            return res
        
        if ('rates' in res) and (len(res['rates']) == 0):
            return {'error': 'No exchange rate is available this period.'}
        
        return res

    def plot_history(self, cur_from, cur_to, days):
        """
        Args:
            param1 (obj): self
            param2 (str): base currency 
            param3 (str): target currency
            param4 (int): number of days

        Returns:
            (bytes): image
        """

        cur_from = self._validate_targets(cur_from)
        cur_to = self._validate_targets(cur_to)
        
        if any(arg is None for arg in [cur_from, cur_to]):
            return None

        if not isinstance(days, int) or days < 1:
            return None
        
        end = datetime.now()
        start = end - timedelta(days=days)

        history_data = self.history(start, end, base=cur_from, target=cur_to)
        if 'error' in history_data:
            print(history_data['error'])
            return None

        rates = history_data['rates']
        if len(rates) < 2:
            return None

        rates = dict(sorted(rates.items()))
        
        date, rate = [], []
        for r in rates:
            date.append(datetime.strptime(r, '%Y-%m-%d'))
            rate.append(rates[r][cur_to])
        
        y_label = '{} to {} rates'.format(cur_from, cur_to)
        return self.plotter.plot_rates(date, rate, y_label)

    def exchange(self, amount, cur_from, cur_to):
        """
        Args:
            param1 (obj): self
            param2 (str): amount of money to convert
            param3 (str): from what currency you convert
            param4 (str): for what currency you convert

        Returns:
            (str): result of converting
        """
        amount, cur_from, cur_to = self._validate_exchange(
            amount, cur_from, cur_to)
        if any(arg is None for arg in [amount, cur_from, cur_to]):
            return None

        resp = self.latest(base=cur_from)
        if 'error' in resp:
            return None
        
        rates = resp['rates']
        rate = decimal.Decimal(rates[cur_to])

        return f'{round(amount * rate, 2)} {cur_to}'
