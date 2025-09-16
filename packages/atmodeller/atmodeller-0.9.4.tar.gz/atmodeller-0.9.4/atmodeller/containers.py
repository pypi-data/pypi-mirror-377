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
"""Containers"""

import logging
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import asdict
from typing import Any, Literal, Optional

import equinox as eqx
import jax.numpy as jnp
import lineax as lx
import numpy as np
import optimistix as optx
from jax import lax
from jaxmod.constants import AVOGADRO, GRAVITATIONAL_CONSTANT
from jaxmod.units import unit_conversion
from jaxmod.utils import as_j64, get_batch_size, partial_rref, to_hashable
from jaxtyping import Array, ArrayLike, Bool, Float, Float64
from lineax import AbstractLinearSolver
from molmass import Formula

from atmodeller.constants import (
    GAS_STATE,
    LOG_NUMBER_DENSITY_LOWER,
    LOG_NUMBER_DENSITY_UPPER,
    LOG_STABILITY_LOWER,
    LOG_STABILITY_UPPER,
    TAU,
)
from atmodeller.eos.core import IdealGas
from atmodeller.interfaces import ActivityProtocol, FugacityConstraintProtocol, SolubilityProtocol
from atmodeller.solubility.library import NoSolubility
from atmodeller.thermodata import (
    CondensateActivity,
    IndividualSpeciesData,
    thermodynamic_data_source,
)
from atmodeller.type_aliases import NpArray, NpBool, NpFloat, NpInt, OptxSolver
from atmodeller.utilities import get_log_number_density_from_log_pressure

logger: logging.Logger = logging.getLogger(__name__)


class Species(eqx.Module):
    """Species

    Args:
        data: Individual species data
        activity: Activity
        solubility: Solubility
        solve_for_stability: Solve for stability
        number_solution: Number of solution quantities
    """

    data: IndividualSpeciesData
    activity: ActivityProtocol
    solubility: SolubilityProtocol
    solve_for_stability: bool
    number_solution: int

    @property
    def name(self) -> str:
        """Unique name by combining Hill notation and state"""
        return self.data.name

    @classmethod
    def create_condensed(
        cls,
        formula: str,
        *,
        state: str = "cr",
        activity: ActivityProtocol = CondensateActivity(),
        solve_for_stability: bool = True,
    ) -> "Species":
        """Creates a condensate

        Args:
            formula: Formula
            state: State of aggregation as defined by JANAF. Defaults to ``cr``.
            activity: Activity. Defaults to ``1.0`` (unity activity).
            solve_for_stability. Solve for stability. Defaults to ``True``.

        Returns:
            A condensed species
        """
        species_data: IndividualSpeciesData = IndividualSpeciesData(formula, state)

        # For a condensate, either both a number density and stability are solved for, or
        # alternatively stability can be enforced in which case the number density is irrelevant
        # and there is nothing to solve for.
        # TODO: Theoretically the scenario could be accommodated whereby a user enforces stability
        # and wants to solve for the number density. But this could give rise to strange
        # inconsistencies so this scenario is not accommodated.
        number_solution: int = 2 if solve_for_stability else 0

        return cls(species_data, activity, NoSolubility(), solve_for_stability, number_solution)

    @classmethod
    def create_gas(
        cls,
        formula: str,
        *,
        state: str = GAS_STATE,
        activity: ActivityProtocol = IdealGas(),
        solubility: SolubilityProtocol = NoSolubility(),
        solve_for_stability: bool = False,
    ) -> "Species":
        """Creates a gas species

        Args:
            formula: Formula
            state: State of aggregation as defined by JANAF. Defaults to
                :const:`~atmodeller.constants.GAS_STATE`
            activity: Activity. Defaults to an ideal gas.
            solubility: Solubility. Defaults to no solubility.
            solve_for_stability. Solve for stability. Defaults to ``False``.

        Returns:
            A gas species
        """
        species_data: IndividualSpeciesData = IndividualSpeciesData(formula, state)

        # For a gas, a number density is always solved for, and stability can be if desired
        number_solution: int = 2 if solve_for_stability else 1

        return cls(species_data, activity, solubility, solve_for_stability, number_solution)

    def __str__(self) -> str:
        return f"{self.name}: {self.activity.__class__.__name__}, {self.solubility.__class__.__name__}"


