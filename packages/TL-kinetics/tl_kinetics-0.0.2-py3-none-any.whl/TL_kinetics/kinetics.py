import numpy as np
from scipy.integrate import solve_ivp, quad

def TL_first_order(E, s, k, beta, n0, Npoints, T0, Tfinal):
    T_eval = np.linspace(T0, Tfinal, Npoints)

    def rhs(T, n):
        return -n * (s / beta) * np.exp(-E / (k * T))

    sol = solve_ivp(rhs, [T0, Tfinal], [n0], t_eval=T_eval, max_step=0.1)
    n_vals = sol.y[0]
    I = -beta * np.gradient(n_vals, T_eval)

    return T_eval, I


def TL_second_order(E, s, k, beta, N, n0, Npoints, T0, Tfinal):
    T_eval = np.linspace(T0, Tfinal, Npoints)

    def rhs(T, n):
        return -(n**2 / N) * (s / beta) * np.exp(-E / (k * T))

    sol = solve_ivp(rhs, [T0, Tfinal], [n0], t_eval=T_eval, max_step=0.1)
    n_vals = sol.y[0]
    I = -beta * np.gradient(n_vals, T_eval)

    return T_eval, I


def TL_general_order(E, s, k, beta, n0, Npoints, T0, Tfinal, b=1.5):
    T_eval = np.linspace(T0, Tfinal, Npoints)

    def integrand(Tp):
        return np.exp(-E / (k * Tp))

    I_vals = []
    for Ti in T_eval:
        integral, _ = quad(integrand, T0, Ti)
        factor = 1 + ((b - 1) * s / beta) * integral
        intensity = s * n0 * np.exp(-E / (k * Ti)) * factor**(-b / (b - 1))
        I_vals.append(intensity)

    I = np.array(I_vals)

    return T_eval, I
