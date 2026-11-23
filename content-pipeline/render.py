#!/usr/bin/env python3
"""Baut aus einem Schnittplan (JSON) ein fertiges TikTok mit HyperFrames.

  render.py <plan.json> [--media <ordner>] [--out <ordner>] [--skip-check]

Ergebnis im Ausgabeordner (Standard: work/out):
  <id>.mp4       Vollversion 1080x1920, 30 fps (für Instagram / Fertig zum Posten)
  <id>_web.mp4   unter config.posting.web_max_mb (für den TikTok-Upload im Browser)
  check_<id>.jpg Kontaktbogen zur Kontrolle

Planformat siehe README.md (Abschnitt "Schnittplan").
"""
import argparse
import html
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HF = "hyperframes@0.8.174"
W, H = 1080, 1920
PHOTO = {".jpg", ".jpeg", ".png", ".heic", ".webp"}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"Fehler bei {' '.join(cmd[:3])}...\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r.stdout


def cover(focus_x, w=W, h=H):
    """Auf 9:16 füllen, horizontal nach focus_x (0 links, 1 rechts) zuschneiden."""
    return (f"scale=w='if(gt(a,{w}/{h}),-2,{w})':h='if(gt(a,{w}/{h}),{h},-2)',"
            f"crop={w}:{h}:'(in_w-{w})*{focus_x}':'(in_h-{h})/2'")


def prep_video(src, seg, dst):
    speed = float(seg.get("speed", 1.0))
    dur = float(seg["dur"])
    vf = f"setpts=PTS/{speed},{cover(seg.get('focus_x', 0.5))},fps=30,format=yuv420p"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(seg.get("start", 0)), "-t", f"{dur * speed + 0.3:.3f}",
         "-i", src, "-vf", vf, "-t", f"{dur:.3f}", "-an", "-c:v", "libx264", "-crf", "17", "-preset", "fast", dst])


def prep_photo(src, seg, dst):
    if src.lower().endswith(".heic"):
        sys.path.insert(0, HERE)
        from sheets import photo_to_jpg
        src = photo_to_jpg(src, dst + ".src.jpg")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", cover(seg.get("focus_x", 0.5)), "-q:v", "2", dst])


def still_from(src, at, focus_x, dst):
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(at), "-i", src, "-frames:v", "1",
         "-vf", cover(focus_x), "-q:v", "2", dst])


def font_size(lines, base=78):
    longest = max((len(s) for s in lines), default=1)
    return int(min(base, 930 / (0.6 * longest)))


def caption_html(cid, lines, start, dur, accent_first):
    size = font_size(lines)
    spans = []
    for i, line in enumerate(lines):
        cls = "box accent" if (i == 0 and accent_first) else "box"
        spans.append(f'<span class="{cls}" style="font-size:{size}px">{html.escape(line)}</span>')
    return (f'<div id="{cid}" class="clip caption" data-start="{start:.3f}" data-duration="{dur:.3f}" '
            f'data-track-index="2">{"".join(spans)}</div>')


