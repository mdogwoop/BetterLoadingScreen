#!/usr/bin/env python3
"""Audit: dump every original parameter we care about so we can diff vs the web demo."""
import UnityPy

env = UnityPy.load("OldLoadingScreen/loading.assetbundle")
objs = list(env.objects)
name = {o.path_id: (getattr(o.read(), "m_Name", "") or "") for o in objs}

def pid(r):
    return r.get("m_PathID") if isinstance(r, dict) else getattr(r, "path_id", None)

go_name = {}
comp_by_go = {}
cameras, pss, psr = [], [], []
for o in objs:
    t = o.type.name
    if t == "GameObject":
        go_name[o.path_id] = o.read_typetree().get("m_Name", "?")
    elif t in ("MeshFilter", "MeshRenderer", "Transform", "Camera", "ParticleSystem", "ParticleSystemRenderer"):
        tt = o.read_typetree()
        comp_by_go.setdefault(pid(tt.get("m_GameObject")), []).append((t, tt))
        if t == "Camera": cameras.append(tt)

print("############ CAMERAS ############")
for c in cameras:
    g = go_name.get(pid(c.get("m_GameObject")), "?")
    print(f"  '{g}': fov={c.get('field of view')} near={c.get('near clip plane')} far={c.get('far clip plane')} ortho={c.get('orthographic')}")

print("\n############ SkyCube / sky ############")
for g, comps in comp_by_go.items():
    gn = go_name.get(g, "?")
    if "sky" not in gn.lower():
        continue
    mr = next((tt for t, tt in comps if t == "MeshRenderer"), None)
    mf = next((tt for t, tt in comps if t == "MeshFilter"), None)
    tr = next((tt for t, tt in comps if t == "Transform"), None)
    print(f"  '{gn}': mesh={name.get(pid(mf.get('m_Mesh')),'?') if mf else '-'}"
          f" mats={[name.get(pid(m),'?') for m in (mr.get('m_Materials',[]) if mr else [])]}")
    if tr: print(f"        scale={tr.get('m_LocalScale')} pos={tr.get('m_LocalPosition')}")

print("\n############ Stars particle color + renderer ############")
for o in objs:
    if o.type.name not in ("ParticleSystem", "ParticleSystemRenderer"):
        continue
    tt = o.read_typetree()
    gn = go_name.get(pid(tt.get("m_GameObject")), "?")
    if o.type.name == "ParticleSystem":
        col = tt.get("InitialModule", {}).get("startColor", {})
        print(f"  PS '{gn}': startColor={col}")
        cbl = tt.get("ColorModule", {})
        print(f"           ColorModule.enabled={cbl.get('enabled')}")
    else:
        mats = [name.get(pid(m), "?") for m in tt.get("m_Materials", [])]
        print(f"  PSR '{gn}': renderMode={tt.get('m_RenderMode')} lengthScale={tt.get('m_LengthScale')} "
              f"velocityScale={tt.get('m_VelocityScale')} maxParticleSize={tt.get('m_MaxParticleSize')} mats={mats}")

print("\n############ Warp tunnel instances (count + transforms) ############")
n = 0
for g, comps in comp_by_go.items():
    mr = next((tt for t, tt in comps if t == "MeshRenderer"), None)
    if not mr: continue
    mats = [name.get(pid(m), "?") for m in mr.get("m_Materials", [])]
    if not any("warp" in (m or "").lower() for m in mats): continue
    n += 1
    gn = go_name.get(g, "?")
    tr = next((tt for t, tt in comps if t == "Transform"), None)
    print(f"  '{gn}' mats={mats} scale={tr.get('m_LocalScale') if tr else '-'}")
print(f"  => {n} warp renderers total")

print("\n############ Stars material color ############")
for o in objs:
    if o.type.name != "Material": continue
    tt = o.read_typetree()
    nm = tt.get("m_Name", "")
    if "stars" not in nm.lower() and "particle" not in nm.lower(): continue
    sp = tt.get("m_SavedProperties", {})
    cols = {k: v for k, v in sp.get("m_Colors", [])}
    print(f"  mat '{nm}': shader={name.get(pid(tt.get('m_Shader')),'?')} TintColor={cols.get('_TintColor')} Color={cols.get('_Color')}")
