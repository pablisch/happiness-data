# api.py

import matplotlib
matplotlib.use("Agg")

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import numpy as np
import math
from urllib.parse import unquote

from fastapi.responses import JSONResponse
import pandas as pd

from helpers.pickle_helpers import load_pickle
from helpers.data_filter import filter_to_eu_only
from charts.contribution_bar_chart import plot_contribution_bar_chart, build_contribution_bar_title
from charts.time_line_graph import plot_time_line_graph, build_timeline_title
from charts.score_card import get_score_card_values, build_score_card_title
from charts.donut_data import compute_factor_donut
from charts.map_data import build_map_payload

app = FastAPI()

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def load_data():
    df = load_pickle("wh")
    df = filter_to_eu_only(df)
    app.state.wh = df
    app.state.map_payload = build_map_payload(df)

@app.get("/data")
def get_data():
    df = app.state.wh.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    records = df.to_dict(orient="records")
    for row in records:
        for k, v in row.items():
            if isinstance(v, float) and math.isnan(v):
                row[k] = None

    return records

@app.get("/contrib_bar/{geo_area}/{year}")
def contrib_bar(
    geo_area: str,
    year: int,
    show_eu: bool = Query(False),
    fixed_scale: bool = Query(False),
):
    geo_area = unquote(geo_area)

    try:
        buf = plot_contribution_bar_chart(
            app.state.wh,
            geo_area=geo_area,
            year=year,
            show_eu=show_eu,
            fixed_scale=fixed_scale,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(buf, media_type="image/png")

@app.get("/contrib_bar_meta/{geo_area}/{year}")
def contrib_bar_meta(
    geo_area: str,
    year: int,
    show_eu: bool = Query(False),
    fixed_scale: bool = Query(False),
):
    geo_area = unquote(geo_area)
    return {
        "title": build_contribution_bar_title(geo_area, year, show_eu),
    }

@app.get("/timeline/{geo_area}")
def timeline(
    geo_area: str,
    show_eu: bool = Query(False),
    fixed_scale: bool = Query(False),
):
    geo_area = unquote(geo_area)

    try:
        buf = plot_time_line_graph(
            app.state.wh,
            geo_area=geo_area,
            show_eu=show_eu,
            fixed_scale=fixed_scale,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(buf, media_type="image/png")

@app.get("/timeline_meta/{geo_area}")
def timeline_meta(
    geo_area: str,
    show_eu: bool = Query(False),
    fixed_scale: bool = Query(False),
):
    geo_area = unquote(geo_area)
    return {
        "title": build_timeline_title(geo_area, show_eu, fixed_scale),
    }

@app.get("/score_card_meta/{geo_area}/{year}")
def score_card_meta(
    geo_area: str,
    year: int,
    show_eu: bool = Query(False),
):
    geo_area = unquote(geo_area)

    vals = get_score_card_values(app.state.wh, geo_area, year)

    return {
        "title": build_score_card_title(geo_area, year, show_eu),
        **vals,
    }

@app.get("/donut/{factor}/{year}")
def donut_data(
    factor: str,
    year: int,
    eu_only: bool = Query(True),
    group_other: bool = Query(True),
):
    return compute_factor_donut(
        app.state.wh,
        factor=factor,
        year=year,
        eu_only=eu_only,
        top_n=8,
        group_other=group_other,
    )

@app.get("/map_data")
def map_data():
    return app.state.map_payload


@app.get("/debug/factor_values/{country}/{factor}/{year}")
def debug_factor_values(country: str, factor: str, year: int):
    df = app.state.wh.copy()

    year_str = str(year)
    if len(year_str) == 4:
        year_str = year_str[-2:]

    value_col = f"ladder_score_{year_str}" if factor == "combined_score" else f"{factor}_{year_str}"

    if value_col not in df.columns:
        return JSONResponse(
            status_code=400,
            content={"error": f"Missing column {value_col}", "available_columns_sample": list(df.columns)[:40]},
        )

    df = df[df["country"].notna()].copy()
    df["country"] = df["country"].astype(str).str.strip()

    c = country.strip()
    rows = df[df["country"] == c].copy()

    if rows.empty:
        # helpful: show close matches
        matches = df["country"].dropna().unique().tolist()
        maybe = [m for m in matches if c.lower() in m.lower()][:20]
        return {"error": f"No rows for country={c}", "maybe": maybe}

    raw = rows[value_col]

    # show values including NaN
    raw_list = []
    for v in raw.tolist():
        if isinstance(v, float) and np.isnan(v):
            raw_list.append(None)
        else:
            raw_list.append(v)

    numeric = pd.to_numeric(raw, errors="coerce")
    mean = float(np.nanmean(numeric.values)) if np.isfinite(numeric.values).any() else None

    return {
        "country": c,
        "factor": factor,
        "year": year,
        "value_col": value_col,
        "row_count_for_country": int(len(rows)),
        "raw_values": raw_list,
        "mean_used_by_donut": mean,
        "unique_values": sorted({v for v in raw_list if v is not None})[:50],
    }
