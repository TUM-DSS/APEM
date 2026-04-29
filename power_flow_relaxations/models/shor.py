from mosek.fusion import Domain, Expr
import numpy as np
from power_flow_relaxations.models.nodal_base_model import NodalBaseModel


class Shor(NodalBaseModel):
    """
    Implementation of the Shor SDP relaxation for ACOPF using MOSEK using only real valued variables.
    """

    def __init__(self, scenario, configuration, **kwargs):
        if configuration is not None:
            configuration.relaxation = True
        super().__init__(scenario, configuration, **kwargs)

        self.W = [self.model.variable(f"W[{t}]", Domain.inPSDCone(2 * len(self.nodes))) for t, _ in self.periods]

    def power_constraints(self):
        n = len(self.nodes)
        for t, _ in self.periods:
            W_t = self.W[t]
            diag_S = Expr.vstack([W_t[2 * i, 2 * i] + W_t[2 * i + 1, 2 * i + 1] for i in range(n)])

            # 0:n-1 --> 0, 2, ..., 2n
            # n:2n-1 --> 1, 3, ..., 2n-1 
            #W_im = W_t[:n, n:] - W_t[n:, :n]
            #W_1 = W_t[[(2 * i, 2 * j + 1) for i in range(n) for j in range(n)]] 
            W_1 = Expr.hstack([W_t[[(2 * i, 2 * j) for i in range(n)]] for j in range(n)])
            W_2 = Expr.hstack([W_t[[(2 * i, 2 * j + 1) for i in range(n)]] for j in range(n)])
            W_3 = Expr.hstack([W_t[[(2 * i + 1, 2 * j) for i in range(n)]] for j in range(n)])
            W_4 = Expr.hstack([W_t[[(2 * i + 1, 2 * j + 1) for i in range(n)]] for j in range(n)])
            W_im = W_2 - W_3
            W_re = Expr.repeat(diag_S, n, 1) - (W_1 + W_4)

            self.model.constraint(W_t == Expr.transpose(W_t))

            # Real power flow constraints
            self.model.constraint(
                self.p_vwt[:, :, t] - (Expr.mulElm(self.G, W_re) + Expr.mulElm(self.B, W_im)) <= self.p_vwt_line_tol
            )

            self.model.constraint(
                self.p_vwt[:, :, t] - (Expr.mulElm(self.G, W_re) + Expr.mulElm(self.B, W_im)) >= -self.p_vwt_line_tol
            )

            # Reactive power flow constraints
            self.model.constraint(
                self.q_vwt[:, :, t] - (- Expr.mulElm(self.B, W_re) + Expr.mulElm(self.G, W_im)) <= self.q_vwt_line_tol
            )

            self.model.constraint(
                self.q_vwt[:, :, t] - (- Expr.mulElm(self.B, W_re) + Expr.mulElm(self.G, W_im)) >= -self.q_vwt_line_tol
            )

            # Voltage magnitude constraints
            self.model.constraint(
                diag_S >= self.V_min ** 2
            )

            self.model.constraint(
                diag_S <= self.V_max ** 2
            )

        self.current_rating_constraints()

    def reference_constraints(self):
        for t, _ in self.periods:
            self.model.constraint(self.W[t][self.reference_bus[0] + 1, :] == 0)
            self.model.constraint(self.W[t][:, self.reference_bus[0] + 1] == 0)
            self.model.constraint(self.W[t][self.reference_bus[0] + 1, self.reference_bus[0] + 1] == 0)
            self.model.constraint(self.W[t][self.reference_bus[0], self.reference_bus[0]] == 1)

    def __str__(self):  # type: ignore
        return "Shor"

    def get_V_vt_values(self) -> dict:
        """
        Returns the approximate voltage magnitudes V_d for each node and period.
        """

        voltages = []
        n = len(self.nodes)
        for t, _ in self.periods:
            W_t = self.W[t].level().reshape((2 * len(self.nodes), 2 * len(self.nodes)))
            W_t = (W_t + W_t.T) / 2

            eigvals, eigvecs = np.linalg.eigh(W_t)
            idx = np.argmax(eigvals)
            lambda1 = eigvals[idx]
            u1 = eigvecs[:, idx]
            V_approx = np.sqrt(lambda1) * u1

            V_approx = np.array([V_approx[2 * i] + 1j * V_approx[2 * i + 1] for i in range(n)])

            phase_ref = np.angle(V_approx[self.reference_bus[0]])
            V_approx = V_approx * np.exp(-1j * phase_ref)

            voltages.append(list(zip(V_approx.real, V_approx.imag)))

        return {
            (v, period): voltages[t][i_v]
            for i_v, v in self.nodes
            for t, period in self.periods
        }
