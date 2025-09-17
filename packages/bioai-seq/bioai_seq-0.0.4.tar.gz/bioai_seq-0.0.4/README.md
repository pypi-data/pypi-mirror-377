# bioai-seq

`bioai-seq` is a lightweight, developer-friendly command-line tool for **basic biological sequence analysis**.  
It’s part of my journey toward becoming a **Bio AI Software Engineer** — combining software engineering, biology, and artificial intelligence into practical, accessible tools.

With `bioai-seq`, you can:

- Run simple analyses on protein or nucleotide sequences from the command line.
- Automatically generate embeddings using **ESM-1b**.
- Compare sequences against a **local Chroma vector database**.
- Retrieve biological metadata from public sources.
- Summarize results using a **local LLM model** for human-readable insights.

## Who is it for?

- **Students & learners** in bioinformatics who want a gentle entry point into sequence analysis without setting up heavy pipelines.
- **Software engineers** curious about biology, wanting to bridge coding and life sciences.
- **AI & ML enthusiasts** exploring how embeddings, vector search, and LLMs can be applied to biological problems.
- **Researchers** who need a lightweight side tool for quick sequence checks.

## How it helps

- 🔎 **Fast exploration** - check what a sequence might be and what it’s related to in seconds.
- 🧠 **Contextual insights** — every result comes with a human-readable LLM summary.
- 📦 **Local-first design** — downloads embeddings DB + LLM once, then works offline.
- 🧩 **Educational bridge** — shows how **AI techniques (embeddings, vector DBs, LLMs)** can be directly applied to **biology**.
- 🌍 **Open & extensible** — MIT/Apache-licensed, free to adapt for your own research or learning.

## How to install

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install bioai-seq

```bash
pip install --upgrade bioai-seq
bioseq
```

## Flow Chart

```mermaid
flowchart TD
  subgraph CLI[CLI Tool]
    A[User Command: analyze] --> B{Check local resources}
    B -->|Missing| C[Download Embedding Chroma DB & Local LLM]
    B -->|Available| D[Proceed]
    C --> D
    D --> E[ESM-1b API: Create Embedding]
    E --> F[Metadata API: Search Metadata]
    F --> G[Chroma DB: Store & Compare Embeddings]
    G --> H[Local LLM: Generate Summary]
    H --> I[Display Results to User]
  end
```

## 🧪 Planned Example Output

```txt
✅ Sequence loaded: 1273 amino acids
🧬 Detected: SARS-CoV-2 spike glycoprotein (likely variant: Omicron)

🔍 Running ESM-2 embeddings...
📦 Comparing against 1000 proteins in vector database...
📚 Top similar sequences:
 - UniProt P0DTC2 (99.8%) — SARS-CoV-2 spike glycoprotein
 - UniProt A0A6H2L9T9 (98.9%) — Bat coronavirus spike protein
 - UniProt A0A2X1VPJ6 (97.5%) — Pangolin coronavirus S protein

------------------------------------------------------------

🔬 Matched Protein Metadata: P0DTC2
🌍 Organism: SARS-CoV-2
🧬 Gene names: S, spike
🧫 Host organisms: Human, Bat
📖 Description: Spike glycoprotein mediates viral entry via ACE2
🏷️ Keywords: Receptor-binding, Glycoprotein, Fusion protein
🔎 Protein evidence: Evidence at protein level

🧩 Features:
 - Signal peptide: 1–13
 - Transmembrane region: 1213–1237
 - RBD domain: 319–541

🔗 External references:
 - [PDB: 6VSB](https://www.rcsb.org/structure/6VSB)
 - [RefSeq: YP_009724390.1](https://www.ncbi.nlm.nih.gov/protein/YP_009724390.1)
 - [Pfam: PF01601](https://www.ebi.ac.uk/interpro/entry/pfam/PF01601)
 - [AlphaFold model](https://alphafold.ebi.ac.uk/entry/P0DTC2)
 - [UniProt entry](https://www.uniprot.org/uniprotkb/P0DTC2)

------------------------------------------------------------

🧠 Summary:
"This sequence matches the SARS-CoV-2 spike glycoprotein. It binds to the ACE2 receptor to mediate viral entry. The receptor binding domain (RBD) spans residues 319–541 and contains key mutations in Omicron variants. The protein is expressed in humans and bats."
```

---

## Deploying to PyPI (Production)

### 1. Clean previous builds

```bash
rm -rf dist build *.egg-info
```

### 2. Build the package

```bash
python3 -m build
```

### 3. Upload to PyPI

```bash
pip install --upgrade twine
twine upload dist/*
```

- Username: `__token__`
- Password: your API token from [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)

---

## Follow the Journey

- 🌍 Blog: [https://bioaisoftware.engineer](https://bioaisoftware.engineer)
- 🧑‍💻 GitHub: [https://github.com/babilonczyk](https://github.com/babilonczyk)
- 💼 LinkedIn: [https://www.linkedin.com/in/jan-piotrzkowski/](https://www.linkedin.com/in/jan-piotrzkowski/)

---

## License

Apache 2.0 - free to use, and improve.
