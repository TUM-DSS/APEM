from enum import Enum

from apem.US_market_model.data.parsing.parse_arpa import ParseARPA
from apem.US_market_model.data.parsing.parse_ieee_rts import ParseIEEERTS
from apem.US_market_model.data.parsing.parse_pjm import ParsePJM
from apem.US_market_model.data.parsing.parse_pypsa_eur_large import ParsePyPSAEurLarge
from apem.US_market_model.data.parsing.parse_pypsa_eur_small import ParsePyPSAEurSmall


class US_Datasets(Enum):
    IEEE_RTS = ParseIEEERTS()
    PJM = ParsePJM()
    PyPSAEurSmall = ParsePyPSAEurSmall()
    PyPSAEurLarge = ParsePyPSAEurLarge()
    ARPA = ParseARPA()
