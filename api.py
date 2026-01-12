# api.py

import matplotlib
matplotlib.use("Agg")  # MUST be before pyplot is imported anywhere

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import numpy as np
import math

from helpers.pickle_helpers import load_pickle
from contribution_bar_chart import plot_contribution_bar_chart

app = FastAPI()

# ---- CORS MIDDLEWARE (ADD THIS) ----
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
# -----------------------------------

@app.on_event("startup")
def load_data():
    app.state.wh = load_pickle("wh")

@app.get("/data")
def get_data():
    df = app.state.wh.copy()

    # 1) Replace +/-inf with NaN
    df = df.replace([np.inf, -np.inf], np.nan)

    # 2) Convert DataFrame to plain Python objects (best chance to normalise dtypes)
    records = df.to_dict(orient="records")

    # 3) Final pass: convert any remaining NaN to None (JSON null)
    for row in records:
        for k, v in row.items():
            if isinstance(v, float) and math.isnan(v):
                row[k] = None

    return records

@app.get("/cols")
def get_columns():
    return {"columns": list(app.state.wh.columns)}

@app.get("/contrib_bar/{geo_area}/{year}")
def contrib_bar(geo_area: str, year: int):
    try:
        buf = plot_contribution_bar_chart(
            app.state.wh,
            geo_area=geo_area,
            year=year,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Cache-Control": "no-store"},
    )
