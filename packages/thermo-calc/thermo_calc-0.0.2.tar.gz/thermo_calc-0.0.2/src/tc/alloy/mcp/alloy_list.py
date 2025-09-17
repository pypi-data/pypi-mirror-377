from mcp.server import FastMCP


def register_alloy_list(app: FastMCP):
    from tc.mcp.types import ToolSuccess
    from tc.mcp.utils import tool_success

    @app.tool(
        title="List Alloys",
        description="Provides a list known alloys that have compositions and material properties.",
        structured_output=True,
    )
    def alloy_list() -> ToolSuccess[list[str] | None]:
        from tc.alloy.alloy_list import alloy_names

        return tool_success(alloy_names())

    _ = alloy_list
