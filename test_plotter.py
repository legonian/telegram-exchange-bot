import unittest
from datetime import datetime, timedelta

from plotter import Plotter


plotter = Plotter()

class TestPlot(unittest.TestCase):
    rates = {
        '2021-02-26': {'EUR': 0.8250144378},
        '2021-03-01': {'EUR': 0.8296689621},
        '2021-03-02': {'EUR': 0.8313934154},
        '2021-03-03': {'EUR': 0.8300132802},
        '2021-03-04': {'EUR': 0.8309788931},
        '2021-03-05': {'EUR': 0.8376612498},
    }
    def test_bug_on_deacreasing_data(self):
        date, rate = [], []
        for r in self.rates:
            date.append(datetime.strptime(r, '%Y-%m-%d'))
            rate.append(self.rates[r]['EUR'])
        
        date1, rate1 = date[:4], rate[:4]
        img1 = plotter.plot_rates(date1, rate1, '')

        img2 = plotter.plot_rates(date, rate, '')

        date3, rate3 = date[:4], rate[:4]
        img3 = plotter.plot_rates(date3, rate3, '')

        self.assertGreater(len(img2), len(img1))
        self.assertGreater(len(img2), len(img3))
        

if __name__ == '__main__':
    unittest.main()
