# api.py

import matplotlib
matplotlib.use("Agg")  # use non-GUI backend (important on macOS!)

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
import random

from helpers.pickle_helpers import *
from charts import *

app = FastAPI()

@app.on_event("startup")
def load_data():
    app.state.wh = load_pickle("wh")

@app.get("/data")
def get_data():
    wh = app.state.wh
    return wh.to_dict(orient="records")

@app.get("/cols")
def get_columns():
    wh = app.state.wh
    return {"columns": list(wh.columns)}


@app.get("/chart")
def get_chart():
    x = [1, 2, 3, 4, 5]
    y = [random.randint(1, 10) for _ in x]

    filename = "chart.png"

    plt.figure()
    plt.plot(x, y)
    plt.title("Random Chart")
    plt.savefig(filename)
    plt.close()

    return FileResponse(filename, media_type="image/png")

# @app.get("/chart/{region}/{year}")
# def region_chart(region: str, year: int):
#     buf = plot_region_happiness_factors(app.state.wh, region, year)
#     return StreamingResponse(buf, media_type="image/png")

@app.get("/chart/{style}/{region}/{year}")
def region_chart(style: str, region: str, year: int):
    df = app.state.wh

    if style == "original":
        buf = plot_region_original(df, region, year)
    elif style == "polished":
        buf = plot_region_polished(df, region, year)
    elif style == "seaborn":
        buf = plot_region_seaborn(df, region, year)
    else:
        raise HTTPException(status_code=404, detail="Unknown chart style")

    return StreamingResponse(buf, media_type="image/png")

