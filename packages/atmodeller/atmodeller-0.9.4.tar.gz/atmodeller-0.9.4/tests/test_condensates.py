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
"""Tests for C-H-O systems with stable or unstable condensates"""

import logging

import numpy as np
from jaxtyping import ArrayLike

from atmodeller import debug_logger
from atmodeller.classes import InteriorAtmosphere
from atmodeller.containers import ConstantFugacityConstraint, Planet, Species, SpeciesCollection
from atmodeller.interfaces import ActivityProtocol, FugacityConstraintProtocol
from atmodeller.output import Output
from atmodeller.thermodata import IronWustiteBuffer
from atmodeller.thermodata.core import CondensateActivity
from atmodeller.utilities import earth_oceans_to_hydrogen_mass

logger: logging.Logger = debug_logger()
logger.setLevel(logging.WARNING)

RTOL: float = 1.0e-8
"""Relative tolerance"""
ATOL: float = 1.0e-8
"""Absolute tolerance"""
TOLERANCE: float = 5.0e-2
"""Tolerance of log output to satisfy comparison with FactSage and FastChem"""

species: SpeciesCollection = SpeciesCollection.create(
    ("H2_g", "H2O_g", "CO_g", "CO2_g", "CH4_g", "O2_g", "C_cr")
)
CHO_system: InteriorAtmosphere = InteriorAtmosphere(species)


def test_graphite_stable(helper) -> None:
    """Tests graphite stable with around 50% condensed C mass fraction"""

    planet: Planet = Planet(surface_temperature=873)
    fugacity_constraints: dict[str, FugacityConstraintProtocol] = {
        "O2_g": IronWustiteBuffer(np.nan)
    }
    oceans: ArrayLike = 1
    h_kg: ArrayLike = earth_oceans_to_hydrogen_mass(oceans)
    c_kg: ArrayLike = 5 * h_kg
    o_kg: ArrayLike = 2.73159e19
    mass_constraints = {"C": c_kg, "H": h_kg, "O": o_kg}

    CHO_system.solve(
        planet=planet, fugacity_constraints=fugacity_constraints, mass_constraints=mass_constraints
    )
    output: Output = CHO_system.output
    solution: dict[str, ArrayLike] = output.quick_look()

    factsage_result: dict[str, float] = {
        "O2_g": 1.27e-25,
        "H2_g": 14.564,
        "CO_g": 0.07276,
        "H2O_g": 4.527,
        "CO2_g": 0.061195,
        "CH4_g": 96.74,
        "C_cr_activity": 1.0,
        "mass_C_cr": 3.54162e20,
    }

    assert helper.isclose(solution, factsage_result, log=True, rtol=TOLERANCE, atol=TOLERANCE)


def test_graphite_unstable(helper) -> None:
    """Tests C-H-O system at IW+0.5 with graphite unstable

    Similar to :cite:p:`BHS22{Table E, row 2}`
    """

    planet: Planet = Planet(surface_temperature=1400)
    fugacity_constraints: dict[str, FugacityConstraintProtocol] = {"O2_g": IronWustiteBuffer(0.5)}
    oceans: ArrayLike = 3
    h_kg: ArrayLike = earth_oceans_to_hydrogen_mass(oceans)
    c_kg: ArrayLike = 1 * h_kg
    mass_constraints = {"C": c_kg, "H": h_kg}

    CHO_system.solve(
        planet=planet, fugacity_constraints=fugacity_constraints, mass_constraints=mass_constraints
    )
    output: Output = CHO_system.output
    solution: dict[str, ArrayLike] = output.quick_look()

    factsage_result: dict[str, float] = {
        "O2_g": 4.11e-13,
        "H2_g": 236.98,
        "CO_g": 46.42,
        "H2O_g": 337.16,
        "CO2_g": 30.88,
        "CH4_g": 28.66,
        "C_cr_activity": 0.12202,
        "mass_C_cr": 0.0,
    }

    assert helper.isclose(solution, factsage_result, log=True, rtol=TOLERANCE, atol=TOLERANCE)


