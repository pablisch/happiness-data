# api.py

import matplotlib
matplotlib.use("Agg")

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import numpy as np
import math
from urllib.parse import unquote

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
