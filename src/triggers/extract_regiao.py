import logging
import os
from datetime import datetime, timezone

import azure.functions as func

from sql_io import get_engine, extract, load

app = func.Blueprint()

SOURCE_SERVER   = str(os.getenv("SQL_SOURCE_SERVER"))
SOURCE_DB       = str(os.getenv("SQL_SOURCE_DATABASE"))
SOURCE_TABLE    = str("regiao") # Tabela de origem do professor
SOURCE_USER     = str(os.getenv("SQL_SOURCE_USER"))
SOURCE_PASSWORD = str(os.getenv("SQL_SOURCE_PASSWORD"))

TARGET_SERVER   = str(os.getenv("SQL_TARGET_SERVER"))
TARGET_DB       = str(os.getenv("SQL_TARGET_DATABASE"))
TARGET_TABLE    = str("regiao") # Tabela de destino
TARGET_USER     = str(os.getenv("SQL_TARGET_USER"))
TARGET_PASSWORD = str(os.getenv("SQL_TARGET_PASSWORD"))

BATCH_SIZE      = int("5000")

# Trigger da Azure Function
@app.timer_trigger(schedule="0 15 * * *", arg_name="timer", run_on_startup=False)
def extract_regiao(timer: func.TimerRequest) -> None:
    
    start = datetime.now(tz=timezone.utc)
    logging.info("ETL %s iniciando em %s", TARGET_TABLE, start.isoformat())
    
    if timer.past_due:
        logging.info("O Timer atrasou, executando agora!")
    
    try:
        source_engine = get_engine(SOURCE_SERVER, SOURCE_DB, SOURCE_USER, SOURCE_PASSWORD)
        target_engine = get_engine(TARGET_SERVER, TARGET_DB, TARGET_USER, TARGET_PASSWORD)
        
        df = extract(source_engine, SOURCE_TABLE, BATCH_SIZE)
        
        load(df, target_engine, TARGET_TABLE, BATCH_SIZE)
        
        elapsed = (datetime.now(tz=timezone.utc) - start).total_seconds()
        logging.info("ETL concluído com sucesso. Duração %.2fs | Registros: %d", elapsed, len(df))
    
    except Exception as e:
        logging.exception("Falha no ETL: %s", e)
        raise
