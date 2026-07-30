#!/bin/bash

SCRIPT_NAME="main.pyw"
DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. Quietly install dependencies into an isolated environment
echo "Sprawdzanie bibliotek..."
uv pip install -r "$DIR/requirements.txt" --quiet

# 2. Run in the background without locking the terminal window
uv run python "$DIR/$SCRIPT_NAME" &

# 3. Exit the shell script immediately
exit 0