def test_water_stable(helper) -> None:
    """Condensed water at 10 bar"""

    species: SpeciesCollection = SpeciesCollection.create(("H2_g", "H2O_g", "O2_g", "H2O_l"))
    planet: Planet = Planet(surface_temperature=411.75)
    interior_atmosphere: InteriorAtmosphere = InteriorAtmosphere(species)

    oceans: float = 1
    h_kg: ArrayLike = earth_oceans_to_hydrogen_mass(oceans)
    o_kg: float = 1.14375e21
    mass_constraints = {"H": h_kg, "O": o_kg}

    interior_atmosphere.solve(planet=planet, mass_constraints=mass_constraints)
    output: Output = interior_atmosphere.output
    solution: dict[str, ArrayLike] = output.quick_look()

    factsage_result: dict[str, float] = {
        "H2O_g": 3.3596,
        "H2_g": 6.5604,
        "O2_g": 5.6433e-58,
        "H2O_l_activity": 1.0,
        "mass_H2O_l": 1.247201e21,
    }

    assert helper.isclose(solution, factsage_result, log=True, rtol=TOLERANCE, atol=TOLERANCE)


def test_graphite_water_stable(helper) -> None:
    """Tests C and water in equilibrium at 430 K and 10 bar"""

    species: SpeciesCollection = SpeciesCollection.create(
        ("H2O_g", "H2_g", "O2_g", "CO_g", "CO2_g", "CH4_g", "H2O_l", "C_cr")
    )
    planet: Planet = Planet(surface_temperature=430)
    interior_atmosphere: InteriorAtmosphere = InteriorAtmosphere(species)

    h_kg: float = 3.10e20
    c_kg: float = 1.08e20
    o_kg: float = 2.48298883581636e21
    mass_constraints = {"C": c_kg, "H": h_kg, "O": o_kg}

    interior_atmosphere.solve(planet=planet, mass_constraints=mass_constraints)
    output: Output = interior_atmosphere.output
    solution: dict[str, ArrayLike] = output.quick_look()

    factsage_result: dict[str, float] = {
        "CH4_g": 0.3241,
        "CO2_g": 4.3064,
        "CO_g": 2.77e-6,
        "C_cr_activity": 1.0,
        "H2O_g": 5.3672,
        "H2O_l_activity": 1.0,
        "H2_g": 0.0023,
        "O2_g": 4.74e-48,
        "mass_C_cr": 8.75101e19,
        "mass_H2O_l": 2.74821e21,
    }

    assert helper.isclose(solution, factsage_result, log=True, rtol=TOLERANCE, atol=TOLERANCE)


def test_impose_stable(helper) -> None:
    """Tests a user-imposed stable condensate

    In general, it is not guaranteed that a system under consideration has a stable condensate, and
    so for most cases the abundance of a condensate should be solved for along with its stability.
    """

    # To enforce condensate stability we must set solve_for_stability to False
    C_cr: Species = Species.create_condensed("C", solve_for_stability=False)
    H2_g: Species = Species.create_gas("H2")
    N2_g: Species = Species.create_gas("N2")
    CHN_g: Species = Species.create_gas("CHN")
    Ar_g: Species = Species.create_gas("Ar")

    species: SpeciesCollection = SpeciesCollection((C_cr, H2_g, N2_g, CHN_g, Ar_g))

    # We still specify a planet, even though the only parameter of relevance is the temperature
    # Melt fraction is set to zero for completeness, but again is irrelevant without solubility.
    planet: Planet = Planet(surface_temperature=1500, mantle_melt_fraction=0)
    interior_atmosphere: InteriorAtmosphere = InteriorAtmosphere(species)

    # Only specify fugacity constraints
    fugacity_constraints: dict[str, FugacityConstraintProtocol] = {
        # Since solve_for_stability is False the activity is imposed, which counts as a constraint
        # and does not need to be re-specified here.
        "H2_g": ConstantFugacityConstraint(0.1),
        "N2_g": ConstantFugacityConstraint(0.2),
        "Ar_g": ConstantFugacityConstraint(0.9),
    }

    interior_atmosphere.solve(planet=planet, fugacity_constraints=fugacity_constraints)
    output: Output = interior_atmosphere.output
    solution: dict[str, ArrayLike] = output.quick_look()

    # TODO: Swap for a like-for-like comparison with FactSage?
    target_result: dict[str, float] = {
        "C_cr_activity": 1.0,
        "H2_g": 0.1,
        "N2_g": 0.2,
        "Ar_g": 0.9,
        "CHN_g": 0.000174719425093,
    }

    assert helper.isclose(solution, target_result, rtol=RTOL, atol=ATOL)


