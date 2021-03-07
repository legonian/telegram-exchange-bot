import threading
import io

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Plotter:
    def __init__(self, max_time=10):
        self.lock = threading.Lock()
    
    def _plot_by_dates(self, x, y, title):
        fig, ax = plt.subplots()
        ax.plot(x, y, 'k')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.grid()
        ax.set(title=title)
        fig.autofmt_xdate()

        return plt

    def plot_rates(self, x, y, rates_label):
        """
        Args:
            param1 (obj): self
            param2 (str): x axis values
            param3 (str): y axis values
            param4 (int): title of graph

        Returns:
            (bytes): image
        """
        with self.lock:
            plot = self._plot_by_dates(x, y, rates_label)

            with io.BytesIO() as buf:
                plot.savefig(buf)
                plot.close()

                buf.seek(0)
                return buf.getvalue()

