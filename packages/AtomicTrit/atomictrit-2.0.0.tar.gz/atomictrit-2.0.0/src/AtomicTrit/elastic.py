# ================================================================================
#  Functions for elastic singlet and triplet phase shifts and cross sections
# ================================================================================

from AtomicTrit.constants import *
from AtomicTrit import potentials

import scipy
from scipy.special import spherical_jn, spherical_yn
from scipy.integrate import odeint


def Wave_Function(rhos,pin,l, mu, potential=potentials.Silvera_Triplet, int_type='Radau'):
    def ddx(y, rho, mu, Potential, l, pin):
        u = y[0]
        v = y[1]
        dudr = v
        dvdr = (-pin ** 2 + 2 * mu * Potential(rho) + l * (l + 1) / (rho ** 2)) * u
        return [dudr, dvdr]

    init = [rhos[0], 1]

    def ddxToint(rhos, y):
        return ddx(y, rhos, mu, potential, l, pin)

    State = scipy.integrate.solve_ivp(ddxToint, (rhos[0], rhos[-1]), init, t_eval=rhos, method=int_type)
    Normalization = np.sqrt(State.y[0] ** 2 + (State.y[1] / pin) ** 2)
    #return (np.sqrt(2 / np.pi) * State.y[0] / Normalization[-1], np.sqrt(2 / np.pi) * State.y[1] / Normalization[-1])
    return (State.y[0] / Normalization[-1], State.y[1] / Normalization[-1])

def GetPhaseShift(rhos, p, l, mu, potential=potentials.Silvera_Triplet, how_to_int='Radau'):

    wf=np.array(Wave_Function(rhos,p, l, mu, potential, how_to_int))
    State = wf[0]
    dState_dx = wf[1]

    Big_delta_l = (rhos * dState_dx - State) / (rhos * State)
    jl_ka = spherical_jn(l, p * rhos)
    jl_prime_ka = spherical_jn(l, p * rhos, derivative=True)
    nl_ka = spherical_yn(l, p * rhos)
    nl_prime_ka = spherical_yn(l, p * rhos, derivative=True)
    
    deltas = np.arctan((p*jl_prime_ka - Big_delta_l*jl_ka) / (p*nl_prime_ka - Big_delta_l * nl_ka))
    #deltas = np.arctan(p * State / dState_dx) - p * rhos
    return deltas

def GetScatteringLength(rhos, p, l, mu, potential=potentials.Silvera_Triplet, how_to_int='Radau'):
    return -np.tan(GetPhaseShift(rhos, p, l, mu, potential, how_to_int)) / p

def GetCrossSection(rhos, p, l, mu, potential=potentials.Silvera_Triplet, how_to_int='Radau'):
    return (8 * np.pi / p**2) * (2*l + 1) * np.sin(GetPhaseShift(rhos, p, l, mu, potential, how_to_int)[-1])**2
