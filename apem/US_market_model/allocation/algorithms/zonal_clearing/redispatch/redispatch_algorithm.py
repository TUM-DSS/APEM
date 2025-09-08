from typing import Union

from apem.US_market_model.allocation.allocation import Allocation, SellersAllocation
from apem.US_market_model.allocation.configuration import Configuration
from apem.US_market_model.allocation.error import Error
from apem.US_market_model.data.parsing.scenario import Scenario
from abc import ABC, abstractmethod


class RedispatchAlgorithm(ABC):
    """
    Abstract class to be extended by each redispatch algorithm.
    """

    @abstractmethod
    def compute_redispatch(self, nodal_scenario: Scenario, zonal_allocation: SellersAllocation,
                           configuration: Configuration, path: str, redispatch_constraint_units: bool,
                           redispatch_threshold: float) -> Union[Allocation, Error]:
        """
        Computes a redispatch solution for a given zonal solution. The redispatch solution satisfies the constraints
        formulated based on a nodal scenario.

        :param nodal_scenario: nodal scenario based on which constraints are formulated
        :type nodal_scenario: Scenario
        :param zonal_allocation: allocation computed with zonal clearing
        :type zonal_allocation: SellersAllocation
        :param configuration: values of some parameters to be set in the optimizer
        :type configuration: Configuration
        :param path: path to store the results
        :type path: str
        :param redispatch_constraint_units: True if all units can be used for redispatch, False otherwise
        :type redispatch_constraint_units: bool
        :param redispatch_threshold: production threshold for filtering what units can be redispatched
        :type redispatch_threshold: float
        :return: redispatch allocation or error
        :rtype: Union[Allocation, Error]
        """
        pass

    @abstractmethod
    def __str__(self):
        pass
