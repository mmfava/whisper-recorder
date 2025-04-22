import json
import typer

from .hardware import detect_hardware, compute_hardware_hash
from .config import save_config, get_config_file

app = typer.Typer(name="whisper-recorder")

@app.command()
def setup(
    force: bool = typer.Option(False, "--force", help="Force re-run setup")
):
    """
    Detect hardware and create configuration file.
    """
    # Determine config file location (respects XDG_CONFIG_HOME)
    config_path = get_config_file()
    detected = detect_hardware()
    hardware_hash = compute_hardware_hash(detected)
    if config_path.exists() and not force:
        try:
            existing = json.loads(config_path.read_text(encoding="utf-8"))
            if existing.get("hardware_hash") == hardware_hash:
                typer.echo("Hardware configuration unchanged. Use --force to overwrite.")
                raise typer.Exit()
        except Exception:
            pass
    # Heuristic for model selection
    vram = detected.get("vram_gb", 0.0) or 0.0
    cpu = detected.get("cpu_cores", 0)
    ram = detected.get("ram_gb", 0.0) or 0.0
    if vram >= 8.0:
        model = "large-v3"
    elif vram >= 4.0 or (cpu >= 8 and ram >= 16.0):
        model = "medium"
    else:
        model = "small"
    # Default configuration: openai_api enabled for summarization
    config = {
        "model": model,
        "hardware_hash": hardware_hash,
        "detected": detected,
        "openai_api": {"enabled": True, "key_env": "OPENAI_API_KEY"}
    }
    save_config(config)
    typer.echo(f"Configuration saved to {config_path}")

@app.command()
def record(
    segment_sec: int = typer.Option(300, "--segment-sec", help="Segment length in seconds"),
    youtube_url: str = typer.Option(
        None,
        "--youtube-url",
        help="YouTube URL to download and ingest audio instead of live recording"
    ),
):
    """
    Record audio from available inputs, or ingest audio from a YouTube URL, segmenting every N seconds.
    """
    if youtube_url:
        from .recorder import record_audio_from_youtube
        record_audio_from_youtube(youtube_url, segment_sec)
    else:
        from .recorder import record_audio
        record_audio(segment_sec=segment_sec)
    
@app.command()
def transcribe(
    model: str = typer.Option(
        None,
        "--model",
        help="Override Whisper model for local inference (e.g. tiny, small, medium, large-v3)"
    ),
    delete_raw: bool = typer.Option(
        False,
        "--delete-raw",
        help="Delete raw audio after transcription"
    ),
    fast: bool = typer.Option(
        False,
        "--fast",
        help="Alias for --model small: use small model for faster CPU inference"
    ),
    use_api: bool = typer.Option(
        False,
        "--use-api",
        help="Use OpenAI Whisper API for transcription instead of local model"
    ),
):
    """
    Transcribe recorded audio segments using Whisper (local or via OpenAI API).
    """
    # Determine mode: API takes precedence
    if use_api:
        if fast or model:
            typer.echo("Warning: --use-api specified, ignoring --model/--fast options and using OpenAI API.")
        selected_model = None
    else:
        # Determine local model override: --fast takes precedence
        if fast:
            if model:
                typer.echo("Warning: --fast specified, ignoring --model option and using 'small'.")
            selected_model = 'small'
        else:
            selected_model = model
    from .transcriber import transcribe_audio
    transcribe_audio(
        model_name=selected_model,
        delete_raw=delete_raw,
        use_api=use_api,
    )
    
@app.command()
def summarize(
    mode: str = typer.Option(
        ..., "--mode", "-m",
        help="Modo de resumo: 'reunião', 'curso' ou 'custom'"
    ),
    prompt: str = typer.Option(
        None, "--prompt", "-p",
        help="Prompt customizado (obrigatório se modo='custom')"
    ),
):
    """
    Gerar resumo a partir da transcrição usando GPT-4o via API OpenAI.
    """
    from .summarizer import summarize_transcription
    summarize_transcription(mode=mode, prompt=prompt)