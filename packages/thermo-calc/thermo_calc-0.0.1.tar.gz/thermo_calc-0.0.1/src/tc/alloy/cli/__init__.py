from .__main__ import app

from .alloy_composition import register_alloy_composition
from .alloy_list import register_alloy_list

# from .initialize_power_velocity_range import (
#     register_process_map_initialize_power_velocity_range,
# )
#
# from .generate_process_map import register_process_map_generate_melt_pool_measurements

# _ = register_process_map_initialize_power_velocity_range(app)
# _ = register_process_map_generate_melt_pool_measurements(app)
_ = register_alloy_composition(app)
_ = register_alloy_list(app)

__all__ = ["app"]
