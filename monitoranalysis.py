from monitor import utc_to_tz
from dateutil import tz
import krakenex
import pymongo
import networkx as nx
import pandas
import numpy as np
import tqdm

def get_prices(asset_pairs, ticker):
    prices = {}
    for asset_key, asset in asset_pairs.iteritems():
        asset_name = str(asset_key.split('.')[0])
        base = str(asset['base'])
        quote = str(asset['quote'])
        assert asset_name == base + quote, '%s != %s + %s' % (asset_name, base, quote)
        assert asset_name in ticker, '`%s` not in ticker.' % asset_name
        last_price, last_volume = map(float, ticker[asset_name]['c'])
        assert last_price > 0
        assert (base, quote) not in ticker
        assert (quote, base) not in ticker
        prices[base, quote] = last_price
        prices[quote, base] = last_price
    return prices


k = krakenex.API()
k.load_key('lost.key')
asset_pairs = k.query_public("AssetPairs")['result']

# Find cycles.
exchange_graph = nx.DiGraph()
fees = {}
for asset_key, asset in asset_pairs.iteritems():
    asset_name = str(asset_key.split('.')[0])
    base = str(asset['base'])
    quote = str(asset['quote'])
    assert asset_name == base + quote, '%s != %s + %s' % (asset_name, base, quote)
    fee = 1-asset['fees'][0][1]/100.
    fees[base, quote] = fee
    fees[quote, base] = fee
    exchange_graph.add_edge(base, quote)
    exchange_graph.add_edge(quote, base)


cycles = map(tuple, nx.simple_cycles(exchange_graph))
edges = {cycle: tuple(zip(cycle[:-1], cycle[1:]) + [(cycle[-1], cycle[0])]) for cycle in cycles}

mongodb_address = None
client = pymongo.MongoClient(mongodb_address)
db = client['kraken']
collection = db['tickers']
cursor = collection.find()

rows = []
for doc in tqdm.tqdm(cursor, total=cursor.count()):
    timestamp = utc_to_tz(doc['timestamp'], tz.gettz('PST'))
    prices = get_prices(asset_pairs, doc['ticker'])
    for cycle in cycles:
        rates = [fees[e]*prices[e] for e in edges[cycle]]
        rate = np.product(rates)
        rows.append(dict(timestamp=timestamp, cycle=cycle, rate=rate))

df = pandas.DataFrame(rows)





