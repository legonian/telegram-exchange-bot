import threading
import io

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Plotter:
    def __init__(self, max_time=10):
        self.lock = threading.Lock()
    
    def _plot_by_dates(self, x, y, x_label, y_label):
        plt.plot(x, y, 'k')
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.grid(axis='y')
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        fig = plt.gcf()
        fig.autofmt_xdate()

        return plt

    def plot_rates(self, x, y, rates_label):
        with self.lock:
            plot = self._plot_by_dates(x, y, '', rates_label)

            with io.BytesIO() as buf:
                buf.truncate(0)
                plot.savefig(buf)
                plot.close()
                buf.seek(0)
                return buf.getvalue()

