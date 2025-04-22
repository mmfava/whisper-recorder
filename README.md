# whisper-recorder

Ferramenta de gravação e transcrição de áudio local utilizando o modelo Whisper, com suporte opcional à geração de resumos estruturados via GPT-4o.

## 🛠️ Instalação

Instale as dependências com `pip`:

```bash
# (opcional) crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# instale as dependências principais
pip install -r requirements.txt

# instale o pacote em modo editável
pip install -e .

# instale dependências de desenvolvimento (ex: pytest)
pip install -r requirements-dev.txt
```

## 🚀 Uso

Inicialize a configuração de hardware:

```bash
whisper-recorder setup [--force]
```

### 📦 Comandos disponíveis

- `whisper-recorder record --segment-sec N`  
  Grava áudio com duração segmentada em `N` segundos.

- `whisper-recorder transcribe [--model MODEL] [--delete-raw] [--fast] [--use-api]`  
  Transcreve o áudio usando o modelo local do Whisper ou a API da OpenAI.

- `whisper-recorder summarize --mode reunião|curso|custom [-p "Prompt..."]`  
  Gera resumo estruturado com base no tipo de conteúdo:
  - `reunião`: lista tópicos, decisões e ações
  - `curso`: texto técnico com blocos de código e diagramas Mermaid
  - `custom`: permite usar um prompt personalizado

- `whisper-recorder run`  
  Executa o pipeline completo: gravação → transcrição → resumo

### 📂 Diretório de saída

Todos os arquivos gerados (áudio bruto, transcrições em JSON/TXT, resumos, logs e métricas) são salvos em:

```
gravações/YYYY-MM-DD_HH-MM-SS/
```

Este diretório está incluído no `.gitignore` por padrão. Se já tiver adicionado esse diretório (ou o ambiente virtual em `other/`), você pode removê-lo do controle de versão com:

```bash
git rm -r --cached gravações other
```

## ⚡ Uso com `uv`

Se estiver utilizando o [uv](https://docs.astral.sh/uv) como gerenciador de projetos, o arquivo `pyproject.toml` já está configurado com metadados PEP 621.

1. Instale ou atualize o `uv`:
   ```bash
   pip install uv
   # ou utilize o instalador standalone
   ```

2. Instale as dependências e crie o ambiente virtual:
   ```bash
   uv lock       # gera o arquivo de lock
   uv sync       # instala as dependências no .venv
   ```

3. Execute os comandos via `uv run`:
   ```bash
   uv run whisper-recorder setup --force

   uv run whisper-recorder record --segment-sec 5
   uv run whisper-recorder record --youtube-url https://www.youtube.com/watch?v=0mtXae5HhTE --segment-sec 120

   uv run whisper-recorder transcribe --fast
   uv run whisper-recorder transcribe --model medium
   uv run whisper-recorder transcribe --use-api

   uv run whisper-recorder summarize --mode reunião
   uv run whisper-recorder summarize --mode curso
   uv run whisper-recorder summarize --mode custom -p "Seu prompt aqui"
   ```

