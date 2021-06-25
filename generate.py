import pandas as pd
import numpy as np
from itertools import combinations
import os
import sys

class Generate:

    tiers = 'F E D C B A S'.split()
    tier_thresholds = np.array([0, 20, 30, 40, 50, 60, 90], dtype=np.float32) * 0.01

    def __init__(self):
        pass

    def init_from_txt(self, input_path=None):
        if input_path is None:
            print('List input file name :')
            print('--> ', end='')
            sys.stdout.flush()
            input_path = input()

        assert input_path is not None, 'No input ?'

        assert '.txt' in input_path, 'Input must be a txt file'

        output_path = input_path.replace('.txt', '.ods')

        c = 2
        output_path_base = output_path
        while os.path.isfile(output_path):

            output_path = output_path_base.replace('.ods', '') + str(c) + '.ods'
            c += 1

        with open(input_path) as f:
            full_data = f.readlines()

        full_data = list(filter(lambda x :  x!='' and x!='\n', full_data))

        matchups = np.array([[s1.strip('\n'), s2.strip('\n')] for s1, s2 in list(combinations(full_data, 2))])

        formatted = { 'X' : matchups[:, 0],
                      'Y' : matchups[: , 1],
                      'Odds for X': np.full(len(matchups), fill_value=50.)}

        df = pd.DataFrame(data=formatted, columns=list(formatted.keys()))

        with pd.ExcelWriter(output_path, engine='odf') as writer:
            df.to_excel(writer, sheet_name='Matchups')


    # main generate function
    def __call__(self, list_path, ods_path):

        if list_path is None:
            print('List input file name :')
            print('--> ', end='')
            sys.stdout.flush()
            list_path = input()

        if ods_path is None:
            print('ods input file name :')
            print('--> ', end='')
            sys.stdout.flush()
            ods_path = input()

        assert '.ods' in ods_path, 'Ods Input must be an ods file'
        assert '.txt' in list_path, 'list Input must be a txt file'


        with open(list_path) as f:
            full_data = f.readlines()

        output_path = ods_path

        char_scores = { x.strip('\n'):1. for x in filter(lambda x :  x!='' and x!='\n', full_data)}

        df = pd.read_excel(ods_path, engine='odf')

        for i in range(df.shape[0]):
            x, y, odds = df['X'][i], df['Y'][i], df['Odds for X'][i]

            assert 0 <= odds <= 100, 'Odds must be between 0 and 100%'

            d_odds = odds - 50.

            char_scores[x] *= 1+d_odds * 0.01
            char_scores[y] *= 1-d_odds * 0.01

        tier_members = [[] for _ in range(len(Generate.tiers))]
        chars = np.array(list(char_scores.keys()))


        scores = np.array(list(char_scores.values()))

        quantiles = np.quantile(scores, Generate.tier_thresholds, axis=0)

        for tier, q in enumerate(reversed(quantiles)):
            argwhere = np.argwhere(scores>q)
            tier_members[tier].extend(chars[argwhere][:,0])
            scores = np.delete(scores, argwhere)
            chars = np.delete(chars, argwhere)

        max_tier_size = 0
        for tier in tier_members:
            if len(tier)> max_tier_size:
                max_tier_size = len(tier)

        columns = []
        for i in range(max_tier_size):
            columns.append([])
            for j in range(len(tier_members)):
                if i < len(tier_members[j]):
                    columns[-1].append(tier_members[j][i])
                else :
                    columns[-1].append('')

        columns = [np.array(column) for column in columns]

        data = {
            'Tiers' : list(reversed(self.tiers)),
        }
        data.update({
            i: column for i, column in enumerate(columns)
        })

        df_tier_list = pd.DataFrame(data=data, columns=list(data.keys()))

        with pd.ExcelWriter(output_path, engine='odf') as writer:
            df.to_excel(writer, sheet_name='Matchups')
            df_tier_list.to_excel(writer, sheet_name='TierList')







