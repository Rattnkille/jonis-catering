#!/usr/bin/env python3
"""Kontaktbögen zum Sichten von Rohmaterial.

  sheets.py <medienordner> <ausgabeordner>

Pro Video ein Bogen mit 12 Bildern und Zeitstempel, für alle Fotos zusammen
Bögen mit Dateinamen. Schreibt zusätzlich index.json (Name, Art, Dauer, Format),
damit Schnittpläne die echten Längen kennen.
"""
import json
import os
import subprocess
import sys

VIDEO = {".mov", ".mp4", ".m4v", ".webm"}
PHOTO = {".jpg", ".jpeg", ".png", ".heic", ".webp"}


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height:stream_side_data=rotation:format=duration", "-of", "json", path],
        capture_output=True, text=True).stdout
    data = json.loads(out or "{}")
    st = (data.get("streams") or [{}])[0]
    w, h = st.get("width", 0), st.get("height", 0)
    rot = next((abs(int(s.get("rotation", 0))) for s in st.get("side_data_list", []) if "rotation" in s), 0)
    if rot in (90, 270):
        w, h = h, w
    return float(data.get("format", {}).get("duration", 0) or 0), w, h


def photo_to_jpg(src, dst):
    """HEIC und Co. in JPG wandeln (pillow-heif), sonst ffmpeg."""
    if src.lower().endswith(".heic"):
        from PIL import Image
        import pillow_heif
        pillow_heif.register_heif_opener()
        im = Image.open(src)
        from PIL import ImageOps
        ImageOps.exif_transpose(im).convert("RGB").save(dst, quality=92)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-q:v", "2", dst], check=True)
    return dst


def main(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    index, photos = [], []
    for name in sorted(os.listdir(src_dir)):
        path = os.path.join(src_dir, name)
        ext = os.path.splitext(name)[1].lower()
        if ext in VIDEO:
            dur, w, h = probe(path)
            index.append({"name": name, "kind": "video", "duration": round(dur, 2), "width": w, "height": h})
            n = 12
            vf = (f"fps={n}/{max(dur, 0.5):.3f},scale=-2:320,"
                  "drawtext=text='%{pts\\:hms}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black,"
                  "tile=6x2")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", vf, "-frames:v", "1",
                            os.path.join(out_dir, f"video_{name}.jpg")])
        elif ext in PHOTO:
            jpg = path
            if ext in {".heic", ".png", ".webp"}:
                os.makedirs(os.path.join(out_dir, "_conv"), exist_ok=True)
                jpg = photo_to_jpg(path, os.path.join(out_dir, "_conv", os.path.splitext(name)[0] + ".jpg"))
            _, w, h = probe(jpg)
            index.append({"name": name, "kind": "photo", "width": w, "height": h})
            photos.append((name, jpg))
    for i in range(0, len(photos), 12):
        chunk = photos[i:i + 12]
        cmd = ["ffmpeg", "-v", "error", "-y"]
        for _, p in chunk:
            cmd += ["-i", p]
        parts = "".join(
            f"[{k}:v]scale=300:400:force_original_aspect_ratio=decrease,pad=300:400:(ow-iw)/2:(oh-ih)/2,"
            f"drawtext=text='{os.path.splitext(n)[0][:18]}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black[p{k}];"
            for k, (n, _) in enumerate(chunk))
        pads = "".join(f"[p{k}]" for k in range(len(chunk)))
        cols = min(6, len(chunk))
        rows = (len(chunk) + cols - 1) // cols
        layout = "|".join(f"{(k % cols) * 300}_{(k // cols) * 400}" for k in range(len(chunk)))
        fc = parts + (f"{pads}xstack=inputs={len(chunk)}:layout={layout}:fill=black[o]" if len(chunk) > 1
                      else "[p0]null[o]")
        subprocess.run(cmd + ["-filter_complex", fc, "-map", "[o]", "-frames:v", "1",
                              os.path.join(out_dir, f"fotos_{i // 12 + 1:02d}.jpg")])
    with open(os.path.join(out_dir, "index.json"), "w") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"{len(index)} Dateien, Bögen in {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
