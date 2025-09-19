from .__main__ import app
from .version import register_version

__all__ = ["app"]

from tc.mcp.cli import app as mcp_app
from tc.alloy.cli import app as alloy_app
from tc.schema.cli import app as schema_app
from tc.phase_transformation.cli import app as phase_transformation_app
from tc.property_diagram.cli import app as property_diagram_app

app.add_typer(mcp_app, name="mcp")
app.add_typer(alloy_app, name="alloy")
app.add_typer(schema_app, name="schema")
app.add_typer(phase_transformation_app, name="phase-transformation")
app.add_typer(property_diagram_app, name="property-diagram")

_ = register_version(app)

if __name__ == "__main__":
    app()
