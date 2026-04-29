from power_flow_relaxations.models.nodal_base_model import NodalBaseModel

import numpy as np

class DCOPF(NodalBaseModel):
    """
    Implementation of the Direct Current Optimal Power Flow Model using MOSEK.
    """

    def __init__(self, scenario, configuration, **kwargs) -> None:
        super().__init__(scenario, configuration, **kwargs)

        self.theta_vt = self.model.variable("theta_vt", [len(self.network), len(self.periods)])

    def power_constraints(self):
        for t, _ in self.periods:
            for i_v, v in self.nodes: 
                for i_w, _ in self.neighbours[v]:
                        
                    self.model.constraint(
                        self.p_vwt[i_v, i_w, t] >= - self.F_max[i_v, i_w] * (1 + self.I_viol[i_v, i_w, t] * self.I_viol_weight)
                    )
                    self.model.constraint(
                        self.p_vwt[i_v, i_w, t] <= self.F_max[i_v, i_w] * (1 + self.I_viol[i_v, i_w, t] * self.I_viol_weight)
                    )
                    self.model.constraint(
                        self.p_vwt[i_v, i_w, t] - self.B[i_v, i_w] * (self.theta_vt[i_v, t] - self.theta_vt[i_w, t]) <= self.p_vwt_line_tol
                    )
                    self.model.constraint(
                        self.p_vwt[i_v, i_w, t] - self.B[i_v, i_w] * (self.theta_vt[i_v, t] - self.theta_vt[i_w, t]) >= -self.p_vwt_line_tol
                    )


    def reference_constraints(self):
        self.model.constraint(self.theta_vt[self.reference_bus[0], :] == 0)

    def get_V_vt_values(self) -> dict[tuple[int, int], tuple[float, float]]:
        value = self.theta_vt.level().reshape([len(self.network), len(self.periods)])
        return {
            (v, period): (np.cos(value[i_v, t]), np.sin(value[i_v, t]))  # type: ignore
            for i_v, v in self.nodes
            for t, period in self.periods
            if value is not None
        }

    def __str__(self):
        return "DCOPF_CVXPY"
