#!/usr/bin/env bash
set -euo pipefail

model_dir="${1:-models}"
url="${MODEL_URL:-}"

if [[ -z "$url" ]]; then
  printf '%s\n' "Set MODEL_URL to a reviewed GGUF download URL before downloading model weights." >&2
  exit 2
fi

mkdir -p "$model_dir"
curl --fail --location --continue-at - "$url" -o "$model_dir/model.gguf"
printf '%s\n' "Downloaded $model_dir/model.gguf. Review the model license before redistribution."
