import typer

from bioai_seq.core.services.remote.get_embedding import get_embedding

HF_API_BASE = "https://babilonczyk-facebook-esm1b-t33-650m-ur50s.hf.space/gradio_api/call/predict"


def analyze(input: str):
    if is_fasta_file(input):
        analyze_fasta_file(input)
    else:
        analyze_sequence(input)


def is_fasta_file(input: str) -> bool:
    """Check if the input is a FASTA file."""
    return input.endswith('.fasta') or input.endswith('.fa')


def analyze_fasta_file(input: str):
    typer.echo(f"🧬 Analyzing FASTA file: {input}")

    file = open(input, 'r')
    fasta_file_sequences = file.readlines()
    file.close()

    # sequence is all lines except the first one
    sequence = ''.join(fasta_file_sequences[1:]).replace('\n', '')
    styled_sequence = typer.style(f" {sequence} ", fg=typer.colors.WHITE, bg=typer.colors.MAGENTA)
    typer.echo(f"🧬 Analyzing sequence: {styled_sequence}")


def analyze_sequence(sequence: str):
    """Analyze a single sequence."""
    styled_sequence = typer.style(f" {sequence} ", fg=typer.colors.WHITE, bg=typer.colors.MAGENTA)
    typer.echo(f"🧬 Analyzing sequence: {styled_sequence}")

    embedding = get_embedding(sequence)
    if embedding:
        typer.echo(f"✅ Retrieved embedding of length {len(embedding)}")
    else:
        typer.echo("❌ Failed to retrieve embedding")