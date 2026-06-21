/**
 * Cloudflare Worker for the "mdog的生日会" portal.
 *
 * Responsibilities (everything else is a plain static asset):
 *   1. Serve the static site from ./public via the ASSETS binding.
 *   2. On the HTML document, rewrite the Open Graph / Twitter image + url to
 *      absolute URLs so Discord / Telegram render the link preview. The embed
 *      text itself ("这里有一个来自mdog的传送门，快来看看") lives in index.html.
 *   3. Geo-gate the "添加到 Google 日历" button: Google Calendar is unreachable
 *      from mainland China, so hide that button when the visitor's country
 *      (Cloudflare's request.cf.country) is CN.
 *
 * run_worker_first is enabled in wrangler.jsonc so this runs for every request
 * and we forward to env.ASSETS ourselves.
 */

const BOT_UA = /(discord|telegram|twitter|facebookexternalhit|slack|whatsapp|linkedin|embed|preview|bot)/i;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Fetch the underlying static asset.
    const assetRes = await env.ASSETS.fetch(request);

    const contentType = assetRes.headers.get("content-type") || "";
    if (!contentType.includes("text/html")) {
      return assetRes; // images, fonts, js, wav, obj … served untouched
    }

    const origin = url.origin;
    const abs = (p) => {
      try { return new URL(p, origin + "/").toString(); } catch { return p; }
    };

    const country = (request.cf && request.cf.country) || null;
    const hideCalendar = country === "CN";
    const ua = request.headers.get("user-agent") || "";
    const isBot = BOT_UA.test(ua);

    let rewriter = new HTMLRewriter()
      // Make preview assets absolute for link-unfurling crawlers.
      .on('meta[property="og:image"], meta[name="twitter:image"]', {
        element(el) {
          const c = el.getAttribute("content");
          if (c) el.setAttribute("content", abs(c));
        },
      })
      .on('meta[property="og:url"]', {
        element(el) { el.setAttribute("content", origin + "/"); },
      });

    // Mainland-China visitors: hide the Google Calendar button.
    if (hideCalendar) {
      rewriter = rewriter.on("#back", {
        element(el) {
          const s = el.getAttribute("style") || "";
          el.setAttribute("style", (s ? s + ";" : "") + "display:none");
        },
      });
    }

    const res = new Response(assetRes.body, assetRes);
    // Geo result varies per visitor and bots need fresh OG — don't cache the doc.
    res.headers.set("cache-control", "no-store");
    res.headers.set("x-geo-country", country || "unknown");
    if (isBot) res.headers.set("x-served-to", "bot");
    return rewriter.transform(res);
  },
};
