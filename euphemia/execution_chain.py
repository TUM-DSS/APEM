from enum import Enum

from apem.data.parsing.parse_arpa import ParseARPA
from apem.data.parsing.parse_ieee_rts import ParseIEEERTS
from apem.data.parsing.parse_pypsa_eur_small import ParsePyPSAEurSmall
from apem.data.parsing.parse_pypsa_eur_large import ParsePyPSAEurLarge
from apem.data.parsing.parse_pjm import ParsePJM
from euphemia.enums.cut_types import CutType
from euphemia.euphemia import Euphemia
from euphemia.data.parsing.parse_eu import ParseEU
from euphemia.utils.paths import EUPHEMIA_ROOT, RAW_DATA_DIR, CONVERTED_DATASET_PATH_MAP


class Datasets(Enum):
    GENERATED = ParseEU(RAW_DATA_DIR / "generated", "Generated")
    OMIE = ParseEU(RAW_DATA_DIR / "omie", "OMIE")
    IEEE_RTS = ParseEU(CONVERTED_DATASET_PATH_MAP[ParseIEEERTS], "IEEE_RTS")
    ARPA = ParseEU(CONVERTED_DATASET_PATH_MAP[ParseARPA], "ARPA")
    PyPSAEurSmall = ParseEU(CONVERTED_DATASET_PATH_MAP[ParsePyPSAEurSmall], "PyPSAEurSmall")
    PyPSAEurLarge = ParseEU(CONVERTED_DATASET_PATH_MAP[ParsePyPSAEurLarge], "PyPSAEurLarge")
    PJM = ParseEU(CONVERTED_DATASET_PATH_MAP[ParsePJM], "PJM")

def retrieve_data(dataset, day=None):
    return dataset.value.parse_data(day)


#def create_configuration(MIP_gap=1e-4, optimality_tol=1e-6, time_limit=60 * 60, work_limit=60 * 60, threads=0,
#                         presparsify=-1, strict_supply_demand_eq=True, relaxation=False, output_flag=0):
#    return Configuration(MIP_gap, optimality_tol, time_limit, work_limit, threads, presparsify, strict_supply_demand_eq,
#                         relaxation, output_flag)


def solve_and_analyse_scenario(dataset):
    scenario = retrieve_data(dataset)

    #file = open(EUPHEMIA_ROOT / "euphemia_results/scenario", 'w+')
    #file.write(scenario.overview())
    #file.close()

    euphemia = Euphemia(scenario)
    euphemia.solve()

def run_evaluation():
    datasets = [Datasets.GENERATED, Datasets.OMIE]
    for dataset in datasets:
        scenario = retrieve_data(dataset)

        print(f"Running Combinatorial Benders Cut on {dataset}")
        euphemia = Euphemia(scenario)
        euphemia.cutting_strategy = CutType.CB
        euphemia.reinsertionDisabled = True
        euphemia.solve()

        print(f"Running Price-based Cut on {dataset}")
        euphemia = Euphemia(scenario)
        euphemia.cutting_strategy = CutType.PB
        euphemia.reinsertionDisabled = True
        euphemia.solve()

        print("Evaluation finished")
