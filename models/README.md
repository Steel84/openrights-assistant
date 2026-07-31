# Local Model Slot

The repository does not commit model weights. They are too large for a source repository and licensing must be checked per model.

Recommended first experiment:

- Qwen2.5-1.5B-Instruct, GGUF, Q4_K_M quantization;
- fallback: Phi-3-mini or Gemma 2B in a compatible GGUF build;
- runtime: `llama.cpp` / `llama-cli`;
- target budget: 1-2 GB storage, 2-3 GB working memory, short answers capped at 256 tokens.

The first local artifact used for integration testing is `qwen2.5-1.5b-instruct-q2_k.gguf` from the official Qwen GGUF repository. Its download size is approximately 719 MB. It is not committed here; use the download script and review the upstream license.

After downloading a model to this directory, run:

```bash
python -m openrights ask --model models/model.gguf "How is overtime compensation calculated?"
```

The generator receives only retrieved passages and is instructed to cite them. Retrieval remains usable if the model is absent.