class SpeciesCollection(eqx.Module):
    """A collection of species

    Args:
        species: An iterable of species
    """

    data: tuple[Species, ...]
    """Species data"""
    active_stability: NpBool
    """Active stability mask"""
    gas_species_mask: NpBool
    """Gas species mask"""
    species_names: tuple[str, ...]
    """Unique names of all species"""
    gas_species_names: tuple[str, ...]
    """Gas species names"""
    condensed_species_names: tuple[str, ...]
    """Condensed species names"""
    molar_masses: NpFloat
    """Molar masses"""
    unique_elements: tuple[str, ...]
    """Unique elements in species in alphabetical order"""
    diatomic_oxygen_index: int
    """Index of diatomic oxygen"""
    number_reactions: int
    """Number of reactions"""
    formula_matrix: NpInt
    """Formula matrix"""
    reaction_matrix: NpFloat
    """Reaction matrix"""
    active_reactions: NpBool
    """Active reactions"""
    number_solution: int
    """Number of solution quantities that cannot depend on traced quantities"""

    def __init__(self, data: Iterable[Species]):
        self.data = tuple(data)

        # Ensure number_solution is static
        self.number_solution = sum([species.number_solution for species in self.data])

        active_stability: list[bool] = [species.solve_for_stability for species in self.data]

        self.active_stability = np.array(active_stability)

        self.gas_species_mask = np.array(
            [species.data.state == GAS_STATE for species in self.data], dtype=bool
        )
        self.species_names = tuple([species_.name for species_ in self.data])
        self.gas_species_names = tuple(
            [species.name for species in self.data if species.data.state == GAS_STATE]
        )
        self.condensed_species_names = tuple(
            [species.name for species in self.data if species.data.state != GAS_STATE]
        )
        self.molar_masses = np.array([species_.data.molar_mass for species_ in self.data])

        # Unique elements
        elements: list[str] = []
        for species_ in self.data:
            elements.extend(species_.data.elements)
        unique_elements: list[str] = list(set(elements))
        self.unique_elements = tuple(sorted(unique_elements))

        self.diatomic_oxygen_index = self.get_diatomic_oxygen_index()

        # Reactions
        self.number_reactions = max(0, self.number_species - len(self.unique_elements))
        self.formula_matrix = self.get_formula_matrix()
        self.reaction_matrix = self.get_reaction_matrix()
        self.active_reactions = np.ones(self.number_reactions, dtype=bool)

    @classmethod
    def create(cls, species_names: Iterable[str]) -> "SpeciesCollection":
        """Creates an instance

        Args:
            species_names: A list or tuple of species names

        Returns
            An instance
        """
        species_list: list[Species] = []
        for species_ in species_names:
            formula, state = species_.split("_")
            hill_formula = Formula(formula).formula
            if state == GAS_STATE:
                species_to_add: Species = Species.create_gas(hill_formula, state=state)
            else:
                species_to_add: Species = Species.create_condensed(hill_formula, state=state)
            species_list.append(species_to_add)

        return cls(species_list)

    @classmethod
    def available_species(cls) -> tuple[str, ...]:
        return thermodynamic_data_source.available_species()

    @property
    def gas_only(self) -> bool:
        """Checks if a gas-only network"""
        return len(self.data) == len(self.gas_species_mask)

    @property
    def number_species(self) -> int:
        """Number of species"""
        return len(self.data)

    def get_diatomic_oxygen_index(self) -> int:
        """Gets the species index corresponding to diatomic oxygen.

        Returns:
            Index of diatomic oxygen, or the first index if diatomic oxygen is not in the species
        """
        for nn, species_ in enumerate(self.data):
            if species_.data.hill_formula == "O2":
                # logger.debug("Found O2 at index = %d", nn)
                return nn

        # FIXME: Bad practice to return the first index because it could be wrong and therefore
        # give rise to spurious results, but an index must be passed to evaluate the species
        # solubility that may depend on fO2. Otherwise, a precheck could be be performed in which
        # all the solubility laws chosen by the user are checked to see if they depend on fO2. And
        # if so, and fO2 is not included in the model, an error is raised.
        return 0

    def get_formula_matrix(self) -> NpInt:
        """Gets the formula matrix.

        Elements are given in rows and species in columns following the convention in
        :cite:t:`LKS17`.

        Returns:
            Formula matrix
        """
        formula_matrix: NpInt = np.zeros(
            (len(self.unique_elements), self.number_species), dtype=np.int_
        )

        for element_index, element in enumerate(self.unique_elements):
            for species_index, species_ in enumerate(self):
                count: int = 0
                try:
                    count = species_.data.composition[element][0]
                except KeyError:
                    count = 0
                formula_matrix[element_index, species_index] = count

        # logger.debug("formula_matrix = %s", formula_matrix)

        return formula_matrix

    def get_reaction_dictionary(self) -> dict[int, str]:
        """Gets reactions as a dictionary.

        Returns:
            Reactions as a dictionary
        """
        reaction_matrix: NpFloat = self.get_reaction_matrix()

        reactions: dict[int, str] = {}
        if reaction_matrix.size != 0:
            for reaction_index in range(reaction_matrix.shape[0]):
                reactants: str = ""
                products: str = ""
                for species_index, name in enumerate(self.species_names):
                    coeff: float = reaction_matrix[reaction_index, species_index].item()
                    if coeff != 0:
                        if coeff < 0:
                            reactants += f"{abs(coeff)} {name} + "
                        else:
                            products += f"{coeff} {name} + "

                reactants = reactants.rstrip(" + ")
                products = products.rstrip(" + ")
                reaction: str = f"{reactants} = {products}"
                reactions[reaction_index] = reaction

        return reactions

    def get_reaction_matrix(self) -> NpFloat:
        """Gets the reaction matrix.

        Returns:
            A matrix of linearly independent reactions or an empty array if no reactions
        """
        transpose_formula_matrix: NpInt = self.get_formula_matrix().T
        reaction_matrix: NpFloat = partial_rref(transpose_formula_matrix)
        # logger.debug("reaction_matrix = %s", reaction_matrix)

        return reaction_matrix

    def __getitem__(self, index: int) -> Species:
        return self.data[index]

    def __iter__(self) -> Iterator[Species]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __str__(self) -> str:
        return str(tuple(str(species) for species in self.data))


