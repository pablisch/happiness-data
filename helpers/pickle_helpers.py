from pathlib import Path
import pickle

# Path to THIS file (your helper)
HERE = Path(__file__).resolve()

# Project root = directory ABOVE the helpers folder
PROJECT_ROOT = HERE.parent.parent

PICKLE_DIR = PROJECT_ROOT / "data" / "pickles"
PICKLE_DIR.mkdir(exist_ok=True)

def write_pickle(data, filename="wh"):
    filepath = PICKLE_DIR / f"{filename}.pkl"
    with open(filepath, "wb") as f:
        pickle.dump(data, f)

def load_pickle(filename = "wh"):
    filepath = PICKLE_DIR / f"{filename}.pkl"
    with open(filepath, "rb") as f:
        return pickle.load(f)