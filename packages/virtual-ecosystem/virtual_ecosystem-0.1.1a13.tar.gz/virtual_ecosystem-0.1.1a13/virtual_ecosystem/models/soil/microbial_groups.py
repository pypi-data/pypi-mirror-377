"""The ``models.soil.microbial_groups`` module contains the classes needed to define
the different microbial functional groups used in the soil model.
"""  # noqa: D205

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from virtual_ecosystem.core.config import Config, ConfigurationError
from virtual_ecosystem.core.constants import CoreConsts
from virtual_ecosystem.core.constants_loader import load_constants
from virtual_ecosystem.core.logger import LOGGER


@dataclass(frozen=True)
class EnzymeConstants:
    """Container for the set of constants associated with a specific enzyme."""

    source: str
    """The microbial group which produces the enzyme."""

    substrate: str
    """The substrate which the enzyme acts upon."""

    maximum_rate: float
    """The maximum rate of the enzyme at the reference temperature [day^-1]."""

    half_saturation_constant: float
    """The half saturation constant for the enzyme at the reference temperature.

    Units of [kg C m^-3]."""

    activation_energy_rate: float
    """Activation energy for enzyme rate with temperature [J K^-1]."""

    activation_energy_saturation: float
    """Activation energy for enzyme saturation with temperature [J K^-1]."""

    # TODO - This should change to Kelvin when we change the default units to Kelvin
    reference_temperature: float
    """The reference temperature that enzyme rate and saturation were measured at [C].
    """

    turnover_rate: float
    """The turnover rate of the enzyme [day^-1]."""

    c_n_ratio: float
    """Ratio of carbon to nitrogen for the enzyme [unitless]."""

    c_p_ratio: float
    """Ratio of carbon to phosphorus for the enzyme [unitless]."""


