import pandas as pd
import numpy as np
from itertools import combinations

class Generate:

    tiers = 'F E D C B A S'.split()
    tier_thresholds = np.array([0, 20, 30, 40, 50, 60, 90], dtype=np.float32) * 0.01

    def __init__(self, input_path):

        self.input_path = input_path
        #self.input_ = pd.read_excel(input_path, engine='odf')


    def init_from_txt(self):
        output_path = self.input_path.replace('.txt', '.ods')
        with open(self.input_path) as f:
            full_data = f.readlines()

        full_data = list(filter(lambda x :  x!='' and x!='\n', full_data))

        matchups = np.array([[s1.strip('\n'), s2.strip('\n')] for s1, s2 in list(combinations(full_data, 2))])

        formatted = { 'X' : matchups[:, 0],
                      'Y' : matchups[: , 1],
                      'Odds for X': np.full(len(matchups), fill_value=50.)}

        formatted['Odds for X'] = np.random.uniform(0, 100, len(matchups))

        df = pd.DataFrame(data=formatted, columns=list(formatted.keys()))

        with pd.ExcelWriter(output_path, engine='odf') as writer:
            df.to_excel(writer, sheet_name='Matchups')


    @staticmethod
    def fuzzy_classifier(score):
        for threshold, name in Generate.tier_limits:
            if score*50 < threshold * Generate.scale:
                return name

        return 'S'

    # main generate function
    def __call__(self):
        with open(self.input_path) as f:
            full_data = f.readlines()

        output_path = self.input_path.replace('.txt', '.ods')

        char_scores = { x.strip('\n'):1. for x in filter(lambda x :  x!='' and x!='\n', full_data)}

        self.input_path = self.input_path.replace('.txt', '.ods')
        df = pd.read_excel(self.input_path, engine='odf')

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

        print(tier_members)

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


        #for char, score in char_scores.items():
        #    tier_members[self.tier_to_index[self.fuzzy_classifier(score)]].append(char)

        #print(tier_members)


        data = {
            'Tiers' : list(reversed(self.tiers)),
        }
        data.update({
            i: column for i, column in enumerate(columns)
        })

        print(data)

        df_tier_list = pd.DataFrame(data=data, columns=list(data.keys()))

        with pd.ExcelWriter(output_path, engine='odf') as writer:
            df.to_excel(writer, sheet_name='Matchups')
            df_tier_list.to_excel(writer, sheet_name='TierList')







