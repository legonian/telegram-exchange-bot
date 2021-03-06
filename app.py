import logging
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import decimal

from api import ExchangeRatesAPI
from cache import Cache


logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

api = ExchangeRatesAPI()
cache = Cache()

class App:
    def _parse_latest(self, args):
        if len(args) == 1:
            return args[0]
        else:
            return None
    
    def _parse_exchange(self, args):
        if len(args) == 3:
            amount, cur_from = api.parse_money(args[0])
            return amount, cur_from, args[2]
        elif len(args) == 4:
            if args[2].lower() == 'to':
                return args[0], args[1], args[3]
        
        return None, None, None

    def _parse_history(self, args):
        if len(args) == 4:
            currencies = args[0].split('/')
            if len(currencies) == 2 and args[2].isdigit():
                [cur_from, cur_to] = currencies
                days = int(args[2])

                return cur_from, cur_to, days
        
        return None, None, None

    def start(self, update, context):
        update.message.reply_text(
            'Use /list to get list of latest exchange rates')

    def latest(self, update, context):
        """Get list of all available exchange rates."""
        chat_id = update.message.chat_id
        usage = 'Usage: /list\nor\n/list <valid currency>'
        try:
            base = self._parse_latest(context.args)

            # Check cache and request new data is cache empty or expired
            cached_rates = cache.rates(base)
            if cached_rates is None:
                rates = api.latest(base=base)['rates']
                if rates is None:
                    update.message.reply_text(usage)
                    return
                cache.save_rates(rates, base)
            else:
                rates = cached_rates
            
            res = f'List of all available rates for {base}:\n'
            for currency in rates:
                res += f'{currency}: {rates[currency]}\n'
            res += f'\nSourse:\n{api.BASE_URL}/latest?base={base}'

            update.message.reply_text(res)

        except (IndexError, ValueError):
            update.message.reply_text(usage)

    def exchange(self, update, context):
        """Get list of all available exchange rates."""
        chat_id = update.message.chat_id
        usage = 'Usage:\n/exchange <number> <currency> to <currency>\nor\n'
        usage += '/exchange <number with symbol> to <currency>\n\n'
        usage += 'Example:\n/exchange 10 EUR to USD\nor\n/exchange 10$ to EUR'
        try:
            amount, cur_from, cur_to = self._parse_exchange(context.args)
            if any(arg is None for arg in [amount, cur_from, cur_to]):
                update.message.reply_text(usage)
                return
            
            resp = api.exchange(amount, cur_from, cur_to)
            if resp is None:
                update.message.reply_text(usage)
                return
            
            update.message.reply_text(resp)

        except (IndexError, ValueError):
            update.message.reply_text(usage)

    def history(self, update, context):
        """Get list of all available exchange rates."""
        chat_id = update.message.chat_id
        usage = 'Usage: /history <currency>/<currency> for <number> days\n\n'
        usage += 'Example:\n/history USD/EUR for 7 days'
        try:
            cur_from, cur_to, days = self._parse_history(context.args)
            if any(arg is None for arg in [cur_from, cur_to, days]):
                update.message.reply_text(usage)
                return

            graph = api.plot_history(cur_from, cur_to, days)
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
