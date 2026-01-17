import pandas as pd

def filter_to_eu_only(df):
    # EU aggregate rows (used for EU averages)
    eu_agg_df = df[df["population_EU_only"].notna()].copy()
    if eu_agg_df.empty:
        raise ValueError("No EU aggregate rows found (population_EU_only is empty)")

    # Countries contributing to EU aggregates (EU membership)
    eu_countries = (
        eu_agg_df["country"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    # EU country rows (selectable countries)
    country_df = df[df["country"].notna()].copy()
    country_df["country"] = country_df["country"].astype(str).str.strip()
    eu_country_df = country_df[country_df["country"].isin(eu_countries)]

    # Keep both EU country rows + EU aggregate rows
    filtered = pd.concat([eu_country_df, eu_agg_df], ignore_index=True)

    return filtered
