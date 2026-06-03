import os
import sys
import tempfile
import threading
import time
import wave

os.environ.setdefault("OMP_NUM_THREADS", "4")

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

        _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
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


def transcribe(
    audio_path, model_size="tiny", language="en", beam_size=1, vad_filter=True
):
    global _whisper_model
    load_model(model_size=model_size)
    return _transcribe_internal(audio_path, language, beam_size, vad_filter)


def _transcribe_internal(audio_path, language, beam_size, vad_filter):
    global _whisper_model
    t0 = time.time()
    _log("transcribing...")
    segments, _ = _whisper_model.transcribe(
        audio_path, language=language, beam_size=beam_size, vad_filter=vad_filter
    )
    text = " ".join(seg.text for seg in segments).strip()
    elapsed = time.time() - t0
    _log(f"transcription done in {elapsed:.1f}s: {text[:60]}")
    return text


def record_and_transcribe(
    duration=3, model_size="tiny", language="en", beam_size=1, vad_filter=True
):
    stop_event = threading.Event()
    timer = threading.Timer(duration, stop_event.set)
    timer.start()
    path = record_audio(stop_event=stop_event)
    timer.cancel()
    try:
        return transcribe(
            path,
            model_size=model_size,
            language=language,
            beam_size=beam_size,
            vad_filter=vad_filter,
        )
    finally:
        os.unlink(path)


def record_audio_vad(
    fs=16000,
    silence_timeout=1.5,
    max_duration=30.0,
    stop_event=None,
    aggressiveness=2,
):
    """
    Record audio with VAD-based auto-stop. Returns WAV path when utterance
    completes (silence_timeout seconds of silence after speech), or None
    if no speech detected.

    Keeps a 0.5s pre-roll buffer to capture the start of speech.
    """
    import webrtcvad
    import sounddevice as sd

    vad = webrtcvad.Vad(aggressiveness)
    frame_duration = 30
    frame_samples = int(fs * frame_duration / 1000)

    pre_roll_frames = int(0.5 / (frame_duration / 1000))
    silence_frames_max = int(silence_timeout / (frame_duration / 1000))
    max_total_frames = int(max_duration / (frame_duration / 1000))

    ring_buffer = []
    speech_buffer = []
    silence_frames = 0
    total_frames = 0
    speaking = False
    utterance_buffer = None
    done = False

    def callback(indata, frames, time_info, status):
        nonlocal silence_frames, total_frames, speaking, utterance_buffer, done

        if done:
            return

        frame = indata.copy()
        total_frames += 1

        if total_frames > max_total_frames:
            if speaking:
                utterance_buffer = speech_buffer.copy()
            done = True
            return

        frame_int16 = (frame * 32767).astype(np.int16)
        is_speech = vad.is_speech(frame_int16.tobytes(), fs)

        ring_buffer.append(frame.copy())
        if len(ring_buffer) > pre_roll_frames:
            ring_buffer.pop(0)

        if is_speech:
            silence_frames = 0
            if not speaking:
                speaking = True
                speech_buffer.clear()
                speech_buffer.extend(ring_buffer)
            speech_buffer.append(frame.copy())
        else:
            if speaking:
                speech_buffer.append(frame.copy())
                silence_frames += 1
                if silence_frames >= silence_frames_max:
                    utterance_buffer = speech_buffer.copy()
                    done = True

    stream = sd.InputStream(
        samplerate=fs,
        channels=1,
        callback=callback,
        blocksize=frame_samples,
        dtype="float32",
    )
    stream.start()

    try:
        while not done:
            if stop_event and stop_event.is_set():
                if speaking and not utterance_buffer:
                    utterance_buffer = speech_buffer.copy()
                done = True
                break
            time.sleep(0.05)
    finally:
        stream.stop()
        stream.close()

    if not utterance_buffer:
        return None

    audio = np.concatenate(utterance_buffer).astype(np.float32)
    path = tempfile.mktemp(suffix=".northh.wav")
    _write_wav(path, fs, audio)
    return path


def record_and_transcribe_vad(
    silence_timeout=1.5,
    max_duration=30.0,
    model_size="tiny",
    language="en",
    beam_size=1,
    vad_filter=True,
    stop_event=None,
    live_callback=None,
    live_interval=2.0,
):
    """
    Record with VAD and transcribe with live partial results.

    If live_callback is provided, it receives (text: str, is_final: bool)
    from the audio callback thread (must be thread-safe).

    Returns transcribed text, or empty string if no speech detected.
    """
    import webrtcvad
    import sounddevice as sd

    load_model(model_size=model_size)

    vad = webrtcvad.Vad(2)
    frame_duration = 30
    fs = 16000
    frame_samples = int(fs * frame_duration / 1000)

    pre_roll_frames = int(0.5 / (frame_duration / 1000))
    silence_frames_max = int(silence_timeout / (frame_duration / 1000))
    max_total_frames = int(max_duration / (frame_duration / 1000))
    live_interval_frames = int(live_interval / (frame_duration / 1000))

    ring_buffer = []
    speech_buffer = []
    silence_frames = 0
    total_frames = 0
    speaking = False
    utterance_buffer = None
    done = False
    last_live_frame = 0

    def callback(indata, frames, time_info, status):
        nonlocal silence_frames, total_frames, speaking, utterance_buffer, done
        nonlocal last_live_frame

        if done:
            return

        frame = indata.copy()
        total_frames += 1

        if total_frames > max_total_frames:
            if speaking:
                utterance_buffer = speech_buffer.copy()
            done = True
            return

        frame_int16 = (frame * 32767).astype(np.int16)
        is_speech = vad.is_speech(frame_int16.tobytes(), fs)

        ring_buffer.append(frame.copy())
        if len(ring_buffer) > pre_roll_frames:
            ring_buffer.pop(0)

        if is_speech:
            silence_frames = 0
            if not speaking:
                speaking = True
                speech_buffer.clear()
                speech_buffer.extend(ring_buffer)
            speech_buffer.append(frame.copy())

            if live_callback and is_speech:
                frames_since = total_frames - last_live_frame
                if frames_since >= live_interval_frames:
                    last_live_frame = total_frames
                    partial_audio = np.concatenate(speech_buffer).astype(np.float32)
                    p_path = tempfile.mktemp(suffix=".northh.partial.wav")
                    _write_wav(p_path, fs, partial_audio)
                    try:
                        txt = _transcribe_internal(
                            p_path, language, beam_size, vad_filter
                        )
                        if txt:
                            live_callback(txt, False)
                    except Exception:
                        pass
                    finally:
                        try:
                            os.unlink(p_path)
                        except OSError:
                            pass
        else:
            if speaking:
                speech_buffer.append(frame.copy())
                silence_frames += 1
                if silence_frames >= silence_frames_max:
                    utterance_buffer = speech_buffer.copy()
                    done = True

    stream = sd.InputStream(
        samplerate=fs,
        channels=1,
        callback=callback,
        blocksize=frame_samples,
        dtype="float32",
    )
    stream.start()

    try:
        while not done:
            if stop_event and stop_event.is_set():
                if speaking and not utterance_buffer:
                    utterance_buffer = speech_buffer.copy()
                done = True
                break
            time.sleep(0.05)
    finally:
        stream.stop()
        stream.close()

    if not utterance_buffer:
        return ""

    audio = np.concatenate(utterance_buffer).astype(np.float32)
    path = tempfile.mktemp(suffix=".northh.wav")
    _write_wav(path, fs, audio)
    try:
        text = _transcribe_internal(path, language, beam_size, vad_filter)
        if live_callback and text:
            live_callback(text, True)
        return text
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
