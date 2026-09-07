#!/usr/bin/env python3
"""Regenerate data.js + photos/ for the Carry Desk street map from a fresh copy of the board's cards.
Input : props.json  — either the PROPS list from the live artifact, or {"props":[...],"arch":{"id":true}}
        data.js     — the existing map data, reused for each card's geocoded lat/lon (so nothing is re-geocoded)
Output: data.js, photos/<id>.jpg   (index.html is the shell and only changes when the map design changes)
Cards with an id not already in data.js fall back to the card's own ZIP-centroid lat/lon and are marked approx.
Usage : python3 refresh.py   then   sh publish.sh "Nightly map refresh"
"""
import json, base64, os, re, datetime, sys
HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, "props.json")))
P = raw["props"] if isinstance(raw, dict) else raw
ARCH = set((raw.get("arch") or {}).keys()) if isinstance(raw, dict) else set()
old = {}
try:
    txt = open(os.path.join(HERE, "data.js")).read()
    old = {r["id"]: r for r in json.loads(re.sub(r"^window\.DATA=|;\s*$", "", txt.strip()))["props"]}
except Exception as e:
    print("no usable data.js, every pin falls back to the ZIP centroid:", e)
os.makedirs(os.path.join(HERE, "photos"), exist_ok=True)
rows, kept = [], set()
for p in P:
    g = old.get(p["id"], {})
    photo = None
    if (p.get("photo") or "").startswith("data:"):
        fn = f"photos/{p['id']}.jpg"
        open(os.path.join(HERE, fn), "wb").write(base64.b64decode(p["photo"].split(",", 1)[1]))
        photo, _ = fn, kept.add(f"{p['id']}.jpg")
    elif g.get("photo") and os.path.exists(os.path.join(HERE, g["photo"])):
        photo = g["photo"]; kept.add(os.path.basename(g["photo"]))
    rows.append({"id": p["id"], "name": p["name"], "area": p["area"], "zip": p["zip"],
                 "lat": g.get("lat", p.get("lat")), "lon": g.get("lon", p.get("lon")),
                 "approx": g.get("approx", True) if g else True,
                 "price": p["price"], "bd": p.get("bd"), "ba": p.get("ba"), "sf": p.get("mls"), "above": p.get("above"),
                 "taxnow": p.get("taxnow") or 0, "taxfwd": p.get("taxfwd") or 0, "hoa": p.get("hoa") or 0,
                 "ptype": p.get("ptype"), "status": p.get("status"), "url": p["url"], "photo": photo,
                 "vt": p.get("vt", "unknown"), "vr": p.get("vr"), "vy": p.get("vy"), "src": p.get("src"),
                 "arch": p["id"] in ARCH, "nb": bool(p.get("nb")), "dl": p.get("dl"),
                 "hood": p.get("hood"), "yr": p.get("yr"), "mi": p.get("mi")})
data = {"built": datetime.date.today().strftime("%d %b %Y").lstrip("0"),
        "home": {"lat": 41.8648, "lon": -87.6243, "label": "1326 S Michigan Ave"}, "props": rows}
open(os.path.join(HERE, "data.js"), "w").write("window.DATA=" + json.dumps(data, separators=(",", ":")) + ";")
stale = [f for f in os.listdir(os.path.join(HERE, "photos")) if f not in kept]
print(f"cards {len(rows)} · photos {sum(1 for r in rows if r['photo'])} · approx pins {sum(1 for r in rows if r['approx'])} "
      f"· dismissed {sum(1 for r in rows if r['arch'])} · new ids {sum(1 for p in P if p['id'] not in old)}"
      + (f" · orphan photo files left in place: {len(stale)}" if stale else ""))
