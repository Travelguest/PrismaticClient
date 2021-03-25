import pandas as pd
import numpy as np
import networkx as nx
import math

import scipy.cluster.hierarchy as sch

PATH_CORR_ALL_YEARS = './data/corr_all_years.pkl'
PATH_TRADE_CAL = './data/trade_cal.ftr'

PATH_STOCK_LIST = './data/stock_list.ftr'
PATH_STOCK_DAILY = './data/stock_daily.ftr'
PATH_STOCK_DAILY_LOG = './data/stock_daily_log.pkl'

PATH_INDUSTRY_LIST = './data/industry_list.ftr'

PATH_CONCEPT_LIST = './data/concept_list.ftr'
PATH_CONCEPT_DAILY = './data/concept_daily.ftr'
PATH_CONCEPT_DAILY_LOG = './data/concept_daily_log.pkl'

PATH_INDEX_INDUSTRY_LIST = './data/index_industry_list.ftr'
PATH_INDEX_DAILY = './data/index_daily.ftr'
PATH_INDEX_DAILY_LOG = './data/index_daily_log.pkl'

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
        self.stock_daily = pd.read_feather(PATH_STOCK_DAILY)
        self.stock_daily_log = pd.read_pickle(PATH_STOCK_DAILY_LOG)
        self.trade_cal = pd.read_feather(PATH_TRADE_CAL)

        # Industry related
        self.industry_list = pd.read_feather(PATH_INDUSTRY_LIST)

        # Concept related
        self.concept_list = pd.read_feather(PATH_CONCEPT_LIST)
        self.concept_daily = pd.read_feather(PATH_CONCEPT_DAILY)
        self.concept_daily_log = pd.read_pickle(PATH_CONCEPT_DAILY_LOG)

        # Index related
        self.index_industry_list = pd.read_feather(PATH_INDEX_INDUSTRY_LIST)
        self.index_daily = pd.read_feather(PATH_INDEX_DAILY)
        self.index_daily_log = pd.read_pickle(PATH_INDEX_DAILY_LOG)

        # Knowledge graph
        # self.knowledge_graph = nx.read_gpickle(PATH_KNOWLEDGE_GRAPH)

        # Default
        self.community_default = pd.read_pickle(PATH_DEFAULT_COMMUNITY)

        # Global variables
        self.features = ['close', 'vol']
        self.query_codes = ['000652', '000538']
        self.query_dates = []
        self.method = None
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
        print(query_codes)
        corr = {str(year): {} for year in range(2011, 2021)}
        for year in range(2011, 2021):
            corr_out = pd.cut(
                self.corr_index_df[str(year)],
                bins=[i / 100 for i in range(-40, 101, 5)],
                precision=2,
                right=True,
                include_lowest=True).value_counts()
            corr[str(year)]['sci'] = [int(corr_out[i / 100]) for i in range(-40, 101, 5)]
            for query_code in self.query_codes:
                corr_out = pd.cut(
                    self.corr_df[str(year)].loc[query_code],
                    bins=[i / 100 for i in range(-40, 101, 5)],
                    precision=2,
                    right=True,
                    include_lowest=True).value_counts()
                corr[str(year)][query_code] = [int(corr_out[i / 100]) for i in range(-40, 101, 5)]
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
        corr = {}
        corr_matrix = self.get_corr_matrix_filtered(year, left_threshold, right_threshold)
        corr_graph = self.get_corr_graph(corr_matrix, left_threshold, right_threshold)
        corr_betweenness = self.get_betweenness_centrality(corr_graph)
        corr_components = self.get_connected_components(corr_graph, corr_betweenness)
        corr['betweenness'] = corr_betweenness
        corr['components'] = corr_components
        return corr

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
        sorted_components = []
        for components in sorted(nx.connected_components(graph), key=len, reverse=True):
            for node in sorted(list(components), key=lambda x: sort_dict[x], reverse=True):
                sorted_components.append(node)
        return sorted_components

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

    # Output to matrix view

    def corr_community_detection(self,
                                 method='pearson',
                                 start_date='2020-01-01',
                                 end_date='2020-06-30',
                                 min_period=0.8):
        # Default case for fast access
        if self.query_codes == ['000652', '000538'] and start_date == '2020-01-01' and end_date == '2020-06-30':
            self.cummunity = self.community_default
            return

        self.query_dates = [start_date, end_date]
        self.method = method
        # filter stock price by timeframe
        stock_price = self.stock_daily_log.loc[start_date:end_date]
        # filter stock price by 0.8*total trade days in the timeframe
        trade_days = self.trade_cal.query('@start_date <= cal_date <= @end_date')['is_open'].sum() * min_period
        trade_days_filter = [(~pd.isna(stock_price.close[column])).sum() > trade_days for column in
                             stock_price.close.columns] * 2
        stock_price = stock_price.transpose()[trade_days_filter].transpose()

        # find individual correlation with other assets
        selected_corr = []
        for feature in self.features:
            selected_stocks = [
                stock_price[feature].corrwith(stock_price[feature][query_code], method=method, drop=True)
                for query_code in self.query_codes
            ]
            selected_corr.append(pd.DataFrame(selected_stocks, index=self.query_codes).transpose())
        self.cummunity = pd.concat(selected_corr, axis=1, keys=self.features)

    def corr_community_filter(self,
                              by='close',
                              left_threshold=0.6,
                              right_threshold=1.0):
        corr_filtered = self.cummunity[by]
        corr_filter_left = pd.eval(
            '|'.join([f'(corr_filtered["{query_code}"]>={left_threshold})' for query_code in self.query_codes]))
        corr_filtered = corr_filtered[corr_filter_left]
        corr_filter_right = pd.eval(
            '|'.join([f'(corr_filtered["{query_code}"]<={right_threshold})' for query_code in self.query_codes]))
        corr_filtered = corr_filtered[corr_filter_right]
        self.community = list(corr_filtered.index.values) if len(corr_filtered) != 0 else None
        if self.community is None:
            return False
        else:
            return self.stock_list[['ts_code', 'name']].merge(pd.Series(self.community, name='ts_code')).merge(
                self.industry_list.query('level == "L1"')[['ts_code', 'industry_name']]).to_dict('records')

    '''
    Correlation matrix
    '''
    # entrance
    def list_to_corr_matrix(self,
                            method='pearson',
                            start_date='2020-01-01',
                            end_date='2020-06-30'):
        if self.community is None:
            return None
        self.query_dates = [start_date, end_date]
        self.method = method
        # filter stock price by timeframe and query_codes
        stock_price = self.stock_daily_log.loc[start_date:end_date]
        stock_price = stock_price.transpose().loc[
            [(feature, index) for feature in self.features for index in self.community]].transpose()

        # find individual correlation with other assets
        selected_corr = []
        for feature in self.features:
            selected_stocks = stock_price[feature].corr(method=method)
            selected_corr.append(selected_stocks)
        return pd.concat(selected_corr, axis=1, keys=self.features)

    def two_phase_hierarchical_clustering(self,
                                          corr_df,
                                          first_by='close',
                                          second_by='vol'):
        if corr_df is None or len(corr_df) <= 1:
            return False
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
        index_price = self.index_daily_log['000001.SH'].loc[self.query_dates[0]:self.query_dates[1]]
        stock_price = self.stock_daily_log.loc[self.query_dates[0]:self.query_dates[1]].close[columns]
        index_corr = list(stock_price.corrwith(index_price, method=self.method, drop=True).values)

        return columns, [
            {'row': row, 'col': col, 'val': val if i != j else index_corr[i],
             'type': 'market' if i == j else 'price' if i <= j else 'vol'}
            for i, (row, col_dict) in enumerate(corr_df.round(5).to_dict(orient='index').items())
            for j, (col, val) in enumerate(col_dict.items())
        ]

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
        index_price = self.index_daily_log[[index_code]].loc[start_date:end_date][::window]
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
        stock_price = self.index_daily_log[['000001.SH']].loc[start_date:end_date][::window]
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
