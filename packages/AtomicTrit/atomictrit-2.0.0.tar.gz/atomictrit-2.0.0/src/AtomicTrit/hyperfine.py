# ================================================================================
# this implements the Breit-Rabi calculation for the hyperfine levels of T and H.
# ================================================================================

import numpy as np
from AtomicTrit.constants import *


def GetHyperFineLevels(B_Values, pm, mf, consts=HydrogenConstants, gL=1,  L=0, S=0.5, I=0.5, J=0.5):

    muN = mue * meeV / (consts.m * DaltonInEV)  # magnetic moment of nucleus

    gJ = gL * (J * (J + 1) + L * (L + 1) - S * (S + 1)) / (2 * J * (J + 1)) + ge * (
                J * (J + 1) - L * (L + 1) + S * (S + 1)) / (2 * J * (J + 1))

    x = B_Values * (gJ * mue - consts.gI * muN) / (h * consts.delW)
    Term1 = -h * consts.delW / (2 * (2 * I + 1)) * np.ones_like(B_Values)
    Term2 = muN * consts.gI * mf * B_Values

    if (abs(mf) == abs(I + .5)):
        sgn = mf / (I + .5)
        Term3 = h * consts.delW / 2 * (1 + sgn * x)
    else:
        Term3 = pm * h * consts.delW / 2 * np.sqrt(1 + 2 * mf * x / (I + .5) + x ** 2)

    delE = (Term1 + Term2 + Term3) / h

    return delE * h * J2eV


def AllHFLevels(B_values, consts=HydrogenConstants):
    delEs = []
    for pm in [-1, 1]:
        F = .5 + pm / 2
        for mF in np.arange(-F, F + 1, 1):
            delEs.append(GetHyperFineLevels(B_values,pm, mF, consts))
    delEs = np.array(delEs)
    delEs = np.sort(delEs, axis=0)
    delEDict = {}
    for i in range(0, 4):
        letter = chr(97 + i)
        delEDict[letter] = delEs[i]
    return delEDict

def Theta(delW,B,gamN):
    return(0.5*np.arctan(delW/(2*B*(game+gamN))))

