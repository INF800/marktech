from pathlib import Path
import pandas as pd
import numpy as np

def load_dfs(files_sorted):
    ret = []
    for file in files_sorted:
        df = pd.read_csv(str(file))
        ret.append(df)
    return pd.concat(ret)


def clean_df(df):
    return df.fillna(method="ffill")


def extract_unvaraiate(df, use_utc=True):
    df = df[['utc_time', 'current_values']]
    
    # set time index
    df['time'] = pd.to_datetime(df['utc_time']).dt.floor('Min')
    df.set_index('time', inplace=True)
    
    # change time zone
    if not use_utc:
        df.index = df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
    
    # univariate feaure & time    
    df['y'] = df.current_values.apply(lambda x: float(x.split()[0].strip().replace(",", "")))
    return df[['y']]
    

def main():
    
    UTC_TIMEZONE = False
    WRITE_DIR = Path('data/feature')
    RAW_DIR = Path('data/raw')
    STOCKS = ['HLL', 'RELI', 'HDBK', 'INFY']

    for stock in STOCKS:
        files = RAW_DIR.glob(f"*{stock}*.csv")
        files = sorted(list(files))

        raw = load_dfs(files)
        clean = clean_df(raw)
        uni = extract_unvaraiate(clean, use_utc=UTC_TIMEZONE)

        path = WRITE_DIR / f'{stock}-univar-latest.csv'
        uni.to_csv(str(path))



if __name__=='__main__':
    main()