class Planet(eqx.Module):
    """Planet properties

    Default values are for a fully molten Earth.

    Note:
        All parameters are stored as JAX arrays (``jnp.ndarray``) rather than Python floats. This
        ensures that JAX sees a consistent type during transformations (e.g., ``jit``, ``grad``,
        ``vmap``), preventing unnecessary recompilation when values change. In JAX, switching
        between a Python float and an array for the same argument will trigger retracing or
        recompilation, so keeping everything as arrays avoids this overhead.

    Args:
        planet_mass: Mass of the planet in kg. Defaults to ``5.972e24`` kg (Earth).
        core_mass_fraction: Mass fraction of the iron core relative to the planetary mass. Defaults
            to ``0.3`` kg/kg (Earth).
        mantle_melt_fraction: Mass fraction of the mantle that is molten. Defaults to ``1.0`` kg/kg.
        surface_radius: Radius of the planetary surface in m. Defaults to ``6371000`` m (Earth).
        surface_temperature: Temperature of the planetary surface. Defaults to ``2000`` K.
    """

    planet_mass: Array = eqx.field(converter=as_j64, default=5.972e24)
    """Mass of the planet in kg"""
    core_mass_fraction: Array = eqx.field(converter=as_j64, default=0.295334691460966)
    """Mass fraction of the core relative to the planetary mass in kg/kg"""
    mantle_melt_fraction: Array = eqx.field(converter=as_j64, default=1.0)
    """Mass fraction of the molten mantle in kg/kg"""
    surface_radius: Array = eqx.field(converter=as_j64, default=6371000)
    """Radius of the surface in m"""
    surface_temperature: Array = eqx.field(converter=as_j64, default=2000)
    """Temperature of the surface in K"""

    @property
    def mantle_mass(self) -> Array:
        """Mantle mass"""
        return self.planet_mass * self.mantle_mass_fraction

    @property
    def mantle_mass_fraction(self) -> Array:
        """Mantle mass fraction"""
        return 1 - self.core_mass_fraction

    @property
    def mantle_melt_mass(self) -> Array:
        """Mass of the molten mantle"""
        return self.mantle_mass * self.mantle_melt_fraction

    @property
    def mantle_solid_mass(self) -> Array:
        """Mass of the solid mantle"""
        return self.mantle_mass * (1.0 - self.mantle_melt_fraction)

    @property
    def mass(self) -> Array:
        """Mass"""
        return self.mantle_mass

    @property
    def melt_mass(self) -> Array:
        """Mass of the melt"""
        return self.mantle_melt_mass

    @property
    def solid_mass(self) -> Array:
        """Mass of the solid"""
        return self.mantle_solid_mass

    @property
    def surface_area(self) -> Array:
        """Surface area"""
        return 4.0 * jnp.pi * jnp.square(self.surface_radius)

    @property
    def surface_gravity(self) -> Array:
        """Surface gravity"""
        return GRAVITATIONAL_CONSTANT * self.planet_mass / jnp.square(self.surface_radius)

    @property
    def temperature(self) -> Array:
        """Temperature"""
        return self.surface_temperature

    def asdict(self) -> dict[str, NpArray]:
        """Gets a dictionary of the values as NumPy arrays.

        Returns:
            A dictionary of the values
        """
        base_dict: dict[str, ArrayLike] = asdict(self)
        base_dict["mantle_mass"] = self.mass
        base_dict["mantle_melt_mass"] = self.melt_mass
        base_dict["mantle_solid_mass"] = self.solid_mass
        base_dict["surface_area"] = self.surface_area
        base_dict["surface_gravity"] = self.surface_gravity

        # Convert all values to NumPy arrays
        base_dict_np: dict[str, NpArray] = {k: np.asarray(v) for k, v in base_dict.items()}

        return base_dict_np


