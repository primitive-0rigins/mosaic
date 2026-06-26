"""
Sidecar model definitions.

Mosaic uses exactly two local models via Ollama:

  Sidecar 1 — Vision model (moondream2, 1.8B)
    Reads pixel tiles visually. Produces descriptions and embeddings.
    Never sees raw text — only images.

  Sidecar 2 — Language model (qwen2.5:1.5b)
    Drives the agentic loop. Evaluates retrieval, reformulates queries,
    synthesizes answers. Operates on tile metadata and agent state.

Both models run locally. No cloud API. No model larger than 3B.
"""

VISION_SIDECAR = "moondream2"       # 1.8B — vision, tile embedding
LANGUAGE_SIDECAR = "qwen2.5:1.5b"  # 1.5B — agentic loop decisions

REQUIRED_MODELS = [VISION_SIDECAR, LANGUAGE_SIDECAR]


def check_sidecars() -> dict[str, bool]:
    """Check which sidecar models are available in Ollama."""
    import ollama
    try:
        available = {m["name"] for m in ollama.list()["models"]}
        return {model: model in available for model in REQUIRED_MODELS}
    except Exception:
        return {model: False for model in REQUIRED_MODELS}
