import logging
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from api import ExchangeRatesAPI


logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class App:
    CURRENCY_MAP = {
        "GBP": "£",
        "CNY": "¥",
        "EUR": "€",
        "JPY": "¥",
        "PLN": "zł",
        "RUB": "₽",
        "USD": "$",
    }

    def __init__(self):
        self.api = ExchangeRatesAPI()
    
    def _parse_latest(self, args):
        if len(args) == 1:
            return args[0]
        else:
            return None
    
    def _parse_money(self, str1):
        """
        Args:
            param1 (obj): self
            param2 (str): string to parse

        Returns:
            (str): parsed number
            (str): parsed currency
        """
        for cur in self.CURRENCY_MAP:
            if self.CURRENCY_MAP[cur] in str1:
                parsed = str1.replace(self.CURRENCY_MAP[cur], '')
                return parsed, cur
        return None, None

    def _parse_exchange(self, args):
        if len(args) == 3 and args[1].lower() == 'to':
            money_str = args[0]
            for cur in self.CURRENCY_MAP:
                if self.CURRENCY_MAP[cur] in money_str:
                    parsed = money_str.replace(self.CURRENCY_MAP[cur], '')
                    return parsed, cur, args[2]
                    
        elif len(args) == 4 and args[2].lower() == 'to':
            if args[2].lower() == 'to':
                return args[0], args[1], args[3]
        
        return None, None, None

    def _parse_history(self, args):
        if len(args) == 4 and args[1].lower() == 'for':
            currencies = args[0].split('/')
            if len(currencies) == 2 and args[2].isdigit() and args[3].lower() == 'days':
                [cur_from, cur_to] = currencies
                days = int(args[2])

                return cur_from, cur_to, days
        
        return None, None, None

    def start(self, update, context):
        usage = ('Use /list to get list of latest exchange rates '
                 'or specify custom currency with /list <valid currency>\n\n'
                 'Also you can use /history and /exchange '
                 'command and specifying arguments, click on command to know '
                 'how to use them')
        update.message.reply_text(usage)

    def latest(self, update, context):
        """Get list of all available exchange rates."""
        chat_id = update.message.chat_id
        usage = ('Usage: /list\nor\n/list <valid currency>'
                 'Example:\n/list\nor\n/list  EUR')
        try:
            base = self._parse_latest(context.args)

            rates = self.api.latest(base=base)
            if (rates is None) or ('error' in rates) or (rates['rates'] is None):
                update.message.reply_text(usage)
                return
            
            rates = rates['rates']
            
            res = f'List of all available rates for {base}:\n'
            for currency in rates:
                res += f'{currency}: {rates[currency]}\n'
            if base is None:
                res += (f'\nSourse:\n{self.api.BASE_URL}/latest?base={self.api.base}\n\n'
                        f'Default currency is {self.api.base}, to use custom one:\n'
                        '/list <valid currency code> (like /list EUR)')
            else:
                res += f'\nSourse:\n{self.api.BASE_URL}/latest?base={base}'
            update.message.reply_text(res)

        except (IndexError, ValueError):
            update.message.reply_text(usage)

    def exchange(self, update, context):
        """Get list of all available exchange rates."""
        chat_id = update.message.chat_id
        usage = ('Usage:\n/exchange <number> <currency> to <currency>\nor\n'
                 '/exchange <number with symbol> to <currency>\n\n'
                 'Example:\n/exchange 10 EUR to USD\nor\n/exchange 10$ to EUR')
        try:
            amount, cur_from, cur_to = self._parse_exchange(context.args)
            if any(arg is None for arg in [amount, cur_from, cur_to]):
                update.message.reply_text(usage)
                return
            
            resp = self.api.exchange(amount, cur_from, cur_to)
            if resp is None:
                update.message.reply_text(usage)
                return
            
            update.message.reply_text(resp)

        except (IndexError, ValueError):
            update.message.reply_text(usage)

    def history(self, update, context):
        """Get list of all available exchange rates."""
        chat_id = update.message.chat_id
        usage = ('Usage: /history <currency>/<currency> for <number> days'
                 '(recommended to use 7 or more days)\n\n'
                 'Example:\n/history USD/EUR for 7 days')
        try:
            cur_from, cur_to, days = self._parse_history(context.args)
            if any(arg is None for arg in [cur_from, cur_to, days]):
                update.message.reply_text(usage)
                return

            graph = self.api.plot_history(cur_from, cur_to, days)
            if graph is None:
                update.message.reply_text(usage)
                return
            update.message.reply_photo(graph)
        except (IndexError, ValueError):
            update.message.reply_text(usage)

def main():
    app = App()
    token = os.environ['EXCHANGE_TELEGRAM_BOT']
    updater = Updater(token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', app.start))
    dispatcher.add_handler(CommandHandler('list', app.latest))
    dispatcher.add_handler(CommandHandler('history', app.history))
    dispatcher.add_handler(CommandHandler('exchange', app.exchange))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