@dataclass(frozen=True)
class MicrobialGroupConstants:
    """Container for the set of constants associated with a microbial functional group.

    This sets out the constants which must be defined for each microbial functional
    group.
    """

    name: str
    """The name of the microbial group functional type."""

    taxonomic_group: str
    """The high level taxonomic group that the microbial group belongs to."""

    max_uptake_rate_labile_C: float
    """Maximum rate at the reference temperature of labile carbon uptake [day^-1]."""

    activation_energy_uptake_rate: float
    """Activation energy for nutrient uptake [J K^-1]."""

    half_sat_labile_C_uptake: float
    """Half saturation constant for uptake of labile carbon (LMWC) [kg C m^-3]."""

    activation_energy_uptake_saturation: float
    """Activation energy for nutrient uptake saturation constants [J K^-1]."""

    max_uptake_rate_ammonium: float
    """Maximum possible rate for ammonium uptake [day^-1]."""

    half_sat_ammonium_uptake: float
    """Half saturation constant for uptake of ammonium [kg N m^-3]."""

    max_uptake_rate_nitrate: float
    """Maximum possible rate for nitrate uptake [day^-1]."""

    half_sat_nitrate_uptake: float
    """Half saturation constant for uptake of nitrate [kg N m^-3]."""

    max_uptake_rate_labile_p: float
    """Maximum possible rate for labile inorganic phosphorus uptake [day^-1]."""

    half_sat_labile_p_uptake: float
    """Half saturation constant for uptake of labile inorganic phosphorus [kg P m^-3].
    """

    turnover_rate: float
    """Microbial maintenance turnover rate at reference temperature [day^-1]."""

    activation_energy_turnover: float
    """Activation energy for microbial maintenance turnover rate [J K^-1]."""

    reference_temperature: float
    """The reference temperature that turnover and uptake rates were measured at [C].
    """

    c_n_ratio: float
    """Ratio of carbon to nitrogen in biomass [unitless]."""

    c_p_ratio: float
    """Ratio of carbon to phosphorus in biomass [unitless]."""

    enzyme_production: dict[str, float]
    """Details of the enzymes produced by the microbial group.
    
    The keys are the substrates for which enzymes are produced, and the values are the
    allocation to enzyme production. This allocation is expressed as a fraction of the
    (gross) cellular biomass growth.
    """

    reproductive_allocation: float
    """Reproductive allocation as fraction of (gross) cellular biomass growth [unitless]
    
    Only fungi generate separate reproductive bodies, so this value **must** be set to
    zero for bacterial functional groups. Providing a non-zero value for a bacterial
    functional group will prevent the soil model from configuring.
    """

    synthesis_nutrient_ratios: dict[str, float]
    """Average carbon to nutrient ratios for the total synthesised biomass.
    
    Microbes have to synthesis both cellular biomass and extracellular enzymes. We
    assume that this occurs in fixed unvarying proportion. This attribute stores the
    carbon nutrient (nitrogen, phosphorus) ratios for the total synthesised biomass.
    """

    @classmethod
    def build_microbial_group(
        cls,
        group_config: dict[str, Any],
        enzyme_classes: dict[str, EnzymeConstants],
        core_constants: CoreConsts,
    ):
        """Class method to build the microbial group including enzyme information.

        Args:
            group_config: The config details for microbial group in question.
            enzyme_classes: Details of the enzyme classes used by the soil model.
            core_constants: Set of constants shared across the Virtual Ecosystem models.

        Raises:
            ValueError: If the taxonomic grouping provided isn't accepted.
        """

        valid_taxonomic_groups = {"fungi", "bacteria"}

        if group_config["taxonomic_group"] not in valid_taxonomic_groups:
            msg = (
                f"Taxonomic group {group_config['taxonomic_group']} not allowed. Must "
                f"be one of {valid_taxonomic_groups}."
            )
            LOGGER.critical(msg)
            raise ValueError(msg)

        if (
            group_config["taxonomic_group"] != "fungi"
            and group_config["reproductive_allocation"] != 0.0
        ):
            msg = (
                f"Only fungi allocate to fruiting bodies, "
                f"{group_config['taxonomic_group']} cannot."
            )
            LOGGER.critical(msg)
            raise ValueError(msg)

        return cls(
            **group_config,
            synthesis_nutrient_ratios=calculate_new_biomass_average_nutrient_ratios(
                taxonomic_group=group_config["taxonomic_group"],
                c_n_ratio=group_config["c_n_ratio"],
                c_p_ratio=group_config["c_p_ratio"],
                enzyme_production=group_config["enzyme_production"],
                reproductive_allocation=group_config["reproductive_allocation"],
                c_n_ratio_fruiting_bodies=core_constants.fungal_fruiting_bodies_c_n_ratio,
                c_p_ratio_fruiting_bodies=core_constants.fungal_fruiting_bodies_c_p_ratio,
                enzyme_classes=enzyme_classes,
            ),
        )

    def find_enzyme_substrates(self) -> list[str]:
        """Substrates that the microbial group produces enzymes for."""

        return [
            substrate
            for substrate, production in self.enzyme_production.items()
            if production > 0.0
        ]


def calculate_new_biomass_average_nutrient_ratios(
    taxonomic_group: str,
    c_n_ratio: float,
    c_p_ratio: float,
    enzyme_production: dict[str, float],
    reproductive_allocation: float,
    c_n_ratio_fruiting_bodies: float,
    c_p_ratio_fruiting_bodies: float,
    enzyme_classes: dict[str, EnzymeConstants],
) -> dict[str, float]:
    """Calculate average carbon nutrient ratios of the newly synthesised biomass.

    Microbes have to synthesise cellular biomass as well as extracellular enzymes, and
    fungi also allocate to reproductive fruiting bodies. This method calculates average
    nutrient ratios of this total biomass synthesis using the relative production
    allocation to each enzyme class, cellular growth and (for fungi) reproductive
    allocation. Carbon nutrient ratios have units of carbon per nutrient and so cannot
    be simply averaged across the different biomass allocations, which are all expressed
    in carbon terms. Instead, they must first be inversed to convert to nutrient per
    carbon units, and then the average of these inverses can be found.

    Args:
        taxonomic_group: Taxonomic group that the microbe belongs to.
        c_n_ratio: Ratio of carbon to nitrogen for the microbial group's cellular
            biomass.
        c_p_ratio: Ratio of carbon to nitrogen for the microbial group's cellular
            biomass.
        enzyme_production: Details of the enzymes produced by the microbial group, i.e.
            which substrates are enzymes produced for, and how much (relative to
            cellular synthesis)
        reproductive_allocation: Allocation of new biomass synthesis to reproductive
            structures (relative to cellular synthesis).
        c_n_ratio_fruiting_bodies: Carbon to nitrogen ratio of fungal fruiting bodies.
        c_p_ratio_fruiting_bodies: Carbon to phosphorus ratio of fungal fruiting bodies.
        enzyme_classes: Details of the enzyme classes used by the soil model.
    """

    enzyme_c_n_inverse = sum(
        allocation / enzyme_classes[f"{taxonomic_group}_{substrate}"].c_n_ratio
        for substrate, allocation in enzyme_production.items()
    )

    enzyme_c_p_inverse = sum(
        allocation / enzyme_classes[f"{taxonomic_group}_{substrate}"].c_p_ratio
        for substrate, allocation in enzyme_production.items()
    )

    total_carbon_gain = 1 + sum(enzyme_production.values()) + reproductive_allocation

    return {
        "nitrogen": total_carbon_gain
        / (
            (1 / c_n_ratio)
            + enzyme_c_n_inverse
            + (reproductive_allocation / c_n_ratio_fruiting_bodies)
        ),
        "phosphorus": total_carbon_gain
        / (
            (1 / c_p_ratio)
            + enzyme_c_p_inverse
            + (reproductive_allocation / c_p_ratio_fruiting_bodies)
        ),
    }


