#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REQ_FILE="$ROOT_DIR/requirements.txt"

if [[ ! -f "$REQ_FILE" ]]; then
  echo "requirements.txt not found at $REQ_FILE" >&2
  exit 1
fi

python -m pip install --upgrade pip
python -m pip install -r "$REQ_FILE"

python -m spacy download en_core_web_sm
python -m nltk.downloader words stopwords
