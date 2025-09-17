import typer
import gdown
from pathlib import Path
import h5py
import chromadb
from tqdm import tqdm


DRIVE_FILE_ID = "1uXralh7DcZf5YlP1my1chEKOEyBci64b"
DB_FOLDER = Path.home() / ".bioai_seq" / "db"
DB_FILE = DB_FOLDER / "swissprot_esm1b.h5"
CHROMA_DIR = DB_FOLDER / "chroma"

# ------------------------------------------------------------------------------------------- 


def is_db_installed():
    return DB_FILE.exists()

# -------------------------------------------------------------------------------------------


def prompt_and_download():
    typer.echo("🧬 Swiss-Prot embedding database (.h5) is required.")
    confirm = typer.confirm("💾 Download & install missing files now? (~1.3 GB for .h5)")
    if not confirm:
        typer.echo("❌ Cannot proceed without vector DB.")
        raise typer.Exit(code=1)

    DB_FOLDER.mkdir(parents=True, exist_ok=True)

    # Download .h5
    if not is_db_installed():
        typer.echo("⬇️ Downloading embeddings from Google Drive...")
        gdown.download(id=DRIVE_FILE_ID, output=str(DB_FILE), quiet=False)

    # Validate
    if DB_FILE.exists() and DB_FILE.stat().st_size > 10_000_000:
        typer.echo("✅ All files downloaded and ready.")
    else:
        typer.echo("❌ Download failed or files incomplete.")
        raise typer.Exit(code=1)
    

# -------------------------------------------------------------------------------------------


def is_db_populated():
    """Check if the Chroma DB is already populated."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name="swissprot")
    count = collection.count()
    typer.echo(f"🔍 Database contains {count} entries.")
    return count > 0


# -------------------------------------------------------------------------------------------


def populate_db():
    typer.echo("🔍 Loading embeddings from .h5 file...")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name="swissprot")

    if collection.count() > 0:
        typer.echo("⚠️ Vector database already populated. Skipping.")
        return

    def extract_embedding(group):
        if "representations" in group:
            return group["representations"]["mean_representations"][()]
        elif "mean_representations" in group:
            return group["mean_representations"][()]
        elif "embedding" in group:
            return group["embedding"][()]
        elif isinstance(group, h5py.Dataset):
            return group[()]
        return None

    with h5py.File(DB_FILE, "r") as f:
        keys = list(f.keys())
        typer.echo(f"📦 Found {len(keys)} entries. Inserting first 1000...")

        first_1000 = keys[:1000]

        # Optional: Preview structure of the first entry
        if first_1000:
            first_key = first_1000[0]
            group = f[first_key]
            typer.echo(f"🔑 First key: {first_key}")
            if isinstance(group, h5py.Group):
                typer.echo(f"📂 Group keys: {list(group.keys())}")
            if hasattr(group, "attrs"):
                typer.echo(f"🧬 Attributes: {dict(group.attrs)}")
            if "representations" in group:
                typer.echo(f"🧪 Representations keys: {list(group['representations'].keys())}")

        typer.echo(f"📦 Populating vector database with {len(first_1000)} protein entries...")

        for key in tqdm(first_1000, desc="🚀 Inserting embeddings"):
            group = f[key]
            embedding = extract_embedding(group)

            if embedding is None:
                tqdm.write(f"❌ Skipping {key}: no valid embedding found.")
                continue

            if embedding.ndim != 1:
                tqdm.write(f"⚠️ Skipping {key}: embedding shape not 1D: {embedding.shape}")
                continue

            collection.add(
                ids=[key],
                embeddings=[embedding.tolist()]
            )

    typer.echo("✅ Vector database populated and saved.")