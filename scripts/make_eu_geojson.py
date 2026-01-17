import json
from pathlib import Path

# EU-27 ISO2 codes
EU_ISO2 = {
    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT",
    "LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE",
}

INFILE = Path("public/europe.geojson")   # your big file (rename if needed)
OUTFILE = Path("public/eu.geojson")      # output small file

def main():
    data = json.loads(INFILE.read_text(encoding="utf-8"))
    features = data.get("features", [])
    out_features = []

    for f in features:
        props = f.get("properties", {}) or {}
        iso2 = props.get("ISO_A2")
        name = props.get("NAME") or props.get("ADMIN") or props.get("NAME_EN")

        if iso2 in EU_ISO2:
            out_features.append({
                "type": "Feature",
                "properties": {
                    "ISO_A2": iso2,
                    "name": name,
                },
                "geometry": f.get("geometry"),
            })

    out = {"type": "FeatureCollection", "features": out_features}
    OUTFILE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {OUTFILE} with {len(out_features)} EU features")

if __name__ == "__main__":
    main()
