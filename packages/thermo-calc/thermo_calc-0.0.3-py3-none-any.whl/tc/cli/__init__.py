from .__main__ import app
from .version import register_version

__all__ = ["app"]

from tc.mcp.cli import app as mcp_app
from tc.alloy.cli import app as alloy_app
from tc.schema.cli import app as schema_app

app.add_typer(mcp_app, name="mcp")
app.add_typer(alloy_app, name="alloy")
app.add_typer(schema_app, name="schema")

_ = register_version(app)

if __name__ == "__main__":
    app()
