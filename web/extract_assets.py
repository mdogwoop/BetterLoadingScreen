#!/usr/bin/env python3
"""
Unpack a Unity AssetBundle and export its textures, cubemaps and audio.

Usage:
    pip install UnityPy
    python3 extract_assets.py ../OldLoadingScreen/loading.assetbundle ./extracted

Exports:
    <out>/textures/*.png   every Texture2D
    <out>/cubemap/*.png    every Cubemap (best-effort; HDR/BC6H may not decode)
    <out>/audio/*          every AudioClip sample

Note: assets inside loading.assetbundle are VRChat property. Extract for personal
study / asset replacement only; do not redistribute.
"""
import sys, os
import UnityPy


def safe(name: str) -> str:
    name = name or "noname"
    return "".join(c if c.isalnum() or c in " -_.()" else "_" for c in name).strip() or "noname"


def main(bundle: str, out: str) -> None:
    for sub in ("textures", "cubemap", "audio"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)

    env = UnityPy.load(bundle)
    n = {"Texture2D": 0, "Cubemap": 0, "AudioClip": 0}

    for obj in env.objects:
        t = obj.type.name
        try:
            if t == "Texture2D":
                data = obj.read()
                img = data.image
                if img:
                    img.save(os.path.join(out, "textures", safe(data.m_Name) + ".png"))
                    n[t] += 1
            elif t == "Cubemap":
                data = obj.read()
                try:
                    data.image.save(os.path.join(out, "cubemap", safe(data.m_Name) + ".png"))
                    n[t] += 1
                except Exception as e:
                    print(f"  cubemap {data.m_Name}: cannot decode ({data.m_TextureFormat}): {e}")
            elif t == "AudioClip":
                data = obj.read()
                for fn, raw in data.samples.items():
                    with open(os.path.join(out, "audio", safe(fn)), "wb") as f:
                        f.write(raw)
                    n[t] += 1
        except Exception as e:
            print(f"  skip {t}: {e}")

    print(f"Texture2D -> {n['Texture2D']}  Cubemap -> {n['Cubemap']}  AudioClip -> {n['AudioClip']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "extracted")
