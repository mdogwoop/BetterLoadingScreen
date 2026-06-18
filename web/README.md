# Web Recreation of the BetterLoadingScreen warp tunnel

A self-contained Three.js recreation of the classic VRChat "warp tunnel" loading
screen that this mod restores. It reproduces the four visual layers found in the
original prefab (`Assets/Bundle/LoadingBackground.prefab`):

| Original object | Web implementation |
|-----------------|--------------------|
| `SkyCube`       | Gradient sky sphere (`scene.background` stand-in) |
| `Tunnel`        | Cylinder with scrolling additive glow texture |
| `Stars`         | Points particle system streaking toward the camera |
| `VRCLogo` / `LoadingInfoPanel` | HTML/CSS overlay |

## Run it

It's a single file with no build step. Open `web/index.html` directly in a
browser, or serve the folder:

```bash
cd web
python3 -m http.server 8000   # then open http://localhost:8000
```

(A static server is recommended so the Three.js ES module CDN import resolves
cleanly on all browsers.)

## Getting 1:1 fidelity with the real assets

This prototype draws a procedural sky and tunnel so it runs with zero asset
files. To match the original exactly:

1. Extract the textures from `OldLoadingScreen/loading.assetbundle` with
   **AssetStudio** (filter Texture2D / Cubemap / Material; look for the `SkyCube`
   material and tunnel texture).
2. Replace the gradient sky with the real cubemap via
   `new THREE.CubeTextureLoader().load([...6 faces])` assigned to
   `scene.background`.
3. Swap the procedurally generated `tunnelTex` canvas for the extracted tunnel
   texture, and drop in the VRChat logo PNG for the overlay.