class ConstantFugacityConstraint(eqx.Module):
    """A constant fugacity constraint

    This must adhere to FugacityConstraintProtocol

    Args:
        fugacity: Fugacity. Defaults to ``np.nan``.
    """

    fugacity: Array = eqx.field(converter=as_j64, default=np.nan)
    """Fugacity"""

    def active(self) -> Bool[Array, "..."]:
        """Active fugacity constraint

        Returns:
            ``True`` if the fugacity constraint is active, otherwise ``False``
        """
        return ~jnp.isnan(self.fugacity)

    def log_fugacity(self, temperature: ArrayLike, pressure: ArrayLike) -> Float[Array, "..."]:
        del temperature
        del pressure

        return jnp.log(self.fugacity)


class FugacityConstraints(eqx.Module):
    """Fugacity constraints

    These are applied as constraints on the gas activity.

    Args:
        constraints: Fugacity constraints
        species: Species corresponding to the columns of ``constraints``
    """

    constraints: tuple[FugacityConstraintProtocol, ...]
    """Fugacity constraints"""
    species: tuple[str, ...]
    """Species corresponding to the entries of constraints"""

    @classmethod
    def create(
        cls,
        species: SpeciesCollection,
        fugacity_constraints: Optional[Mapping[str, FugacityConstraintProtocol]] = None,
    ) -> "FugacityConstraints":
        """Creates an instance

        Args:
            species: Species
            fugacity_constraints: Mapping of a species name and a fugacity constraint. Defaults to
                ``None``.

        Returns:
            An instance
        """
        fugacity_constraints_: Mapping[str, FugacityConstraintProtocol] = (
            fugacity_constraints if fugacity_constraints is not None else {}
        )

        # All unique species
        unique_species: tuple[str, ...] = species.species_names

        constraints: list[FugacityConstraintProtocol] = []

        for species_name in unique_species:
            if species_name in fugacity_constraints_:
                constraints.append(fugacity_constraints_[species_name])
            else:
                # NOTE: This is also applied to condensates, which is OK because it returns nans.
                # Hence for condensates nans means no imposed activity, and for gas species nans
                # means no imposed fugacity.
                constraints.append(ConstantFugacityConstraint())

        return cls(tuple(constraints), unique_species)

    def active(self) -> Array:
        """Active fugacity constraints

        Returns:
            Mask indicating whether fugacity constraints are active or not
        """
        mask_list: list[Array] = [constraint.active() for constraint in self.constraints]

        return jnp.array(mask_list)

    def asdict(self, temperature: ArrayLike, pressure: ArrayLike) -> dict[str, NpArray]:
        """Gets a dictionary of the evaluated fugacity constraints as NumPy Arrays

        Args:
            temperature: Temperature in K
            pressure: Pressure

        Returns:
            A dictionary of the evaluated fugacity constraints
        """
        log_fugacity_list: list[NpFloat] = []

        for constraint in self.constraints:
            log_fugacity: NpFloat = np.asarray(constraint.log_fugacity(temperature, pressure))
            log_fugacity_list.append(log_fugacity)

        out: dict[str, NpArray] = {
            # Subtle, but np.exp will collapse scalar array to 0-D, violating the type hint.
            f"{key}_fugacity": np.exp(np.atleast_1d(log_fugacity_list[idx]))
            for idx, key in enumerate(self.species)
            if not np.all(np.isnan(log_fugacity_list[idx]))
        }

        return out

    def log_fugacity(self, temperature: ArrayLike, pressure: ArrayLike) -> Array:
        """Log fugacity

        Args:
            temperature: Temperature in K
            pressure: Pressure

        Returns:
            Log fugacity
        """
        # NOTE: Must avoid the late-binding closure issue
        fugacity_funcs: list[Callable] = [
            to_hashable(constraint.log_fugacity) for constraint in self.constraints
        ]
        # jax.debug.print("fugacity_funcs = {out}", out=fugacity_funcs)

        # Temperature must be a float array to ensure branches have have identical types
        temperature = as_j64(temperature)

        def apply_fugacity(index: ArrayLike, temperature: ArrayLike, pressure: ArrayLike) -> Array:
            # jax.debug.print("index = {out}", out=index)
            return lax.switch(
                index,
                fugacity_funcs,
                temperature,
                pressure,
            )

        indices: Array = jnp.arange(len(self.constraints))
        vmap_fugacity: Callable = eqx.filter_vmap(apply_fugacity, in_axes=(0, None, None))
        log_fugacity: Array = vmap_fugacity(indices, temperature, pressure)
        # jax.debug.print("log_fugacity = {out}", out=log_fugacity)

        return log_fugacity

    def log_number_density(self, temperature: ArrayLike, pressure: ArrayLike) -> Array:
        """Log number density

        Args:
            temperature: Temperature in K
            pressure: Pressure

        Returns:
            Log number density
        """
        log_fugacity: Array = self.log_fugacity(temperature, pressure)
        log_number_density: Array = get_log_number_density_from_log_pressure(
            log_fugacity, temperature
        )

        return log_number_density


