# initial_data_layer.py
import pandas as pd
import pickle

from helpers.data_clean_helpers import *
from helpers.pickle_helpers import *

def load_raw_data():
    wh21 = pd.read_csv("./data/world-happiness-report-2021.csv")
    wh22 = pd.read_csv("./data/world-happiness-report-2022.csv")
    wh23 = pd.read_csv("./data/world-happiness-report-2023.csv")
    w_pop = pd.read_csv("./data/population.csv")
    eu = pd.read_csv("./data/Eu_member.csv")
    return wh21, wh22, wh23, w_pop, eu

def process_data():
    wh21, wh22, wh23, w_pop, eu = load_raw_data()

    wh21 = clean_wh21_data(wh21)
    print(wh21.head())
    wh22 = clean_wh22_data(wh22)
    wh23 = clean_wh23_data(wh23)
    print(w_pop.head(10))
    w_pop = w_pop[["Country", "Population"]].rename(columns={"Country": "country", "Population": "population"})
    eu = eu[["Country", "Population[2]", "Area (km2)"]].rename(columns={"Country": "country", "Population[2]": "population_EU_only", "Area (km2)": "area_km2_EU_only"})

    wh21["country"] = wh21["country"].str.replace("Palestinian Territories", "State of Palestine", regex=False).str.strip()
    wh22["country"] = wh22["country"].str.replace("Palestinian Territories", "State of Palestine", regex=False).str.strip()
    wh22["country"] = wh22["country"].str.replace("*", "", regex=False).str.strip()
    wh22["country"] = wh22["country"].str.replace("Czechia", "Czech Republic", regex=False).str.strip()
    wh23["country"] = wh23["country"].str.replace("Turkiye", "Turkey", regex=False).str.strip()
    wh23["country"] = wh23["country"].str.replace("Czechia", "Czech Republic", regex=False).str.strip()

    check_common_countries(wh21, wh22, wh23)

    print(f"wh21: {wh21.head(50)}")
    print(f"wh22: {wh22.head()}")
    print(f"wh23: {wh23.head()}")

    wh = (
        wh21
        .merge(wh22, on="country", how="inner")
        .merge(wh23, on="country", how="inner")
    )

    print(f"wh: {wh.head()}")
    # print(w_pop)

    # check_population_country_matches(wh, w_pop)

    wh = (
        wh.merge(w_pop, on="country", how="left")
        .merge(eu, on="country", how="left")
    )

    wh["population_EU_only"] = numeric_object_to_int(wh, "population_EU_only")
    wh["area_km2_EU_only"] = numeric_object_to_int(wh, "area_km2_EU_only")
    wh.country = wh.country.astype("string")
    wh.region = wh.region.astype("string")

    # print(wh.head(50))
    print(wh.dtypes)
    #
    print(wh.region.unique())

    write_pickle(wh, "wh")



process_data()
