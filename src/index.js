/**
 * Cloudflare Worker for the "mdog的生日会" portal.
 *
 * Responsibilities (everything else is a plain static asset):
 *   1. Serve the static site from ./public via the ASSETS binding.
 *   2. On the HTML document:
 *      - localize <title> + Open Graph / Twitter meta by Accept-Language
 *        (zh / ja / English fallback) so link unfurls and the tab title match;
 *      - rewrite the OG/Twitter image + url to absolute URLs so Discord /
 *        Telegram render the preview image.
 *   3. Geo-gate the "Add to Google Calendar" button: Google Calendar is
 *      unreachable from mainland China, so hide it when the visitor's country
 *      is CN. Country comes from the CF-IPCountry request header that
 *      Cloudflare sets on every edge request (request.cf.country is not
 *      reliably populated for static-asset Workers).
 *
 * run_worker_first is enabled in wrangler.jsonc so this runs for every request
 * and we forward to env.ASSETS ourselves.
 */

const META = {
  zh: { title: "mdog的生日会", desc: "这里有一个来自mdog的传送门，快来看看" },
  en: { title: "mdog's Birthday Party", desc: "A portal from mdog is waiting — come take a look!" },
  ja: { title: "mdogの誕生日会", desc: "mdogからのポータルが届いています。ぜひ見に来てね！" },
};

function pickLang(request) {
  const al = (request.headers.get("accept-language") || "").toLowerCase();
  const first = al.split(",")[0].trim();
  if (first.startsWith("zh")) return "zh";
  if (first.startsWith("ja")) return "ja";
  return "en";
}

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

    // Country: CF-IPCountry is set by Cloudflare on every edge request.
    const country = request.headers.get("cf-ipcountry") || (request.cf && request.cf.country) || "XX";
    const hideCalendar = country === "CN";

    const lang = pickLang(request);
    const meta = META[lang];

    let rewriter = new HTMLRewriter()
      .on("html", { element(el) { el.setAttribute("lang", lang); } })
      .on("title", { element(el) { el.setInnerContent(meta.title); } })
      // Localize the social/title meta.
      .on('meta[property="og:title"], meta[property="og:site_name"], meta[name="twitter:title"]', {
        element(el) { el.setAttribute("content", meta.title); },
      })
      .on('meta[property="og:description"], meta[name="twitter:description"]', {
        element(el) { el.setAttribute("content", meta.desc); },
      })
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
    // Per-visitor geo + language, so don't let the document be cached/shared.
    res.headers.set("cache-control", "no-store");
    res.headers.set("vary", "accept-language");
    res.headers.set("x-geo-country", country);
    res.headers.set("x-lang", lang);
    return rewriter.transform(res);
  },
};
