"""
Audio recording and segmentation module.
"""
from pathlib import Path
import wave
from datetime import datetime

def record_audio(segment_sec: int = 300) -> None:
    """
    Record audio from the default input device, segmenting every segment_sec seconds.
    Files are saved under gravações/YYYY-MM-DD_HH-MM-SS/raw_audio_XX.wav
    """
    # Detect unsupported WSL2 environment
    import platform, os as _os
    if platform.system() == 'Linux':
        try:
            if 'microsoft' in _os.read_text('/proc/sys/kernel/osrelease').lower():
                raise RuntimeError(
                    'Audio recording under WSL2 is not supported. '
                    'Please run on a native Linux or Windows host with audio capture support.'
                )
        except Exception:
            pass
    # Audio parameters
    sample_rate = 48000
    channels = 2
    sample_width = 2  # bytes (16-bit PCM)

    # Prepare output directory
    base_dir = Path('gravações')
    now = datetime.now().astimezone()
    session_dir = base_dir / now.strftime('%Y-%m-%d_%H-%M-%S')
    session_dir.mkdir(parents=True, exist_ok=True)

    frames_per_segment = int(segment_sec * sample_rate)
    file_index = 0

    print(f'Recording to {session_dir}. Press Ctrl+C to stop.')
    # Lazy import of sounddevice
    try:
        import sounddevice as sd
    except ImportError:
        raise RuntimeError("sounddevice is required for recording. Install it via 'pip install sounddevice'.")
    # Open input stream
    with sd.InputStream(samplerate=sample_rate, channels=channels, dtype="int16") as stream:
        while True:
            try:
                data, overflow = stream.read(frames_per_segment)
                if overflow:
                    print('Warning: Audio buffer overflowed')
                # Write WAV file
                filename = session_dir / f'raw_audio_{file_index:02d}.wav'
                with wave.open(str(filename), 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(sample_width)
                    wf.setframerate(sample_rate)
                    wf.writeframes(data.tobytes())
                print(f'Saved {filename}')
                file_index += 1
            except KeyboardInterrupt:
                print('Recording stopped by user')
                break
  
def record_audio_from_youtube(url: str, segment_sec: int = 300) -> None:
    """
    Download audio from a YouTube URL, convert to WAV (48 kHz, 16-bit, stereo),
    and segment into chunks of segment_sec seconds.
    Files are saved under gravações/YYYY-MM-DD_HH-MM-SS/raw_audio_XX.wav
    """
    try:
        from yt_dlp import YoutubeDL
    except ImportError:
        raise RuntimeError(
            "yt-dlp is required for downloading from YouTube. "
            "Install it via 'pip install yt-dlp'."
        )
    import tempfile
    import os
    import wave
    from datetime import datetime
    from pathlib import Path
    import shutil

    # Create temporary directory for download and conversion
    tmpdir = tempfile.mkdtemp(prefix="wr_ytdl_")
    try:
        # Download and extract audio as WAV with ffmpeg
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '0'
            }],
            'postprocessor_args': ['-ar', '48000', '-ac', '2', '-sample_fmt', 's16'],
            'quiet': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Determine output WAV path
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            wav_file = base + '.wav'
            if not os.path.exists(wav_file):
                # fallback: find any .wav in tmpdir
                wavs = [f for f in os.listdir(tmpdir) if f.lower().endswith('.wav')]
                if wavs:
                    wav_file = os.path.join(tmpdir, wavs[0])
                else:
                    raise RuntimeError(
                        "Failed to extract WAV audio from YouTube URL"
                    )
        # Open the WAV and segment
        sample_rate = 48000
        channels = 2
        sample_width = 2
        # Prepare output directory
        base_dir = Path('gravações')
        now = datetime.now().astimezone()
        session_dir = base_dir / now.strftime('%Y-%m-%d_%H-%M-%S')
        session_dir.mkdir(parents=True, exist_ok=True)
        with wave.open(wav_file, 'rb') as wf:
            framerate = wf.getframerate()
            nchannels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            n_frames = wf.getnframes()
            frames_per_segment = int(segment_sec * framerate)
            file_index = 0
            for start in range(0, n_frames, frames_per_segment):
                wf.setpos(start)
                frames = wf.readframes(frames_per_segment)
                out_path = session_dir / f'raw_audio_{file_index:02d}.wav'
                with wave.open(str(out_path), 'wb') as out_wf:
                    out_wf.setnchannels(nchannels)
                    out_wf.setsampwidth(sampwidth)
                    out_wf.setframerate(framerate)
                    out_wf.writeframes(frames)
                print(f'Saved {out_path}')
                file_index += 1
    finally:
        # Clean up temporary files
        shutil.rmtree(tmpdir, ignore_errors=True)