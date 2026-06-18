"""
One-time patch: add/fix known-institution coordinates in affiliation_geocache.json.
Run once, then delete this file.
"""
import json, os

CACHE_PATH = "affiliation_geocache.json"

with open(CACHE_PATH, "r", encoding="utf-8") as f:
    cache = json.load(f)

def add(name, lat, lon, address=""):
    if cache.get(name) is None:          # overwrite null or missing
        cache[name] = {"lat": lat, "lon": lon, "address": address}

# ── Institutions previously in cache as null ──────────────────────────────────
add("Beijing University of Posts and Telecommunications",
    39.9642, 116.3510, "Beijing, China")
add("Brookhaven National Laboratory",
    40.8699, -72.8773, "Upton, Long Island, New York, United States")
add("Brooklyn College, CUNY",
    40.6313, -73.9529, "Brooklyn, New York, United States")
add("Carnegie Mellon University",
    40.4432, -79.9428, "Pittsburgh, Pennsylvania, United States")
add("Central Research Institute, 2012 Labs, Huawei Tech. Co. Ltd",
    22.5460, 113.9420, "Shenzhen, Guangdong, China")
add("China University of Petroleum-Beijing",
    40.0009, 116.3260, "Beijing, China")
add("Ewha Womans University",
    37.5628, 126.9469, "Seoul, South Korea")
add("Heilongjiang University, Harbin, China",
    45.7683, 126.5699, "Harbin, Heilongjiang, China")
add("IFP Energies Nouvelles, Rueil-Malmaison, France",
    48.8789,   2.1897, "Rueil-Malmaison, Île-de-France, France")
add("JPMorgan Chase",
    40.7545, -73.9769, "New York, New York, United States")
add("Kings College London",
    51.5115,  -0.1160, "London, England, United Kingdom")
add("Los Alamos National Lab",
    35.8816, -106.2951, "Los Alamos, New Mexico, United States")
add("Meta Platforms Inc.",
    37.4851, -122.1483, "Menlo Park, California, United States")
add("Metax Research Institute, Nanjing, China",   # was wrongly set to Meta HQ
    32.0603, 118.7969, "Nanjing, Jiangsu, China")
add("Nanjing University",
    32.1132, 118.9015, "Nanjing, Jiangsu, China")
add("Nanjing University of Information Science and Technology",
    32.2059, 118.7139, "Nanjing, Jiangsu, China")

# ── 27 affiliations not yet in cache ──────────────────────────────────────────
add("National Renewable Energy Laboratory",
    39.7406, -105.1686, "Golden, Colorado, United States")
add("Shenzhen University of Advanced Technology",
    22.5892, 113.9718, "Shenzhen, Guangdong, China")
add("Stanford University",
    37.4275, -122.1697, "Stanford, California, United States")
add("Stony Brook University",
    40.9149, -73.1259, "Stony Brook, New York, United States")
add("Thales, cortAIx Labs",
    48.7264,   2.2799, "Massy, Île-de-France, France")
add("UMass Lowel",                          # typo variant in the CSV
    42.6519, -71.3174, "Lowell, Massachusetts, United States")
add("Univ of Nebraska Omaha",
    41.2565, -96.0091, "Omaha, Nebraska, United States")
add("University Of Bisha",
    19.9942,  42.6054, "Bisha, Asir, Saudi Arabia")
add("University of California, Los Angeles",
    34.0695, -118.4452, "Los Angeles, California, United States")
add("University of Chinese Academy of Sciences",
    39.9077, 116.2441, "Beijing, China")
add("University of Dhaka",
    23.7338,  90.3956, "Dhaka, Bangladesh")
add("University of Electronic Science and Technology of China",
    30.7500, 103.9341, "Chengdu, Sichuan, China")
add("University of Georgia",
    33.9481, -83.3773, "Athens, Georgia, United States")
add("University of Maryland, College Park",
    38.9904, -76.9438, "College Park, Maryland, United States")
add("University of Oulu, Oulu 90570, Finland",
    65.0599,  25.4660, "Oulu, Finland")
add("University of Peloponnese\nTripoli",   # has newline in CSV
    37.5271,  22.3717, "Tripoli, Peloponnese, Greece")
add("University of Peloponnese, Tripoli",
    37.5271,  22.3717, "Tripoli, Peloponnese, Greece")
add("University of Science and Technology Beijing",
    39.9889, 116.3574, "Beijing, China")
add("University of Southampton",
    50.9338,  -1.3958, "Southampton, England, United Kingdom")
add("University of Texas at Arlington",
    32.7284, -97.1120, "Arlington, Texas, United States")
add("University of Washington",
    47.6553, -122.3035, "Seattle, Washington, United States")
# Encoding-corrupted variants from latin-1 CSV read
add("Universit? C?te d'Azur, CNRS, I3S, Sophia Antipolis,?France",
    43.6140,   7.0710, "Sophia Antipolis, Alpes-Maritimes, France")
add("Universit? de Strasbourg",
    48.5788,   7.7622, "Strasbourg, Bas-Rhin, France")
add("Zhejiang Gongshang University",
    30.2841, 120.1551, "Hangzhou, Zhejiang, China")
add("Zhejiang University",
    30.3073, 120.0883, "Hangzhou, Zhejiang, China")
add("Zhejiang University of Technology  ",      # trailing spaces in CSV
    30.3150, 120.1500, "Hangzhou, Zhejiang, China")
add("Zhengzhou University of Light Industry",
    34.7593, 113.6609, "Zhengzhou, Henan, China")

# ── Also fix Metax entry that was set to Meta HQ coords ───────────────────────
cache["Metax Research Institute, Nanjing, China"] = {
    "lat": 32.0603, "lon": 118.7969, "address": "Nanjing, Jiangsu, China"
}

with open(CACHE_PATH, "w", encoding="utf-8") as f:
    json.dump(cache, f, indent=2, ensure_ascii=False)

print(f"Geocache patched: {len(cache)} total entries.")
