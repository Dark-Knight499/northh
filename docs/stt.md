# Speech-to-Text

North supports offline speech-to-text via `faster-whisper` (tiny model) + `sounddevice`.

## Recording Modes

Two modes, toggled via `Ctrl+T` (persisted to settings):

### Push-to-Talk (default)

Press `Ctrl+R` to start recording — `Ctrl+R` again to stop and transcribe.

```
Capture → [Ctrl+R]
  → recording... [●] (listening)
  → [Ctrl+R] again
  → transcribing...
  → text appears in editor
```

### Live

Press `Ctrl+R` once — automatically detects when you stop speaking (1.5s silence) and transcribes. Partial results appear every ~2s during speech.

```
Capture → [Ctrl+R]
  → listening... (waiting for speech)
  → speech detected → recording... [●]
  → partial text appears live
  → silence detected → transcribing...
  → final text replaces partial
```

## Keybindings

| Key       | Action                       |
|-----------|------------------------------|
| Ctrl+R    | Start / stop recording       |
| Ctrl+L    | Toggle language (EN / HI)    |
| Ctrl+T    | Toggle mode (PTT / LIVE)     |

## CLI Usage

```bash
northh idea --voice                  # English (default)
northh idea --voice --lang hi        # Hindi
northh project myproj --voice        # Project entry via speech
northh domain mydom --voice --lang hi
northh journal --voice
```

## Language Support

| Flag       | Language |
|------------|----------|
| `--lang en` | English  |
| `--lang hi` | Hindi    |

Language is passed directly to the model — no detection pass, so speed is identical for both.

## Settings

Stored in `~/.northh/settings.json`:

```json
{
  "stt_mode": "push-to-talk"
}
```

Toggle via `Ctrl+T` in the Capture screen.

## Architecture

### `src/functions/stt.py`

| Function                     | Purpose                                  |
|------------------------------|------------------------------------------|
| `load_model()`               | Pre-warm whisper model in background     |
| `record_audio()`             | Raw recording with stop_event (PTT)      |
| `transcribe()`               | Transcribe a WAV file                    |
| `_transcribe_internal()`     | Shared transcription core                |
| `record_and_transcribe()`    | Timer-based recording + transcribe       |
| `record_audio_vad()`         | VAD-based recording with auto-stop       |
| `record_and_transcribe_vad()`| VAD recording + live partial results     |

### `src/functions/settings.py`

JSON-based persistent settings at `~/.northh/settings.json`.

## Performance Notes

- `beam_size=1`: 3-5x speedup over default `beam_size=5`
- `language="en"` / `language="hi"`: skips language detection
- `OMP_NUM_THREADS=4`: matches physical cores (Ryzen 5 3450U)
- `compute_type="int8"`: fastest on CPU (float16 not supported on this CPU)
- `vad_filter=True`: removes silent segments before transcription
- First model load: ~1.9s, subsequent: ~0.7s
- Tiny model transcribes at roughly 1x real-time on this CPU
