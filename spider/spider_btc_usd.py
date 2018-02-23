#!/usr/bin/python

import os
import sys
import asyncio
import ccxt.async as ccxt
#import cfscrape
sys.path.append("..")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
import util
import bz_conf


symbol = 'BTC/USD'
exchanges = [
    'bitfinex',     # 可空, 门槛 $10000
    'okcoinusd',     # 可空, 
    'bitstamp', 
    'gemini', 
    'kraken',       # 可空, 
    'exmo', 
    'quadrigacx', 
    'gdax', 
    #'poloniex'    # 可空
    #'cex',
    #'wex',
    #'itbit',
    #'bittrex',
    ]



db = util.db_banzhuan(util.symbol_2_string(symbol), bz_conf.db_dir)
list_exchanges = util.init_spider(db, exchanges)


async def get_ticker(exchange):
    while True:
        try:
            s = await util.verify_symbol(exchange, symbol)

            ticker = await exchange.fetch_ticker(s)
            db.add_bid_ask(exchange.id, ticker['timestamp'], ticker['bid'], ticker['ask'])
            print(exchange.id, ticker['timestamp'], ticker['bid'], ticker['ask'])


            '''
            # 可以取到价格和数量，没测过哪个速度快
            order_book = await exchange.fetch_order_book(s, 1)      # 取深度信息，只取1层
            dt = order_book['timestamp']
            bid1 = order_book['bids'][0][0]
            bid1_quantity = order_book['bids'][0][1]
            ask1 = order_book['asks'][0][0]
            ask1_quantity = order_book['asks'][0][1]
            db.add_bid_ask(exchange.id, dt, bid1, ask1)
            print(exchange.id, dt, bid1, ask1)
            '''
            
        except ccxt.RequestTimeout as e:
            print('RequestTimeout=', type(e).__name__, e.args)
        except ccxt.DDoSProtection as e:
            print('DDoSProtection=', type(e).__name__, e.args)
            await asyncio.sleep(exchange.rateLimit / 1000)
        except ccxt.AuthenticationError as e:
            print('AuthenticationError=', type(e).__name__, e.args)
        except ccxt.ExchangeNotAvailable as e:
            print('ExchangeNotAvailable=', type(e).__name__, e.args)
            await asyncio.sleep(exchange.rateLimit / 1000)
        except ccxt.ExchangeError as e:
            print('ExchangeError=', type(e).__name__, e.args)
            await asyncio.sleep(exchange.rateLimit / 1000)
        except ccxt.NetworkError as e:
            print('NetworkError=', type(e).__name__, e.args)





[asyncio.ensure_future(get_ticker(exchange)) for exchange in list_exchanges]
pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))


