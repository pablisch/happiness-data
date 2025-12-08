# api.py
import matplotlib
matplotlib.use("Agg")  # use non-GUI backend (important on macOS!)

from fastapi import FastAPI
from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
import random

app = FastAPI()

@app.get("/data")
def get_data():
    return {
        "numbers": [random.randint(1, 100) for _ in range(5)]
    }

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
