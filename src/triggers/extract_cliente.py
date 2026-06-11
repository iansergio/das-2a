import azure.functions as func
import logging
import os
import datetime

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

app = func.Blueprint()

@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_cliente(timer: func.TimerRequest) -> None:
    # Source
    source_server = os.getenv("SQL_SERVER_SOURCE")
    source_db = os.getenv("SQL_DATABASE_SOURCE")
    source_user = os.getenv("SQL_USER_SOURCE")
    source_password = os.getenv("SQL_PASSWORD_SOURCE")
    
    source_conn_url = URL.create(
        "mssql+pyodbc",
        username=source_user,
        password=source_password,
        host=source_server,
        port=1433,
        database=source_db,
        
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "Encrypt": "yes",
            "TrustServerCertificate": "no",
            "Connection Timeout": "30"
        }
    )
    
    source_engine = create_engine(source_conn_url)
    
    try:
        start = datetime.datetime.now()
        
        with source_engine.connect() as source_conn:
            res = source_conn.execute(text("SELECT * FROM erp.cliente"))
            df = pd.DataFrame(res.fetchall(), columns=list(res.keys()))
            
            tempo = datetime.datetime.now() - start
            logging.info(f"Tempo de execução: {tempo.total_seconds():.2f}s")
            
    except Exception as e:
        logging.exception("Erro ao ler erp.cliente")
        raise
    
    # Target
    target_server = os.getenv("SQL_SERVER_TARGET")
    target_db = os.getenv("SQL_DATABASE_TARGET")
    target_user = os.getenv("SQL_USER_TARGET")
    target_password = os.getenv("SQL_PASSWORD_TARGET")
    
    target_conn_url = URL.create(
        "mssql+pyodbc",
        username=target_user,
        password=target_password,
        host=target_server,
        port=1433,
        database=target_db,
        
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "Encrypt": "yes",
            "TrustServerCertificate": "no",
            "Connection Timeout": "30"
        }
    )
    
    target_engine = create_engine(target_conn_url)
    
    try:
        with target_engine.connect() as target_conn:
            df.to_sql(name='cliente', con=target_conn, if_exists='append', schema='erp', index=False)
            print(f"Execução finalizada. Registros: {len(df)}")
            
    except Exception as e:
        logging.exception("Erro ao inserir em erp.cliente")
        raise
