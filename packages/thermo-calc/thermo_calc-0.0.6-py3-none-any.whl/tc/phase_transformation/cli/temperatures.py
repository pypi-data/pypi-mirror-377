import typer

from rich import print as rprint

from ow.cli.options import WorkspaceOption


def register_phase_transformation_temperatures(app: typer.Typer):
    from tc.schema.composition import Composition

    @app.command(name="temperatures")
    def phase_transformation_temperatures(
        composition_filename: str,
        workspace: WorkspaceOption = None,
    ) -> None:
        """List known alloy composition."""
        from tc.phase_transformation.temperatures import (
            compute_phase_transformation_temperatures,
        )
        from ow.cli.utils import get_workspace_path

        workspace_path = get_workspace_path(workspace)

        composition_path = workspace_path / "compositions" / composition_filename
        composition = Composition.load(composition_path)

        phase_transformation_temperatures_path = (
            workspace_path / "phase_transformation_temperatures" / composition_filename
        )

        try:
            temperatures = compute_phase_transformation_temperatures(composition)
            temperatures.save(phase_transformation_temperatures_path)
            rprint(
                f"✅ [bold green]Phase transformation temperatures saved successfully[/bold green] → {phase_transformation_temperatures_path}"
            )

        except Exception as e:
            rprint("⚠️  [yellow]Unable to determine phase transformation[/yellow]")
            rprint(f"[yellow]Encountered Error: {e}[/yellow]")
            _ = typer.Exit()

    _ = phase_transformation_temperatures
