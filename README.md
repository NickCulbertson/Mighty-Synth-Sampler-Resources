# Mighty Synth Sampler Resources

This is the start of the Mighty Synth Sampler Resources repo. Here you'll find links to videos, scripts, and examples to help you get the most out of the app.

---

## `convert_to_wv.py` Normalize and compress samples to WavPack

A Python script that walks a folder of `.wav` files, peak-normalizes each one to 0 dB, then converts to WavPack (`.wv`) lossless compression. Useful when preparing sound packs for distribution, smaller files, no quality loss, and Mighty Synth Sampler auto-detects `.wv` files when present.

### What it does

1. Scans the current directory **and all subdirectories** for `.wav` files
2. Encodes each `.wav` to `.wv` using `wavpack`
3. Leaves the original `.wav` and the new `.wv` side by side. Mighty Synth Sampler automatically uses the `.wv` when both are present, so your SFZ files don't need any changes.

The script is **non-destructive by default** your original `.wav` files are unchanged.

### Optional behaviors (off by default)

Two toggles at the top of the script:

- **Peak-normalize to 0 dB before converting** set `NORMALIZE_BEFORE_CONVERT = True`. Each `.wav` is analyzed via `ffmpeg` and gain is applied so its peak hits 0 dB. ⚠️ This modifies the original `.wav` file in place. Back up first if you want to keep pristine originals.
- **Delete originals after conversion** uncomment the `os.remove(wav_path)` line near the end of `convert_to_wv()`. Useful when prepping a pack for distribution where you only want the `.wv` files shipped.

### Requirements

- **Python 3** (preinstalled on modern macOS; otherwise `brew install python`)
- **Homebrew** (for the next two dependencies) install from [brew.sh](https://brew.sh)
- **WavPack** `brew install wavpack`
- **FFmpeg** `brew install ffmpeg`

### Setup

1. Install the dependencies above
2. **Check your `wavpack` path**:
   ```bash
   which wavpack
   ```
   - On **Apple Silicon Macs** (M1/M2/M3/M4): the path is usually `/opt/homebrew/bin/wavpack`
   - On **Intel Macs**: the path is usually `/usr/local/bin/wavpack`
3. **Edit `convert_to_wv.py` line 9** to match your machine's path:
   ```python
   WAVPACK_PATH = '/opt/homebrew/bin/wavpack'   # Apple Silicon
   # or
   WAVPACK_PATH = '/usr/local/bin/wavpack'      # Intel
   ```

### Usage

1. Copy `convert_to_wv.py` into the folder containing your `.wav` samples (or a parent folder, it walks subdirectories)
2. Open Terminal, `cd` to that folder, and run:
   ```bash
   python3 convert_to_wv.py
   ```
3. Watch the console for progress. Each file logs its conversion result.

### Tweaking the script

A few values in the script you can adjust:

- **`WAVPACK_FLAGS = ['-q', '-r', '-b24']`** (line 13) `-q` quiet, `-r` adds runtime checksum, `-b24` forces 24-bit. For maximum lossless compression replace with `['-hh']` (slightly slower encoding, ~5–10% smaller files).
- **Normalization threshold** (line 59) `if abs(gain) < 0.1` skips files needing less than 0.1 dB gain. Increase to skip more aggressively.
- **Parallel workers** (line 138) `max_workers=4` runs 4 conversions at once. Increase on faster machines; decrease if your machine struggles.

### Why use `.wv` for sound packs?

WavPack is a **lossless** compression format. Typical compression ratio: 30–70% smaller than the source `.wav` with bit-perfect audio. Mighty Synth Sampler reads `.wv` files natively, if a `.wv` exists next to a `.wav` referenced in your SFZ, the app uses the `.wv` automatically. Your SFZ files don't need any changes.

---

## More resources

More videos, scripts, and examples coming. If you have a request or want to contribute, get in touch via [mobypixel.com](http://www.mobypixel.com).
