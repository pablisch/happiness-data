import pandas as pd

def filter_to_eu_only(df):
    """
    Return exactly ONE row per EU member state.
    EU membership is inferred from presence of population_EU_only.
    No duplication. No synthetic aggregate rows.
    """

    # EU member states are those with EU-only population present
    eu_countries = (
        df.loc[df["population_EU_only"].notna(), "country"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    # Keep only valid country rows
    country_df = df[df["country"].notna()].copy()
    country_df["country"] = country_df["country"].astype(str).str.strip()

    eu_country_df = country_df[country_df["country"].isin(eu_countries)].copy()

    # CRITICAL: ensure one row per country
    eu_country_df = (
        eu_country_df
        .drop_duplicates(subset=["country"], keep="first")
        .reset_index(drop=True)
    )

    return eu_country_df
