import typer
from pathlib import Path

from bioai_seq.core import db
from bioai_seq.core.commands import analyze as analyze_command
from bioai_seq.core.services.remote.get_embedding import get_embedding

app = typer.Typer()

DB_FOLDER = Path.home() / ".bioai_seq" / "db"
CHROMA_DIR = DB_FOLDER / "chroma"

# -------------------------------------------------------------------------------------------
# Callbacks

@app.callback()
def setup():
    """Setup the bioai-seq environment (runs before every command)."""
    if not db.is_db_installed():
        db.prompt_and_download()
    if db.is_db_installed() and not db.is_db_populated():
        db.populate_db()


@app.callback(invoke_without_command=True)
def show_help(ctx: typer.Context):
    """Learn more about available commands."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

# -------------------------------------------------------------------------------------------
# Commands

@app.command()
@app.command("a")
def analyze(input: str):
    """Analyze a FASTA file or a sequence."""
    analyze_command.analyze(input)

# -------------------------------------------------------------------------------------------
# Main

if __name__ == "__main__":
    app(prog_name="cli.py")