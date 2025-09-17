from mcp.server import FastMCP


def register_alloy_temperature(app: FastMCP):
    from tc.mcp.types import ToolSuccess, ToolError
    from tc.mcp.utils import tool_success, tool_error
    from tc.schema.composition import Composition

    @app.tool(
        title="Get Solidus Liquidus temperature",
        description="Calculate the solidus and liquids temperature given an alloy composition.",
        structured_output=True,
    )
    def temperature_solidus_liquidus(composition: Composition) -> ToolSuccess[tuple[float, float]] | ToolError:
        from tc.alloy.temperature import get_temperature_solidus_liquidus

        try:
            return tool_success(get_temperature_solidus_liquidus(composition))

        except Exception as e:
            return tool_error(
                "Failed to get alloy liquidus and solidus temperatures",
                "ALLOY_TEMPERATURE_FAILED",
                exception_type=type(e).__name__,
                exception_message=str(e),
            )

    _ = temperature_solidus_liquidus
