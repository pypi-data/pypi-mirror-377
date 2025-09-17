# Tools for simulate TL Glow Curves


This library provides functions to simulate **thermoluminescence (TL) glow curves** using three kinetic models:

* **First-order kinetics**
* **Second-order kinetics**
* **General-order kinetics** (with the kinetic order `b`)

It is intended for research and modeling of thermoluminescence phenomena.

---

## Installation

Once the package is available on PyPI:

```
pip install mi_libreria_TL
```

Or if you are using the raw `tl_models.py` file, simply place it in your project and import the functions:

```
from tl_models import TL_first_order, TL_second_order, TL_general_order
```

---

## Function Descriptions

`TL_first_order(E, s, k, beta, n0, Npoints, T0, Tfinal)`
Simulates a **first-order TL glow peak**.

`TL_second_order(E, s, k, beta, N, n0, Npoints, T0, Tfinal)`
Simulates a **second-order TL glow peak**.

`TL_general_order(E, s, k, beta, n0, Npoints, T0, Tfinal, b=1.5)`
Simulates a **general-order TL glow peak**.

---

## Parameter Meaning

| Parameter | Units    | Description                                                                |
| --------- | -------- | -------------------------------------------------------------------------- |
| `E`       | eV       | Activation energy of the trap (depth below conduction band).               |
| `s`       | s⁻¹      | Frequency factor (attempt-to-escape frequency).                            |
| `k`       | eV/K     | Boltzmann constant (≈ 8.617 × 10⁻⁵ eV/K).                                  |
| `beta`    | K/s      | Heating rate (temperature increase per second).                            |
| `n0`      | carriers | Initial number of trapped carriers at `T0`.                                |
| `N`       | carriers | Total trap concentration (used in second-order kinetics).                  |
| `Npoints` | —        | Number of temperature steps in the simulation.                             |
| `T0`      | K        | Initial temperature (Kelvin).                                              |
| `Tfinal`  | K        | Final temperature (Kelvin).                                                |
| `b`       | —        | Kinetic order parameter (`b=1` → first order, `b=2` → second order, etc.). |

---

## Example Usage

```
import matplotlib.pyplot as plt
from tl_models import TL_first_order, TL_second_order, TL_general_order

# Example parameters
E = 1.0          # eV, trap depth
s = 1e12         # s^-1, frequency factor
k = 8.617e-5     # eV/K, Boltzmann constant
beta = 1         # K/s, heating rate
N = 1e10         # total traps
n0 = N           # assume all traps are filled initially
Npoints = 500
T0 = 273.15 + 25     # Initial temperature (298 K = 25 °C)
Tfinal = 273.15 + 250  # Final temperature (523 K = 250 °C)

# First-order TL
T1, I1 = TL_first_order(E, s, k, beta, n0, Npoints, T0, Tfinal)

# Second-order TL
T2, I2 = TL_second_order(E, s, k, beta, N, n0, Npoints, T0, Tfinal)

# General-order TL
Tg, Ig = TL_general_order(E, s, k, beta, n0, Npoints, T0, Tfinal, b=1.5)

# Plotting
plt.plot(T1 - 273.15, I1, label="First-order")
plt.plot(T2 - 273.15, I2, label="Second-order")
plt.plot(Tg - 273.15, Ig, label="General-order (b=1.5)")
plt.xlabel("Temperature (°C)")
plt.ylabel("TL Intensity (a.u.)")
plt.legend()
plt.show()
```

---

## Output

Each function returns:

* `T_eval`: array of temperature values (K).
* `I`: array of simulated TL intensity values (arbitrary units).

You can directly plot `T_eval` vs `I` to visualize the TL glow peak.

