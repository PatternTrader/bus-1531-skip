#!/usr/bin/env python3
"""Render the 11 AM bus 1531 SKIP stickers: animated GIF + WhatsApp-ready animated WebP (512x512).

Everything is drawn on a white background. Transparent edges come out black in WhatsApp,
so the rounded card sits on white instead.
"""
import os, subprocess, pathlib, shutil, tempfile
from PIL import Image
HERE = pathlib.Path(__file__).resolve().parent
CHROME = next((c for c in ["google-chrome", "chromium", "chromium-browser",
                           "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"]
               if shutil.which(c) or pathlib.Path(c).exists()), "google-chrome")
ROOT = ["--no-sandbox"] if os.geteuid() == 0 else []  # Chrome refuses its sandbox as root
SIZE = 512
STOPS = ["93", "84", "82", "59", "55", "51", "41", "36", "23", "16", "12"]
FRAMES, MS = 10, 200
def flatten(im):
    """Crop to the tile and drop alpha onto white; WhatsApp paints transparent pixels black."""
    im = im.convert("RGBA").crop((0, 0, SIZE, SIZE))
    bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im); return bg
out = HERE / "docs" / "stickers"; out.mkdir(parents=True, exist_ok=True)
tmp = pathlib.Path(tempfile.mkdtemp())
for n in STOPS:
    imgs = []
    for f in range(FRAMES):
        png = tmp / f"{n}-{f}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", *ROOT,
                        "--default-background-color=ffffffff", "--window-size=512,640",  # viewport must clear 512 tall
                        "--virtual-time-budget=4000", f"--screenshot={png}",
                        f"file://{HERE}/frame.html?n={n}&f={f}"], check=True, capture_output=True)
        imgs.append(flatten(Image.open(png)))
    # MP4: WhatsApp plays short silent videos as looping GIFs (GIF files often arrive as stills)
    for i, im in enumerate(imgs * 2):
        im.save(tmp / f"v{n}-{i:02d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(1000 // MS), "-i", str(tmp / f"v{n}-%02d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-an", "-movflags", "+faststart",
                    str(out / f"skip-{n}.mp4")], check=True)
    imgs[0].save(out / f"skip-{n}.webp", save_all=True, append_images=imgs[1:], duration=MS, loop=0, lossless=False, quality=80)
    imgs[0].save(out / f"skip-{n}.gif", save_all=True, append_images=imgs[1:], duration=MS, loop=0, disposal=1)
    imgs[0].save(out / f"skip-{n}.png")
    print(n, flush=True)
