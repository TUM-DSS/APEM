from enum import Enum

from apem.market_models import EU_model, US_model


class MarketModels(Enum):
    US_model = US_model
    EU_model = EU_model
