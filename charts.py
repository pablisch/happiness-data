import matplotlib.pyplot as plt

def plot_region_happiness_factors(df, region: str, year: int | str, filename: str | None = None):
    """
    Create a bar chart of average contributory factors to happiness
    for a given region and year.

    df:      your main DataFrame
    region:  region name, e.g. "Western Europe"
    year:    21, 22, 23 or 2021/2022/2023 (we just look at the suffix)
    filename: if provided, save to this path and return it; otherwise return (fig, ax)
    """
    # Make sure we're using the suffix style in your columns: _21, _22, _23
    year_str = str(year)
    if len(year_str) == 4:  # 2021 -> "21"
        year_str = year_str[-2:]
    suffix = f"_{year_str}"

    # The contributory factor base names
    factor_basenames = [
        "GDP",
        "social_support",
        "life_expectancy",
        "freedom",
        "generosity",
        "corruption",
        "dystopia",
        "other",
    ]

    # Build full column names like GDP_21, social_support_21, ...
    factor_cols = [f"{name}{suffix}" for name in factor_basenames]

    # Safety: check columns exist
    missing = [c for c in factor_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns for year {year_str}: {missing}")

    # Filter to the chosen region
    region_df = df[df["region"] == region]
    if region_df.empty:
        raise ValueError(f"No rows found for region '{region}'")

    # Compute mean for each factor
    means = region_df[factor_cols].mean()

    # Prepare labels (prettier than raw column names)
    labels = [
        "GDP",
        "Social support",
        "Life expectancy",
        "Freedom",
        "Generosity",
        "Corruption (low = better)",
        "Dystopia (base)",
        "Residual (other)",
    ]

    values = means.values

    # Plot
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
