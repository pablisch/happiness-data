# data_clean_helpers.py

import pandas as pd

cols_to_keep = [
    "Explained by: Log GDP per capita",
    "Explained by: Social support",
    "Explained by: Healthy life expectancy",
    "Explained by: Freedom to make life choices",
    "Explained by: Generosity",
    "Explained by: Perceptions of corruption",
    "Dystopia + residual",
]

wh21_cols_to_keep = [
    "Country name",
    "Regional indicator",
    "Ladder score"
] + cols_to_keep

wh22_cols_to_keep = [
    "Country",
    "Happiness score"
] + cols_to_keep
wh22_cols_to_keep[2] = "Explained by: GDP per capita"
wh22_cols_to_keep[8] = "Dystopia (1.83) + residual"

wh23_cols_to_keep = [
    "Country name",
    "Ladder score"
] + cols_to_keep

def clean_wh21_data(df):
    suffix = "_21"
    df = df[wh21_cols_to_keep].rename(columns={
        "Country name": "country",
        "Regional indicator": "region",
        "Ladder score": f"ladder_score{suffix}",
        "Explained by: Log GDP per capita": f"GDP{suffix}",
        "Explained by: Social support": f"social_support{suffix}",
        "Explained by: Healthy life expectancy": f"life_expectancy{suffix}",
        "Explained by: Freedom to make life choices": f"freedom{suffix}",
        "Explained by: Generosity": f"generosity{suffix}",
        "Explained by: Perceptions of corruption": f"corruption{suffix}",
        "Dystopia + residual": f"dystopia_res{suffix}",
    })
    dystopia_h = 2.43
    df[f"dystopia{suffix}"] = dystopia_h
    df[f"other{suffix}"] = df[f"dystopia_res{suffix}"] - dystopia_h
    df = df.drop(columns=[f"dystopia_res{suffix}"])
    return df

def clean_wh22_data(df):
    suffix = "_22"
    df = df[wh22_cols_to_keep].rename(columns={
        "Country": "country",
        "Happiness score": f"ladder_score{suffix}",
        "Explained by: GDP per capita": f"GDP{suffix}",
        "Explained by: Social support": f"social_support{suffix}",
        "Explained by: Healthy life expectancy": f"life_expectancy{suffix}",
        "Explained by: Freedom to make life choices": f"freedom{suffix}",
        "Explained by: Generosity": f"generosity{suffix}",
        "Explained by: Perceptions of corruption": f"corruption{suffix}",
        "Dystopia (1.83) + residual": f"dystopia_res{suffix}",
        # "Dystopia + residual": f"dystopia_res{suffix}",
    })
    dystopia_h = 1.83
    df[f"dystopia{suffix}"] = dystopia_h
    df[f"other{suffix}"] = df[f"dystopia_res{suffix}"] - dystopia_h
    df = df.drop(columns=[f"dystopia_res{suffix}"])
    return df

def clean_wh23_data(df):
    suffix = "_23"
    df = df[wh23_cols_to_keep].rename(columns={
        "Country name": "country",
        "Ladder score": f"ladder_score{suffix}",
        "Explained by: Log GDP per capita": f"GDP{suffix}",
        "Explained by: Social support": f"social_support{suffix}",
        "Explained by: Healthy life expectancy": f"life_expectancy{suffix}",
        "Explained by: Freedom to make life choices": f"freedom{suffix}",
        "Explained by: Generosity": f"generosity{suffix}",
        "Explained by: Perceptions of corruption": f"corruption{suffix}",
        "Dystopia + residual": f"dystopia_res{suffix}",
    })
    dystopia_h = 1.778
    df[f"dystopia{suffix}"] = dystopia_h
    df[f"other{suffix}"] = df[f"dystopia_res{suffix}"] - dystopia_h
    df = df.drop(columns=[f"dystopia_res{suffix}"])
    return df

def check_common_countries(df21, df22, df23):
    c21 = set(df21["country"])
    c22 = set(df22["country"])
    c23 = set(df23["country"])

    # Countries that appear in *any* df
    all_countries = c21 | c22 | c23

    # Countries that appear in *all* dfs
    common_countries = c21 & c22 & c23

    # Countries that are in at least one df but not in all of them
    not_in_all = all_countries - common_countries

    not_in_21 = all_countries - c21
    not_in_22 = common_countries - c22
    not_in_23 = common_countries - c23
    not_in_22_or_23 = common_countries - (c22 | c23)

    # print(f"not_in_all: {len(not_in_all)} - {not_in_all}")
    # print(f"not_in_21: {len(not_in_21)} - {not_in_21}")
    # print(f"not_in_22: {len(not_in_22)} - {not_in_22}")
    # print(f"not_in_23: {len(not_in_23)} - {not_in_23}")
    # print(f"not_in_22_or_23: {len(not_in_22_or_23)} - {not_in_22_or_23}")
    #
    # print("\n\n")
    #
    # for country in sorted(not_in_all):
    #     print(
    #         country,
    #         {
    #             "in_21": country in c21,
    #             "in_22": country in c22,
    #             "in_23": country in c23,
    #         }
    #     )

def check_population_country_matches(wh_df, pop_df):
    wh_countries = set(wh_df["country"])
    pop_countries = set(pop_df["country"])

    # Countries that appear in *either* df
    all_countries = wh_countries | pop_countries

    # Countries that appear in *both* dfs
    common_countries = wh_countries & wh_countries

    # Countries that are in at least one df but not in all of them
    not_in_all = all_countries - common_countries

    for country in sorted(not_in_all):
        print(
            country,
            {
                "in_wh": country in wh_countries,
                "in_pop": country in pop_countries,
            }
        )

# convert numeric object type to int, e.g. 1,234,567 (object) -> 1234567 (int)
def numeric_object_to_int(df, col):
    df[col] = (
        df[col]
        .astype(str)  # convert objects to string
        .str.replace(",", "", regex=False)  # remove thousands separators
        .str.strip()  # remove whitespace
    )
    df[col] = pd.to_numeric(df[col], errors="coerce").round().astype("Int64")
    return df[col]