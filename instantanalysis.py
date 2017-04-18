import krakenex
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas
import seaborn
import datetime

pandas.set_option('display.width', 1000)

import pprint
pp = pprint.PrettyPrinter()

import itertools
for index in itertools.count():

    now = datetime.datetime.now()

    k = krakenex.API()
    k.load_key('lost.key')

    asset_pairs = k.query_public("AssetPairs")['result']

    key_string = ','.join(asset_pairs)
    ticker = k.query_public("Ticker",{'pair': key_string})['result']


    # pp.pprint(asset_pairs)
    # pp.pprint(ticker)


    exchange_graph = nx.DiGraph()

    for asset_key, asset in asset_pairs.iteritems():
        if asset_key.endswith('.d') or 'DASH' in asset_key:
            continue
        asset_name = str(asset_key.split('.')[0])
        base = str(asset['base'])
        quote = str(asset['quote'])
        assert asset_name == base + quote, '%s != %s + %s' % (asset_name, base, quote)
        assert asset_name in ticker, '`%s` not in ticker.' % asset_name
        last_price, last_volume = map(float, ticker[asset_name]['c'])
        fees = asset['fees']
        fee = 1-fees[0][1]/100.
        assert last_price > 0

        exchange_graph.add_edge(base, quote, rate=last_price*fee)
        exchange_graph.add_edge(quote, base, rate=1. / last_price*fee)

    # pp.pprint(exchange_graph.edges())
    # pp.pprint(exchange_graph.nodes())

    # plt.figure(figsize=(12,12))
    # # pos = nx.spring_layout(exchange_graph)
    # pos = nx.circular_layout(exchange_graph)
    # nx.draw_networkx(
    #     exchange_graph.to_undirected(),
    #     pos,
    #     node_color='orange',
    #     with_labels=True,
    #     font_size=8,
    #     node_size=1000,
    # )
    # edge_labels = {e: '%.2e' % exchange_graph.get_edge_data(*e)['last_price'] for e in exchange_graph.edges()}
    # nx.draw_networkx_edge_labels(
    #     exchange_graph,
    #     pos,
    #     edge_labels=edge_labels,
    #     font_size=8,
    #     bbox=dict(alpha=1, ec='w', fc='w', boxstyle='round', pad=0.1),
    # )
    # plt.show()


    cycle = ('XETH', 'XXBT', 'ZGBP')
    edges = tuple(zip(cycle[:-1], cycle[1:]) + [(cycle[-1], cycle[0])])
    rates = [exchange_graph.get_edge_data(*e)['rate'] for e in edges]
    rate = np.product(rates)

    print now, cycle, edges, rates, rate
    import time
    time.sleep(5)

# cycle_df = pandas.DataFrame({'cycle': map(tuple, nx.simple_cycles(exchange_graph))})
#
# def get_edges(row):
#     cycle = row['cycle']
#     return tuple(zip(cycle[:-1], cycle[1:]) + [(cycle[-1], cycle[0])])
# cycle_df['edges'] = cycle_df.apply(get_edges, axis=1)
#
# def get_rates(row):
#     edges = row['edges']
#     return [exchange_graph.get_edge_data(*e)['rate'] for e in edges]
# cycle_df['rates'] = cycle_df.apply(get_rates, axis=1)
#
# def get_rate(row):
#     rates = row['rates']
#     return np.product(rates)
# cycle_df['rate'] = cycle_df.apply(get_rate, axis=1)
#
# cycle_df['length'] = cycle_df.apply(lambda row: len(row['cycle']), axis=1)
#
# # print df.ix[df[df['length']==3]['rate'].idxmax()]
#
# records = []
# for index, row in cycle_df.iterrows():
#     for currency in row['cycle']:
#         records.append((currency, row['length'], row['rate']))
# df = pandas.DataFrame.from_records(records, columns=['currency', 'length', 'rate'])
#
# fg = seaborn.FacetGrid(
#     data=df,
#     col='currency',
#     col_order=sorted(df['currency'].unique()),
#     col_wrap=5,
#     sharex=True,
#     sharey=True,
#     margin_titles=True
# )
#
# def facet(data, color):
#     plt.scatter(data['length'], data['rate'], color=color, s=10)
#
# for (i, j, k), data in fg.facet_data():
#     if k == 0:
#         ax = fg.facet_axis(i, j)
#         ax.axhline(y=1.0, linestyle='--', color='r', linewidth=1.)
#
# fg.map_dataframe(facet)
# fg.set_xlabels('cycle length')
# fg.set_ylabels('rate')
# fg.set(ylim=(1., 1.1))
# fg.set(xlim=(2, 8))
# plt.suptitle(str(now))
# plt.subplots_adjust(left=0.065, bottom=0.07, right=0.95, top=0.92, wspace=0.1, hspace=0.12)
# plt.show()


