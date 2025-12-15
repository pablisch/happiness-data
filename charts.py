# import matplotlib.pyplot as plt
# from io import BytesIO
#
# def plot_region_happiness_factors(
#     df,
#     region: str,
#     year: int | str,
# ) -> BytesIO:
#     year_str = str(year)
#     if len(year_str) == 4:  # 2021 -> "21"
#         year_str = year_str[-2:]
#     suffix = f"_{year_str}"
#
#     factor_basenames = [
#         "GDP",
#         "social_support",
#         "life_expectancy",
#         "freedom",
#         "generosity",
#         "corruption",
#         "other",
#     ]
#
#     factor_cols = [f"{name}{suffix}" for name in factor_basenames]
#
#     missing = [c for c in factor_cols if c not in df.columns]
#     if missing:
#         raise ValueError(f"Missing expected columns for year 20{year_str}: {missing}")
#
#     region_df = df[df["region"] == region]
#     if region_df.empty:
#         raise ValueError(f"No rows found for region '{region}'")
#
#     means = region_df[factor_cols].mean()
#
#     labels = [
#         "GDP",
#         "Social support",
#         "Life expectancy",
#         "Freedom",
#         "Generosity",
#         "Corruption (low = better)",
#         "Residual (other)",
#     ]
#
#     values = means.values
#
#     fig, ax = plt.subplots(figsize=(8, 4))
#     ax.bar(labels, values)
#     ax.set_ylabel("Average contribution to ladder score")
#     ax.set_title(f"Average happiness contributors\nRegion: {region}  Year: 20{year_str}")
#     ax.set_xticklabels(labels, rotation=30, ha="right")
#
#     plt.tight_layout()
#
#     # 🔽 New bit: render to in-memory PNG and return buffer
#     buf = BytesIO()
#     fig.savefig(buf, format="png", bbox_inches="tight")
#     plt.close(fig)          # important to avoid memory leaks
#     buf.seek(0)             # rewind so StreamingResponse can read from start
#     return buf

# charts.py
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")  # for seaborn style

base_width = 12
base_height = 8

def _compute_region_factors(df, region: str, year: int | str):
    year_str = str(year)
    if len(year_str) == 4:  # 2021 -> "21"
        year_str = year_str[-2:]
    suffix = f"_{year_str}"

    factor_basenames = [
        "GDP",
        "social_support",
        "life_expectancy",
        "freedom",
        "generosity",
        "corruption",
        "other",
    ]
    factor_cols = [f"{name}{suffix}" for name in factor_basenames]

    missing = [c for c in factor_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns for year 20{year_str}: {missing}")

    region_df = df[df["region"] == region]
    if region_df.empty:
        raise ValueError(f"No rows found for region '{region}'")

    means = region_df[factor_cols].mean()

    labels = [
        "GDP",
        "Social support",
        "Life expectancy",
        "Freedom",
        "Generosity",
        "Corruption (low = better)",
        "Residual (other)",
    ]
    values = means.values

    return labels, values, year_str

def plot_region_original(df, region: str, year: int | str) -> BytesIO:
    labels, values, year_str = _compute_region_factors(df, region, year)

    fig, ax = plt.subplots(figsize=(base_width, base_height))
    ax.bar(labels, values)
    ax.set_ylabel("Average contribution to ladder score")
    ax.set_title(f"Average happiness contributors\nRegion: {region}  Year: 20{year_str}")
    ax.set_xticklabels(labels, rotation=30, ha="right")

    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

def plot_region_polished(df, region: str, year: int | str) -> BytesIO:
    labels, values, year_str = _compute_region_factors(df, region, year)

    fig, ax = plt.subplots(figsize=(base_width, base_height))
    ax.bar(labels, values)

    ax.set_ylabel("Average contribution to ladder score", fontsize=11)
    ax.set_title(
        f"Average happiness contributors\nRegion: {region}  Year: 20{year_str}",
        fontsize=13,
    )
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.tick_params(axis="y", labelsize=9)

    ax.grid(axis="y", alpha=0.3)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

def plot_region_seaborn(df, region: str, year: int | str) -> BytesIO:
    labels, values, year_str = _compute_region_factors(df, region, year)

    plot_df = pd.DataFrame({
        "Factor": labels,
        "Contribution": values,
    })

    fig, ax = plt.subplots(figsize=(base_width, base_height))

    sns.barplot(
        data=plot_df,
        x="Factor",
        y="Contribution",
        ax=ax,
    )

    ax.set_ylabel("Average contribution to ladder score", fontsize=11)
    ax.set_xlabel("")
    ax.set_title(
        f"Average happiness contributors\nRegion: {region}  Year: 20{year_str}",
        fontsize=13,
    )

    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right", fontsize=9)
    ax.tick_params(axis="y", labelsize=9)

    sns.despine(ax=ax)
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

