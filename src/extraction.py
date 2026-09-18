import pandas as pd
from config.database import engine

def extract(path:str):
    df = pd.read_csv(path)
    staging_dataset(df)
    return df

def staging_dataset(data_frame):
    data_frame.to_sql(
        "superstore_raw",
        con=engine,
        schema="staging",
        if_exists="replace",
        index=False
    )
