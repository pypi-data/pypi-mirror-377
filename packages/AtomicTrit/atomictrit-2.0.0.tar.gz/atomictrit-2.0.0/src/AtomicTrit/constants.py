# ================================================================================
#  A compilation of constants that are used throughout the code.
# ================================================================================

import numpy as np

# Fundamental constants
h              = 6.6260715e-34          # Planck constant in m^2 kg / s
kb             = 1.380649e-23           # Boltzmann constant in JK^-1
ge             = 2.00231930436092       # Electron g-factor
meeV           = 5.1099895069e5         # mass of electron
mue            = 9.2847646917e-24       # magnetic moment of electron
game           = -28024.9513861e6       # electron gamma factor in Hz T^-1
finestructure  = 7.2973525643e-3
mu_dip_couple  = np.sqrt(4 * np.pi * finestructure) / (2 * meeV)
amu            = 1.672621925e-27

# Unit conversions
BohrInAng      = .529177210544
HartreeInEV    = 27.211386245981
hcInEVAngstrom = 1973.2698044
BohrInEV       = BohrInAng/hcInEVAngstrom
cmm1_in_eV     = 1.23984198E-4
J2eV           = 6.2415090744e18
K2eV           = kb*J2eV
DaltonInEV     = 931.49410372*1e6
NatUnits_cm3sm1= 11.6


# H and T constants
class TritiumConstants:
    delW = 1.516701470775e9      # Hyperfine splitting of hydrogen in Hz
    gI   = 5.957924930           # Tritium nuclear g-factor
    m    = 3.01604928            # Mass of tritium in Dalton
    mu   = m * DaltonInEV / 2    # Reduced mass of T-T
    gam  = 45.41483817 * 1e6     # Gyromagnetic constant for T In Hz T^-1
    nm   = 2808.92113668e6       # nuclear mass of tritium

class HydrogenConstants:
    delW = 1.4204057517667e9     # Hyperfine splitting of hydrogen in Hz
    gI   = 5.585694706           # Hydrogen nuclear g-factor
    m    = 1.00727646657894      # Mass of hydrogen in Dalton
    mu   = m*DaltonInEV/2        # Reduced mass of H-H
    gam  = 42.56385437*1e6       # Gyromagnetic constant for H In Hz T^-1
    nm   = 938.27208942e6        #mass of proton




# Uncertainties


# Fundamental constants uncertainty
uge            = .00000000000036
umeeV          = .00000000016e6
umue           = .0000000029e-24
ugame          = .0000087e6
ufinestructure = .0000000011e-3
umu_dip_couple = mu_dip_couple * (ufinestructure/finestructure + umeeV/meeV)

#Unit conversions uncertainty
uBohrInAng = .00000000082
uHartreeInEV = .00000000030

# H and T constants uncertainties
udelWH = .0000000000010e9
udelWT = .0000000000007e9
ugIH = .000000056
ugIT = .000000012
umH = .0000000000083
umT = .00000000010












