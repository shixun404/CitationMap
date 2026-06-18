"""
Extract unique affiliations from unique_citing_papers_affiliation.csv,
geocode them using the CitationMap implementation (known-affiliation hardcodes
+ existing geocache), and write a CSV: affiliation, latitude, longitude.

Pass --geocode as a CLI argument to also query Nominatim for cache misses
(requires network access to nominatim.openstreetmap.org).
"""
import io
import json
import os
import sys
import time

import pandas as pd

# Force UTF-8 output so special characters don't crash on Windows cp1252.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))
from citation_map.citation_map import fill_known_affiliations, affiliation_invalid

CSV_PATH   = "unique_citing_papers_affiliation.csv"
CACHE_PATH = "affiliation_geocache.json"
OUT_CSV    = "unique_affiliations_geocoded.csv"

USE_NOMINATIM = "--geocode" in sys.argv

# ── 1. Read CSV and extract unique affiliations ────────────────────────────────
df = pd.read_csv(CSV_PATH, header=0, encoding="latin-1",
                 usecols=[0, 1, 2], names=["citing_paper", "author", "affiliation"])
df["affiliation"] = df["affiliation"].fillna("").str.strip()

unique_affiliations = sorted({a for a in df["affiliation"] if a})
print(f"Found {len(unique_affiliations)} unique affiliations.\n")

# ── 2. Load existing geocache ──────────────────────────────────────────────────
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        geocache = json.load(f)
    print(f"Loaded {len(geocache)} entries from geocache.\n")
else:
    geocache = {}
    print("No geocache found; starting fresh.\n")

# ── 3. Resolve affiliations: cache → known-dict → (optional) Nominatim ────────
if USE_NOMINATIM:
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="citation_mapper", timeout=15)
    print("Nominatim live geocoding enabled.\n")
else:
    print("Cache-only mode (pass --geocode to also query Nominatim).\n")

results = []
new_entries = 0
missing = []

def _save_cache():
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(geocache, f, indent=2, ensure_ascii=False)

for affiliation in unique_affiliations:
    # --- Cache hit ---
    if affiliation in geocache:
        entry = geocache[affiliation]
        if entry is not None:
            results.append({
                "affiliation": affiliation,
                "latitude":    entry["lat"],
                "longitude":   entry["lon"],
            })
        else:
            results.append({"affiliation": affiliation, "latitude": None, "longitude": None})
        continue

    # --- Cache miss ---
    new_entries += 1

    if affiliation_invalid(affiliation):
        geocache[affiliation] = None
        results.append({"affiliation": affiliation, "latitude": None, "longitude": None})
        _save_cache()
        continue

    # Check CitationMap hard-coded known affiliations (companies, etc.)
    known = fill_known_affiliations(affiliation)
    if known is not None:
        _, city, state, country, lat, lon = known
        geocache[affiliation] = {"lat": lat, "lon": lon, "address": f"{city}, {state}, {country}"}
        results.append({"affiliation": affiliation, "latitude": lat, "longitude": lon})
        _save_cache()
        continue

    if USE_NOMINATIM:
        geo = None
        for attempt in range(3):
            try:
                geo = geolocator.geocode(affiliation)
                break
            except Exception as exc:
                safe = affiliation.encode("ascii", "replace").decode()
                if attempt < 2:
                    print(f"[Retry {attempt+1}] {safe}: {type(exc).__name__}. Waiting 3s...")
                    time.sleep(3)
                else:
                    print(f"[Skip] {safe}: {type(exc).__name__}")
        if geo is not None:
            geocache[affiliation] = {"lat": geo.latitude, "lon": geo.longitude, "address": geo.address}
            results.append({"affiliation": affiliation, "latitude": geo.latitude, "longitude": geo.longitude})
        else:
            geocache[affiliation] = None
            results.append({"affiliation": affiliation, "latitude": None, "longitude": None})
        _save_cache()
        time.sleep(1)
    else:
        missing.append(affiliation)
        results.append({"affiliation": affiliation, "latitude": None, "longitude": None})

# ── 4. Write output CSV ────────────────────────────────────────────────────────
out_df = pd.DataFrame(results, columns=["affiliation", "latitude", "longitude"])
out_df.to_csv(OUT_CSV, index=False, encoding="utf-8")

located = out_df["latitude"].notna().sum()
print(f"\nLocated {located}/{len(out_df)} affiliations  →  {OUT_CSV}")

if missing:
    print(f"\n{len(missing)} affiliations not in cache (run with --geocode to resolve them):")
    for m in missing:
        safe = m.encode("ascii", "replace").decode()
        print(f"  - {safe}")
