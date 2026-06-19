#!/usr/bin/env python3
"""Probe the FORGE3D/WarpTunnel shader: list every compiled backend/subprogram
and dump any human-readable (GLSL/Metal) source we can recover."""
import sys, os
import UnityPy

env = UnityPy.load(sys.argv[1] if len(sys.argv) > 1 else "OldLoadingScreen/loading.assetbundle")
os.makedirs("extracted/shaders", exist_ok=True)

# Unity serialized-shader program GPU backends
GPU = {
    0: "GLLegacy", 1: "GLES31AEP", 2: "GLES31", 3: "GLES3", 4: "GLES",
    5: "GLCore32", 6: "GLCore41", 7: "GLCore43", 8: "DX9V_2_0", 9: "DX9V_3_0",
    10: "DX11_9x", 11: "d3d11", 12: "d3d11_9x", 13: "Metal", 14: "OpenGLCore",
    15: "Vulkan", 16: "Switch", 18: "PS4", 21: "Metal",
}

for o in env.objects:
    if o.type.name != "Shader":
        continue
    d = o.read()
    name = ""
    try:
        name = d.m_ParsedForm.m_Name
    except Exception:
        name = getattr(d, "m_Name", "")
    if "warp" not in (name or "").lower():
        continue
    print(f"\n===== {name} =====")
    # platforms compiled
    try:
        plats = list(d.platforms)
        print("platforms:", [GPU.get(p, p) for p in plats])
    except Exception as e:
        print("platforms: <none>", e)

    # walk parsed form
    try:
        pf = d.m_ParsedForm
        for si, ss in enumerate(pf.m_SubShaders):
            for pi, ps in enumerate(ss.m_Passes):
                for stage in ("progVertex", "progFragment"):
                    prog = getattr(ps, stage, None)
                    if not prog:
                        continue
                    for sp in prog.m_SubPrograms:
                        gpu = GPU.get(sp.m_GpuProgramType, sp.m_GpuProgramType)
                        print(f"  ss{si} pass{pi} {stage}: backend={gpu}")
    except Exception as e:
        print("parsed-form walk failed:", e)

    # full export (UnityPy decompresses + emits whatever source it can)
    try:
        txt = d.export()
        out = "extracted/shaders/" + name.replace("/", "_") + ".full.shader"
        with open(out, "w", encoding="utf-8", errors="replace") as f:
            f.write(txt)
        readable = any(k in txt for k in ("gl_FragColor", "SV_Target", "void main", "fragment", "GLSL", "#version"))
        print(f"  export -> {out} ({len(txt)} chars)  readable_source={readable}")
    except Exception as e:
        print("  export failed:", e)
