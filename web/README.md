# Web Recreation of the BetterLoadingScreen warp tunnel

A self-contained Three.js recreation of the classic VRChat "warp tunnel" loading
screen that this mod restores. It reproduces the four visual layers found in the
original prefab (`Assets/Bundle/LoadingBackground.prefab`):

| Original object | Web implementation |
|-----------------|--------------------|
| `SkyCube`       | Background sphere mapped with the tileable `Stars-010-Cyan` starfield (gradient fallback) |
| Nebula clouds   | `Nebula-*` images as additive sprite billboards (black = transparent) around the front hemisphere |
| `Tunnel`        | Cylinder with a dim, scrolling additive `warp_tunnel_mask` texture |
| `Stars`         | Points streaking toward the camera, using the soft round `Default-Particle` sprite |
| `MenuMusic`     | `PartiallyOffline.wav`, started via the "Enable sound" button |
| `VRCLogo` / `LoadingInfoPanel` | HTML/CSS overlay |

Note on textures: `Stars-010-Cyan` is a *tileable starfield image*, not a point
sprite, and the `Nebula-*` files are black-background clouds meant for additive
blending — using them the wrong way (e.g. a star tile as a `Points` sprite)
renders as scattered translucent squares rather than a smooth sky.

Each asset loads from `web/assets/` with a graceful fallback to a procedural
stand-in, so the scene runs even when those (VRChat-owned) files are absent.

## Run it

It's a single file with no build step. Open `web/index.html` directly in a
browser, or serve the folder:

```bash
cd web
python3 -m http.server 8000   # then open http://localhost:8000
```

(A static server is recommended so the Three.js ES module CDN import resolves
cleanly on all browsers.)

## Supplying the real assets

The textures and audio are VRChat property, so they are **not** committed here.
Extract them yourself and drop them into `web/assets/`:

```bash
pip install UnityPy
python3 web/extract_assets.py OldLoadingScreen/loading.assetbundle extracted
cp extracted/textures/Nebula-*.png \
   extracted/textures/warp_tunnel_mask.png \
   extracted/textures/Stars-010-Cyan.png \
   extracted/textures/Default-Particle.png \
   "extracted/audio/Scifi Loading Screen Loop 3.wav" \
   web/assets/
```

The exact filenames the page looks for are listed in the `buildSky`,
`buildNebulae`, `buildTunnel` and star-sprite sections near the top of the
`index.html` script.

Without these files everything still renders — the sky becomes a teal→black
gradient, the tunnel uses a procedural streak texture, and audio is disabled.
