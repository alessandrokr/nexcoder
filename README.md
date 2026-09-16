# nexcoder

`nexcoder` is a small coding assistant built around the OpenAI API. It is intended to work with both hosted models and local models served by [llama.cpp](https://github.com/ggml-org/llama.cpp), so you can choose between cloud quality and local, private generation for each task.

The project is at an early stage. The package and command-line entry point are in place; the generation workflow is being built out.

## Why nexcoder?

Most coding tools force you to choose between convenience and control. nexcoder is meant to keep both options available:

- use an OpenAI-compatible cloud endpoint when you want a capable hosted model;
- point the same client at a local llama.cpp server when code should stay on your machine;
- keep the model connection separate from the rest of the coding workflow, making it easy to switch providers.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- an OpenAI API key for cloud generation, or a running llama.cpp server for local generation

## Development setup

Clone the repository and install it with uv:

```bash
uv sync
```

Run the current command-line entry point with:

```bash
uv run nexcoder
```

At the moment this prints a short greeting while the generation commands are being implemented.

## Providers

### OpenAI or another hosted endpoint

The cloud backend will use the standard OpenAI client configuration. Keep credentials in your shell environment rather than committing them to the repository:

```bash
export OPENAI_API_KEY="your-api-key"
```

On Windows PowerShell, the equivalent is:

```powershell
$env:OPENAI_API_KEY = "your-api-key"
```

### Local llama.cpp

llama.cpp can expose a model through its OpenAI-compatible HTTP server. A typical local server looks like this:

```bash
llama-server -m ./models/your-model.gguf --port 8080
```

The client can then use the local base URL, usually `http://localhost:8080/v1`, instead of a hosted provider. No cloud API key is needed for local-only generation.

## Project status

This is an intentionally small starting point rather than a finished coding agent. The next pieces are the provider configuration, prompt and context handling, and a useful CLI around code-generation tasks.

## License

No license has been selected yet.
