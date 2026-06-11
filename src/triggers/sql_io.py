import logging

import pandas as pd

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

def get_engine(server: str, database: str, user: str, password: str) -> Engine:
    
    connection_url = URL.create(
        "mssql+pyodbc",
        host=server,
        port=1433,
        database=database,
        username=user,
        password=password,
        
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "Encrypt": "yes",
            "TrustServerCertificate": "no",
            "Connection Timeout": "30"
        }
    )
    
    return create_engine(connection_url)

def extract(engine, table: str, batch_size: int) -> pd.DataFrame:
    
    query = f"""SELECT * FROM erp.{table}"""

    chunks = []
    
    with engine.connect() as conn:
        for chunk in pd.read_sql(text(query), conn, chunksize=batch_size):
            chunks.append(chunk)

    df = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
    logging.info("Extração concluída: %d registros lidos de %s", len(df), table)
    return df

def load(df: pd.DataFrame, engine, table: str, batch_size: int) -> None:
    
    if df.empty:
        logging.info("Nada a carregar, DataFrame vazio")
        return

    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM erp.{table}"))
        
        conn.execute(text(f"SET IDENTITY_INSERT erp.{table} ON"))
        
        df.to_sql(
            schema='erp',
            name=table,
            con=conn,
            if_exists="append",
            index=False,
            chunksize=batch_size
        )
        
        conn.execute(text(f"SET IDENTITY_INSERT erp.{table} OFF"))
