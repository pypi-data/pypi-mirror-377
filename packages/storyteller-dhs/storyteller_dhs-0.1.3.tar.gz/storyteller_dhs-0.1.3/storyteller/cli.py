import os
import subprocess
import click

from storyteller.mintilo_ai_app.processor import build_dataset
from storyteller.mintilo_ai_app.exporter import export_csv, export_metadata


@click.group()
def storyteller():
    """Storyteller CLI tool."""
    pass


@storyteller.command()
@click.argument('db_path_arg', required=False, type=click.Path(exists=True))
@click.option('--db_path', type=click.Path(exists=True), help='Path to the SQLite database')
@click.option('--port', default=8001, show_default=True, type=int, help='Port to run Storyteller on')
@click.option('--enable-fts', is_flag=True, default=True, help='Enable FTS before starting server')
def start(db_path_arg, db_path, port, enable_fts):
    """
    Start Storyteller with the given database and optional port.
    You can provide the database path either as a positional argument or with --db_path.
    """
    db_path_final = db_path or db_path_arg
    if not db_path_final:
        raise click.UsageError("You must provide a database path either as a positional argument or with --db_path.")

    # == Paths
    base_dir = os.path.dirname(__file__)

    metadata_path = os.path.join(base_dir, "metadata.yaml")
    print("INFO - Using metadata path:", metadata_path)

    assets_dir = os.path.join(base_dir, "assets")
    print("INFO - Using assets directory:", assets_dir)

    templates_dir = os.path.join(base_dir, "templates")
    print("INFO - Using templates directory:", templates_dir)

    # Enable FTS if requested
    if enable_fts:
        tables = [
            "HR_variable", "IR_variable", "BR_variable", "KR_variable",
            "MR_variable", "CR_variable", "PR_variable"
        ]
        click.echo("INFO - Enabling FTS on tables...")
        for table in tables:
            try:
                subprocess.run(
                    ["sqlite-utils", "enable-fts", db_path_final, table, "Label"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                click.echo(f"✓ FTS enabled on {table}")
            except subprocess.CalledProcessError as e:
                if "already exists" in e.stderr:
                    click.echo(f"× FTS already enabled on {table}, skipping")
                else:
                    click.echo(f"× Error enabling FTS on {table}: {e.stderr}")

    # == Start server with the provided database path
    storyteller_cmd = [
        "datasette",
        db_path_final,
        "--port", str(port),
        "--metadata", metadata_path,
        "--template-dir", templates_dir,
        "--static", f"assets:{assets_dir}"
    ]
    subprocess.Popen(storyteller_cmd, cwd=os.path.abspath('.'))

    click.echo(f"INFO - Started Storyteller for {db_path_final} on port {port}")


@click.command("enable_fts")
@click.option('--db_path', required=True, type=click.Path(exists=True), help='Path to the SQLite database')
def enable_fts(db_path):
    """Enable FTS on Label column for specific tables."""
    tables = [
        "HR_variable", "IR_variable", "BR_variable", "KR_variable",
        "MR_variable", "CR_variable", "PR_variable"
    ]
    for table in tables:
        click.echo(f"Attempting {table}...")
        try:
            subprocess.run(
                ["sqlite-utils", "enable-fts", db_path, table, "Label"],
                check=True,
                capture_output=True,
                text=True
            )
            click.echo(f"✓ FTS enabled on {table}")
        except subprocess.CalledProcessError as e:
            if "already exists" in e.stderr:
                click.echo(f"× FTS already enabled on {table}, skipping")
            else:
                click.echo(f"× Error enabling FTS on {table}: {e.stderr}")

    click.echo("INFO - Completed FTS setup")


@storyteller.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--menu', type=click.Choice(['mintiloai'], case_sensitive=False), required=True)
def query(db_path, menu):
    """Run predefined queries and export datasets."""
    if menu == 'mintiloai':
        click.echo("INFO - Running Mintilo AI dataset preparation...")
        df, queries = build_dataset(db_path)
        csv_path = export_csv(df, db_path)
        metadata_path = export_metadata(db_path, queries)
        click.echo(f"INFO - CSV exported: {csv_path}")
        click.echo(f"INFO - Metadata exported: {metadata_path}")


if __name__ == "__main__":
    storyteller()
