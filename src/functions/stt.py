import os
import sys
import tempfile
import threading
import time
import wave

import numpy as np

_whisper_model = None
_MODEL_LOCK = threading.Lock()
_MODEL_LOADED = threading.Event()


def _log(msg):
    print(f"[stt] {msg}", file=sys.stderr, flush=True)


def _write_wav(path, fs, audio):
    audio = (audio * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fs)
        w.writeframes(audio.tobytes())


def load_model(model_size="tiny"):
    global _whisper_model
    if _whisper_model is not None:
        return
    with _MODEL_LOCK:
        if _whisper_model is not None:
            return
        t0 = time.time()
        _log(f"loading whisper model '{model_size}'...")
        from faster_whisper import WhisperModel

        _whisper_model = WhisperModel(model_size, device="cpu", compute_type="default")
        elapsed = time.time() - t0
        _log(f"model loaded in {elapsed:.1f}s")
        _MODEL_LOADED.set()


def record_audio(fs=16000, stop_event=None):
    import sounddevice as sd

    if stop_event is None:
        stop_event = threading.Event()

    _log("starting recording...")
    chunks = []

    def callback(indata, frames, time, status):
        if status:
            _log(f"recording status: {status}")
        chunks.append(indata.copy())

    stream = sd.InputStream(
        samplerate=fs, channels=1, callback=callback, blocksize=1024
    )
    stream.start()
    stop_event.wait()
    stream.stop()
    stream.close()

    duration = len(chunks) * 1024 / fs if chunks else 0
    _log(f"recording stopped ({len(chunks)} chunks, {duration:.1f}s)")

    audio = np.concatenate(chunks) if chunks else np.zeros((0,), dtype=np.float32)
    path = tempfile.mktemp(suffix=".northh.wav")
    _write_wav(path, fs, audio)
    return path


def transcribe(audio_path, model_size="tiny", language=None):
    global _whisper_model
    load_model(model_size=model_size)

    t0 = time.time()
    _log("transcribing...")
    segments, _ = _whisper_model.transcribe(audio_path, language=language)
    text = " ".join(seg.text for seg in segments).strip()
    elapsed = time.time() - t0
    _log(f"transcription done in {elapsed:.1f}s: {text[:60]}")
    return text


def record_and_transcribe(duration=3, model_size="tiny", language=None):
    stop_event = threading.Event()
    timer = threading.Timer(duration, stop_event.set)
    timer.start()
    path = record_audio(stop_event=stop_event)
    timer.cancel()
    try:
        return transcribe(path, model_size=model_size, language=language)
    finally:
        os.unlink(path)
