# Recommended Ollama Models

Pull with: `ollama pull <model-name>`

## For code generation / bug fixes (local-implementer)

| Model | Size | Best for |
|-------|------|----------|
| `qwen2.5-coder:14b` | ~9 GB | **Recommended** — strong code quality, follows instructions well |
| `qwen2.5-coder:7b` | ~5 GB | Faster on constrained hardware, slightly lower quality |
| `deepseek-coder-v2:16b` | ~9 GB | Strong alternative, good on Python/JS/TS |
| `codellama:13b` | ~7 GB | Older but reliable for straightforward completions |

## For general reasoning / planning (if routing planning local too)

| Model | Size | Best for |
|-------|------|----------|
| `llama3.1:8b` | ~5 GB | Fast general assistant, good instruction following |
| `llama3.1:70b` | ~40 GB | Near-cloud quality if you have the VRAM |
| `mistral:7b` | ~4 GB | Lightweight, fast on CPU |

## Hardware guidance

| VRAM | Recommended model |
|------|------------------|
| 8 GB | `qwen2.5-coder:7b` or `mistral:7b` |
| 16 GB | `qwen2.5-coder:14b` ← sweet spot |
| 24 GB+ | `deepseek-coder-v2:16b` or `llama3.1:70b` (Q4) |
| CPU only | `qwen2.5-coder:7b` with `num_thread` set in Modelfile |

## Verify a model works

```bash
ollama run qwen2.5-coder:14b "Write a Python function that reverses a string"
```
