import json
import typer
import requests

HF_API_BASE = "https://babilonczyk-facebook-esm1b-t33-650m-ur50s.hf.space/gradio_api/call/predict"


# The Hugging Face API streams responses using SSE (Server-Sent Events).
# The relevant line looks like this:
#
#   event: complete
#   data: [{"mean_embedding": [0.12899, 0.21760, 0.15301, ... ]}]
#
# We need to capture the "data:" line, parse the JSON, and extract
# the "mean_embedding" list of floats.

def get_embedding(sequence: str) -> list[float]:
    payload = {"data": [sequence]}
    try:
        typer.echo("🔍 Requesting embedding from remote model...")
        res = requests.post(HF_API_BASE, json=payload)
        res.raise_for_status()
        event_id = res.json().get("event_id")
        if not event_id:
            typer.echo("❌ Failed to get event_id")
            return []

        # Poll result from stream endpoint
        stream_url = f"{HF_API_BASE}/{event_id}"
        with requests.get(stream_url, stream=True) as stream:
            for line in stream.iter_lines():
                if not line:
                    continue

                decoded = line.decode("utf-8").strip()

                if decoded.startswith("data:"):
                    try:
                        data = json.loads(decoded[len("data:"):].strip())
                        if isinstance(data, list) and "mean_embedding" in data[0]:
                            embedding = data[0]["mean_embedding"]
                            return embedding
                    except json.JSONDecodeError:
                        typer.echo(f"⚠️ Failed to parse JSON: {decoded}")
        return []
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        return []