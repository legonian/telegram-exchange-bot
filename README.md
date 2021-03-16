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

The Bot is hosted by PythonAnywhere though it can be silent due to limitation 
of free account of PythonAnywhere. You can try access bot in telegram by link 
https://t.me/simple_exchange_test_bot.

<img alt="Example" src="https://raw.githubusercontent.com/legonian/telegram-exchange-bot/main/example.png">

## Installation

To run the bot yourself it's recommended to use Python 3.8 version (but also 
tested with Python 3.7.3 on ARM and it works). Bot requre 
``EXCHANGE_TELEGRAM_BOT`` environment variable to be set to your unique 
telegram bot token. To download, install python dependancies, and run bot type 
following commands:
```
$ git clone https://github.com/legonian/telegram-exchange-bot.git
$ cd telegram-exchange-bot
$ pip3 install --user -r requirements.txt
$ python3 app.py
```
