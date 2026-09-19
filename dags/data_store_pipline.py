from datetime import datetime
from airflow.decorators import dag, task

@dag(
    schedule=None,
    start_date=datetime(2026, 9, 18),
    catchup=False,
)
def pipline_etl():
    # 1 Extraction
    @task()
    def extract(path):
        import pandas as pd
        return pd.read_csv(path)

    # 2 Staging
    @task()
    def staging(df):
        from config.database import engine

        df.to_sql(
            "superstore_raw",
            con=engine,
            schema="staging",
            if_exists="replace",
            index=False
        )

    # 3 Transform
    @task()
    def transform(df):
        from src.cleaning import duplicate_data, text_cleaning, data_types_parsing, impossible_and_suspicious_values, imputation, structural_standardisation, pseudonymisation

        return pseudonymisation(
            structural_standardisation(
                imputation(
                    impossible_and_suspicious_values(
                        data_types_parsing(
                            text_cleaning(
                                duplicate_data(df)
                            )
                        )
                    )
                )
            )
        )

    # 4 Loading
    @task()
    def load(df):
        from src.loading import load
        load(df)

    df = extract('/opt/airflow/project/data/row.csv')
    staging(df)
    load(transform(df))

# Appell dag
pipline_etl()