"""Debug STT: find fastest config for this CPU."""

import os
import sys
import tempfile
import time
import wave

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _write_wav(path, fs, audio):
    audio = (audio * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fs)
        w.writeframes(audio.tobytes())


if __name__ == "__main__":
    print("=" * 60)
    print("STT Performance Debug")
    print("=" * 60)

    import multiprocessing

    print(f"\nCPU cores: {multiprocessing.cpu_count()}")

    # Record some audio once, reuse for all transcription tests
    import sounddevice as sd

    fs = 16000
    dur = 4
    print(f"\nRecording {dur}s of audio (speak during this)...")
    audio = sd.rec(int(fs * dur), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    path = tempfile.mktemp(suffix=".stt-test.wav")
    _write_wav(path, fs, audio.flatten())
    print(f"WAV: {os.path.getsize(path)} bytes")

    from faster_whisper import WhisperModel

    configs = [
        ("int8", {}),
        ("int8", {"num_workers": 2}),
        ("int8", {"num_workers": 4}),
        ("int8", {"cpu_threads": 2}),
        ("int8", {"cpu_threads": 4}),
        ("float32", {}),
        ("float32", {"num_workers": 4}),
    ]

    print(
        f"\n{'compute':16s} {'opts':30s} {'load':>6s} {'transcribe':>10s} {'xRT':>6s} {'text':30s}"
    )
    print("-" * 100)

    for ct, opts in configs:
        opt_str = str(opts) if opts else ""
        try:
            t0 = time.time()
            model = WhisperModel("tiny", device="cpu", compute_type=ct, **opts)
            t1 = time.time()
            load_t = t1 - t0

            t2 = time.time()
            segments, _ = model.transcribe(path)
            text = " ".join(seg.text for seg in segments).strip()
            t3 = time.time()
            transcribe_t = t3 - t2

            xrt = dur / transcribe_t if transcribe_t > 0 else 0
            print(
                f"{ct:16s} {opt_str:30s} {load_t:5.2f}s {transcribe_t:8.2f}s {xrt:5.1f}x {text[:30]:30s}"
            )
        except Exception as e:
            print(f"{ct:16s} {opt_str:30s} {'N/A':>6s} {'FAILED':>10s}")

    os.unlink(path)
    print("\nDone.")
