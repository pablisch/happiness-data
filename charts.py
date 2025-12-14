import matplotlib.pyplot as plt

def plot_region_happiness_factors(df, region: str, year: int | str, filename: str | None = None):
    year_str = str(year)
    if len(year_str) == 4:  # 2021 -> "21"
        year_str = year_str[-2:]
    suffix = f"_{year_str}"
    print(year_str)
    print(suffix)

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

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values)
    ax.set_ylabel("Average contribution to ladder score")
    ax.set_title(f"Average happiness contributors\nRegion: {region}  Year: 20{year_str}")
    ax.set_xticklabels(labels, rotation=30, ha="right")

    plt.tight_layout()

    if filename is not None:
        fig.savefig(filename, bbox_inches="tight")
        plt.close(fig)
        return filename

    return fig, ax