class TotalPressureConstraint(eqx.Module):
    """Total pressure constraint

    Args:
        log_pressure: Log total pressure
    """

    log_pressure: Float[Array, "..."] = eqx.field(converter=as_j64, default=np.nan)

    @classmethod
    def create(
        cls, total_pressure_constraint: Optional[ArrayLike] = None
    ) -> "TotalPressureConstraint":
        """Creates an instance

        Args:
            total_pressure_constraint. Defaults to ``None``.

        Returns:
            An instance
        """
        total_pressure_constraint_: ArrayLike = (
            total_pressure_constraint if total_pressure_constraint is not None else np.nan
        )

        return cls(np.log(total_pressure_constraint_))

    def active(self) -> Bool[Array, "..."]:
        """Active total pressure constraint

        Returns:
            Mask indicating whether the total pressure constraint is active or not
        """
        return ~jnp.isnan(jnp.atleast_1d(self.log_pressure))

    def asdict(self) -> dict[str, NpArray]:
        """Gets a dictionary of the total pressure constraint as a NumPy array

        Returns:
            A dictionary of the total pressure constraint
        """
        out: dict[str, NpArray] = {"total_pressure": np.asarray(np.exp(self.log_pressure))}

        return out

    def log_number_density(self, temperature: ArrayLike) -> Float[Array, "..."]:
        """Log number density

        Args:
            temperature: Temperature in K

        Returns:
            Log number density
        """
        log_number_density: Array = get_log_number_density_from_log_pressure(
            self.log_pressure, temperature
        )

        return log_number_density


