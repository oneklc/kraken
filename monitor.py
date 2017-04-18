import krakenex
from datetime import datetime
import pymongo
from datetime import tzinfo
from dateutil import tz
import time
import itertools


def utc_to_tz(utc, tzone):
    return utc.replace(tzinfo=tz.gettz('UTC')).astimezone(tzone)


def monitor(kraken_api, asset_pairs, collection, period=10):
    key_string = ','.join(asset_pairs)
    for step in itertools.count():
        print 'Collecting ticker...'
        ticker = kraken_api.query_public("Ticker", {'pair': key_string})['result']
        now = datetime.utcnow()
        print 'Collected %d-th ticker at time `%s`.' % (step, str(utc_to_tz(now, tz.gettz('PST'))))
        print 'Inserting ticker in mongo.'
        collection.insert_one(dict(
            timestamp=now,
            ticker=ticker
        ))
        print '...done!'
        print 'Waiting for %d seconds...' % period
        time.sleep(period)

if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter()

    k = krakenex.API()
    k.load_key('lost.key')

    mongodb_address = None
    client = pymongo.MongoClient(mongodb_address)
    db = client['kraken']
    collection = db['tickers']

    asset_pairs = k.query_public("AssetPairs")['result']

    # Monitor
    monitor(k, asset_pairs, collection)

    # cursor = collection.find()
    # for doc in cursor:
    #     timestamp_utc = doc['timestamp']
    #     timestamp_utc = timestamp_utc.replace(tzinfo=tz.gettz('UTC'))
    #     timestamp = timestamp_utc.astimezone(tz.gettz('PST'))
    #     print timestamp
    #     pp.pprint(doc['ticker'])