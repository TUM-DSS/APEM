from implementation.execution_chain import *
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

solve_and_analyse_scenario(Datasets.EU, PowerFlowModels.Zonal_NTC, PricingAlgorithms.Join)
