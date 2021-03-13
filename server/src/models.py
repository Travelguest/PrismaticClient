import pandas as pd
import numpy as np

import scipy.cluster.hierarchy as sch

from datetime import datetime, timedelta
import dateutil.parser
import time
import re

import networkx as nx

PATH_STOCK_LIST = './data/stock_list.ftr'
PATH_STOCK_DAILY = './data/stock_daily.ftr'
PATH_TRADE_CAL = './data/trade_cal.ftr'

PATH_INDUSTRY_LIST = './data/industry_list.ftr'
PATH_INDUSTRY_MEMBER_LIST = './data/industry_member_list.ftr'

PATH_CONCEPT_LIST = './data/concept_list.ftr'
PATH_CONCEPT_MEMBER_LIST = './data/concept_member_list.ftr'
PATH_CONCEPT_DAILY = './data/concept_daily.ftr'

PATH_INDEX_INDUSTRY_LIST = './data/index_industry_list.ftr'
PATH_INDEX_DAILY = './data/index_daily.ftr'


class Model:
    def __init__(self):
        # Stocks related
        self.stock_list = pd.read_feather(PATH_STOCK_LIST)
        self.stock_daily = pd.read_feather(PATH_STOCK_DAILY)
        self.trade_cal = pd.read_feather(PATH_TRADE_CAL)

        # Industry related
        self.industry_list = pd.read_feather(PATH_INDUSTRY_LIST)
        self.industry_member_list = pd.read_feather(PATH_INDUSTRY_MEMBER_LIST)

        # Concept related
        self.concept_list = pd.read_feather(PATH_CONCEPT_LIST)
        self.concept_member_list = pd.read_feather(PATH_CONCEPT_MEMBER_LIST)
        self.concept_daily = pd.read_feather(PATH_CONCEPT_DAILY)

        # Index related
        self.index_industry_list = pd.read_feather(PATH_INDEX_INDUSTRY_LIST)
        self.index_daily = pd.read_feather(PATH_INDEX_DAILY)

        # Calculate stock log change
        self.stock_daily_log = self.stock_daily.pivot_table(values=['close', 'vol'], index='trade_date',
                                                            columns='ts_code')
        self.stock_daily_log = np.log(self.stock_daily_log)
        self.stock_daily_log = self.stock_daily_log - self.stock_daily_log.shift(1)
        self.stock_daily_log = self.stock_daily_log.loc['2011-01-01':]

        # Calculate concept log change
        self.concept_daily_log = self.concept_daily.pivot_table(values=['close'], index='trade_date',
                                                                columns='concept_id')
        self.concept_daily_log = np.log(self.concept_daily_log)
        self.concept_daily_log = self.concept_daily_log - self.concept_daily_log.shift(1)
        self.concept_daily_log = self.concept_daily_log.close.loc['2011-01-01':]

        # Calculate index log change
        self.index_daily_log = self.index_daily.pivot_table(values=['close'], index='trade_date', columns='in_code')
        self.index_daily_log = np.log(self.index_daily_log)
        self.index_daily_log = self.index_daily_log - self.index_daily_log.shift(1)
        self.index_daily_log = self.index_daily_log.close.loc['2011-01-01':]

        # Global variables
        self.features = ['close', 'vol']
        self.query_codes = ['000652', '000538']

    def set_query_codes(self, query_codes):
        if query_codes is None:
            return False
        if len(self.stock_list.query('ts_code == @query_codes')) == len(query_codes):
            self.query_codes = query_codes
            return True
        else:
            return False

    def corr_community_detection(self,
                                 method='pearson',
                                 start_date='2020-01-01',
                                 end_date='2020-06-30',
                                 min_period=0.8):
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
        return pd.concat(selected_corr, axis=1, keys=self.features)

    def corr_community_filter(self,
                              corr,
                              by='close',
                              threshold=0.5):
        corr_filter = pd.eval(
            '|'.join([f'(corr.{by}["{query_code}"].abs()>{threshold})' for query_code in self.query_codes])
        )
        corr_filter = corr[by][corr_filter]
        return list(corr_filter.index.values)

    def list_to_corr_matrix(self,
                            community_list=None,
                            method='pearson',
                            start_date='2020-01-01',
                            end_date='2020-06-30'):
        if community_list is None:
            return None
        # filter stock price by timeframe and query_codes
        stock_price = self.stock_daily_log.loc[start_date:end_date]
        stock_price = stock_price.transpose().loc[
            [(feature, index) for feature in self.features for index in community_list]].transpose()

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
                corr_df_first_hc.columns.values[i:j]]
            sub_corr_col = sub_corr_df.columns.tolist()
            if j - i > 1:
                dist = sch.distance.pdist(sub_corr_df.values)
                link = sch.linkage(dist, method='complete')
                index = sch.fcluster(link, dist.max(initial=0) / 2, 'distance')
                sub_corr_col = [sub_corr_col[ind] for ind in np.argsort(index)]
            i = j
            columns.extend(sub_corr_col)

        corr_dfs = [(corr_df[feature].reindex(columns, axis=0).reindex(columns, axis=1)) for feature in self.features]
        corr_df = corr_dfs[1].copy()
        for idx, col in enumerate(corr_dfs[0].columns):
            corr_df.loc[col][idx:] = corr_dfs[0].loc[col][idx:]
        return pd.concat(corr_dfs + [corr_df], axis=1, keys=self.features + ['combined'])
