import azure.functions as func
import logging
import os
import datetime

from sqlalchemy import create_engine, text

app = func.Blueprint()

@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_cliente(timer: func.TimerRequest) -> None:
    
    server = os.getenv("SQL_SERVER_SOURCE")
    db = os.getenv("SQL_DATABASE_SOURCE")
    user = os.getenv("SQL_USER_SOURCE")
    password = os.getenv("SQL_PASSWORD_SOURCE")
    
    conn_str = ("Driver={SQL Server};"
        f"conn_strServer=tcp:{server}.database.windows.net,1433;"
        f"Database={db};"
        f"Uid={user};"
        f"Pwd={password};"
    )
    
    engine = create_engine(conn_str)
    
    try:
        start = datetime.datetime.now()
        
        with engine.connect() as conn:
            res = conn.execute(text("SELECT * FROM erp.pedido"))
            
            for row in res:
                logging.info(row)
                
            tempo = datetime.datetime.now() - start
            logging.info(f"Tempo de execução: {tempo.total_seconds():.2f}s")   

    except Exception as e:
        logging.error(f"Erro ao ler erp.cliente: {str(e)}")
        raise
