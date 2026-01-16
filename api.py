# api.py

import matplotlib
matplotlib.use("Agg")  # MUST be before pyplot is imported anywhere

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import numpy as np
import math
from urllib.parse import unquote  # ✅ NEW: decode geo_area safely

from helpers.pickle_helpers import load_pickle
from charts.contribution_bar_chart import plot_contribution_bar_chart, build_contribution_bar_title
from charts.time_line_graph import plot_time_line_graph, build_timeline_title


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
    app.state.wh = load_pickle("wh")

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
):
    # Decode (e.g. "Czech%20Republic" -> "Czech Republic")
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
    # Decode here too so title matches the chart selection
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
):
    # print_eu_ladder_score_range(app.state.wh.copy())
    try:
        buf = plot_time_line_graph(
            app.state.wh,
            geo_area=geo_area,
            show_eu=show_eu,
            fixed_scale=fixed_scale,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Cache-Control": "no-store"},
    )

