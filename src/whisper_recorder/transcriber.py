"""
Transcription and diarization module (to be implemented).
"""
"""
Transcription and diarization module.
"""
import json
from pathlib import Path
import wave
import numpy as np
import torch
import whisper

from .config import load_config

def transcribe_audio(
    model_name: str = None,
    delete_raw: bool = False,
    use_api: bool = False,
) -> None:
    """
    Transcribe recorded audio segments using Whisper.
    Outputs transcription.json and transcription.txt in the session directory.
    """
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        print("Config not found. Please run 'whisper-recorder setup' first.")
        return
    # Choose transcription path: local model or OpenAI API
    if use_api:
        # Check for OpenAI API key
        import os, openai
        key_env = config.get('openai_api', {}).get('key_env', 'OPENAI_API_KEY')
        api_key = os.getenv(key_env)
        if not api_key:
            print(f"Environment variable '{key_env}' not set. Please set your OpenAI API key to use the API.")
            return
        openai.api_key = api_key
        api_model = 'whisper-1'
    else:
        # Local model: determine model name (auto-downgrade on CPU-only)
        model_to_load = model_name or config.get('model')
        if model_name is None and not torch.cuda.is_available():
            print("No CUDA GPU detected, switching to 'small' model for faster CPU inference.")
            model_to_load = 'small'
        print(f"Loading Whisper model '{model_to_load}'...")
        model = whisper.load_model(model_to_load)

    # Find latest session directory
    base_dir = Path('gravações')
    if not base_dir.exists():
        print("No recordings found. Please run 'whisper-recorder record' first.")
        return
    sessions = [p for p in base_dir.iterdir() if p.is_dir()]
    if not sessions:
        print("No recordings found. Please run 'whisper-recorder record' first.")
        return
    session_dir = sorted(sessions)[-1]

    # Gather audio files
    audio_files = sorted(session_dir.glob('raw_audio_*.wav'))
    if not audio_files:
        print(f"No audio segments found in {session_dir}")
        return

    segments_info = []
    # Helper to format timestamps
    def fmt_ts(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    # Transcribe each segment (skip silent chunks)
    SILENCE_RMS_THRESHOLD = 500  # RMS below this is considered silence
    for wav in audio_files:
        # Quick silence detection
        try:
            with wave.open(str(wav), 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
            samples = np.frombuffer(frames, dtype=np.int16)
            rms = float(np.sqrt(np.mean(samples.astype(np.float32)**2)))
        except Exception:
            rms = None
        if rms is not None and rms < SILENCE_RMS_THRESHOLD:
            print(f"Skipping {wav.name} (silence, RMS={rms:.1f})")
            continue
        # Perform transcription
        if use_api:
            print(f"Transcribing {wav.name} via OpenAI Whisper API...")
            with open(wav, 'rb') as audio_f:
                # Using OpenAI Python v1.x interface for audio transcription
                raw_result = openai.audio.transcriptions.create(
                    file=audio_f,
                    model=api_model,
                    response_format='verbose_json'
                )
            # Convert API response to plain dict if necessary
            try:
                result = raw_result.to_dict()
            except Exception:
                result = raw_result
        else:
            print(f"Transcribing {wav.name}...")
            result = model.transcribe(str(wav))
        for seg in result.get('segments', []):
            segments_info.append({
                'segment_file': wav.name,
                'start': seg['start'],
                'end': seg['end'],
                'speaker': 'Pessoa 1',
                'text': seg['text'].strip(),
            })

    # Write JSON
    json_path = session_dir / 'transcription.json'
    with json_path.open('w', encoding='utf-8') as jf:
        json.dump(segments_info, jf, indent=2, ensure_ascii=False)
    print(f"Saved transcription JSON to {json_path}")

    # Write TXT
    txt_path = session_dir / 'transcription.txt'
    with txt_path.open('w', encoding='utf-8') as tf:
        for seg in segments_info:
            ts = fmt_ts(seg['start'])
            tf.write(f"[{ts}] {seg['speaker']}: {seg['text']}\n")
    print(f"Saved transcription TXT to {txt_path}")

    # Optionally delete raw audio
    if delete_raw:
        for wav in audio_files:
            try:
                wav.unlink()
            except Exception:
                pass
        print("Deleted raw audio segments.")