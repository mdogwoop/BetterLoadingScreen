# mdog的生日会 — Cloudflare Worker portal

A self-contained Three.js "warp tunnel" page repurposed as a countdown to
mdog's birthday party (UTC+8 2027-07-01 23:00), served by a Cloudflare Worker.

This `worker` branch contains **only** what the site needs — no Unity mod,
extraction scripts, or unused assets. All external dependencies are localized
(Three.js + OBJLoader under `public/vendor/`, Noto Emoji under `public/fonts/`),
so the page loads with **no third-party CDN**.

## Layout

```
public/            # static site root (served via the ASSETS binding)
  index.html
  assets/          # textures, audio, birthday.png, warp_tunnel.obj
  fonts/           # localized Noto Emoji (monochrome) subset
  vendor/          # three.module.js + OBJLoader.js
src/index.js       # the Worker
wrangler.jsonc     # Worker + static-assets config
```

## What the Worker does

The Worker (`src/index.js`) runs in front of the static assets and, **only for
the HTML document**:

1. **Discord / Telegram link unfurling** — rewrites the Open Graph / Twitter
   `image` and `url` meta tags to absolute URLs so the crawlers render the
   preview card. The embed copy ("这里有一个来自mdog的传送门，快来看看") is in
   `public/index.html`.
2. **China geo-gating** — Google Calendar is unreachable from mainland China, so
   when `request.cf.country === "CN"` the "添加到 Google 日历" button (`#back`) is
   hidden via `HTMLRewriter`. Everyone else sees it.

All other requests (images, fonts, JS, audio, mesh) are served straight from
`ASSETS` untouched.

## Develop locally

**Prerequisite:** Node.js **v22+** (Wrangler 4 requires it).

```bash
npm install
npm run dev            # http://localhost:8787
```

`request.cf.country` is only populated on Cloudflare's edge. To test the
China-hiding path locally, run against the real edge:

```bash
npx wrangler dev --remote
```

…then use a CN egress, or temporarily flip the `hideCalendar` condition in
`src/index.js`.

## Deploy

You need a Cloudflare account (free plan is fine). Authenticate once, then
deploy:

```bash
npx wrangler login
npm run deploy
```

Wrangler prints the deployed `*.workers.dev` URL (or attach a custom domain in
the Cloudflare dashboard / via `routes` in `wrangler.jsonc`). Share that URL —
Discord and Telegram will show the birthday preview card, and visitors outside
mainland China get the Google Calendar button.
