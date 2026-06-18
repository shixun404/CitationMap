"""
Retry geocoding for the affiliations currently cached as None (failed before).
Builds a few cleaned query candidates per affiliation (drop parenthetical noise,
postal codes, take the most meaningful comma segment) and queries Nominatim.
Updates affiliation_geocache.json and rewrites unique_affiliations_geocoded.csv.
"""
import json
import re
import time

import pandas as pd
from geopy.geocoders import Nominatim

CACHE_PATH = "affiliation_geocache.json"
OUT_CSV    = "unique_affiliations_geocoded.csv"

with open(CACHE_PATH, "r", encoding="utf-8") as f:
    geocache = json.load(f)

geolocator = Nominatim(user_agent="citation_mapper", timeout=15)


def candidates(name: str):
    """Yield progressively cleaned query strings for an affiliation."""
    seen = set()

    def add(q, out):
        q = q.strip(" ,-")
        if q and q.lower() not in seen:
            seen.add(q.lower())
            out.append(q)

    out = []
    add(name, out)

    # Drop parenthetical chunks and postal codes / street numbers.
    no_paren = re.sub(r"\([^)]*\)", "", name)
    no_postal = re.sub(r"\b\d{4,6}\b", "", no_paren)
    add(no_postal, out)

    # Comma segments: prefer the one mentioning University/Institute/College/etc.
    segs = [s.strip() for s in re.split(r"[,，]", no_postal) if s.strip()]
    keyword = re.compile(
        r"\b(universi|institut|college|school|laborator|centre|center|"
        r"academy|polytechnic|hospital|company|corporation|inc|ltd|co\.)",
        re.IGNORECASE)
    for s in segs:
        if keyword.search(s):
            add(s, out)
    # Fall back to the longest segment.
    if segs:
        add(max(segs, key=len), out)
    return out


# Affiliations currently unresolved (cached as None).
missing = sorted(k for k, v in geocache.items() if v is None)
print(f"Retrying {len(missing)} previously-failed affiliations.\n")

recovered = 0
for name in missing:
    found = None
    for q in candidates(name):
        for attempt in range(2):
            try:
                geo = geolocator.geocode(q)
                if geo is not None:
                    found = (q, geo)
                break
            except Exception as exc:
                if attempt == 0:
                    time.sleep(3)
                else:
                    safe = q.encode("ascii", "replace").decode()
                    print(f"   [err] {safe}: {type(exc).__name__}")
            time.sleep(1)
        if found:
            break
        time.sleep(1)

    safe_name = name.encode("ascii", "replace").decode()
    if found:
        q, geo = found
        geocache[name] = {"lat": geo.latitude, "lon": geo.longitude, "address": geo.address}
        recovered += 1
        print(f"[OK] {safe_name}  ->  ({geo.latitude:.4f}, {geo.longitude:.4f})  via \"{q.encode('ascii','replace').decode()}\"")
    else:
        print(f"[--] {safe_name}  (still unresolved)")

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(geocache, f, indent=2, ensure_ascii=False)

print(f"\nRecovered {recovered}/{len(missing)} affiliations.")

# Rewrite the output CSV from the (now updated) cache, keeping the same affiliation set.
df = pd.read_csv(OUT_CSV)
def lookup(a):
    e = geocache.get(a)
    return (e["lat"], e["lon"]) if e else (None, None)
df["latitude"], df["longitude"] = zip(*df["affiliation"].map(lookup))
df.to_csv(OUT_CSV, index=False, encoding="utf-8")
located = df["latitude"].notna().sum()
print(f"Output rewritten: {located}/{len(df)} located  ->  {OUT_CSV}")