def test_impose_stable_activity(helper) -> None:
    """Tests a user-imposed stable condensate with a non-unity activity

    In general, it is not guaranteed that a system under consideration has a stable condensate, and
    so for most cases the abundance of a condensate should be solved for along with its stability.
    """

    # To enforce condensate stability we must set solve_for_stability to False
    # Impose a non-unity activity for C(cr)
    activity: ActivityProtocol = CondensateActivity(0.9)
    C_cr: Species = Species.create_condensed("C", activity=activity, solve_for_stability=False)
    H2_g: Species = Species.create_gas("H2")
    N2_g: Species = Species.create_gas("N2")
    CHN_g: Species = Species.create_gas("CHN")
    Ar_g: Species = Species.create_gas("Ar")

    species: SpeciesCollection = SpeciesCollection((C_cr, H2_g, N2_g, CHN_g, Ar_g))

    # We still specify a planet, even though the only parameter of relevance is the temperature
    # Melt fraction is set to zero for completeness, but again is irrelevant without solubility.
    planet: Planet = Planet(surface_temperature=1500, mantle_melt_fraction=0)
    interior_atmosphere: InteriorAtmosphere = InteriorAtmosphere(species)

    # Only specify fugacity constraints
    fugacity_constraints: dict[str, FugacityConstraintProtocol] = {
        # Since solve_for_stability is False the activity is imposed, which counts as a constraint
        # and does not need to be re-specified here.
        "H2_g": ConstantFugacityConstraint(0.1),
        "N2_g": ConstantFugacityConstraint(0.2),
        "Ar_g": ConstantFugacityConstraint(0.9),
    }

    interior_atmosphere.solve(planet=planet, fugacity_constraints=fugacity_constraints)
    output: Output = interior_atmosphere.output
    solution: dict[str, ArrayLike] = output.quick_look()

    # TODO: Swap for a like-for-like comparison with FactSage?
    target_result: dict[str, float] = {
        "C_cr_activity": 0.9,
        "H2_g": 0.1,
        "N2_g": 0.2,
        "Ar_g": 0.9,
        "CHN_g": 0.000157247482584,
    }

    assert helper.isclose(solution, target_result, rtol=RTOL, atol=ATOL)


def test_impose_stable_pressure(helper) -> None:
    """Tests a user-imposed stable condensate with a total pressure constraint

    In general, it is not guaranteed that a system under consideration has a stable condensate, and
    so for most cases the abundance of a condensate should be solved for along with its stability.
    """

    # To enforce condensate stability we must set solve_for_stability to False
    C_cr: Species = Species.create_condensed("C", solve_for_stability=False)
    H2_g: Species = Species.create_gas("H2")
    N2_g: Species = Species.create_gas("N2")
    CHN_g: Species = Species.create_gas("CHN")
    Ar_g: Species = Species.create_gas("Ar")

    species: SpeciesCollection = SpeciesCollection((C_cr, H2_g, N2_g, CHN_g, Ar_g))

    planet: Planet = Planet(surface_temperature=1500, mantle_melt_fraction=0)
    interior_atmosphere: InteriorAtmosphere = InteriorAtmosphere(species)

    # Specify fugacity constraints for some species
    fugacity_constraints: dict[str, FugacityConstraintProtocol] = {
        # Since solve_for_stability is False the activity is imposed, which counts as a constraint
        # and does not need to be re-specified here.
        "H2_g": ConstantFugacityConstraint(0.1),
        "N2_g": ConstantFugacityConstraint(0.2),
    }
    # Specify the total pressure of the system
    total_pressure_constraint: ArrayLike = 1

    interior_atmosphere.solve(
        planet=planet,
        fugacity_constraints=fugacity_constraints,
        total_pressure_constraint=total_pressure_constraint,
    )
    output: Output = interior_atmosphere.output
    solution: dict[str, ArrayLike] = output.quick_look()

    # TODO: Swap for a comparison with FactSage?
    target_result: dict[str, float] = {
        "C_cr_activity": 1.0,
        "H2_g": 0.1,
        "N2_g": 0.2,
        "Ar_g": 0.699825280574906,
        "CHN_g": 0.000174719425093,
    }

    assert helper.isclose(solution, target_result, rtol=RTOL, atol=ATOL)
