from datetime import datetime
from pathlib import Path
import pandas as pd


def load_csv_files(directory: Path, pattern: str):
    files = sorted(list(directory.glob(pattern)))
    ret = []
    for file in files:
        df = pd.read_csv(str(file))
        ret.append(df)
    return pd.concat(ret)