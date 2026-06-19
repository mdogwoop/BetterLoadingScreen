#!/usr/bin/env python3
"""Export the FORGE3D/WarpTunnel shader source + the tunnel meshes to files."""
import sys, os
import UnityPy

env = UnityPy.load(sys.argv[1] if len(sys.argv) > 1 else "OldLoadingScreen/loading.assetbundle")
os.makedirs("extracted/shaders", exist_ok=True)
os.makedirs("extracted/meshes", exist_ok=True)

def nm(d):
    return getattr(d, "m_Name", "") or ""

for o in env.objects:
    if o.type.name == "Shader":
        try:
            d = o.read()
            name = ""
            try:
                name = d.m_ParsedForm.m_Name
            except Exception:
                name = nm(d)
            if "warp" not in (name or "").lower():
                continue
            safe = (name or "shader").replace("/", "_")
            try:
                txt = d.export()  # shaderlab/HLSL text if available
            except Exception as e:
                txt = f"<export failed: {e}>"
            with open(f"extracted/shaders/{safe}.shader", "w", encoding="utf-8", errors="replace") as f:
                f.write(txt)
            print(f"shader '{name}' -> extracted/shaders/{safe}.shader  ({len(txt)} chars)")
        except Exception as e:
            print("shader fail", e)
    elif o.type.name == "Mesh":
        d = o.read()
        name = nm(d)
        try:
            obj = d.export()  # handles compressed/streamed vertex data
            out = ("extracted/meshes/" + (name or "mesh") + ".obj").replace(" ", "_")
            with open(out, "w", encoding="utf-8", errors="replace") as f:
                f.write(obj)
            # quick stats
            vcount = obj.count("\nv ")
            print(f"mesh '{name}' -> {out}  (~{vcount} verts)")
        except Exception as e:
            print(f"mesh '{name}' export failed: {e}")
