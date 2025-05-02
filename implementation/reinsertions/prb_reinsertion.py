from fontTools.merge.util import recalculate

from implementation.utils.extraction import get


def PRMIC_PRB_reinsertion(self, is_prmic_not_prb: bool):
    from implementation.euphemia import Euphemia

    counter = 0
    rejected_orders, paradoxically_rejected_orders = calculate_paradoxically_rejected_orders(self, is_prmic_not_prb)

    print(f'Rejected orders: {len(rejected_orders)}')

    if is_prmic_not_prb:
        for id in rejected_orders['complex']:
            if check_PRCO(self, id):
                paradoxically_rejected_orders['complex'].append(id)
        for id in rejected_orders['scalable_complex']:
            if check_PRSCO(self, id):
                paradoxically_rejected_orders['scalable_complex'].append(id)
    else:
        for id in rejected_orders['block']:
            if check_PRB(self, id):
                paradoxically_rejected_orders['block'].append(id)

    while (len(paradoxically_rejected_orders['block']) + len(paradoxically_rejected_orders['complex']) + len(paradoxically_rejected_orders['scalable_complex']) > 0
           or counter >= 20):
        recalculate_list = False
        print(f"Checking {paradoxically_rejected_orders} paradoxically rejected orders...")
        for order_type, ids in paradoxically_rejected_orders.items():
            break_outer_loop = False
            for id in ids:
                print(f'{order_type} order {id} is paradoxically rejected. Attempting to activate it...')
                # New model with block activated and (S)CO fixed
                reinsertion_run = Euphemia(self.scenario)
                reinsertion_run.reinsertion_run = True
                if not is_prmic_not_prb:
                    for _, order in self.complex_orders.iterrows():
                        reinsertion_run.model.addConstr(reinsertion_run.accept_complex[order['id']] == self.current_alloc_solution[f'accept_complex[{order["id"]}]'][0])
                    #TODO SCOs

                reinsertion_run.current_best_objective = self.current_best_objective
                if (order_type == 'block'):
                    reinsertion_run.model.addConstr(reinsertion_run.accept_block[id] == 1, name=f'accept-{id}')
                elif (order_type == 'complex'):
                    reinsertion_run.model.addConstr(reinsertion_run.accept_complex[id] == 1, name=f'accept-{id}')
                elif (order_type == 'scalable_complex'):
                    reinsertion_run.model.addConstr(reinsertion_run.accept_scalable[id] == 1, name=f'accept-{id}')

                reinsertion_run.solve()

                if reinsertion_run.found_solution:
                    if self.current_best_objective >= reinsertion_run.current_best_objective:
                        print(f'Could not activate {order_type} {id}.')
                    else:
                        print(f'Activated {order_type} {id}.')
                        print(f'Activation of {order_type} {id} improved surplus from {self.current_best_objective} to {reinsertion_run.current_best_objective}')
                        # Save better results in master problem and recalculate order list
                        self.current_alloc_solution = reinsertion_run.current_alloc_solution
                        self.current_best_objective = reinsertion_run.current_best_objective
                        self.set_prices(reinsertion_run.prices, reinsertion=False)

                        recalculate_list = True
                        break_outer_loop = True
                        break
                else:
                    print(f'Could not activate PRB {id}.')
            if break_outer_loop:
                break

        if recalculate_list:
            paradoxically_rejected_orders = [block_id for block_id in rejected_orders if check_PRB(self, block_id)]
        # No recalculation -> All PABs checked
        else:
            break

    print(f'PRB reinsertion finished with {len(paradoxically_rejected_orders)} left.')

def calculate_paradoxically_rejected_orders(self, is_prmic_not_prb: bool):
    rejected_orders = {'block': [], 'complex': [], 'scalable_complex': []}
    paradoxically_rejected_orders = {'block': [], 'complex': [], 'scalable_complex': []}
    if not is_prmic_not_prb:
        for _, order in self.block_orders.iterrows():
            id = order['id']
            if self.current_alloc_solution[f'accept_block[{id}]'][0] == 0:
                rejected_orders['block'].append(order['id'])
    else:
        for _, order in self.complex_orders.iterrows():
            id = order['id']
            if self.current_alloc_solution[f'accept_complex[{id}]'][0] == 0:
                rejected_orders['complex'].append(order['id'])
        for _, order in self.scalable_complex_orders.iterrows():
            id = order['id']
            if self.current_alloc_solution[f'accept_scalable_complex[{id}]'][0] == 0:
                rejected_orders['scalable_complex'].append(order['id'])

    return rejected_orders, paradoxically_rejected_orders


def check_PRB(self, order: int) -> bool:
    p = get(self.block_orders, 'p', order)
    q = {t: get(self.block_orders, f'q{t}', order) for t in self.periods}
    sale = True if sum(q.values()) > 0 else False
    avg_mcp = sum(self.prices[t] * q_t for t, q_t in q.items()) / sum(q.values())

    if sale and p < avg_mcp or not sale and avg_mcp < p:
        return True

    return False