def make_full_set_of_microbial_groups(
    config: Config,
    enzyme_classes: dict[str, EnzymeConstants],
    core_constants: CoreConsts,
) -> dict[str, MicrobialGroupConstants]:
    """Make the full set of functional groups used in the soil model.

    Args:
        config: The complete virtual ecosystem config.
        enzyme_classes: Details of the enzyme classes used by the soil model.
        core_constants: Set of constants shared across the Virtual Ecosystem models.

    Raises:
        ConfigurationError: If the soil model configuration is missing, if expected
            functional groups are not defined, or if unexpected functional groups are
            defined.

    Returns:
        A dictionary containing each functional group used in the soil model (currently
        bacteria and fungi).
    """

    if "soil" not in config:
        msg = "Model configuration for soil model not found."
        LOGGER.critical(msg)
        raise ConfigurationError(msg)

    expected_groups = {
        "saprotrophic_fungi",
        "ectomycorrhiza",
        "arbuscular_mycorrhiza",
        "bacteria",
    }
    defined_groups = {
        group["name"] for group in config["soil"]["microbial_group_definition"]
    }

    undefined_groups = expected_groups.difference(defined_groups)
    unexpected_groups = defined_groups.difference(expected_groups)
    if undefined_groups:
        msg = (
            "The following expected soil microbial groups are not defined: "
            f"{', '.join(undefined_groups)}"
        )
        LOGGER.critical(msg)
    if unexpected_groups:
        msg = (
            "The following microbial groups are not valid: "
            f"{', '.join(unexpected_groups)}"
        )
        LOGGER.critical(msg)
    if undefined_groups or unexpected_groups:
        raise ConfigurationError(
            "The soil microbial group configuration contains errors. Please check the "
            "log."
        )

    return {
        group_name: MicrobialGroupConstants.build_microbial_group(
            group_config=next(
                functional_group
                for functional_group in config["soil"]["microbial_group_definition"]
                if functional_group["name"] == group_name
            ),
            core_constants=core_constants,
            enzyme_classes=enzyme_classes,
        )
        for group_name in expected_groups
    }