class MassConstraints(eqx.Module):
    """Mass constraints of elements

    Args:
        log_abundance: Log number of atoms
        elements: Elements corresponding to the columns of ``log_abundance``
    """

    log_abundance: Float64[Array, "dim elements"] = eqx.field(converter=as_j64)
    elements: tuple[str, ...]

    @classmethod
    def create(
        cls,
        species: SpeciesCollection,
        mass_constraints: Optional[Mapping[str, ArrayLike]] = None,
    ) -> "MassConstraints":
        """Creates an instance

        Args:
            species: Species
            mass_constraints: Mapping of element name and mass constraint in kg. Defaults to
                ``None``.

        Returns:
            An instance
        """
        mass_constraints_: Mapping[str, ArrayLike] = (
            mass_constraints if mass_constraints is not None else {}
        )

        # All unique elements in alphabetical order
        unique_elements: tuple[str, ...] = species.unique_elements

        # Determine the maximum length of any array in mass_constraints_
        max_len: int = get_batch_size(mass_constraints_)

        # Initialise to all nans assuming that there are no mass constraints
        log_abundance: NpFloat = np.full((max_len, len(unique_elements)), np.nan, dtype=np.float64)

        # Populate mass constraints
        for nn, element in enumerate(unique_elements):
            if element in mass_constraints_.keys():
                molar_mass: ArrayLike = Formula(element).mass * unit_conversion.g_to_kg
                log_abundance_: ArrayLike = (
                    np.log(mass_constraints_[element]) + np.log(AVOGADRO) - np.log(molar_mass)
                )
                log_abundance[:, nn] = log_abundance_  # broadcasts scalar along that column

        # jax.debug.print("log_abundance = {out}", out=log_abundance)

        return cls(log_abundance, unique_elements)

    def asdict(self) -> dict[str, NpArray]:
        """Gets a dictionary of the values as NumPy arrays

        Returns:
            A dictionary of the values
        """
        abundance: NpArray = np.exp(self.log_abundance)
        out: dict[str, NpArray] = {
            f"{element}_number": abundance[:, idx]
            for idx, element in enumerate(self.elements)
            if not np.all(np.isnan(abundance[:, idx]))
        }

        return out

    def active(self) -> Bool[Array, "..."]:
        """Active mass constraints

        The array is squeezed to ensure it is consistently 1-D when possible. This avoids
        unnecessary recompilations when
        :attr:`~atmodeller.containers.MassConstraints.log_abundance` is sometimes batched and
        sometimes not.

        Returns:
            Mask indicating whether elemental mass constraints are active or not
        """
        return ~jnp.isnan(jnp.atleast_1d(self.log_abundance.squeeze()))

    def log_number_density(self, log_atmosphere_volume: ArrayLike) -> Float64[Array, "..."]:
        """Log number density

        The array is squeezed to ensure it is consistently 1-D when possible. This avoids
        unnecessary recompilations when
        :attr:`~atmodeller.containers.MassConstraints.log_abundance` is sometimes batched and
        sometimes not.

        Args:
            log_atmosphere_volume: Log volume of the atmosphere

        Returns:
            Log number density
        """
        log_number_density: Float64[Array, "..."] = (
            self.log_abundance.squeeze() - log_atmosphere_volume
        )

        return log_number_density


