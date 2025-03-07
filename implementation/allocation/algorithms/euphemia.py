import ast
import os
import random
import shutil
from typing import Optional
import gurobipy as gp
from gurobipy import GRB
import re

from implementation.data.parsing.scenario import ZonalScenario
from implementation.utils.extraction import get


class Euphemia:
    def __init__(self, scenario: ZonalScenario):
        self.model = gp.Model('Euphemia')
        self.periods = scenario.periods
        self.step_orders = scenario.step_orders
        self.block_orders = scenario.block_orders
        self.complex_orders = scenario.complex_orders
        self.complex_step_orders = scenario.complex_step_orders
        self.scalable_complex_orders = scenario.scalable_complex_orders
        self.scalable_step_orders = scenario.scalable_step_orders

        self.accept_step = self.model.addVars(list(self.step_orders['id']), vtype=GRB.CONTINUOUS, lb=0, ub=1,
                                              name='accept_step')
        self.accept_block = self.model.addVars(list(self.block_orders['id']), vtype=GRB.BINARY, lb=0, ub=1,
                                               name='accept_block')
        # required for the big-M constraint to satisfy the MAR condition of block orders
        self.MAR_aux = self.model.addVars(list(self.block_orders['id']), vtype=GRB.BINARY, name='y')

        # required for flexible orders - decide in which period the order is accepted
        self.flex_period = self.model.addVars(
            list(self.block_orders[self.block_orders['block_type'] == 'flexible']['id']), self.periods,
            vtype=GRB.BINARY, name='flex_period')
        self.accept_complex = self.model.addVars(list(self.complex_orders['id']), vtype=GRB.BINARY, lb=0, ub=1,
                                                 name='accept_mic_complex')
        self.accept_complex_step = self.model.addVars(list(self.complex_step_orders['id']), vtype=GRB.CONTINUOUS,
                                                      lb=0, ub=1, name='accept_complex_step')
        self.accept_scalable = self.model.addVars(list(self.scalable_complex_orders['id']), vtype=GRB.BINARY,
                                                  lb=0, ub=1, name='accept_mic_scalable')
        self.accept_scalable_step = self.model.addVars(list(self.scalable_step_orders['id']), vtype=GRB.CONTINUOUS,
                                                       lb=0, ub=1, name='accept_scalable_step')
        self.M = 10 ** 6
        self.prices = {}
        self.prices_reinsertion = {}
        self.price_lower_bound = -10
        self.price_upper_bound = 100
        self.delta_PAB = 50
        self.delta_MIC = 50
        self.max_iterations = 30
        self.iteration = 0
        self.paths = {
            "alloc": "euphemia_results/allocation",
            "prices": "euphemia_results/prices",
            "pab": "euphemia_results/pab",
            "block_inm_threshold": "euphemia_results/block_inm_threshold",
            "complex_mic": "euphemia_results/complex_mic",
            "complex_mic_inm_threshold": "euphemia_results/complex_mic_inm_threshold",
            "scalable_mic": "euphemia_results/scalable_mic",
            "scalable_mic_inm_threshold": "euphemia_results/scalable_mic_inm_threshold",
            "debug": "euphemia_results/debug",

        }

        for attr, path in self.paths.items():
            setattr(self, attr, path)
            if os.path.exists(path):
                shutil.rmtree(path)
            os.makedirs(path, exist_ok=True)

    def solve(self) -> None:
        """
        Compute market clearing prices, matched volumes, selection of block and complex orders that will be executed,
        accepted percentage for each curtailable block.
        Determine the market clearing price for each zone while ensuring that no block and complex MIC orders are
        paradoxically accepted and the primal-dual relations are satisfied.
        Add cut to the master problem that renders the current solution infeasible if no prices were found.
        The prices computed satisfy:
            - complementary slackness conditions
            - price bounds
            - no PAB constraints
            - MIC
        """
        self.add_objective()
        self.add_market_constraints()
        self.add_network_constraints()

        self.iteration = 1
        success = True
        while self.iteration < self.max_iterations:
            print(f"\nIteration {self.iteration}\n")
            success = True

            print("Solving master problem...")
            self.solve_master_problem()
            infeasible = self.check_infeasibility(self.model)
            if infeasible:
                print(f"Model is infeasible - iteration {self.iteration}")
                exit()

            print(f"Economic surplus: {self.get_objective()}")

            print("Solving price determination subproblem...")
            self.solve_price_determination_subproblem()

            print("Computing PAB...")
            pab = self.get_block_bids(threshold=False)
            if len(pab) > 0:
                success = False
                print(f"There are {len(pab)} PAB. Adding block cut...")
                cut_added = self.add_block_cut()
                increase_count = 0
                while not cut_added and increase_count < 5:
                    increase_count += 1
                    self.delta_PAB += 10
                    print(f"Increasing delta_PAB to {self.delta_PAB}.\n")
                    cut_added = self.add_block_cut()

                if not cut_added:
                    print("Reject PAB.")
                    self.model.addConstrs(self.accept_block[i] == 0 for i in pab)

                self.delta_PAB -= 10 * increase_count
                self.iteration += 1
                continue

            print("No PAB.")

            print("Computing complex orders with MIC/MP condition violated...")
            violated_MIC_MP_complex = self.get_MIC_complex_orders(threshold=False)
            if len(violated_MIC_MP_complex) > 0:
                success = False
                print(f"MIC/MP conditions violated in {len(violated_MIC_MP_complex)} complex orders.")
                cut_added = self.add_MIC_complex_cut()
                increase_count = 0
                while not cut_added and increase_count < 5:
                    increase_count += 1
                    self.delta_MIC += 10
                    print(f"Increasing delta_MIC to {self.delta_MIC}.\n")
                    cut_added = self.add_MIC_complex_cut()

                if not cut_added:
                    print("Reject complex orders with MIC condition violated.")
                    self.model.addConstrs(self.accept_complex[i] == 0 for i in violated_MIC_MP_complex)

                self.delta_MIC -= 10 * increase_count
                self.iteration += 1
                continue

            print(f"MIC condition satisfied in complex orders.")

            print("Computing scalable complex orders with MIC/MP condition violated...")
            violated_MIC_MP_scalable = self.get_MIC_scalable_orders(threshold=False)
            if len(violated_MIC_MP_scalable) > 0:
                success = False
                print(f"MIC/MP conditions violated in {len(violated_MIC_MP_scalable)} scalable complex orders.")
                cut_added = self.add_MIC_scalable_cut()
                increase_count = 0
                while not cut_added and increase_count < 5:
                    increase_count += 1
                    self.delta_MIC += 10
                    print(f"Increasing delta_MIC to {self.delta_MIC}.\n")
                    cut_added = self.add_MIC_scalable_cut()

                if not cut_added:
                    print("Reject scalable complex orders with MIC condition violated.")
                    self.model.addConstrs(self.accept_scalable[i] == 0 for i in violated_MIC_MP_scalable)

                self.delta_MIC -= 10 * increase_count
                self.iteration += 1
                continue

            print(f"MIC condition satisfied in scalable complex orders.")

            if success:
                print("Pricing subproblem solved.")
                break
            else:
                print("Could not find a solution.\n")

        if not success:
            print("Could not find a solution.\n")

        print("\nPRB reinsertion...\n")
        self.PRB_reinsertion()

        print(f'Final economic surplus: {self.get_objective()}')

    def add_objective(self) -> None:
        # 1) step orders
        step_orders_obj = gp.quicksum(
            self.accept_step[i] * get(self.step_orders, 'q', i) * get(self.step_orders, 'p', i)
            for i in list(self.step_orders['id']))

        # 3) block orders
        block_orders_obj = gp.quicksum(
            self.accept_block[i] * gp.quicksum(get(self.block_orders, f'q{t}', i) for t in self.periods) *
            get(self.block_orders, 'p', i)
            for i in list(self.block_orders['id']))

        # 4) complex orders - consider step suborders
        complex_orders_obj = gp.quicksum(
            self.accept_complex_step[i] * get(self.complex_step_orders, 'q', i) * get(self.complex_step_orders, 'p', i)
            for i in list(self.complex_step_orders['id']))

        # 5) scalable complex orders
        scalable_orders_obj = gp.quicksum(
            self.accept_scalable_step[i] * get(self.scalable_step_orders, 'q', i) *
            get(self.scalable_step_orders, 'p', i) for i in list(self.scalable_step_orders['id']))

        # sign(type(sco))FixedTerm_sco B_ACCEPT_sco

        # 7) tariff

        # 8) max curtailment

        self.model.setObjective(-step_orders_obj - block_orders_obj - complex_orders_obj - scalable_orders_obj,
                                GRB.MAXIMIZE)

    def add_market_constraints(self) -> None:
        # supply - demand balance
        self.model.addConstrs(
            (gp.quicksum(self.accept_step[i] * get(self.step_orders, 'q', i)
                         for i in list(self.step_orders['id']) if get(self.step_orders, 't', i) == t) +
             gp.quicksum(self.accept_block[i] * get(self.block_orders, f'q{t}', i)
                         for i in list(self.block_orders['id'])) +
             gp.quicksum(self.accept_complex_step[i] * get(self.complex_step_orders, 'q', i)
                         for i in list(self.complex_step_orders['id']) if get(self.complex_step_orders, 't', i) == t) +
             gp.quicksum(self.accept_scalable_step[i] * get(self.scalable_step_orders, 'q', i)
                         for i in list(self.scalable_step_orders['id']) if get(self.scalable_step_orders, 't', i) == t)
             == 0
             for t in self.periods), name='power_balance')

        # block order acceptance
        # accept_block[i] = 0 or accept_block[i] >= MAR
        self.model.addConstrs(
            self.accept_block[i] >= get(self.block_orders, 'MAR', i) * self.MAR_aux[i] for i in
            list(self.block_orders['id']))

        self.model.addConstrs(self.accept_block[i] <= self.M * self.MAR_aux[i] for i in list(self.block_orders['id']))

        # exclusive groups
        exclusive_groups = list(self.block_orders[self.block_orders['block_type'] == 'exclusive']['code_prm'])
        exclusive_blocks = list(self.block_orders[self.block_orders['block_type'] == 'exclusive']['id'])

        self.model.addConstrs(
            gp.quicksum(
                self.accept_block[i] for i in exclusive_blocks if get(self.block_orders, 'code_prm', i) == eg) <= 1
            for eg in exclusive_groups)

        # linked blocks
        linked_blocks = list(self.block_orders[self.block_orders['block_type'] == 'linked']['id'])
        block_to_parent = {i: int(get(self.block_orders, 'code_prm', i)) for i in linked_blocks}

        self.model.addConstrs(self.accept_block[i] <= self.accept_block[block_to_parent[i]] for i in linked_blocks)

        # flexible blocks
        flexible_blocks = list(self.block_orders[self.block_orders['block_type'] == 'flexible']['id'])
        self.model.addConstrs(gp.quicksum(self.flex_period[i, t] for t in self.periods) <= 1 for i in flexible_blocks)
        self.model.addConstrs(self.accept_block[i] == gp.quicksum(self.flex_period[i, t] for t in self.periods)
                              for i in flexible_blocks)

        # complex orders
        complex_step_orders = list(self.complex_step_orders['id'])

        self.model.addConstrs(
            self.accept_complex_step[i] <= self.accept_complex[get(self.complex_step_orders, 'complex_order_id', i)]
            for i in complex_step_orders)

        # scalable complex orders
        scalable_step_orders = list(self.scalable_step_orders['id'])

        self.model.addConstrs(
            self.accept_scalable_step[i] <= self.accept_scalable[get(self.scalable_step_orders, 'scalable_order_id', i)]
            for i in scalable_step_orders)

        # load gradient condition
        # complex orders
        load_gradient_complex_ids = self.complex_orders.loc[self.complex_orders['load_gradient'].notna(), 'id'].tolist()

        for i in load_gradient_complex_ids:
            periods_orders = {}
            inc_dec = get(self.complex_orders, 'load_gradient', i)
            for t in self.periods:
                # for a specific complex order sum over all associated step orders from the current period
                orders_i_t = self.complex_step_orders.loc[
                    (self.complex_step_orders['complex_order_id'] == i) & (
                            self.complex_step_orders['t'] == t), 'id'].tolist()

                periods_orders[t] = gp.quicksum(
                    self.accept_complex_step[i] * abs(get(self.complex_step_orders, 'q', i)) for i in orders_i_t)

            self.model.addConstrs(
                periods_orders[t] - periods_orders[t - 1] <= inc_dec * self.accept_complex[i] for t in
                self.periods[1:])
            self.model.addConstrs(
                periods_orders[t - 1] - periods_orders[t] <= inc_dec * self.accept_complex[i] for t in
                self.periods[1:])

        # scalable complex orders
        load_gradient_scalable_ids = self.scalable_complex_orders.loc[
            self.scalable_complex_orders['load_gradient'].notna(), 'id'].tolist()

        for i in load_gradient_scalable_ids:
            periods_orders = {}
            inc_dec = get(self.scalable_complex_orders, 'load_gradient', i)
            for t in self.periods:
                orders_i_t = self.scalable_step_orders.loc[
                    (self.scalable_step_orders['scalable_order_id'] == i) & (
                            self.scalable_step_orders['t'] == t), 'id'].tolist()

                periods_orders[t] = gp.quicksum(
                    self.accept_scalable_step[i] * abs(get(self.scalable_step_orders, 'q', i)) for i in orders_i_t)

            self.model.addConstrs(
                periods_orders[t] - periods_orders[t - 1] <= inc_dec * self.accept_scalable[i] for t in
                self.periods[1:])
            self.model.addConstrs(
                periods_orders[t - 1] - periods_orders[t] <= inc_dec * self.accept_scalable[i] for t in
                self.periods[1:])

            # MAP
            self.model.addConstrs(
                periods_orders[t] >= get(self.scalable_complex_orders, f'MAP{t}', i) * self.accept_scalable[i]
                for t in self.periods)

        # MAP for scalable complex orders that do not have the load gradient condition
        for i in self.scalable_complex_orders['id'].tolist():
            if i not in load_gradient_scalable_ids:
                periods_orders = {}
                for t in self.periods:
                    orders_i_t = self.scalable_step_orders.loc[
                        (self.scalable_step_orders['scalable_order_id'] == i) & (
                                self.scalable_step_orders['t'] == t), 'id'].tolist()

                    periods_orders[t] = gp.quicksum(
                        self.accept_scalable_step[i] * abs(get(self.scalable_step_orders, 'q', i)) for i in orders_i_t)

                self.model.addConstrs(
                    periods_orders[t] >= get(self.scalable_complex_orders, f'MAP{t}', i) * self.accept_scalable[i]
                    for t in self.periods)

        self.model.write(os.path.join(self.paths['debug'], f"master_{self.iteration}.lp"))
        self.model.setParam("OutputFlag", 0)

    def add_network_constraints(self) -> None:
        # ATC

        # PTDF

        # ramping
        pass

    def solve_master_problem(self) -> None:
        """
        Search for a good selection of block and MIC orders that maximizes the economic surplus.
        """
        self.model.optimize()

        file = open(self.paths['alloc'] + f'/iteration_{self.iteration}', 'w+')

        if self.model.status == GRB.OPTIMAL:
            file.write(f"Objective Value: {self.get_objective()}\n")
            for var in self.model.getVars():
                file.write(f"{var.varName} = {var.X}\n")
        else:
            file.write(f"Status: {self.model.status}")
        file.close()

    def solve_price_determination_subproblem(self, reinsertion: Optional[bool] = False) -> None:
        """
        Compute shadow prices.
        """
        fixed_model = self.model.fixed()
        fixed_model.optimize()
        prices = {}
        for i in [i for i in fixed_model.getConstrs() if "power_balance" in i.ConstrName]:
            match = re.search(r'\[(\d+)\]', i.ConstrName)
            period = int(match.group(1))
            prices[period] = -i.getAttr("Pi")

        self.set_prices(prices, reinsertion=reinsertion)

        with open(self.paths['prices'] + f'/iteration_{self.iteration}_reinsertion_{reinsertion}.txt', 'w') as file:
            for key, value in prices.items():
                file.write(f"{key}: {value}\n")

    def get_block_bids(self, threshold: bool, reinsertion: Optional[bool] = False) -> list:
        """
        Compute accepted block orders that satisfy a condition.
        If threshold is True, compute block orders that are in-the-money by less than delta_PAB.
        If threshold is False, compute block orders that are paradoxically accepted.
        """
        res = []
        for i in list(self.block_orders['id']):
            if self.accept_block[i].X == 0:
                continue
            p = get(self.block_orders, 'p', i)
            q = {t: get(self.block_orders, f'q{t}', i) for t in self.periods if get(self.block_orders, f'q{t}', i) != 0}
            sale = True if sum(q.values()) > 0 else False

            if not reinsertion:
                avg_mcp = sum(self.prices[q_t] for q_t in q.keys()) / len(q)
            else:
                avg_mcp = sum(self.prices_reinsertion[q_t] for q_t in q.keys()) / len(q)

            if threshold:
                if sale and avg_mcp - self.delta_PAB < p < avg_mcp or not sale and avg_mcp < p < avg_mcp - self.delta_PAB:
                    res.append(i)
            else:
                if sale and p > avg_mcp or not sale and avg_mcp > p:
                    res.append(i)

        path_key = 'pab' if not threshold else 'block_inm_threshold'
        file_path = f"{self.paths[path_key]}/iteration_{self.iteration}.txt"

        with open(file_path, 'w') as file:
            file.writelines(f"{bid}\n" for bid in res)

        return res

    def add_block_cut(self, single: Optional[bool] = False) -> bool:
        """
        If single is False, reject all block orders that are in-the-money by less than delta_PAB.
        If single is True, reject a single block order.
        """
        in_the_money_blocks = self.get_block_bids(threshold=True)
        if len(in_the_money_blocks) == 0:
            print("No INM block orders left to reject.")
            return False
        if not single:
            self.model.addConstrs(self.accept_block[i] == 0 for i in in_the_money_blocks)
        else:
            random_block = random.choice(in_the_money_blocks)
            self.model.addConstr(self.accept_block[random_block] == 0)

        print("Block cut successfully added.")
        return True

    def get_MIC_complex_orders(self, threshold: Optional[bool] = False, reinsertion: Optional[bool] = False) -> list:
        """
        If threshold is False, return a list with complex orders that do not have the MIC/MP condition satisfied.
        If threshold is True, return a list of complex orders that are in-the-money by at most delta_MIC.
        """
        prices = self.prices if not reinsertion else self.prices_reinsertion

        mic_complex_order_ids = self.complex_orders.loc[self.complex_orders['condition'] == 'MIC', 'id'].tolist()
        mp_complex_order_ids = self.complex_orders.loc[self.complex_orders['condition'] == 'MP', 'id'].tolist()

        res = []
        for i in mic_complex_order_ids + mp_complex_order_ids:
            if self.accept_complex[i].X == 0:
                continue
            fixed_term = get(self.complex_orders, 'fixed_term', i)
            variable_term = get(self.complex_orders, 'variable_term', i)
            step_orders = ast.literal_eval(get(self.complex_orders, 'step_orders', i))

            expected = sum(variable_term * abs(get(self.complex_step_orders, 'q', j)) * self.accept_complex_step[j].X
                           for j in step_orders) + fixed_term
            actual = 0
            for t in self.periods:
                step_orders_t = self.complex_step_orders[
                    (self.complex_step_orders['id'].isin(step_orders)) & (self.complex_step_orders['t'] == t)][
                    'id'].tolist()

                if i in mic_complex_order_ids:
                    actual += sum(
                        (prices[t] - get(self.complex_step_orders, 'p', j)) *
                        abs(get(self.complex_step_orders, 'q', j)) * self.accept_complex_step[j].X
                        for j in step_orders_t)
                else:
                    actual += sum(
                        prices[t] *
                        abs(get(self.complex_step_orders, 'q', j)) * self.accept_complex_step[j].X
                        for j in step_orders_t)

            if not threshold:
                if i in mic_complex_order_ids and expected > actual:
                    res.append(i)
                elif i in mp_complex_order_ids and expected < actual:
                    res.append(i)
            else:
                if i in mic_complex_order_ids and expected < actual < expected + self.delta_MIC:
                    res.append(i)
                elif i in mp_complex_order_ids and expected - self.delta_MIC < actual < expected:
                    res.append(i)

            path_key = 'complex_mic_inm_threshold' if threshold else 'complex_mic'
            file_path = f"{self.paths[path_key]}/iteration_{self.iteration}.txt"

            with open(file_path, 'w') as file:
                file.writelines(f"{bid}\n" for bid in res)

        return res

    def get_MIC_scalable_orders(self, threshold: Optional[bool] = False, reinsertion: Optional[bool] = False) -> list:
        """
        If threshold is False, return a list with scalable complex orders that do not have the MIC/MP condition
        satisfied. If threshold is True, return a list of scalable complex orders that are in-the-money by at most
        delta_MIC.
        """
        prices = self.prices if not reinsertion else self.prices_reinsertion

        mic_scalable_order_ids = self.scalable_complex_orders.loc[
            self.scalable_complex_orders['condition'] == 'MIC', 'id'].tolist()
        mp_scalable_order_ids = self.scalable_complex_orders.loc[
            self.scalable_complex_orders['condition'] == 'MP', 'id'].tolist()

        res = []
        for i in mic_scalable_order_ids + mp_scalable_order_ids:
            if self.accept_scalable[i].X == 0:
                continue
            fixed_term = get(self.scalable_complex_orders, 'fixed_term', i)
            step_orders = ast.literal_eval(get(self.scalable_complex_orders, 'step_orders', i))

            expected, actual = 0, 0
            for t in self.periods:
                step_orders_t = self.scalable_step_orders[
                    (self.scalable_step_orders['id'].isin(step_orders)) & (self.scalable_step_orders['t'] == t)][
                    'id'].tolist()

                if i in mic_scalable_order_ids:
                    actual += sum(
                        (prices[t] - get(self.scalable_step_orders, 'p', j)) *
                        abs(get(self.scalable_step_orders, 'q', j)) * self.accept_scalable_step[j].X
                        for j in step_orders_t)
                else:
                    actual += sum(
                        prices[t] *
                        abs(get(self.scalable_step_orders, 'q', j)) * self.accept_scalable_step[j].X
                        for j in step_orders_t)

                expected += sum(get(self.scalable_step_orders, 'p', j) * abs(get(self.scalable_step_orders, 'q', j)) *
                                self.accept_scalable_step[j].X for j in step_orders_t)

            expected += fixed_term

            if not threshold:
                if i in mic_scalable_order_ids and expected > actual:
                    res.append(i)
                elif i in mp_scalable_order_ids and expected < actual:
                    res.append(i)
            else:
                if i in mic_scalable_order_ids and expected < actual < expected + self.delta_MIC:
                    res.append(i)
                elif i in mp_scalable_order_ids and expected - self.delta_MIC < actual < expected:
                    res.append(i)

            path_key = 'scalable_mic_inm_threshold' if threshold else 'scalable_mic'
            file_path = f"{self.paths[path_key]}/iteration_{self.iteration}.txt"

            with open(file_path, 'w') as file:
                file.writelines(f"{bid}\n" for bid in res)

        return res

    def add_MIC_complex_cut(self, single: Optional[bool] = False) -> bool:
        """
        If single is False, add cuts to reject complex orders that are in-the-money by less than delta_MIC.
        If single is True, add a single cut.
        """
        in_the_money_MIC_complex_orders = self.get_MIC_complex_orders(threshold=True)
        if len(in_the_money_MIC_complex_orders) == 0:
            print("No INM complex MIC orders left to reject.")
            return False
        else:
            if not single:
                self.model.addConstrs(self.accept_complex[i] == 0 for i in in_the_money_MIC_complex_orders)
            else:
                random_order = random.choice(in_the_money_MIC_complex_orders)
                self.model.addConstr(self.accept_complex[random_order] == 0)

        print("MIC complex cut successfully added.")
        return True

    def add_MIC_scalable_cut(self, single: Optional[bool] = False) -> bool:
        """
        If single is False, add cuts to reject scalable complex orders that are in-the-money by less than delta_MIC.
        If single is True, add a single cut.
        """
        in_the_money_MIC_scalable_orders = self.get_MIC_scalable_orders(threshold=True)
        if len(in_the_money_MIC_scalable_orders) == 0:
            print("No INM scalable complex MIC orders left to reject.")
            return False
        else:
            if not single:
                self.model.addConstrs(self.accept_scalable[i] == 0 for i in in_the_money_MIC_scalable_orders)
            else:
                random_order = random.choice(in_the_money_MIC_scalable_orders)
                self.model.addConstr(self.accept_scalable[random_order] == 0)

        print("MIC scalable complex cut successfully added.")
        return True

    def check_PRB(self, order: int) -> bool:
        p = get(self.block_orders, 'p', order)
        q = {t: get(self.block_orders, f'q{t}', order) for t in self.periods if
             get(self.block_orders, f'q{t}', order) != 0}
        sale = True if sum(q.values()) > 0 else False
        avg_mcp = sum(self.prices[q_t] for q_t in q.keys()) / len(q)

        if sale and p < avg_mcp or not sale and avg_mcp < p:
            return True

        return False

    def PRB_reinsertion(self):
        rejected_blocks = [i for i in self.block_orders['id'] if self.accept_block[i].X == 0]
        print(f"Checking {len(rejected_blocks)} rejected blocks...")
        obj = self.get_objective()
        for i in rejected_blocks:
            if self.check_PRB(i):
                print(f'Block {i} is paradoxically rejected. Attempting to activate it...')
                self.model.addConstr(self.accept_block[i] == 1, name=f'accept-{i}')
                self.solve_master_problem()
                infeasible = self.check_infeasibility(self.model, reinsertion=True)
                ok = False
                if not infeasible:
                    new_obj = self.get_objective()
                    if obj <= new_obj:
                        self.solve_price_determination_subproblem(reinsertion=True)
                        pab = self.get_block_bids(threshold=False, reinsertion=True)
                        if len(pab) == 0:
                            violated_complex_mic = self.get_MIC_complex_orders(reinsertion=True)
                            if len(violated_complex_mic) == 0:
                                violated_scalable_mic = self.get_MIC_scalable_orders(reinsertion=True)
                                if len(violated_scalable_mic) == 0:
                                    ok = True
                if not ok:
                    self.model.remove(self.model.getConstrByName(f'accept-{i}'))
                    self.solve_master_problem()
                    print(f'Could not activate PRB {i}.')
                else:
                    self.set_prices(self.prices_reinsertion)
                    print(f'Activated block {i}.')
        print('PRB reinsertion finished.')

    def check_in_the_money_complex(self, order_id: int) -> bool:
        """
        Check if a complex MIC/MP order is in-the-money.
        """
        pass

    def check_in_the_money_scalable(self, order_id: id) -> bool:
        """
        Check if a scalable complex order is in-the-money.
        """
        pass

    def volume_indeterminacy_subproblem(self):
        # later
        pass

    def check_infeasibility(self, model: gp.Model, reinsertion: Optional[bool] = False) -> bool:
        """
        Check if model is infeasible. If applicable, compute an Irreducible Inconsistent Subsystem (IIS).
        """
        try:
            if model.status == GRB.INFEASIBLE:
                print("Model is infeasible. Computing IIS...")
                model.computeIIS()
                iis_file = os.path.join(self.paths['debug'],
                                        f"master_iip_{self.iteration}_reinsertion_{reinsertion}.ilp")
                model.write(iis_file)
                print(f"IIS file saved at: {iis_file}")
                return True
            else:
                return False
        except gp.GurobiError as e:
            print(f'An error occurred while checking infeasibility: {e}')

    def set_prices(self, prices: dict, reinsertion: Optional[bool] = False) -> None:
        if not reinsertion:
            self.prices = prices
        else:
            self.prices_reinsertion = prices

    def get_objective(self) -> float:
        return self.model.getObjective().getValue()

    def __str__(self):
        return 'Euphemia'
