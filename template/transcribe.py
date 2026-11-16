import json, sys, glob, os, subprocess
import numpy as np
from faster_whisper import WhisperModel
model = WhisperModel("medium", device="cpu", compute_type="int8")
out = {}
for path in sorted(glob.glob(sys.argv[1] + "/*.mp3")):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    segments, _ = model.transcribe(audio, language="ar", word_timestamps=True, beam_size=5)
    words = []
    for s in segments:
        for w in s.words:
            words.append({"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)})
    name = os.path.basename(path)
    out[name] = words
    print(name, " ".join(x["w"] for x in words), flush=True)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
