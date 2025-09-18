from mcp.server.fastmcp import FastMCP

from tc.alloy.mcp import register_alloy_resources, register_alloy_known_alloy 
from tc.schema.mcp import register_schema_composition

app = FastMCP(name="thermo-calc")

_ = register_alloy_known_alloy(app)
_ = register_alloy_resources(app)
_ = register_schema_composition(app)


def main():
    """Entry point for the direct execution server."""
    app.run()


if __name__ == "__main__":
    main()
