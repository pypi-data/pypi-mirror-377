# Perceptron SDK

Python SDK and CLI for perceptive-language models. The SDK is provider-agnostic and lets you compose visual + language tasks, run them locally for inspection, or execute them via a configured provider. Choose a provider and optional model per call; keep your application code stable across model updates.

---

## Installation
- Prerequisites: Python 3.10+, `pip` 23+ (or [`uv`](https://github.com/astral-sh/uv))

```bash
pip install perceptron

# Optional extras
pip install "perceptron[torch]"   # TensorStream helpers (requires PyTorch)
pip install "perceptron[dev]"     # Dev tools (ruff, pytest, pre-commit)
```

Using `uv`:
```bash
uv pip install perceptron
uv pip install "perceptron[torch]"
uv pip install "perceptron[dev]"
```

The CLI entry point `perceptron` is available after install.

---

## Configuration
Set credentials and defaults via environment, programmatically, or the CLI. The SDK ships with a `fal` provider; you can add others by extending `perceptron.client._PROVIDER_CONFIG`.

- `PERCEPTRON_PROVIDER`: provider identifier (default `fal`)
- `PERCEPTRON_API_KEY`: API key for the selected provider
- `PERCEPTRON_BASE_URL`: override provider base URL when needed
- `FAL_KEY`: alternative env var used when `provider=fal`

Programmatic configuration:
```python
from perceptron import configure, config

configure(provider="fal", api_key="sk_live_...", base_url="https://api.example/v1")

with config(max_tokens=512):
    ...  # temporary overrides inside the context
```

CLI helper:
```bash
perceptron config --provider fal --api-key sk_live_...
```

No credentials? Helpers return compile-only payloads so you can inspect tasks without sending requests.

---

## Python Quickstart
```python
from perceptron import caption, detect

# Caption an image (provider default model)
result = caption("/path/to/image.png", style="concise")
print(result.text)

# Stream grounded detections; optionally select a specific model
for event in detect("local.png", classes=["person", "forklift"], model="perceptron", stream=True):
    if event["type"] == "text.delta":
        print("chunk", event["chunk"])
    elif event["type"] == "points.delta":
        print("bbox", event["points"])
    elif event["type"] == "final":
        print("final", event["result"]["points"])
```

### Few-shot detection from COCO
```python
from perceptron import detect_from_coco

runs = detect_from_coco(
    "/datasets/demo",
    split="train",
    shots=4,                 # build balanced in-context examples automatically
    classes=["defect", "ok"],
)

for sample in runs:
    print(sample.image_path.name)
    for box in sample.result.points or []:
        print(" -", box.mention, box)
```

---

## CLI Usage
The CLI mirrors the high-level helpers and supports directory batching (JSON summaries written alongside input folders).

```bash
# Generate captions
perceptron caption image.jpg
perceptron caption ./images --style detailed

# OCR with a custom prompt
perceptron ocr schematic.png --prompt "Extract component labels"

# Batched detection (writes detections.json)
perceptron detect ./frames --classes defect,warning

# Grounded question answering
perceptron question image.jpg "What stands out?" --expects box --format json
```

Directory mode disables streaming and logs raw responses, plus per-file validation issues.

---

## High-Level APIs
- `caption(image, *, style="concise", stream=False, **kwargs)`
- `ocr(image, *, prompt=None, stream=False, **kwargs)`
- `detect(image, *, classes=None, examples=None, stream=False, **kwargs)`
- `detect_from_coco(dataset_dir, *, split=None, classes=None, shots=0, limit=None, **kwargs)`

Notes
- Pass `model="..."`, `provider="..."`, `max_tokens=...`, etc., through `**kwargs` on any helper.
- `detect_from_coco` discovers annotations, constructs balanced examples when `shots > 0`, and returns `CocoDetectResult` objects.
- For advanced workflows, build tasks with the typed DSL (`text`, `system`, `image`, `point`, `box`, `polygon`, `collection`) and decorate with `@perceive` / `@async_perceive`.

### Using the DSL with `@perceive`
```python
from perceptron import perceive, image, text

@perceive(expects="box")
def describe_landmark(path):
    return image(path) + text("Highlight the main structures in one sentence.")

result = describe_landmark("./landmark.jpg")
print(result.text)
for box in result.points or []:
    print(box.mention, box)

# Inspect the compiled payload without executing the request
print(describe_landmark.inspect("./landmark.jpg"))
```

Set `stream=True` in the decorator to receive incremental events (`text.delta`, `points.delta`, `final`). Swap `expects` to `text`, `point`, or `polygon` when you need alternate structures.

---

## Troubleshooting
| Symptom | Likely Cause | Resolution |
| --- | --- | --- |
| Compile-only result (no text) | Missing provider credentials | Export `FAL_KEY` / `PERCEPTRON_API_KEY` or call `configure(...)` |
| `stream_buffer_overflow` warning | Long streaming responses exceeded buffer | Increase `max_buffer_bytes` via `configure` |
| Empty JSON output in directory mode | No supported image extensions | Ensure files end with `.jpg`, `.png`, `.webp`, `.gif`, `.bmp`, `.tif`, `.tiff`, `.heic`, or `.heif` |
| Bounding-box bounds errors | Inconsistent coordinates or missing `image=` anchors | Validate input annotations and ensure images are attached |

---

## Development
- Install tooling: `python -m pip install -e .[dev]` (or `uv pip install --editable .[dev]`)
- Enable git hooks: `pre-commit install`
- Run all checks: `pre-commit run --all-files`

Repository layout
- `src/perceptron` – core SDK and DSL
- `tests` – high-level API and DSL tests

---

## License
Model weights are released under the Creative Commons Attribution-NonCommercial 4.0 International License. For commercial licensing, contact sales@perceptron.inc.

## Contacts & Support
- Technical: [support@perceptron.inc](mailto:support@perceptron.inc)
- Commercial: [sales@perceptron.inc](mailto:sales@perceptron.inc)
- Careers: [join-us@perceptron.inc](mailto:join-us@perceptron.inc)
