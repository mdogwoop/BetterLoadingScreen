#!/usr/bin/env python3
"""Find which mesh + transform the warp_tunnel materials are applied to."""
import UnityPy

env = UnityPy.load("OldLoadingScreen/loading.assetbundle")
objs = list(env.objects)
name = {}
for o in objs:
    try:
        name[o.path_id] = getattr(o.read(), "m_Name", "") or ""
    except Exception:
        name[o.path_id] = ""

# index transforms + meshfilters + renderers by their GameObject
def pid(ref):
    try:
        return ref.get("m_PathID") if isinstance(ref, dict) else ref.path_id
    except Exception:
        return None

go_tt = {}          # gameobject path_id -> typetree
comp_by_go = {}     # gameobject path_id -> list of (type, typetree)
for o in objs:
    if o.type.name in ("MeshFilter", "MeshRenderer", "Transform"):
        tt = o.read_typetree()
        g = pid(tt.get("m_GameObject"))
        comp_by_go.setdefault(g, []).append((o.type.name, tt))
    elif o.type.name == "GameObject":
        go_tt[o.path_id] = o.read_typetree()

for g, comps in comp_by_go.items():
    mr = next((tt for t, tt in comps if t == "MeshRenderer"), None)
    if not mr:
        continue
    mats = [name.get(pid(m), "?") for m in mr.get("m_Materials", [])]
    if not any("warp" in (m or "").lower() for m in mats):
        continue
    gname = go_tt.get(g, {}).get("m_Name", "?")
    mf = next((tt for t, tt in comps if t == "MeshFilter"), None)
    mesh = name.get(pid(mf.get("m_Mesh")), "?") if mf else "?"
    tr = next((tt for t, tt in comps if t == "Transform"), None)
    print(f"\nGameObject '{gname}'")
    print(f"   mesh      = {mesh}")
    print(f"   materials = {mats}")
    if tr:
        lp, lr, ls = tr.get("m_LocalPosition"), tr.get("m_LocalRotation"), tr.get("m_LocalScale")
        print(f"   localPos  = {lp}")
        print(f"   localRot  = {lr}")
        print(f"   localScale= {ls}")
