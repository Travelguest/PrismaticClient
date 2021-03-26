import pandas as pd
import numpy as np
import networkx as nx
import math

import scipy.cluster.hierarchy as sch

PATH_CORR_ALL_YEARS = './data/corr_all_years.pkl'
PATH_TRADE_CAL = './data/trade_cal.ftr'

PATH_STOCK_LIST = './data/stock_list.ftr'
PATH_STOCK_DAILY = './data/stock_daily.pkl'
PATH_STOCK_DAILY_LOG = './data/stock_daily_log.pkl'

PATH_INDUSTRY_LIST = './data/industry_list.ftr'

PATH_CONCEPT_LIST = './data/concept_list.ftr'

PATH_INDEX_INDUSTRY_LIST = './data/index_industry_list.ftr'
PATH_INDEX_DAILY = './data/index_daily.pkl'

PATH_KNOWLEDGE_GRAPH = './data/knowledge_graph.pkl'

PATH_DEFAULT_COMMUNITY = './data/default_community.pkl'

PINUS_WINDOW_SIZE = 250


class Model:
    def __init__(self):
        # All correlations matrix
        self.corr_df = pd.read_pickle(PATH_CORR_ALL_YEARS)
        self.corr_index_df = self.corr_df.drop(columns=[(str(year), '000001.SH') for year in range(2011, 2021)]).iloc[0]
        self.corr_df = self.corr_df.drop(columns=[(str(year), '000001.SH') for year in range(2011, 2021)]).iloc[1:]

        # Stocks related
        self.stock_list = pd.read_feather(PATH_STOCK_LIST)
        self.stock_daily = pd.read_pickle(PATH_STOCK_DAILY)
        self.stock_daily_log = pd.read_pickle(PATH_STOCK_DAILY_LOG)
        self.trade_cal = pd.read_feather(PATH_TRADE_CAL)

        # Industry related
        self.industry_list = pd.read_feather(PATH_INDUSTRY_LIST)

        # Concept related
        self.concept_list = pd.read_feather(PATH_CONCEPT_LIST)

        # Index related
        self.index_industry_list = pd.read_feather(PATH_INDEX_INDUSTRY_LIST)
        self.index_daily = pd.read_pickle(PATH_INDEX_DAILY)

        # Knowledge graph
        # self.knowledge_graph = nx.read_gpickle(PATH_KNOWLEDGE_GRAPH)

        # Default
        self.community_default = pd.read_pickle(PATH_DEFAULT_COMMUNITY)

        # Global variables
        self.features = ['close', 'vol']
        self.query_codes = ['000652', '000538']
        self.query_dates = []
        self.community = None

    """
    Initiation
    """
    # entrance get stock list
    def get_stock_list(self):
        stock_list = self.stock_list[['ts_code', 'name']].merge(
            self.industry_list.query('level == "L1" or level == "L3"')[['ts_code', 'industry_name']]).groupby(
            ['ts_code', 'name']).agg(list).reset_index()
        stock_list['level1'] = stock_list['industry_name'].apply(lambda x: x[0])
        stock_list['level3'] = stock_list['industry_name'].apply(lambda x: x[1])
        return stock_list[['ts_code', 'name', 'level1', 'level3']].to_dict('records')

    # get ten years market index distribution
    def get_corr_dist(self, query_codes):
        self.query_codes = query_codes if query_codes is not None else []
        corr = {str(year): {} for year in range(2011, 2021)}
        for year in range(2011, 2021):
            corr_out = pd.cut(
                self.corr_index_df[str(year)],
                bins=[i / 100 for i in range(-50, 101, 5)],
                precision=2,
                right=True,
                include_lowest=True).value_counts()
            corr[str(year)]['sci'] = [int(corr_out[i / 100]) for i in range(-50, 101, 5)]
            for query_code in self.query_codes:
                corr_out = pd.cut(
                    self.corr_df[str(year)].loc[query_code],
                    bins=[i / 100 for i in range(-50, 101, 5)],
                    precision=2,
                    right=True,
                    include_lowest=True).value_counts()
                corr[str(year)][query_code] = [int(corr_out[i / 100]) for i in range(-50, 101, 5)]
        return corr

    """
    Get dynamic graph data
    """

    # get cluster data for all years
    def get_corr_clusters_all_years(self, left_threshold, right_threshold):
        corr = {str(year): {} for year in range(2011, 2021)}
        for year in range(2011, 2021):
            year = str(year)
            corr[year] = self.get_corr_clusters_one_year(year, left_threshold, right_threshold)
        return corr

    # Get cluster data for one year
    def get_corr_clusters_one_year(self, year, left_threshold, right_threshold):
        print(f'Running cluster analysis for {year}')
        year = str(year)
        corr_matrix = self.get_corr_matrix_filtered(year, left_threshold, right_threshold)
        corr_graph = self.get_corr_graph(corr_matrix, left_threshold, right_threshold)
        corr_betweenness = self.get_betweenness_centrality(corr_graph)
        corr_nodes, corr_components = self.get_connected_components(corr_graph, corr_betweenness)
        return {
            'betweenness': corr_betweenness,
            'nodes': corr_nodes,
            'components': corr_components
        }

    # Get the correlation filtered matrix
    def get_corr_matrix_filtered(self, year, left_threshold, right_threshold):
        corr_filter = pd.eval('|'.join([
            f'{left_threshold} <= self.corr_df["{year}"]["{query_code}"] <= {right_threshold}'
            for query_code in self.query_codes
        ]))
        corr_filter = self.corr_df[str(year)].loc[corr_filter]
        return corr_filter.filter(items=corr_filter.index)

    # Get the correlation filtered graph
    def get_corr_graph(self, corr_df, left_threshold, right_threshold):
        G = nx.Graph()
        corr_df[(left_threshold <= corr_df) & (corr_df <= right_threshold)].apply(
            lambda u: [G.add_edge(u.name, v, w=1.01 - weight) for v, weight in u.items() if
                       not math.isnan(weight) and left_threshold <= weight <= right_threshold and u.name != v]
        )
        G.add_nodes_from(self.query_codes)
        return G

    def get_betweenness_centrality(self, graph):
        return nx.algorithms.centrality.betweenness_centrality(graph, endpoints=True, weight='weight')

    def get_connected_components(self, graph, sort_dict):
        connected_components = sorted(nx.connected_components(graph), key=len, reverse=True)
        component_dict = {node: i for i, components in enumerate(connected_components) for node in list(components)}
        sorted_components = []
        for components in connected_components:
            for node in sorted(list(components), key=lambda x: sort_dict[x], reverse=True):
                sorted_components.append(node)
        return sorted_components, component_dict

    # Get business tag table
    def get_business_tag_table(self, left_threshold, right_threshold):
        all_nodes = pd.eval('|'.join([
            f'{left_threshold} <= self.corr_df.loc["{query_code}"] <= {right_threshold}'
            for query_code in self.query_codes]))
        all_nodes = list(set([code for _, code in all_nodes[all_nodes].index]))

        industry_tags = self.industry_list.merge(
            pd.Series(all_nodes, name='ts_code'))[['industry_name', 'ts_code', 'level']].groupby(
            ['industry_name', 'level']).count().reset_index().set_index('level').sort_values(by='ts_code',
                                                                                             ascending=False)
        concept_tags = self.concept_list.merge(
            pd.Series(all_nodes, name='ts_code'))[['name', 'ts_code']].groupby(
            'name').count().reset_index().sort_values(by='ts_code', ascending=False)
        industry_tags.columns = ['name', 'count']
        concept_tags.columns = ['name', 'count']

        return {
            'L1': industry_tags.loc['L1'].to_dict(orient='records'),
            'L2': industry_tags.loc['L2'].to_dict(orient='records'),
            'L3': industry_tags.loc['L3'].to_dict(orient='records'),
            'concept': concept_tags.to_dict(orient='records')
        }

    '''
    Correlation matrix
    '''
    # entrance
    def list_to_corr_matrix(self,
                            stock_list=None,
                            start_time='2020-01-01',
                            end_time='2020-06-30'):
        if stock_list is None:
            stock_list = ['000538', '000652']
        self.query_dates = [start_time, end_time]
        # filter stock price by timeframe and query_codes
        stock_price = self.stock_daily_log.loc[self.query_dates[0]:self.query_dates[1]]
        stock_price = stock_price.transpose().loc[
            [(feature, stock) for feature in self.features for stock in stock_list]].transpose()

        # find individual correlation with other assets
        selected_corr = []
        for feature in self.features:
            selected_stocks = stock_price[feature].corr()
            selected_corr.append(selected_stocks)
        return pd.concat(selected_corr, axis=1, keys=self.features)

    def two_phase_hierarchical_clustering(self,
                                          corr_df,
                                          first_by='close',
                                          second_by='vol'):
        if corr_df is None or len(corr_df) <= 1:
            return False
        corr_df = corr_df.dropna(axis=0, how='all').dropna(axis=1, how='all')
        dist = sch.distance.pdist(corr_df[first_by].values)
        link = sch.linkage(dist, method='complete')
        index = sch.fcluster(link, dist.max(initial=0) / 2, 'distance')
        columns = corr_df[first_by].columns.tolist()
        columns = [columns[i] for i in np.argsort(index)]
        corr_df_first_hc = corr_df[second_by].reindex(columns, axis=0).reindex(columns, axis=1)

        _, counts = np.unique(index, return_counts=True)
        i, j = 0, 0
        columns = []
        for count in counts:
            j += count
            sub_corr_df = corr_df_first_hc[corr_df_first_hc.columns.values[i:j]].loc[
                corr_df_first_hc.columns.values[i:j]
            ]
            sub_corr_col = sub_corr_df.columns.tolist()
            if j - i > 1:
                dist = sch.distance.pdist(sub_corr_df.values)
                link = sch.linkage(dist, method='complete')
                index = sch.fcluster(link, dist.max(initial=0) / 2, 'distance')
                sub_corr_col = [sub_corr_col[ind] for ind in np.argsort(index)]
            i = j
            columns.extend(sub_corr_col)

        # Combine the matrix
        corr_dfs = [
            (corr_df['close'].reindex(columns, axis=0).reindex(columns, axis=1)),
            (corr_df['vol'].reindex(columns, axis=0).reindex(columns, axis=1))
        ]
        corr_df = corr_dfs[1]
        for idx, col in enumerate(corr_dfs[0].columns):
            corr_df.loc[col][idx:] = corr_dfs[0].loc[col][idx:]

        # Find correlation with index
        index_price = self.index_daily.log['000001.SH'].loc[self.query_dates[0]:self.query_dates[1]]
        stock_price = self.stock_daily_log.loc[self.query_dates[0]:self.query_dates[1]].close[columns]
        index_corr = list(stock_price.corrwith(index_price, drop=True).values)

        return columns, [
            {'row': row, 'col': col, 'val': val if i != j else index_corr[i],
             'type': 'market' if i == j else 'price' if i <= j else 'vol'}
            for i, (row, col_dict) in enumerate(corr_df.round(5).to_dict(orient='index').items())
            for j, (col, val) in enumerate(col_dict.items())
        ]

    def get_stock_return(self,
                         stock_list=None,
                         start_time='2020-01-01',
                         end_time='2020-06-30'):
        if stock_list is None:
            stock_list = ['000538', '000652']
        result = self.stock_daily.loc[start_time:end_time][stock_list]
        return [{'row': stock, 'val': np.exp(result[stock].log.sum())} for stock in stock_list]

    '''
    Pinus view related
    '''
    def find_index_code(self, query_code='000652'):
        industry_code = self.industry_list.query(
            'ts_code == @query_code and level == "L1"').industry_code.to_list()[0]
        return self.index_industry_list.query('industry_code == @industry_code').iloc[0]

    def rolling_corr_market(self,
                            query_code='000652',
                            index_code='000001.SH',
                            start_date='2020-01-01',
                            end_date='2020-06-30'):
        # find appropriate window size
        trade_days = self.trade_cal.query('@start_date <= cal_date <= @end_date')['is_open'].sum()
        window = int(max(1, trade_days / PINUS_WINDOW_SIZE))

        # filter stock price by timeframe
        index_price = self.index_daily.log[[index_code]].loc[start_date:end_date][::window]
        stock_price = self.stock_daily_log.close[query_code].loc[start_date:end_date]
        index_stock_price = index_price.merge(stock_price, left_index=True, right_index=True)
        index_price = index_stock_price[index_stock_price.columns[0]]
        stock_price = index_stock_price[index_stock_price.columns[1]]

        # find individual correlation with market
        pinus = {day: index_price.rolling(day, min_periods=1).corr(stock_price) for day in
                 range(len(index_stock_price), 1, -1)}
        pinus = pd.DataFrame(pinus).round(4).replace([np.inf, -np.inf], np.nan)
        pinus.index = pinus.index.strftime("%Y-%m-%d")
        return pinus.drop(index=pinus.index[0]).transpose()

    def rolling_corr_stock(self,
                           query_code_left='000652',
                           query_code_right='000538',
                           start_date='2020-01-01',
                           end_date='2020-06-30'):
        # find appropriate window size
        trade_days = self.trade_cal.query('@start_date <= cal_date <= @end_date')['is_open'].sum()
        window = int(max(1, trade_days / PINUS_WINDOW_SIZE))

        # filter stock price by timeframe
        stock_price = self.index_daily.log[['000001.SH']].loc[start_date:end_date][::window]
        stock_price_left = self.stock_daily_log.close[query_code_left].loc[start_date:end_date]
        stock_price_right = self.stock_daily_log.close[query_code_right].loc[start_date:end_date]
        stock_price = stock_price.merge(
            stock_price_left, left_index=True, right_index=True
        ).merge(stock_price_right, left_index=True, right_index=True)
        stock_price_left = stock_price[stock_price.columns[1]]
        stock_price_right = stock_price[stock_price.columns[2]]

        # find individual correlation with market
        pinus = {day: stock_price_left.rolling(day, min_periods=1).corr(stock_price_right) for day in
                 range(len(stock_price), 1, -1)}
        pinus = pd.DataFrame(pinus).round(4).replace([np.inf, -np.inf], np.nan)
        pinus.index = pinus.index.strftime("%Y-%m-%d")
        return pinus.drop(index=pinus.index[0]).transpose()

    def query_stock_daily(self,
                          query_codes=None,
                          start_date='2020-02-01',
                          end_date='2020-04-30'):
        if query_codes is None:
            query_codes = ['000538', '000652']
        result = self.stock_daily.loc[start_date:end_date][query_codes]
        response = {'date': list(result.index.astype(str))}
        for query_code in query_codes:
            response[query_code] = result[query_code].to_dict(orient='records')
        return response

    def query_stock_index_daily(self,
                                stock_code='000538',
                                index_type='market',
                                start_date='2020-02-01',
                                end_date='2020-04-30'):
        if index_type == 'market':
            index_code = '000001.SH'
            index_name = 'SSE Composite Index'
        else:
            index_code = self.find_index_code(stock_code)
            index_name = index_code['name']
            index_code = index_code['in_code']

        columns = list([(item, index_code) for item in ['close', 'pct', 'log']])
        result = self.index_daily.loc[start_date:end_date][columns].round(5)
        return {
            'date': list(result.index.astype(str)),
            'stock': self.stock_daily.loc[start_date:end_date][stock_code].round(5).to_dict(orient='records'),
            'index': [{k[0]: v for k, v in record.items()} for record in result.to_dict(orient='records')],
            'index_name': index_name,
            'stock_name': stock_code
        }
