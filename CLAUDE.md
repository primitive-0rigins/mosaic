# CLAUDE.md

This is a public GitHub repository under Primitive Origin LLC.

## Privacy Rules

- Never commit real file paths from Meda's machine
- Never commit Ollama host addresses other than the default localhost
- Never commit API keys, tokens, or credentials of any kind
- All example documents and queries use placeholder content only

## What This Repo Is

A showcase of systems-level thinking from Primitive Origin LLC. Mosaic is the first system to combine agentic retrieval, pixel tile ingestion, and hypergraph memory. The code is real and buildable.

## Coding Guidelines

- Python 3.11+. Use `pyproject.toml` for deps — no `requirements.txt`.
- All async code uses `asyncio`. Do not mix threading models.
- Pydantic for data validation at boundaries. Dataclasses for internal structs.
- No model larger than 3B. Both sidecars run local via Ollama — never call a cloud API.
- The vision sidecar (moondream2) reads tiles as images only — never convert tiles to text before embedding.
- The hypergraph is the source of truth for memory — do not build parallel data structures that duplicate it.
- Hyperedges must connect >= 2 nodes. Single-node "edges" are not valid.

## Architecture

See `docs/architecture.md`. Three layers, two sidecars, one hypergraph. Do not add a fourth layer without a clear reason.
