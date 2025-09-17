import json
import requests
import typer

API_URL = "https://babilonczyk-swiss-prot.hf.space/gradio_api/call/predict"


# The Hugging Face API streams responses using SSE (Server-Sent Events).
# Relevant lines look like:
#
#   event: complete
#   data: ["{\"id\": \"P12345\", \"entry_name\": \"Protein_XYZ\", ...}"]
#
# The "data:" line contains a JSON-encoded string. Inside it is another JSON
# object representing the metadata (hence we parse twice: outer list -> inner JSON string -> dict).

def find_metadata_by_id(target_id: str) -> dict:
    """
    Fetch Swiss-Prot metadata for a given UniProt ID from the remote HuggingFace model.

    Args:
        target_id (str): The UniProt accession ID (e.g., "P12345").

    Returns:
        dict: A dictionary containing protein metadata (fields depend on the model output).
              Returns an empty dict if the request fails or no metadata is found.

    Behavior:
        1. Sends the UniProt ID to the Hugging Face Space via POST request.
        2. Retrieves the `event_id` from the initial JSON response.
        3. Opens a streaming connection to poll results.
        4. Looks for a line beginning with "data:".
        5. Parses the outer JSON array, which contains a stringified JSON object.
        6. Decodes the stringified object into a Python dict and returns it.

    Example:
        >>> find_metadata_by_id("P12345")
        {
            "id": "P12345",
            "entry_name": "Protein_XYZ",
            "function": "...",
            "organism": "Homo sapiens",
            ...
        }
    """
    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json={"data": [target_id.strip().upper()]}
        )
        response.raise_for_status()

        event_id = response.json().get("event_id")
        if not event_id:
            typer.echo("❌ No event_id returned")
            return {}

        result_url = f"{API_URL}/{event_id}"
        with requests.get(result_url, stream=True) as stream:
            for line in stream.iter_lines():
                if line:
                    decoded = line.decode("utf-8")

                    if decoded.startswith("data: "):
                        data = json.loads(decoded[6:])

                        if isinstance(data, list) and len(data) > 0:
                            # The API returns a JSON string inside the list → parse it
                            return json.loads(data[0])

        return {}

    except Exception as e:
        print(f"❌ Error fetching metadata for ID {target_id}: {e}")
        return {}