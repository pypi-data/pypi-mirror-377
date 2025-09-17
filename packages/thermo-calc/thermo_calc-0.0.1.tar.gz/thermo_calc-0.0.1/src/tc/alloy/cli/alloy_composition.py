import typer

from rich import print as rprint


def register_alloy_composition(app: typer.Typer):
    from tc.alloy.types import Alloy

    @app.command(name="composition")
    def alloy_composition(alloy: Alloy) -> None:
        """List known alloy composition."""
        from tc.alloy.alloy_composition import get_alloy_composition

        try:
            composition = get_alloy_composition(alloy)
            print(composition)
        except:
            rprint("⚠️  [yellow]Unable to find composition for alloy[/yellow]")
            _ = typer.Exit()

    _ = alloy_composition
