#
# Copyright 2024 Dan J. Bower
#
# This file is part of Atmodeller.
#
# Atmodeller is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Atmodeller is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Atmodeller. If not,
# see <https://www.gnu.org/licenses/>.
#
"""Solubility laws for hydrogen species

For every law there should be a test in the test suite.
"""

import equinox as eqx
import jax.numpy as jnp
import numpy as np
from jaxmod.units import unit_conversion
from jaxmod.utils import as_j64
from jaxtyping import Array, ArrayLike

from atmodeller import override
from atmodeller.eos._chabrier import H2_chabrier21_bounded
from atmodeller.solubility.core import Solubility, SolubilityPowerLaw, SolubilityPowerLawLog10
from atmodeller.type_aliases import Scalar

H2_andesite_hirschmann12: Solubility = SolubilityPowerLawLog10(1.01058631, 0.60128868)
"""H2 in synthetic andesite :cite:p:`HWA12`

Log-scale linear fit to fH2 vs H2 concentration for andesite in :cite:t:`HWA12{Table 2}`.
Experiments conducted from 0.7-3 GPa at 1400 C.
"""

H2_basalt_hirschmann12: Solubility = SolubilityPowerLawLog10(1.10083602, 0.52413928)
"""H2 in synthetic basalt :cite:p:`HWA12`

Log-scale linear fit to fH2 vs. H2 concentration for basalt in :cite:t:`HWA12{Table 2}`.
Experiments conducted from 0.7-3 GPa, 1400 C.
"""

H2_silicic_melts_gaillard03: Solubility = SolubilityPowerLaw(0.163, 1.252)
"""Fe-H redox exchange in silicate glasses :cite:p:`GSM03`

Power law fit for fH2 vs. H2 (ppm-wt) from :cite:t:`GSM03{Table 4}` data. Experiments at
pressures from 0.02-70 bar, temperatures from 300-1000C.
"""

H2O_ano_dio_newcombe17: Solubility = SolubilityPowerLaw(727, 0.5)
"""H2O in anorthite-diopside-eutectic compositions :cite:p:`NBB17`

Power law from :cite:t:`NBB17{Figure 5(A)}` for anorthite-diopside glass. Experiments conducted
at 1 atm and 1350 C. Melts equilibrated in 1 atm furnace with H2/CO2 gas mixtures that spanned
fO2 from IW-3 to IW+4.8 and pH2/pH2O from 0.003-24.
"""

H2O_basalt_dixon95: Solubility = SolubilityPowerLaw(965, 0.5)
"""H2O in MORB liquids :cite:p:`DSH95`

Refitted data to a power law by Paolo Sossi (fitting :cite:t:`DSH95{Figure 4}`, TODO: CHECK).
Experiments conducted at 1200 C, 200-717 bars with pure H2O.
"""

H2O_basalt_mitchell17: Solubility = SolubilityPowerLaw(258.946, 0.669)
"""H2O in basaltic melt :cite:p:`MGO17`

Refitted the H2O wt. % vs. fH2O fitted line from :cite:t:`MGO17{Figure 8}` to a power-law.
Experiments conducted at 1200 C and 1000 MPa total pressure. This fit includes data from
their experiments and prior studies on H2O solubility in basaltic melt at 1200 C and P at or
below 600 MPa.
"""

H2O_lunar_glass_newcombe17: Solubility = SolubilityPowerLaw(683, 0.5)
"""H2O in lunar basalt :cite:p:`NBB17`

Power law from :cite:t:`NBB17{Figure 5(A)}` for Lunar glass. Experiments conducted at 1 atm and
1350 C. Melts equilibrated in 1-atm furnace with H2/CO2 gas mixtures that spanned fO2 from IW-3
to IW+4.8.
"""

H2O_peridotite_sossi23: Solubility = SolubilityPowerLaw(647, 0.5)
"""H2O in peridotite liquids :cite:p:`STB23`

Power law parameters in the abstract for peridotitic glasses. Experiments conducted at 2173 K
and 1 bar and range of fO2 from IW-1.9 to IW+6.0.
"""


class _H2_chachan18(Solubility):
    """H2 solubility :cite:p:`CS18`

    Args:
        f_calibration: Calibration fugacity
        T_calibration: Calibration temperature
        X_calibration: Mass fraction at calibration conditions
        T0: Arrhenius temperature factor in K, which expresses the repulsive interaction of the
            molecule with magma. Defaults to 4000 K, which is the middle of the range the authors
            explore (from 3000 K to 5000 K).
    """

    f_calibration: float = eqx.field(converter=float)
    """Calibration fugacity"""
    T_calibration: float = eqx.field(converter=float)
    """Calibration temperature"""
    X_calibration: float = eqx.field(converter=float)
    """Mass fraction at calibration conditions"""
    T0: float = eqx.field(converter=float)
    """Arrhenius temperature factor in K"""
    A: float = eqx.field(converter=float)
    """Constant factor"""

    def __init__(
        self,
        f_calibration: Scalar,
        T_calibration: Scalar,
        X_calibration: Scalar,
        T0: Scalar = 4000,
    ):
        self.f_calibration = f_calibration
        self.T_calibration = T_calibration
        self.X_calibration = X_calibration
        self.T0 = T0
        self.A = np.exp(
            (self.T0 / self.T_calibration) + np.log(self.X_calibration / self.f_calibration)
        )
        # jax.debug.print("A = ", self.A)

    @override
    def concentration(self, fugacity: ArrayLike, *, temperature: ArrayLike, **kwargs) -> Array:
        del kwargs
        mass_fraction: Array = jnp.exp(-self.T0 / temperature) * self.A * fugacity
        ppmw: Array = mass_fraction * unit_conversion.fraction_to_ppm

        return ppmw


H2_chachan18: Solubility = _H2_chachan18(
    f_calibration=1500, T_calibration=1673, X_calibration=0.001
)
"""H2 by combining theory and experiment :cite:p:`CS18`"""

# At 1 GPa in the presence of pure H2, the molecular H2 concentration is 0.19 wt.%"
# Need to convert pressure to H2 fugacity
# With Chabrier EOS, f_calibration = 23986.034649111516
# With Zhang and Duan EOS, f_calibration2 = 28421.194323648964
T_calibration: Scalar = 1673
P_calibration: Scalar = unit_conversion.GPa_to_bar
f_calibration: Array = H2_chabrier21_bounded.fugacity(as_j64(T_calibration), as_j64(P_calibration))
X_calibration: Scalar = 0.0019

H2_kite19: Solubility = _H2_chachan18(
    f_calibration=float(f_calibration),
    T_calibration=T_calibration,
    X_calibration=X_calibration,
)
"""H2 by combining theory and experiment :cite:p:`KFS19`."""
