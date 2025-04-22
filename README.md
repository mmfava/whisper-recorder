# whisper-recorder

Recorder and transcriber tool using Whisper for local transcription and optional GPT-4o summarization.

## Installation

Install dependencies using pip:
```bash
# (optional) create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install runtime requirements
pip install -r requirements.txt

# install the package in editable mode
pip install -e .

# install development requirements (pytest)
pip install -r requirements-dev.txt
```

## Usage

Initialize hardware configuration:
```bash
whisper-recorder setup [--force]
```

- Other commands available:
  - `whisper-recorder record --segment-sec N`  # record audio with optional segment length
  - `whisper-recorder transcribe [--model MODEL] [--delete-raw] [--fast] [--use-api]`  # use local Whisper model or OpenAI Whisper API
  - `whisper-recorder summarize --mode reunião|curso|custom [-p "Prompt..."]`
    # generate structured summary:
    #   modo 'reunião'  → lista tópicos, decisões e ações
    #   modo 'curso'     → texto técnico com diagramas Mermaid e blocos de código
    #   modo 'custom'    → usa prompt personalizado fornecido pelo usuário
  - `whisper-recorder run`  (executa pipeline completo: record → transcribe → summarize)

### Output Directory

All generated files (raw audio segments, transcription JSON/TXT, summaries, logs and metrics) are saved under the
`gravações/YYYY-MM-DD_HH-MM-SS/` directory. This directory is gitignored by default and should not be committed.

If you have already added or committed this directory (or the local virtualenv `other/`), you can untrack them:
```bash
git rm -r --cached gravações other
```  

## Managing with uv
If you use `uv` as your project manager, the `pyproject.toml` has PEP 621 metadata:

1. Install or upgrade `uv` (see https://docs.astral.sh/uv):
   ```bash
   pip install uv
   # or use the standalone installer
   ```
2. Install dependencies and create the virtual environment:
   ```bash
   uv lock       # generate lockfile from pyproject.toml
   uv sync       # install dependencies into .venv
   ```
3. Run CLI commands through `uv run` (auto-activates .venv):
   ```bash
   uv run whisper-recorder setup --force
   uv run whisper-recorder record --segment-sec 5  # record from microphone, segment length 5s
   uv run whisper-recorder record --youtube-url https://www.youtube.com/watch?v=0mtXae5HhTE --segment-sec 120  # download and segment YouTube audio
   uv run whisper-recorder transcribe --fast          # fast inference using 'small' model
   uv run whisper-recorder transcribe --model medium  # use specific model
   uv run whisper-recorder transcribe --use-api       # transcription via OpenAI Whisper API
   uv run whisper-recorder summarize --mode reunião   # generate meeting summary
   uv run whisper-recorder summarize --mode curso     # generate course summary
   uv run whisper-recorder summarize --mode custom -p "Seu prompt aqui"  # custom summary via prompt
   ```