def make_full_set_of_enzymes(
    config: Config,
) -> dict[str, EnzymeConstants]:
    """Make the full set of enzyme classes used in the soil model.

    Args:
        config: The complete virtual ecosystem config.

    Raises:
        ConfigurationError: If the soil model configuration is missing, if expected
            enzyme classes are not defined, or if unexpected enzyme classes are
            defined.

    Returns:
        A dictionary containing each enzyme class used in the soil model.
    """

    if "soil" not in config:
        msg = "Model configuration for soil model not found."
        LOGGER.critical(msg)
        raise ConfigurationError(msg)

    expected_classes = {
        ("fungi", "pom"),
        ("fungi", "maom"),
        ("bacteria", "pom"),
        ("bacteria", "maom"),
    }
    defined_classes = {
        (group["source"], group["substrate"])
        for group in config["soil"]["enzyme_class_definition"]
    }

    undefined_classes = expected_classes.difference(defined_classes)
    unexpected_classes = defined_classes.difference(expected_classes)
    if undefined_classes:
        msg = "The following expected enzyme classes are not defined: " + ", ".join(
            f"{source}_{substrate}" for source, substrate in undefined_classes
        )
        LOGGER.critical(msg)
    if unexpected_classes:
        msg = "The following enzyme classes are not valid: " + ", ".join(
            f"{source}_{substrate}" for source, substrate in unexpected_classes
        )
        LOGGER.critical(msg)
    if undefined_classes or unexpected_classes:
        raise ConfigurationError(
            "The soil enzyme classes configuration contains errors. Please check the "
            "log."
        )

    return {
        f"{microbe}_{substrate}": EnzymeConstants(
            **next(
                enzyme_class
                for enzyme_class in config["soil"]["enzyme_class_definition"]
                if enzyme_class["source"] == microbe
                and enzyme_class["substrate"] == substrate
            )
        )
        for (microbe, substrate) in expected_classes
    }


def find_microbial_stoichiometries(config: Config) -> dict[str, dict[str, float]]:
    """Find the stoichiometries of each microbial functional group.

    This is a helper function for the animal model, as microbial stoichiometries need to
    be known for soil consumption reasons.

    Args:
        config: The complete virtual ecosystem config.

    Returns:
        A dictionary containing the carbon to nutrient ratios of each microbial
        functional group, for both nitrogen and phosphorus [unitless]
    """
    core_constants = load_constants(config, "core", "CoreConsts")
    enzyme_classes = make_full_set_of_enzymes(config=config)
    microbial_groups = make_full_set_of_microbial_groups(
        config=config, enzyme_classes=enzyme_classes, core_constants=core_constants
    )

    return {
        group: {"nitrogen": params.c_n_ratio, "phosphorus": params.c_p_ratio}
        for (group, params) in microbial_groups.items()
    }


@dataclass
class CarbonSupply:
    """Rate of carbon supply to each of the plant symbiotic microbial groups."""

    nitrogen_fixers: NDArray[np.floating]
    """Carbon supply to the nitrogen fixing bacteria [kg C m^-3 day^-1]."""

    ectomycorrhiza: NDArray[np.floating]
    """Carbon supply to ectomycorrhizal fungi [kg C m^-3 day^-1]."""

    arbuscular_mycorrhiza: NDArray[np.floating]
    """Carbon supply to arbuscular mycorrhizal fungi [kg C m^-3 day^-1]."""


def calculate_symbiotic_carbon_supply(
    total_plant_supply: NDArray[np.floating],
    nitrogen_fixer_fraction: float,
    ectomycorrhiza_fraction: float,
) -> CarbonSupply:
    """Calculate supply of carbon from plants to each microbial symbiotic partner.

    This function splits the total carbon supply from the plants between the different
    symbiotic microbial groups based on (configurable) constant fractions.

    Args:
        total_plant_supply: Total supply of carbon from the plant to symbiotic microbial
            partners [kg C m^-3 day^-1]
        nitrogen_fixer_fraction: Fraction of carbon supplied by plants to symbiotes that
            goes to nitrogen fixers [unitless]
        ectomycorrhiza_fraction: Fraction of plant carbon supply to mycorrhizal fungi
            that goes to ectomycorrhiza [unitless]

    Returns:
        The carbon supply to each symbiotic microbial partner [kg C m^-3 day^-1]
    """

    n_fixer_supply = total_plant_supply * nitrogen_fixer_fraction

    mycorrhiza_supply = total_plant_supply * (1 - nitrogen_fixer_fraction)
    ectomycorrhiza_supply = mycorrhiza_supply * ectomycorrhiza_fraction
    arbuscular_mycorrhiza_supply = mycorrhiza_supply * (1 - ectomycorrhiza_fraction)

    return CarbonSupply(
        nitrogen_fixers=n_fixer_supply,
        ectomycorrhiza=ectomycorrhiza_supply,
        arbuscular_mycorrhiza=arbuscular_mycorrhiza_supply,
    )
