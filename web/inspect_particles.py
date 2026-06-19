#!/usr/bin/env python3
"""Dump the Stars ParticleSystem settings (rate, max particles, size, lifetime)."""
import UnityPy

env = UnityPy.load("OldLoadingScreen/loading.assetbundle")
objs = list(env.objects)
name = {o.path_id: (getattr(o.read(), "m_Name", "") or "") for o in objs if True}

def pid(r):
    return r.get("m_PathID") if isinstance(r, dict) else getattr(r, "path_id", None)

# map GameObject name for each PS via its m_GameObject
for o in objs:
    if o.type.name not in ("ParticleSystem", "ParticleSystemRenderer"):
        continue
    tt = o.read_typetree()
    gname = name.get(pid(tt.get("m_GameObject")), "?")
    print(f"\n===== {o.type.name} on '{gname}' =====")
    if o.type.name == "ParticleSystemRenderer":
        print("  renderMode:", tt.get("m_RenderMode"), " maxParticleSize:", tt.get("m_MaxParticleSize"),
              " lengthScale:", tt.get("m_LengthScale"), " velocityScale:", tt.get("m_VelocityScale"))
        continue
    main = tt.get("InitialModule", {})
    emis = tt.get("EmissionModule", {})
    shape = tt.get("ShapeModule", {})
    def mm(curve):
        # MinMaxCurve: scalar / minmax
        if isinstance(curve, dict):
            return {k: curve.get(k) for k in ("minMaxState", "scalar", "minScalar") if k in curve}
        return curve
    print("  duration:", tt.get("lengthInSec"), " looping:", tt.get("looping"))
    print("  maxNumParticles:", main.get("maxNumParticles"))
    print("  startLifetime:", mm(main.get("startLifetime")))
    print("  startSize:", mm(main.get("startSize")))
    print("  startSpeed:", mm(main.get("startSpeed")))
    print("  gravity:", main.get("gravityModifier"))
    print("  emission.enabled:", emis.get("enabled"))
    print("  emission.rateOverTime:", mm(emis.get("rateOverTime")))
    print("  emission.rateOverDistance:", mm(emis.get("rateOverDistance")))
    if "m_Bursts" in emis:
        print("  bursts:", emis.get("m_Bursts"))
    print("  shape.type:", shape.get("type"), " radius:", shape.get("radius"), " enabled:", shape.get("enabled"))
