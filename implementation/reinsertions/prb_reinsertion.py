from fontTools.merge.util import recalculate

from implementation.utils.extraction import get


def PRB_reinsertion(self):
    from implementation.euphemia import Euphemia
    counter = 0
    rejected_blocks = []
    for _, order in self.block_orders.iterrows():
        id = order['id']
        if self.current_alloc_solution[f'accept_block[{id}]'][0] == 0:
            rejected_blocks.append(order['id'])
    print(f'Rejected blocks: {len(rejected_blocks)}')
    paradoxically_rejected_blocks = [block_id for block_id in rejected_blocks if check_PRB(self, block_id)]
    while len(paradoxically_rejected_blocks) > 0 or counter >= 20:
        recalculate_list = False
        print(f"Checking {len(paradoxically_rejected_blocks)} paradoxically rejected blocks...")
        for i in paradoxically_rejected_blocks:
            print(f'Block {i} is paradoxically rejected. Attempting to activate it...')
            # New model with block activated and (S)CO fixed
            prb_reinsertion_run = Euphemia(self.scenario)
            prb_reinsertion_run.reinsertion_run = True
            for _, order in self.complex_orders.iterrows():
                prb_reinsertion_run.model.addConstr(prb_reinsertion_run.accept_complex[order['id']] == self.current_alloc_solution[f'accept_complex[{order["id"]}]'][0])
            #TODO SCOs

            prb_reinsertion_run.current_best_objective = self.current_best_objective
            prb_reinsertion_run.model.addConstr(prb_reinsertion_run.accept_block[i] == 1, name=f'accept-{i}')
            prb_reinsertion_run.solve()

            if prb_reinsertion_run.found_solution:
                if self.current_best_objective >= prb_reinsertion_run.current_best_objective:
                    print(f'Could not activate PRB {i}.')
                else:
                    print(f'Activated block {i}.')
                    rejected_blocks = [order['id'] for _, order in prb_reinsertion_run.block_orders.iterrows() if
                                       prb_reinsertion_run.current_alloc_solution[f'accept_block[{id}]'] == 0]
                    self.current_alloc_solution = prb_reinsertion_run.current_alloc_solution
                    print(f'Activation of block {i} improved surplus from {self.current_best_objective} to {prb_reinsertion_run.current_best_objective}')
                    self.current_best_objective = prb_reinsertion_run.current_best_objective
                    self.set_prices(prb_reinsertion_run.prices, reinsertion=False)
                    recalculate_list = True
                    break
            else:
                print(f'Could not activate PRB {i}.')

        if recalculate_list:
            paradoxically_rejected_blocks = [block_id for block_id in rejected_blocks if check_PRB(self, block_id)]
        # No recalculation -> All PABs checked
        else:
            break

    print(f'PRB reinsertion finished with {len(paradoxically_rejected_blocks)} left.')


def check_PRB(self, order: int) -> bool:
    p = get(self.block_orders, 'p', order)
    q = {t: get(self.block_orders, f'q{t}', order) for t in self.periods}
    sale = True if sum(q.values()) > 0 else False
    avg_mcp = sum(self.prices[t] * q_t for t, q_t in q.items()) / sum(q.values())

    if sale and p < avg_mcp or not sale and avg_mcp < p:
        return True

    return False
