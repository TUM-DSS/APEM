from collections import defaultdict
from typing import Tuple

import pandas as pd

from src.data.parsing.scenario import Scenario


class DataConversion:
    """
    Convert bids following the US bidding language to bids expected in the Euphemia implementation.
    """

    def __init__(self, scenario: Scenario):
        self.df_buyers = scenario.df_buyers
        self.df_sellers = scenario.df_sellers
        self.periods = scenario.periods
        self.blocks_buyers = scenario.blocks_buyers
        self.blocks_sellers = scenario.blocks_sellers
        self.block_bids = None

    def compute_buyers_inelastic_bids(self) -> pd.DataFrame:
        """
        Generate block bids to encode inelastic demand.
        """
        info = defaultdict(dict)

        df_dict_records = self.df_buyers.to_dict(orient='records')
        count = 1
        for bid in df_dict_records:
            info[bid['buyer']][bid['period']] = -bid['inelastic_dem']
            info[bid['buyer']]['id'] = str(bid['buyer']) + str(count)
            count += 1

        df = pd.DataFrame.from_dict(info, orient='index').reset_index(drop=True)
        df = df.rename(columns={i: f'q{i}' for i in self.periods})
        df['block_type'] = 'normal'
        df['code_prm'] = pd.NA
        df['MAR'] = 1
        # set a large limit price such that the blocks are always accepted
        df['p'] = 10 ** 6

        columns = ['id', 'block_type', 'code_prm', 'p'] + [f'q{i}' for i in self.periods] + ['MAR']
        df = df[columns]
        return df

    def compute_buyers_elastic_bids(self) -> pd.DataFrame:
        """
        Generate step orders to encode price-elastic demand.
        """
        elastic_dem = [f'val{i}' for i in self.blocks_buyers] + [f'size{i}' for i in self.blocks_buyers]
        info = self.df_buyers[['buyer', 'period'] + elastic_dem]

        data = []
        buyers = self.df_buyers['buyer'].unique().tolist()
        for b in buyers:
            count = 1
            for i in self.blocks_buyers:
                buyer_info = info[info['buyer'] == b]

                order = {'id': str(b) + str(count),
                         't': buyer_info['period'].values[0],
                         'p': buyer_info[f'val{i}'].values[0],
                         'q': buyer_info[f'size{i}'].values[0]
                         }
                data.append(order)
                count += 1

        df_step_orders = pd.DataFrame(data)
        return df_step_orders

    def generate_no_min_uptime_bids(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate scalable complex orders and associated sub-orders to encode the bids of the sellers that fulfill
        the following criteria:
            - minimum uptime = 0
            - minimum production level >= 0
            - no-load cost = 0
        Assume cost1 is the smallest marginal cost.
        """
        sellers = self.df_sellers[self.df_sellers['min_uptime'].isin([0, 1])]['seller'].unique().tolist()
        scalable_orders, scalable_step_orders, step_orders = [], [], []
        for s in sellers:
            suborders_ids = []
            scalable_id = str(s) + 'X' + 'MAR'
            seller_info = self.df_sellers[self.df_sellers['seller'] == s]

            for t in self.periods:
                id_step_min = str(s) + 'X' + f'{t}'
                scalable_step_order_min = {'id': id_step_min,
                                           'scalable_order_id': scalable_id,
                                           't': t,
                                           'p': seller_info['cost1'].values[0],
                                           'q': seller_info['min_prod'].values[0]
                                           }
                suborders_ids.append(id_step_min)
                scalable_step_orders.append(scalable_step_order_min)

                for block in self.blocks_sellers:
                    id_step_block = str(s) + 'X' + f'{t}' + 'X' + f'{block}'
                    q = seller_info[f'size{block}'].values[0]

                    if block == 1:
                        q = seller_info[f'size{block}'].values[0] - seller_info['min_prod'].values[0]

                    if q == 0:
                        continue

                    scalable_step_order_block = {'id': id_step_block,
                                                 'scalable_order_id': str(s) + 'X' + 'MAR',
                                                 't': t,
                                                 'p': seller_info[f'cost{block}'].values[0],
                                                 'q': q
                                                 }

                    suborders_ids.append(id_step_block)
                    scalable_step_orders.append(scalable_step_order_block)

            scalable_order = {'id': scalable_id,
                              'step_orders': suborders_ids,
                              'fixed_term': 0,
                              'condition': pd.NA,
                              'load_gradient': pd.NA,
                              **{f'MAR{t}': seller_info['min_prod'].values[0] if not seller_info.empty else pd.NA
                                 for t in self.periods}
                              }
            scalable_orders.append(scalable_order)

        df_scalable_orders = pd.DataFrame(scalable_orders)
        df_scalable_step_orders = pd.DataFrame(scalable_step_orders)

        return df_scalable_orders, df_scalable_step_orders

    def set_block_bids(self) -> None:
        pass

    def set_step_orders(self) -> None:
        pass
