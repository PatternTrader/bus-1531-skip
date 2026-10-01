#!/usr/bin/env python3
"""Render the 11 AM bus 1531 SKIP stickers: animated GIF + WhatsApp-ready animated WebP (512x512)."""
import subprocess, pathlib, tempfile
from PIL import Image
HERE = pathlib.Path(__file__).resolve().parent
STOPS = ["93", "84", "82", "59", "55", "51", "41", "36", "23", "16", "12"]
FRAMES, MS = 10, 200
out = HERE / "docs" / "stickers"; out.mkdir(parents=True, exist_ok=True)
tmp = pathlib.Path(tempfile.mkdtemp())
for n in STOPS:
    imgs = []
    for f in range(FRAMES):
        png = tmp / f"{n}-{f}.png"
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--default-background-color=00000000", "--window-size=512,512",
                        "--virtual-time-budget=4000", f"--screenshot={png}",
                        f"file://{HERE}/frame.html?n={n}&f={f}"], check=True, capture_output=True)
        imgs.append(Image.open(png).convert("RGBA"))
    # MP4: WhatsApp plays short silent videos as looping GIFs (GIF files often arrive as stills)
    for i, im in enumerate(imgs * 2):
        bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im); bg.save(tmp / f"v{n}-{i:02d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(1000 // MS), "-i", str(tmp / f"v{n}-%02d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-an", "-movflags", "+faststart",
                    str(out / f"skip-{n}.mp4")], check=True)
    imgs[0].save(out / f"skip-{n}.webp", save_all=True, append_images=imgs[1:], duration=MS, loop=0, lossless=False, quality=80)
    imgs[0].save(out / f"skip-{n}.gif", save_all=True, append_images=imgs[1:], duration=MS, loop=0, disposal=2)
    imgs[0].save(out / f"skip-{n}.png")
    print(n, flush=True)
