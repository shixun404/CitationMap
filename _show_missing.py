import pandas as pd
df = pd.read_csv("unique_affiliations_geocoded.csv")
miss = df[df["latitude"].isna()]
print("Missing:", len(miss))
for a in miss["affiliation"]:
    print(" -", a.encode("ascii", "replace").decode())
