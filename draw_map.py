"""
Draw the unique affiliations on a world map, following the CitationMap
implementation (folium.Map centered at [20, 0], zoom 2, colorful pin markers
with the affiliation name as the popup).
"""
import random

import folium
import pandas as pd

CSV_PATH    = "unique_affiliations_geocoded.csv"
OUTPUT_HTML = "citation_map.html"

df = pd.read_csv(CSV_PATH)
df = df.dropna(subset=["latitude", "longitude"])

citation_map = folium.Map(location=[20, 0], zoom_start=2)

# Same palette used by CitationMap's create_map().
colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
          'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
          'darkpurple', 'pink', 'lightblue', 'lightgreen',
          'gray', 'black', 'lightgray']

for _, row in df.iterrows():
    folium.Marker(
        [row["latitude"], row["longitude"]],
        popup=str(row["affiliation"]),
        icon=folium.Icon(color=random.choice(colors)),
    ).add_to(citation_map)

citation_map.save(OUTPUT_HTML)
print(f"Plotted {len(df)} affiliations  ->  {OUTPUT_HTML}")
