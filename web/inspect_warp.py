#!/usr/bin/env python3
"""Dump the warp-tunnel mesh / material / shader / script setup from the bundle."""
import sys
import UnityPy

env = UnityPy.load(sys.argv[1] if len(sys.argv) > 1 else "OldLoadingScreen/loading.assetbundle")
objs = list(env.objects)

def nm(d):
    return getattr(d, "m_Name", "") or ""

# resolve a PPtr-ish dict {m_PathID:..} to a name
path_names = {}
for o in objs:
    try:
        d = o.read()
        path_names[o.path_id] = nm(d)
    except Exception:
        pass

print("=" * 70, "\nMATERIALS\n", "=" * 70)
for o in objs:
    if o.type.name != "Material":
        continue
    tt = o.read_typetree()
    n = tt.get("m_Name", "")
    if "warp" not in n.lower() and "tunnel" not in n.lower():
        continue
    print(f"\n## Material: {n}")
    sh = tt.get("m_Shader", {})
    print("   shader pathid:", sh.get("m_PathID"), "->", path_names.get(sh.get("m_PathID"), "?"))
    sp = tt.get("m_SavedProperties", {})
    for k, v in sp.get("m_TexEnvs", []):
        tp = v.get("m_Texture", {}).get("m_PathID", 0)
        print(f"   tex  {k:22s} = {path_names.get(tp,'-'):26s} scale={v.get('m_Scale')} offset={v.get('m_Offset')}")
    for k, v in sp.get("m_Floats", []):
        print(f"   float {k:22s} = {round(v,4)}")
    for k, v in sp.get("m_Colors", []):
        print(f"   color {k:22s} = {v}")

print("\n" + "=" * 70, "\nSHADERS (names)\n", "=" * 70)
for o in objs:
    if o.type.name != "Shader":
        continue
    try:
        tt = o.read_typetree()
        pp = tt.get("m_ParsedForm", {})
        print(" shader:", pp.get("m_Name") or tt.get("m_Name"), " pathid", o.path_id)
    except Exception as e:
        print(" shader read fail", o.path_id, e)

print("\n" + "=" * 70, "\nMONOBEHAVIOURS (F3D / warp)\n", "=" * 70)
for o in objs:
    if o.type.name != "MonoBehaviour":
        continue
    try:
        d = o.read()
        sref = getattr(d, "m_Script", None)
        sname = path_names.get(sref.path_id, "") if sref else ""
        tt = o.read_typetree()
        gname = tt.get("m_Name", "")
        if "f3d" not in sname.lower() and "warp" not in sname.lower() and "tunnel" not in sname.lower():
            continue
        print(f"\n## script={sname}  name='{gname}'")
        for k, v in tt.items():
            if k in ("m_GameObject", "m_Script", "m_ObjectHideFlags", "m_Enabled",
                     "m_CorrespondingSourceObject", "m_PrefabInstance", "m_PrefabAsset", "m_Name"):
                continue
            print(f"   {k} = {v}")
    except Exception:
        pass

print("\n" + "=" * 70, "\nMESHES\n", "=" * 70)
def export_obj(mesh, path):
    verts = mesh.m_Vertices
    nverts = len(verts) // 3
    with open(path, "w") as f:
        for i in range(nverts):
            f.write(f"v {verts[i*3]} {verts[i*3+1]} {verts[i*3+2]}\n")
        if getattr(mesh, "m_UV0", None):
            uv = mesh.m_UV0
            for i in range(len(uv)//2):
                f.write(f"vt {uv[i*2]} {uv[i*2+1]}\n")
        idx = mesh.m_Indices
        for i in range(0, len(idx)-2, 3):
            f.write(f"f {idx[i]+1} {idx[i+1]+1} {idx[i+2]+1}\n")
    return nverts, len(mesh.m_Indices)//3

for o in objs:
    if o.type.name != "Mesh":
        continue
    d = o.read()
    n = nm(d)
    nv = len(d.m_Vertices)//3 if d.m_Vertices else 0
    line = f" mesh '{n}'  verts={nv}"
    try:
        out = ("extracted/meshes/" + (n or "mesh") + ".obj").replace(' ', '_')
        nv2, nf = export_obj(d, out)
        line += f"  -> {out} ({nf} tris)"
    except Exception as e:
        line += f"  export failed: {e}"
    print(line)
