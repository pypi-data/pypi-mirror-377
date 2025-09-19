from pint import Quantity
from tc_python import (
    CalculationAxis,
    Linear,
    TCPython,
    ThermodynamicQuantity,
    PhaseNameStyle,
)
from typing_extensions import cast

from tc.database.utils import select_thermocalc_database
from tc.schema import Composition, PhaseTransformationTemperatures

T_AXIS_MIN = 500.0
T_AXIS_MAX = 3500.0


def compute_phase_transformation_temperatures(
    composition: Composition,
) -> PhaseTransformationTemperatures:
    """
    Uses Thermo-Calc to compute solidus & liquidus from elements/fractions.
    Returns (solidus_K, liquidus_K, database_name)
    """
    database = select_thermocalc_database(composition)

    elements = composition.elements()
    fractions = composition.fractions()

    with TCPython() as client:
        client.set_cache_folder("cache")
        client.set_ges_version(6)

        calc = (
            client.select_database_and_elements(database, elements)
            .get_system()
            .with_property_diagram_calculation()
            .with_axis(
                CalculationAxis(ThermodynamicQuantity.temperature())
                .set_min(T_AXIS_MIN)
                .set_max(T_AXIS_MAX)
                .with_axis_type(Linear().set_min_nr_of_steps(50))
            )
        )

        # Set composition via mass fractions. Skip the first element; Thermo-Calc will normalize.
        for el, wf in list(fractions.items())[1:]:
            calc.set_condition(f"W({el})", wf)

        diagram = calc.calculate()
        diagram.set_phase_name_style(PhaseNameStyle.ALL)

        groups = diagram.get_values_grouped_by_quantity_of(
            ThermodynamicQuantity.temperature(),
            ThermodynamicQuantity.volume_fraction_of_a_phase("LIQUID"),
        )

    solidus_T = None
    liquidus_T = None

    for group in groups.values():
        xT = group.x
        yL = group.y
        last_zero_idx = max(
            (i for i, y in enumerate(yL) if abs(y) < 1e-12), default=None
        )
        first_one_idx = None
        if last_zero_idx is not None:
            for i in range(last_zero_idx + 1, len(yL)):
                if abs(yL[i] - 1.0) < 1e-12:
                    first_one_idx = i
                    break
        if last_zero_idx is not None:
            solidus_T = xT[last_zero_idx]
        if first_one_idx is not None:
            liquidus_T = xT[first_one_idx]

    if solidus_T is None or liquidus_T is None:
        raise RuntimeError(
            f"Could not determine solidus/liquidus using {database} "
            f"in range [{T_AXIS_MIN:.1f}, {T_AXIS_MAX:.1f}] K."
        )

    temperature_melt = cast(Quantity, Quantity((liquidus_T + solidus_T) / 2, "K"))
    temperature_liquidus = cast(Quantity, Quantity(liquidus_T, "K"))
    temperature_solidus = cast(Quantity, Quantity(solidus_T, "K"))

    phase_transformation_temperatures = PhaseTransformationTemperatures(
        name=composition.name,
        temperature_melt=temperature_melt,
        temperature_liquidus=temperature_liquidus,
        temperature_solidus=temperature_solidus,
    )

    return phase_transformation_temperatures
