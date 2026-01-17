# api.py

import matplotlib

from charts.donut_data import compute_factor_donut

matplotlib.use("Agg")  # MUST be before pyplot is imported anywhere

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import numpy as np
import math
from urllib.parse import unquote  # decode geo_area safely

from helpers.pickle_helpers import load_pickle
from helpers.data_filter import filter_to_eu_only
from charts.contribution_bar_chart import plot_contribution_bar_chart, build_contribution_bar_title
from charts.time_line_graph import plot_time_line_graph, build_timeline_title
from charts.score_card import get_score_card_values, build_score_card_title
from charts.map_data import build_map_payload


app = FastAPI()

# ---- CORS MIDDLEWARE ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------------------------


@app.on_event("startup")
def load_data():
    df = load_pickle("wh")
    df = filter_to_eu_only(df)
    app.state.wh = df
    app.state.map_payload = build_map_payload(app.state.wh)


@app.get("/data")
def get_data():
    df = app.state.wh.copy()

    # 1) Replace +/-inf with NaN
    df = df.replace([np.inf, -np.inf], np.nan)

    # 2) Convert DataFrame to plain Python objects
    records = df.to_dict(orient="records")

    # 3) Convert any NaN to None (JSON null)
    for row in records:
        for k, v in row.items():
            if isinstance(v, float) and math.isnan(v):
                row[k] = None

    return records


@app.get("/cols")
def get_columns():
    return {"columns": list(app.state.wh.columns)}


@app.get("/contrib_bar/{geo_area}/{year}")
def contrib_bar(
    geo_area: str,
    year: int,
    show_eu: bool = Query(False),
    fixed_scale: bool = Query(False),
    # NEW: chart sizing from frontend panel
    w: int = Query(520, ge=250, le=2000),
    h: int = Query(220, ge=150, le=1600),
):
    geo_area = unquote(geo_area)

    try:
        buf = plot_contribution_bar_chart(
            app.state.wh,
            geo_area=geo_area,
            year=year,
            show_eu=show_eu,
            fixed_scale=fixed_scale,
            width_px=w,     # NEW
            height_px=h,    # NEW
        )
    except TypeError:
        # Backward-compatible error message if charts function not updated yet
        raise HTTPException(
            status_code=500,
            detail="plot_contribution_bar_chart() does not accept width_px/height_px yet. Update charts/contribution_bar_chart.py.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Cache-Control": "no-store"},
    )


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
        "geo_area": geo_area,
        "year": year,
        "show_eu": show_eu,
        "fixed_scale": fixed_scale,
    }


@app.get("/timeline_meta/{geo_area}")
def timeline_meta(
    geo_area: str,
    show_eu: bool = Query(False),
    fixed_scale: bool = Query(False),
):
    geo_area = unquote(geo_area)

    try:
        title = build_timeline_title(geo_area=geo_area, show_eu=show_eu, fixed_scale=fixed_scale)
        return {"title": title}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/timeline/{geo_area}")
def timeline(
    geo_area: str,
    show_eu: bool = Query(False),
    fixed_scale: bool = Query(False),
    # NEW: chart sizing from frontend panel
    w: int = Query(520, ge=250, le=2000),
    h: int = Query(220, ge=150, le=1600),
):
    geo_area = unquote(geo_area)

    try:
        buf = plot_time_line_graph(
            app.state.wh,
            geo_area=geo_area,
            show_eu=show_eu,
            fixed_scale=fixed_scale,
            width_px=w,     # NEW
            height_px=h,    # NEW
        )
    except TypeError:
        raise HTTPException(
            status_code=500,
            detail="plot_time_line_graph() does not accept width_px/height_px yet. Update charts/time_line_graph.py.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/score_card_meta/{geo_area}/{year}")
def score_card_meta(
    geo_area: str,
    year: int,
    show_eu: bool = Query(False),
):
    geo_area = unquote(geo_area)

    try:
        vals = get_score_card_values(app.state.wh, geo_area=geo_area, year=year)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "title": build_score_card_title(geo_area, year, show_eu=show_eu),
        "geo_area": geo_area,
        "year": year,
        "show_eu": show_eu,

        "country_score": vals["country_score"],
        "eu_score": vals["eu_score"],
        "delta_vs_eu": vals["delta_vs_eu"],

        "delta_min": vals["delta_min"],
        "delta_max": vals["delta_max"],

        "years": vals["years"],
        "selected_year": vals["selected_year"],
        "deltas_vs_selected_year": vals["deltas_vs_selected_year"],
        "year_delta_min": vals["year_delta_min"],
        "year_delta_max": vals["year_delta_max"],
        "overall_rank": vals["overall_rank"],
        "overall_total": vals["overall_total"],
        "factor_labels": vals["factor_labels"],
        "factor_values": vals["factor_values"],
        "factor_ranks": vals["factor_ranks"],
    }


@app.get("/donut/{factor}/{year}")
def donut_data(
    factor: str,
    year: int,
    eu_only: bool = Query(True),
    group_other: bool = Query(True),
):
    try:
        return compute_factor_donut(
            app.state.wh,
            factor=factor,
            year=year,
            eu_only=eu_only,
            top_n=8,
            group_other=group_other,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/map_data")
def map_data():
    return app.state.map_payload
