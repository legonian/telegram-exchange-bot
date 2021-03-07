# Exchange Telegram Bot

Exchange Bot is Telegram bot written in Python. App using python-telegram-bot 
Bot API framework and fetching data from api.exchangeratesapi.io.

## Features

This bot using following tools/features:
+ Getting list of rates
+ Caching results
+ Converting currency
+ Plot graph of exchange rates for custom amount of days
+ Testing of api class

## Demo

Bot hosted by PythonAnywhere or Raspberry Pi and can be accessed in telegram by 
``@simple_exchange_test_bot`` name or by link 
https://t.me/simple_exchange_test_bot.

<img alt="Example" src="https://raw.githubusercontent.com/legonian/telegram-exchange-bot/main/example.png">

## Installation

To run this bot app better to use Python 3.8 (also tested with Python 3.7.3 on 
ARM). App requre ``EXCHANGE_TELEGRAM_BOT`` environment variable to be set to 
your unique telegram bot token. To download, install python dependancies and run
type following commands:
```
$ git clone https://github.com/legonian/telegram-exchange-bot.git
$ cd telegram-exchange-bot
$ pip3 install --user -r requirements.txt
$ python3 app.py
```