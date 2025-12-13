# data_clean_helpers.py

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

def clean_wh21_data(df):
    return df[wh21_cols_to_keep].rename(columns={
        "Country name": "country",
        "Regional indicator": "region",
        "Ladder score": "ladder_score",
        "Explained by: Log GDP per capita": "GDP",
        "Explained by: Social support": "social_support",
        "Explained by: Healthy life expectancy": "life_expectancy",
        "Explained by: Freedom to make life choices": "freedom",
        "Explained by: Generosity": "generosity",
        "Explained by: Perceptions of corruption": "corruption",
        "Dystopia + residual": "dystopia_res",
    })

def clean_wh22_data(df):
    return df[wh22_cols_to_keep].rename(columns={
        "Country": "country",
        "Happiness score": "ladder_score",
        "Explained by: Log GDP per capita": "GDP",
        "Explained by: Social support": "social_support",
        "Explained by: Healthy life expectancy": "life_expectancy",
        "Explained by: Freedom to make life choices": "freedom",
        "Explained by: Generosity": "generosity",
        "Explained by: Perceptions of corruption": "corruption",
        "Dystopia + residual": "dystopia_res",
    })