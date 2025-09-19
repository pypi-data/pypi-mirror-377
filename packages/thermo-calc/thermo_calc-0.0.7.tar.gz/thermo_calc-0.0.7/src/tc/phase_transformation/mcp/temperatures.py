from mcp.server import FastMCP
from pathlib import Path


def register_phase_transformation_temperatures(app: FastMCP):
    from tc.mcp.types import ToolSuccess, ToolError
    from tc.mcp.utils import tool_success, tool_error
    from tc.schema.composition import Composition

    @app.tool(
        title="Phase Transformation Solidus / Liquidus Temperatures",
        description="Calculate the solidus and liquids temperature given an alloy composition.",
        structured_output=True,
    )
    def phase_transformation_temperatures(
        workspace_name: str,
        composition_filename: str,
    ) -> ToolSuccess[Path] | ToolError:
        from tc.phase_transformation.temperatures import (
            compute_phase_transformation_temperatures,
        )

        from ow.cli.utils import get_workspace_path

        workspace_path = get_workspace_path(workspace_name)

        composition_path = workspace_path / "compositions" / composition_filename
        composition = Composition.load(composition_path)
        phase_transformation_temperatures_path = (
            workspace_path / "phase_transformation_temperatures" / composition.name
        )

        try:
            temperatures = compute_phase_transformation_temperatures(composition)
            temperatures.save(phase_transformation_temperatures_path)
            return tool_success(phase_transformation_temperatures_path)

        except Exception as e:
            return tool_error(
                "Failed to get phase transformation liquidus and solidus temperatures",
                "PHASE_TRANSFORMATION_TEMPERATURES_FAILED",
                exception_type=type(e).__name__,
                exception_message=str(e),
            )

    _ = phase_transformation_temperatures
