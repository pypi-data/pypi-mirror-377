from pint import Quantity

from .database import select_thermocalc_database
from tc.schema import Composition

T_AXIS_MIN = 500.0
T_AXIS_MAX = 3500.0

def get_temperature_solidus_liquidus(composition: Composition) -> tuple[float, float] 
    """
    Uses Thermo-Calc to compute solidus & liquidus from elements/fractions.
    Returns (solidus_K, liquidus_K, database_name)
    """
    database = select_thermocalc_database(composition)

    print(database)
    return database

    # with TCPython() as tc:
    #     tc.set_cache_folder("cache")
    #     tc.set_ges_version(6)
    #
    #     calc = (
    #         tc.select_database_and_elements(database, elements)
    #           .get_system()
    #           .with_property_diagram_calculation()
    #           .with_axis(
    #               CalculationAxis(ThermodynamicQuantity.temperature())
    #               .set_min(T_axis_min)
    #               .set_max(T_axis_max)
    #               .with_axis_type(Linear().set_min_nr_of_steps(50))
    #           )
    #     )
    #
    #     # Set composition via mass fractions. Skip the first element; Thermo-Calc will normalize.
    #     for el, wf in list(fractions.items())[1:]:
    #         calc.set_condition(f"W({el})", wf)
    #
    #     diagram = calc.calculate()
    #     diagram.set_phase_name_style(PhaseNameStyle.ALL)
    #
    #     groups = diagram.get_values_grouped_by_quantity_of(
    #         ThermodynamicQuantity.temperature(),
    #         ThermodynamicQuantity.volume_fraction_of_a_phase("LIQUID"),
    #     )
    #
    # solidus_T = None
    # liquidus_T = None
    #
    # for group in groups.values():
    #     xT = group.x
    #     yL = group.y
    #     last_zero_idx = max((i for i, y in enumerate(yL) if abs(y) < 1e-12), default=None)
    #     first_one_idx = None
    #     if last_zero_idx is not None:
    #         for i in range(last_zero_idx + 1, len(yL)):
    #             if abs(yL[i] - 1.0) < 1e-12:
    #                 first_one_idx = i
    #                 break
    #     if last_zero_idx is not None:
    #         solidus_T = xT[last_zero_idx]
    #     if first_one_idx is not None:
    #         liquidus_T = xT[first_one_idx]
    #
    # if solidus_T is None or liquidus_T is None:
    #     raise RuntimeError(
    #         f"Could not determine solidus/liquidus using {database} "
    #         f"in range [{T_axis_min:.1f}, {T_axis_max:.1f}] K."
    #     )
    #
    # return float(solidus_T), float(liquidus_T), database

