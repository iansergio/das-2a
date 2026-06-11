import logging
import os
from datetime import datetime, timezone

import azure.functions as func
import pandas as pd

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

app = func.Blueprint()

SOURCE_SERVER   = str(os.getenv("SQL_SOURCE_SERVER"))
SOURCE_DB       = str(os.getenv("SQL_SOURCE_DATABASE"))
SOURCE_TABLE    = str("regiao")
SOURCE_USER     = str(os.getenv("SQL_SOURCE_USER"))
SOURCE_PASSWORD = str(os.getenv("SQL_SOURCE_PASSWORD"))
TARGET_SERVER   = str(os.getenv("SQL_TARGET_SERVER"))
TARGET_DB       = str(os.getenv("SQL_TARGET_DATABASE"))
TARGET_TABLE    = str("regiao")
TARGET_USER     = str(os.getenv("SQL_TARGET_USER"))
TARGET_PASSWORD = str(os.getenv("SQL_TARGET_PASSWORD"))
BATCH_SIZE      = int("5000")

def _get_engine(server: str, database: str, user: str, password: str):
    
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
    
    query = f"""
        SELECT * 
        FROM erp.{table}
    """

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
        df.to_sql(
            name=table,
            con=conn,
            if_exists="append",
            index=False,
            chunksize=batch_size
        )

@app.timer_trigger(schedule="0 3 * * *", arg_name="timer", run_on_startup=False)
def extract_regiao(timer: func.TimerRequest) -> None:
    start = datetime.now(tz=timezone.utc)
    logging.info("ETL %s iniciando em %s", TARGET_TABLE, start.isoformat())
    
    if timer.past_due:
        logging.info("O Timer atrasou, executando agora!")
    
    try:
        source_engine = _get_engine(SOURCE_SERVER, SOURCE_DB, SOURCE_USER, SOURCE_PASSWORD)
        target_engine = _get_engine(TARGET_SERVER, TARGET_DB, TARGET_USER, TARGET_PASSWORD)
        
        df = extract(source_engine, SOURCE_TABLE, BATCH_SIZE)
        
        load(df, target_engine, TARGET_TABLE, BATCH_SIZE)
        
        elapsed = (datetime.now(tz=timezone.utc) - start).total_seconds()
        logging.info("ETL concluído com sucesso. Duração %.2fs | Registros: %d", elapsed, len(df))
    
    except Exception as e:
        logging.exception("Falha no ETL: %s", e)
        raise
