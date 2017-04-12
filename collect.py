"""

pip install krakenex
pip install pymongo
"""

import krakenex
from pymongo import MongoClient, ASCENDING
from datetime import datetime
from time import sleep


k = krakenex.API()
k.load_key('lost.key')

# k.query_private('AddOrder', {'pair': 'XXBTZEUR',
#                              'type': 'buy',
#                              'ordertype': 'limit',
#                              'price': '1',
#                              'volume': '1',
#                              'close[pair]': 'XXBTZEUR',
#                              'close[type]': 'sell',
#                              'close[ordertype]': 'limit',
#                              'close[price]': '9001',
#                              'close[volume]': '1'})

assets = k.query_public("Assets")
# <asset_name> = asset name
#     altname = alternate name
#     aclass = asset class
#     decimals = scaling decimal places for record keeping
#     display_decimals = scaling decimal places for output display


assetPairs = k.query_public("AssetPairs")
# <pair_name> = pair name
#     altname = alternate pair name
#     aclass_base = asset class of base component
#     base = asset id of base component
#     aclass_quote = asset class of quote component
#     quote = asset id of quote component
#     lot = volume lot size
#     pair_decimals = scaling decimal places for pair
#     lot_decimals = scaling decimal places for volume
#     lot_multiplier = amount to multiply lot volume by to get currency volume
#     leverage_buy = array of leverage amounts available when buying
#     leverage_sell = array of leverage amounts available when selling
#     fees = fee schedule array in [volume, percent fee] tuples
#     fees_maker = maker fee schedule array in [volume, percent fee] tuples (if on maker/taker)
#     fee_volume_currency = volume discount currency
#     margin_call = margin call level
#     margin_stop = stop-out/liquidation margin level

#convert asset pairs into comma delimted string to send to ticker api call
key_string = ','.join(assetPairs['result'].keys())
#ticker = k.query_public("Ticker",{'pair': key_string})

# <pair_name> = pair name
#     a = ask array(<price>, <whole lot volume>, <lot volume>),
#     b = bid array(<price>, <whole lot volume>, <lot volume>),
#     c = last trade closed array(<price>, <lot volume>),
#     v = volume array(<today>, <last 24 hours>),
#     p = volume weighted average price array(<today>, <last 24 hours>),
#     t = number of trades array(<today>, <last 24 hours>),
#     l = low array(<today>, <last 24 hours>),
#     h = high array(<today>, <last 24 hours>),
#     o = today's opening price


# Get trade volume
# URL: https://api.kraken.com/0/private/TradeVolume
#
# Input:
#
# pair = comma delimited list of asset pairs to get fee info on (optional)
# fee-info = whether or not to include fee info in results (optional)
# Result: associative array
#

# currency = volume currency
# volume = current discount volume
# fees = array of asset pairs and fee tier info (if requested)
#     fee = current fee in percent
#     minfee = minimum fee for pair (if not fixed fee)
#     maxfee = maximum fee for pair (if not fixed fee)
#     nextfee = next tier's fee for pair (if not fixed fee.  nil if at lowest fee tier)
#     nextvolume = volume level of next tier (if not fixed fee.  nil if at lowest fee tier)
#     tiervolume = volume level of current tier (if not fixed fee.  nil if at lowest fee tier)
# fees_maker = array of asset pairs and maker fee tier info (if requested) for any pairs on maker/taker schedule
#     fee = current fee in percent
#     minfee = minimum fee for pair (if not fixed fee)
#     maxfee = maximum fee for pair (if not fixed fee)
#     nextfee = next tier's fee for pair (if not fixed fee.  nil if at lowest fee tier)
#     nextvolume = volume level of next tier (if not fixed fee.  nil if at lowest fee tier)
#     tiervolume = volume level of current tier (if not fixed fee.  nil if at lowest fee tier)


client = MongoClient('192.168.1.83', 27017)
db = client.kraken
tickers = db.tickers
tickers.create_index([('timestamp', ASCENDING)], unique=True)

#for i in range(10):
i=0
while True:
    i+=1
    try:
        ticker_data = k.query_public("Ticker", {'pair': key_string})['result']
        # trade_volume = k.query_private("TradeVolume", {'pair': key_string, 'fee-info': True})['result']
    except IOError:
        print(IOError)
        continue

    now = datetime.utcnow()
    print( 'Collected {}th ticker at time {} '.format( i,str(now)))
    print('Inserting ticker in mongo.')
    print(ticker_data)
    ticker_id =  tickers.insert_one({
        "timestamp": now,
        "ticker": ticker_data,
        #"trade_volume": trade_volume
    })


    print("inserted: {}".format(ticker_id))
    sleep(5)

