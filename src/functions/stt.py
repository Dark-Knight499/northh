import os
import tempfile
import threading
import wave

import numpy as np

_whisper_model = None
_MODEL_LOCK = threading.Lock()


def _write_wav(path, fs, audio):
    audio = (audio * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fs)
        w.writeframes(audio.tobytes())


def record_audio(fs=16000, stop_event=None):
    import sounddevice as sd

    if stop_event is None:
        stop_event = threading.Event()

    chunks = []

    def callback(indata, frames, time, status):
        if status:
            print(f"recording status: {status}", file=__import__("sys").stderr)
        chunks.append(indata.copy())

    stream = sd.InputStream(
        samplerate=fs, channels=1, callback=callback, blocksize=1024
    )
    stream.start()
    stop_event.wait()
    stream.stop()
    stream.close()

    audio = np.concatenate(chunks) if chunks else np.zeros((0,), dtype=np.float32)
    path = tempfile.mktemp(suffix=".northh.wav")
    _write_wav(path, fs, audio)
    return path


def transcribe(audio_path, model_size="tiny", language=None):
    global _whisper_model
    if _whisper_model is None:
        with _MODEL_LOCK:
            if _whisper_model is None:
                from faster_whisper import WhisperModel

                _whisper_model = WhisperModel(
                    model_size, device="cpu", compute_type="int8"
                )

    segments, _ = _whisper_model.transcribe(audio_path, language=language)
    return " ".join(seg.text for seg in segments).strip()


def record_and_transcribe(duration=5, model_size="tiny", language=None):
    stop_event = threading.Event()
    timer = threading.Timer(duration, stop_event.set)
    timer.start()
    path = record_audio(stop_event=stop_event)
    timer.cancel()
    try:
        return transcribe(path, model_size=model_size, language=language)
    finally:
        os.unlink(path)
