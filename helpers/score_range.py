def print_eu_ladder_score_range(df):
    """
    Prints min/max ladder scores across EU countries
    for 2021–2023 and the overall EU range.
    """
    # Filter to EU countries
    eu_df = df[df["population_EU_only"].notna()]

    if eu_df.empty:
        print("No EU rows found (population_EU_only is empty).")
        return

    score_cols = [
        "ladder_score_21",
        "ladder_score_22",
        "ladder_score_23",
    ]

    # Per-year mins and maxs
    mins = eu_df[score_cols].min()
    maxs = eu_df[score_cols].max()

    print("EU ladder score minimums by year:")
    print(mins)
    print()

    print("EU ladder score maximums by year:")
    print(maxs)
    print()

    print("Overall EU ladder score range:")
    print(f"Min: {mins.min():.3f}")
    print(f"Max: {maxs.max():.3f}")
