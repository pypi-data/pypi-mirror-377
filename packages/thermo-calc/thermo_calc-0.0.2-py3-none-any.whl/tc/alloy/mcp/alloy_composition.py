from mcp.server import FastMCP


def register_alloy_composition(app: FastMCP):
    from tc.mcp.types import ToolSuccess, ToolError
    from tc.mcp.utils import tool_success, tool_error
    from tc.alloy.types import Alloy
    from tc.schema.composition import Composition

    @app.tool(
        title="Get Alloy Composition",
        description="Provide the elements and composition for an alloy.",
        structured_output=True,
    )
    def alloy_composition(alloy: Alloy) -> ToolSuccess[Composition | None] | ToolError:
        from tc.alloy.alloy_composition import get_alloy_composition

        try:
            return tool_success(get_alloy_composition(alloy))

        except Exception as e:
            return tool_error(
                "Failed to get alloy composition",
                "ALLOY_COMPOSITION_FAILED",
                exception_type=type(e).__name__,
                exception_message=str(e),
            )

    _ = alloy_composition
