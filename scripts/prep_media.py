#!/usr/bin/env python3
"""Prépare une photo ou une vidéo d'iPhone pour le site.

Usage :
    python3 scripts/prep_media.py SOURCE DESTINATION

Le type est déduit de l'extension de DESTINATION :
    .jpg -> photo : 1600 px max, sRGB, JPEG progressif, métadonnées (GPS) supprimées
    .mp4 -> clip  : muet, 720 px de large, 30 i/s, 15 s max, HDR ramené en SDR,
                    + une image d'aperçu DESTINATION-poster.jpg

Dépendances : sips (macOS), ffmpeg, Pillow.
"""
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps

PHOTO_MAX = 1600
CLIP_WIDTH = 720
CLIP_MAX_SECONDS = 15
SRGB = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"

# Vidéos iPhone en HDR (HLG / BT.2020) -> SDR BT.709, sinon couleurs délavées.
HDR_TO_SDR = (
    "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
    "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
)


def save_clean_jpeg(src: pathlib.Path, dest: pathlib.Path) -> None:
    """Réenregistre sans EXIF ni profil ICC (le contenu est déjà en sRGB).

    L'orientation EXIF est appliquée aux pixels avant d'être supprimée.
    """
    with Image.open(src) as im:
        ImageOps.exif_transpose(im).convert("RGB").save(dest, "JPEG", quality=82, optimize=True, progressive=True)


def prep_photo(src: pathlib.Path, dest: pathlib.Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mid = pathlib.Path(tmp) / "mid.jpg"
        subprocess.run(
            ["sips", "-s", "format", "jpeg", "-Z", str(PHOTO_MAX), "--matchTo", SRGB,
             str(src), "--out", str(mid)],
            check=True, capture_output=True,
        )
        save_clean_jpeg(mid, dest)


def is_hdr(src: pathlib.Path) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=color_transfer", "-of", "csv=p=0", str(src)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return out in ("arib-std-b67", "smpte2084")


def prep_clip(src: pathlib.Path, dest: pathlib.Path) -> None:
    filters = [f"scale={CLIP_WIDTH}:-2", "fps=30"]
    if is_hdr(src):
        filters.insert(0, HDR_TO_SDR)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(src),
         "-t", str(CLIP_MAX_SECONDS), "-an", "-map_metadata", "-1",
         "-vf", ",".join(filters),
         "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-movflags", "+faststart", str(dest)],
        check=True,
    )
    poster = dest.with_name(dest.stem + "-poster.jpg")
    with tempfile.TemporaryDirectory() as tmp:
        frame = pathlib.Path(tmp) / "frame.png"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(dest), "-frames:v", "1", str(frame)],
            check=True,
        )
        save_clean_jpeg(frame, poster)
    print(f"OK: {poster} ({poster.stat().st_size / 1024:.0f} KB)")


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dest = pathlib.Path(sys.argv[1]).expanduser(), pathlib.Path(sys.argv[2])
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.suffix == ".jpg":
        prep_photo(src, dest)
    elif dest.suffix == ".mp4":
        prep_clip(src, dest)
    else:
        sys.exit("DESTINATION doit finir par .jpg ou .mp4")
    print(f"OK: {dest} ({dest.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