class SolverParameters(eqx.Module):
    """Solver parameters

    Args:
        solver: Solver. Defaults to ``optx.Newton``
        atol: Absolute tolerance. Defaults to ``1.0e-6``.
        rtol: Relative tolerance. Defaults to ``1.0e-6``.
        linear_solver: Linear solver. Defaults to ``AutoLinearSolver(well_posed=False)``.
        norm: Norm. Defaults to ``optx.rms_norm``.
        throw: How to report any failures. Defaults to ``False``.
        max_steps: The maximum number of steps the solver can take. Defaults to ``256``
        jac: Whether to use forward- or reverse-mode autodifferentiation to compute the Jacobian.
            Can be either ``fwd`` or ``bwd``. Defaults to ``fwd``.
        multistart: Number of multistarts. Defaults to ``10``.
        multistart_perturbation: Perturbation for multistart. Defaults to ``30``.
        tau: Tau factor for species stability. Defaults to :const:`~atmodeller.constants.TAU`.
    """

    solver: type[OptxSolver] = optx.Newton
    """Solver"""
    atol: float = 1.0e-6
    """Absolute tolerance"""
    rtol: float = 1.0e-6
    """Relative tolerance"""
    linear_solver: AbstractLinearSolver = lx.AutoLinearSolver(well_posed=None)
    """Linear solver
    
    https://docs.kidger.site/lineax/api/solvers/   
    """
    norm: Callable = optx.max_norm
    """Norm""" ""
    throw: bool = False
    """How to report any failures"""
    max_steps: int = 256
    """Maximum number of steps the solver can take"""
    jac: Literal["fwd", "bwd"] = "fwd"
    """Whether to use forward- or reverse-mode autodifferentiation to compute the Jacobian"""
    multistart: int = 10
    """Number of multistarts"""
    multistart_perturbation: float = 30.0
    """Perturbation for multistart"""
    tau: Array = eqx.field(converter=as_j64, default=TAU)  # NOTE: Must be an array to trace tau
    """Tau factor for species stability"""

    def get_solver_instance(self) -> OptxSolver:
        return self.solver(
            rtol=self.rtol,
            atol=self.atol,
            norm=self.norm,
            linear_solver=self.linear_solver,  # type: ignore because there is a parameter
            # For debugging LM solver. Not valid for all solvers (e.g. Newton)
            # verbose=frozenset({"step_size", "y", "loss", "accepted"}),
        )

    def get_options(self, number_species: int) -> dict[str, Any]:
        """Gets the solver options.

        Args:
            number_species: Number of species

        Returns:
            Solver options
        """
        options: dict[str, Any] = {
            "lower": self._get_lower_bound(number_species),
            "upper": self._get_upper_bound(number_species),
            "jac": self.jac,
        }

        return options

    def _get_lower_bound(self, number_species: int) -> Float[Array, " dim"]:
        """Gets the lower bound for truncating the solution during the solve.

        Args:
            number_species: Number of species

        Returns:
            Lower bound for truncating the solution during the solve
        """
        return self._get_hypercube_bound(
            number_species, LOG_NUMBER_DENSITY_LOWER, LOG_STABILITY_LOWER
        )

    def _get_upper_bound(self, number_species: int) -> Float[Array, " dim"]:
        """Gets the upper bound for truncating the solution during the solve.

        Args:
            number_species: Number of species

        Returns:
            Upper bound for truncating the solution during the solve
        """
        return self._get_hypercube_bound(
            number_species, LOG_NUMBER_DENSITY_UPPER, LOG_STABILITY_UPPER
        )

    def _get_hypercube_bound(
        self, number_species: int, log_number_density_bound: float, stability_bound: float
    ) -> Float[Array, " dim"]:
        """Gets the bound on the hypercube.

        Args:
            number_species: Number of species
            log_number_density_bound: Bound on the log number density
            stability_bound: Bound on the stability

        Returns:
            Bound on the hypercube that contains the root
        """
        bound: Array = jnp.concatenate(
            (
                log_number_density_bound * jnp.ones(number_species),
                stability_bound * jnp.ones(number_species),
            )
        )

        return bound


