# api.py

import matplotlib
matplotlib.use("Agg")  # use non-GUI backend (important on macOS!)

from fastapi import FastAPI
from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
import random

from helpers.pickle_helpers import *

app = FastAPI()

@app.on_event("startup")
def load_data():
    app.state.wh = load_pickle("wh")

@app.get("/data")
def get_data():
    wh = app.state.wh
    return wh.to_dict(orient="records")

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
