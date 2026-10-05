#!/usr/bin/env python3
"""Download Wikipedia's kit drawings for every Everton season into ./kits.
The drawings are layered from freely licensed Wikimedia Commons files (no club or sponsor logos).
Writes ./kits/kits.json for the chart. Safe to re-run: files already downloaded are kept."""
import html, json, os, re, time, urllib.error, urllib.parse, urllib.request

UA = "EvertonChart/1.0 (https://engoyd.github.io/everton/; https://github.com/EngoyD/everton)"
API = "https://en.wikipedia.org/w/api.php"
FIRST, LAST = 1878, 2026
PARTS = [("la", "pattern_la", "leftarm", "Kit left arm"), ("b", "pattern_b", "body", "Kit body"),
         ("ra", "pattern_ra", "rightarm", "Kit right arm"), ("sh", "pattern_sh", "shorts", "Kit shorts"),
         ("so", "pattern_so", "socks", "Kit socks")]
OVERLAYS = {"la": "Kit left arm.svg", "b": "Kit body.svg", "ra": "Kit right arm.svg", "sh": "Kit shorts.svg", "so": "Kit socks long.svg"}
WHICH = {"1": "home", "2": "away", "3": "third"}

def get(url, tries=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                wait = int(e.headers.get("Retry-After") or 0) or 5 * (i + 1)
                print(f"    Wikimedia asked us to slow down; waiting {wait}s")
                time.sleep(wait)
                continue
            raise

def api(params):
    params = {"format": "json", "formatversion": "2", **params}
    return json.loads(get(API + "?" + urllib.parse.urlencode(params)))

def title(s):
    return f"{s}–{s + 1}" if (s + 1) % 100 == 0 else f"{s}–{(s + 1) % 100:02d}"

def clean(v):
    return re.sub(r"<!--.*?-->", "", v or "", flags=re.S).strip()

def text(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h or ""))).strip()

def kits_from(wikitext):
    vals = {}
    for m in re.finditer(r"\|\s*(pattern_la|pattern_b|pattern_ra|pattern_sh|pattern_so|leftarm|body|rightarm|shorts|socks)([1-3])\s*=\s*([^\n|}]*)", wikitext):
        vals[(m.group(1), m.group(2))] = clean(m.group(3))
    out = {}
    for n, name in WHICH.items():
        if not vals.get(("body", n)):
            continue
        kit = {}
        for key, pat, col, _ in PARTS:
            kit[key] = {"c": vals.get((col, n), ""), "p": vals.get((pat, n), "")}
        out[name] = kit
    return out

os.makedirs("kits/files", exist_ok=True)
pages = {f"{title(s)} Everton F.C. season": s for s in range(FIRST, LAST + 1)}
found = {}
print("Reading season articles...")
titles = list(pages)
for i in range(0, len(titles), 50):
    batch = titles[i:i + 50]
    q = api({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main", "redirects": "1", "titles": "|".join(batch)})["query"]
    back = {t: t for t in batch}
    for n in q.get("normalized", []):
        back[n["to"]] = back.get(n["from"], n["from"])
    for r in q.get("redirects", []):
        back[r["to"]] = back.get(r["from"], r["from"])
    for p in q.get("pages", []):
        if not p.get("revisions"):
            continue
        orig = back.get(p["title"], p["title"])
        s = pages.get(orig)
        if s is None:
            continue
        k = kits_from(p["revisions"][0]["slots"]["main"]["content"])
        if k:
            found[s] = k
    time.sleep(1)
if LAST not in found:
    q = api({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main", "titles": "Everton F.C."})["query"]
    k = kits_from(q["pages"][0]["revisions"][0]["slots"]["main"]["content"]) if q["pages"][0].get("revisions") else {}
    if k:
        found[LAST] = k
print(f"  kit details found for {len(found)} seasons")

wanted = {}
for s, ks in found.items():
    for kit in ks.values():
        for key, _, _, prefix in PARTS:
            p = kit[key]["p"]
            if p:
                wanted[f"{prefix}{p}.png"] = None
files, credits = {}, {}

def fetch_files(names, width=None):
    names = list(names)
    for i in range(0, len(names), 50):
        batch = names[i:i + 50]
        params = {"action": "query", "prop": "imageinfo", "iiprop": "url|extmetadata",
                  "iiextmetadatafilter": "Artist|LicenseShortName", "titles": "|".join("File:" + n for n in batch)}
        if width:
            params["iiurlwidth"] = str(width)
        q = api(params)["query"]
        norm = {n["to"]: n["from"] for n in q.get("normalized", [])}
        for p in q.get("pages", []):
            if not p.get("imageinfo"):
                continue
            ii = p["imageinfo"][0]
            name = norm.get(p["title"], p["title"])[5:]
            url = ii.get("thumburl") or ii["url"]
            ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or ".png"
            local = "kits/files/" + re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.splitext(name)[0]) + ext
            if not os.path.exists(local):
                with open(local, "wb") as fh:
                    fh.write(get(url))
                time.sleep(0.3)
            files[name] = local
            em = ii.get("extmetadata") or {}; em = em if isinstance(em, dict) else {}
            credits[local] = f"{text(em.get('Artist', {}).get('value')) or 'Wikimedia contributor'}, {text(em.get('LicenseShortName', {}).get('value')) or 'free licence'}"
        time.sleep(1)

print(f"Downloading {len(wanted)} pattern files and 5 base layers...")
fetch_files(wanted)
fetch_files(OVERLAYS.values(), width=250)

out = {"kits": {}, "overlays": {k: files.get(v, "") for k, v in OVERLAYS.items()}, "credits": credits}
for s, ks in sorted(found.items()):
    out["kits"][str(s)] = {}
    for which, kit in ks.items():
        out["kits"][str(s)][which] = {key: {"c": kit[key]["c"], "f": files.get(f"{prefix}{kit[key]['p']}.png", "") if kit[key]["p"] else ""}
                                     for key, _, _, prefix in PARTS}
with open("kits/kits.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(f"\nDone: kits for {len(found)} seasons, {len(files)} drawing files saved in ./kits.")
