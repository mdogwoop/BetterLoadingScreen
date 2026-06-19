#!/usr/bin/env python3
"""Pull the compiled DXBC programs out of the warp-tunnel shaders so fxc can
disassemble them."""
import os, struct
import lz4.block
import UnityPy

env = UnityPy.load("OldLoadingScreen/loading.assetbundle")
os.makedirs("extracted/shaders/dxbc", exist_ok=True)

for o in env.objects:
    if o.type.name != "Shader":
        continue
    d = o.read()
    name = getattr(d.m_ParsedForm, "m_Name", "") if hasattr(d, "m_ParsedForm") else getattr(d, "m_Name", "")
    if "warp" not in name.lower():
        continue
    blob = bytes(d.compressedBlob)
    dec = lz4.block.decompress(blob, uncompressed_size=int(list(d.decompressedLengths)[0]))
    safe = name.replace("/", "_")
    # scan for DXBC containers; each header stores its total size at offset 24
    i, n = 0, 0
    seen = set()
    while True:
        j = dec.find(b"DXBC", i)
        if j < 0:
            break
        total = struct.unpack_from("<I", dec, j + 24)[0]
        chunk = dec[j:j + total]
        h = hash(chunk)
        if 0 < total < len(dec) - j + 4 and h not in seen:
            seen.add(h)
            out = f"extracted/shaders/dxbc/{safe}_{n}.cso"
            with open(out, "wb") as f:
                f.write(chunk)
            print(f"{out}  ({total} bytes)")
            n += 1
        i = j + 4
    print(f"== {name}: {n} unique DXBC programs ==")