def build(plan, media_dir, build_dir):
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    assets = os.path.join(build_dir, "assets")
    shutil.copytree(os.path.join(HERE, "template", "assets"), assets)
    shutil.copy(os.path.join(HERE, "template", "hyperframes.json"), build_dir)

    scenes, captions, tweens = [], [], []
    t = 0.0
    last = None
    for k, seg in enumerate(plan["segments"]):
        src = os.path.join(media_dir, seg["src"])
        if not os.path.exists(src):
            sys.exit(f"Datei fehlt: {src}")
        dur = float(seg["dur"])
        is_photo = os.path.splitext(src)[1].lower() in PHOTO
        if is_photo:
            name = f"seg{k:02d}.jpg"
            prep_photo(src, seg, os.path.join(assets, name))
            z = float(seg.get("zoom", 1.08))
            scenes.append(f'<div id="s{k}" class="clip scene" data-start="{t:.3f}" data-duration="{dur:.3f}" '
                          f'data-track-index="0"><img id="i{k}" src="assets/{name}" alt="" /></div>')
            a, b = (1.0, z) if k % 2 == 0 else (z, 1.0)
            tweens.append(f'tl.fromTo("#i{k}", {{scale:{a}}}, {{scale:{b}, duration:{dur:.3f}, ease:"none"}}, {t:.3f});')
        else:
            name = f"seg{k:02d}.mp4"
            prep_video(src, seg, os.path.join(assets, name))
            scenes.append(f'<video id="v{k}" class="clip scene" src="assets/{name}" data-start="{t:.3f}" '
                          f'data-duration="{dur:.3f}" data-media-start="0" data-track-index="0" playsinline muted></video>')
        if seg.get("text"):
            cid = f"c{k}"
            captions.append(caption_html(cid, seg["text"], t, dur, seg.get("accent_first", False)))
            tweens.append(f'tl.fromTo("#{cid} .box", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:0.3, '
                          f'ease:"power3.out", stagger:0.07}}, {t + 0.05:.3f});')
        last = (src, seg, is_photo)
        t += dur

    end = plan.get("end")
    if end:
        dur = float(end.get("dur", 2.6))
        src = os.path.join(media_dir, end["src"]) if end.get("src") else last[0]
        seg = end if end.get("src") else last[1]
        bg = os.path.join(assets, "end.jpg")
        if os.path.splitext(src)[1].lower() in PHOTO:
            prep_photo(src, seg, bg)
        else:
            still_from(src, float(seg.get("start", 0)) + float(seg.get("dur", 0)) * 0.8, seg.get("focus_x", 0.5), bg)
        lines = "".join(f'<div class="end-line">{html.escape(s)}</div>' for s in end.get("lines", []))
        scenes.append(
            f'<div id="endcard" class="clip scene" data-start="{t:.3f}" data-duration="{dur:.3f}" data-track-index="0">'
            f'<img id="end-bg" src="assets/end.jpg" alt="" /><div class="end-dim"></div>'
            f'<div class="end-card"><div class="end-brand">JONIS</div><div class="end-sub">Pizza Catering</div>'
            f'<div class="end-lines">{lines}</div><div class="end-url">jonis-catering.de</div></div></div>')
        tweens.append(f'tl.fromTo("#endcard .end-card > div", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.4, '
                      f'ease:"power3.out", stagger:0.1}}, {t + 0.1:.3f});')
        tweens.append(f'tl.fromTo("#end-bg", {{scale:1.0}}, {{scale:1.06, duration:{dur:.3f}, ease:"none"}}, {t:.3f});')
        t += dur

    with open(os.path.join(HERE, "template", "index.html")) as f:
        page = f.read()
    page = (page.replace("{{DURATION}}", f"{t:.3f}")
                .replace("{{SCENES}}", "\n      ".join(scenes))
                .replace("{{CAPTIONS}}", "\n      ".join(captions))
                .replace("{{TWEENS}}", "\n      ".join(tweens)))
    with open(os.path.join(build_dir, "index.html"), "w") as f:
        f.write(page)
    return t


def finish(raw, out_dir, vid, web_max_mb):
    full = os.path.join(out_dir, f"{vid}.mp4")
    web = os.path.join(out_dir, f"{vid}_web.mp4")
    silence = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest"]
    run(["ffmpeg", "-v", "error", "-y", "-i", raw] + silence +
        ["-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", full])
    for kbps in (3800, 3200, 2600, 2000):
        run(["ffmpeg", "-v", "error", "-y", "-i", raw] + silence +
            ["-c:v", "libx264", "-preset", "medium", "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.15)}k",
             "-bufsize", f"{kbps * 2}k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
             "-movflags", "+faststart", web])
        if os.path.getsize(web) / 1e6 < web_max_mb:
            break
    run(["ffmpeg", "-v", "error", "-y", "-i", full, "-vf",
         "fps=21/" + run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", full]).strip()
         + ",scale=216:384,tile=7x3", "-frames:v", "1", os.path.join(out_dir, f"check_{vid}.jpg")])
    return full, web


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--media", default=os.path.join(HERE, "work", "media"))
    ap.add_argument("--out", default=os.path.join(HERE, "work", "out"))
    ap.add_argument("--skip-check", action="store_true")
    a = ap.parse_args()
    with open(a.plan) as f:
        plan = json.load(f)
    with open(os.path.join(HERE, "config.json")) as f:
        cfg = json.load(f)
    vid = plan["id"]
    build_dir = os.path.join(HERE, "work", "build", vid)
    os.makedirs(a.out, exist_ok=True)
    dur = build(plan, a.media, build_dir)
    if not a.skip_check:
        out = run(["npx", "--yes", HF, "check"], cwd=build_dir)
        if "Check passed" not in out:
            sys.exit(out[-3000:])
        tail = out.split("Contrast", 1)[-1].split("Snapshots", 1)[0]
        if "✗" in tail:
            print("Hinweis Kontrast:\n" + tail.strip())
    raw = os.path.join(build_dir, "render.mp4")
    run(["npx", "--yes", HF, "render", "-q", "high", "-f", "30", "-o", raw], cwd=build_dir)
    full, web = finish(raw, a.out, vid, cfg["posting"]["web_max_mb"])
    print(json.dumps({"id": vid, "duration": round(dur, 2), "full": full, "web": web,
                      "web_mb": round(os.path.getsize(web) / 1e6, 2),
                      "check": os.path.join(a.out, f"check_{vid}.jpg")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
