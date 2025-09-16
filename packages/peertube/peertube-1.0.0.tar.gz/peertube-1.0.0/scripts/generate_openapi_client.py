#!/usr/bin/env python3
"""Generate OpenAPI client from PeerTube OpenAPI specification.

This script generates a Python client from the PeerTube OpenAPI specification
using openapi-python-client.
"""

import subprocess
import sys
from pathlib import Path


def generate_client() -> bool:
    """Generate the OpenAPI client from the specification."""
    repo_root = Path(__file__).parent.parent
    openapi_file = repo_root / "assets" / "openapi.json"
    output_dir = repo_root / "src" / "peertube" / "generated_client"

    if not openapi_file.exists():
        msg = f"OpenAPI specification not found at {openapi_file}"
        raise FileNotFoundError(msg)

    # Command to generate the client
    cmd = [
        "openapi-python-client",
        "generate",
        "--path",
        str(openapi_file),
        "--output-path",
        str(output_dir),
        "--config",
        str(repo_root / "openapi-client-config.yaml"),
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Generated client successfully:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate client:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print("openapi-python-client not found. Install it with:")
        print("pip install openapi-python-client")
        return False
    else:
        return True


if __name__ == "__main__":
    success = generate_client()
    sys.exit(0 if success else 1)
