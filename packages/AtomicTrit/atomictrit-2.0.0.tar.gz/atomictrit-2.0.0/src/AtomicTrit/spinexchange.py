# ================================================================================
# this contains the important functions for calculating spin exchange loss rates
# ================================================================================


from AtomicTrit import elastic
from AtomicTrit import dipolelosses
from AtomicTrit import hyperfine
from AtomicTrit import constants
from AtomicTrit import spinbasis
from AtomicTrit import potentials
import numpy as np

SpinExChannels=[]
SpinExChannels.append({'alpha':'c','beta':'c','alphaprime':'a','betaprime':'a'})
SpinExChannels.append({'alpha':'c','beta':'c','alphaprime':'a','betaprime':'c'})
SpinExChannels.append({'alpha':'c','beta':'c','alphaprime':'b','betaprime':'d'})


def GetSpatialPart(channel=SpinExChannels[0], B_value=1e-5, consts=constants.HydrogenConstants, Temperature=5e-4, triplet_potential=potentials.Silvera_Triplet,singlet_potential=potentials.Kolos_Singlet2_VDW,rhos=np.linspace(1e-9,0.75,2000),l=0,how_to_int='Radau'):
    HFLevels = hyperfine.AllHFLevels(B_value, consts)

    aHf =  HFLevels[channel['alpha']]
    bHf =  HFLevels[channel['beta']]
    apHf = HFLevels[channel['alphaprime']]
    bpHf = HFLevels[channel['betaprime']]

    Pin  = dipolelosses.p_of_temp(consts.mu, Temperature)
    Pout = dipolelosses.pprime(Pin, aHf, bHf, apHf, bpHf, consts.mu)
    Pabs = dipolelosses.p_abs(consts.mu, Pin, aHf, bHf, apHf, bpHf)

    const = np.pi**2 / (2*consts.mu * Pin)*constants.NatUnits_cm3sm1
    tdeltaaa = elastic.GetPhaseShift(rhos, Pabs, l, consts.mu, triplet_potential, how_to_int)[-1]
    sdeltaaa = elastic.GetPhaseShift(rhos, Pabs, l, consts.mu, singlet_potential, how_to_int)[-1]

    SpatialPart = (2*l+1)*(const * (Pin * Pout / Pabs ** 2) **(2*l+1)* (np.sin(tdeltaaa - sdeltaaa) ** 2))

    return (SpatialPart)


def GetSpinPart(channel=SpinExChannels[0], B_value=1e-5, consts=constants.HydrogenConstants):

    th = hyperfine.Theta(2*consts.delW, B_value, consts.gam)
    trans = spinbasis.TransformMatrix(spinbasis.TripletProj - spinbasis.SingletProj, spinbasis.Rotator)
    El = (spinbasis.GetElement(trans, channel['alpha'], channel['beta'], 1, channel['alphaprime'], channel['betaprime'], 1)) ** 2
    SpinPart = El.subs(spinbasis.sr2, np.sqrt(2)).subs(spinbasis.sr3, np.sqrt(3)).subs(spinbasis.c, np.cos(th)).subs(spinbasis.s, np.sin(th))

    return (SpinPart)


def GetGFactor(channel=SpinExChannels[0],  B_value=1e-5, consts=constants.HydrogenConstants, Temperature=5e4, triplet_potential=potentials.Silvera_Triplet,singlet_potential=potentials.Kolos_Singlet2_VDW,rhos=np.linspace(1e-9,0.75,20000),l=0,how_to_int='Radau'):

    SpinPart    = GetSpinPart(    channel, B_value, consts)
    SpatialPart = GetSpatialPart( channel, B_value, consts, Temperature, triplet_potential, singlet_potential, rhos,l, how_to_int)

    return (SpinPart*SpatialPart)

def GetSummedGFactor( channel=SpinExChannels[0],  B_value=1e-5, consts=constants.HydrogenConstants, Temperature=5e4, triplet_potential=potentials.Silvera_Triplet, singlet_potential=potentials.Jamieson_Singlet_VDW, PWaves= [0,2,4,6],  rhos=np.linspace(1e-9,0.75,2000)):
    G=0
    for pi in range(0,len(PWaves)):
        G+=GetGFactor(channel,  B_value, consts, Temperature, triplet_potential,singlet_potential, rhos,PWaves[pi])
    return G
