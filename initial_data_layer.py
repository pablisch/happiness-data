# initial_data_layer.py
import pandas as pd

def load_raw_data():
    wh21 = pd.read_csv("./data/world-happiness-report-2021.csv")
    wh22 = pd.read_csv("./data/world-happiness-report-2022.csv")
    wh23 = pd.read_csv("./data/world-happiness-report-2023.csv")
    w_pop = pd.read_csv("./data/population.csv")
    eu = pd.read_csv("./data/Eu_member.csv")
    return wh21, wh22, wh23, w_pop, eu


def process_data():
    wh21, wh22, wh23, w_pop, eu = load_raw_data()

    print(wh21.head())
    print(wh22.head())
    print(wh23.head())
    print(w_pop.head())
    print(eu.head())

    # 👉 Do all your expensive work here:
    # joins, groupbys, feature engineering, etc.
    # Example:
    # combined = (
    #     pd.concat([df1, df2, df3, df4, df5], ignore_index=True)
    #     .dropna()
    # )

    # Maybe you precompute some aggregates that many charts need:
    # totals_by_day = combined.groupby("date")["value"].sum().reset_index()
    # totals_by_category = combined.groupby("category")["value"].sum().reset_index()

    # Return whatever you need for charts later
    # return {
    #     "combined": combined,
    #     "totals_by_day": totals_by_day,
    #     "totals_by_category": totals_by_category,
    # }

process_data()