class Parameters(eqx.Module):
    """Parameters

    Args:
        species: Species
        planet: Planet
        fugacity_constraints: Fugacity constraints
        mass_constraints: Mass constraints
        total_pressure_constraint: Total pressure constraint
        solver_parameters: Solver parameters
        batch_size: Batch size. Defaults to ``1``.
    """

    species: SpeciesCollection
    """Species"""
    planet: Planet
    """Planet"""
    fugacity_constraints: FugacityConstraints
    """Fugacity constraints"""
    mass_constraints: MassConstraints
    """Mass constraints"""
    total_pressure_constraint: TotalPressureConstraint
    """Total pressure constraint"""
    solver_parameters: SolverParameters
    """Solver parameters"""
    batch_size: int = 1
    """Batch size"""

    @classmethod
    def create(
        cls,
        species: SpeciesCollection,
        planet: Optional[Planet] = None,
        fugacity_constraints: Optional[Mapping[str, FugacityConstraintProtocol]] = None,
        mass_constraints: Optional[Mapping[str, ArrayLike]] = None,
        total_pressure_constraint: Optional[ArrayLike] = None,
        solver_parameters: Optional[SolverParameters] = None,
    ):
        """Creates an instance

        Args:
            species: Species
            planet: Planet. Defaults to a new instance of ``Planet``.
            fugacity_constraints: Mapping of a species name and a fugacity constraint. Defaults to
                a new instance of ``FugacityConstraints``.
            mass_constraints: Mapping of element name and mass constraint in kg. Defaults to
                a new instance of ``MassConstraints``.
            total_pressure_constraint: Total pressure constraint. Defaults to a new instance of
                ``TotalPressureConstraint``.
            solver_parameters: Solver parameters. Defaults to a new instance of
                ``SolverParameters``.

        Returns:
            An instance
        """
        planet_: Planet = Planet() if planet is None else planet
        fugacity_constraints_: FugacityConstraints = FugacityConstraints.create(
            species, fugacity_constraints
        )
        mass_constraints_: MassConstraints = MassConstraints.create(species, mass_constraints)
        total_pressure_constraint_: TotalPressureConstraint = TotalPressureConstraint.create(
            total_pressure_constraint
        )

        # These pytrees only contain arrays intended for vectorisation (no hidden JAX/NumPy arrays
        # that should remain scalar)
        batch_size: int = get_batch_size(
            (planet, fugacity_constraints, mass_constraints, total_pressure_constraint_)
        )
        solver_parameters_: SolverParameters = (
            SolverParameters() if solver_parameters is None else solver_parameters
        )
        # Always broadcast tau so we can apply vmap to the solver once, even if some calculations
        # need to be repeated due to failures.
        tau_broadcasted: Float[Array, " batch"] = jnp.broadcast_to(
            solver_parameters_.tau, (batch_size,)
        )
        get_leaf: Callable = lambda t: t.tau  # noqa: E731
        solver_parameters_ = eqx.tree_at(get_leaf, solver_parameters_, tau_broadcasted)

        return cls(
            species,
            planet_,
            fugacity_constraints_,
            mass_constraints_,
            total_pressure_constraint_,
            solver_parameters_,
            batch_size,
        )
