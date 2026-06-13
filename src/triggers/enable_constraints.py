import os

import azure.functions as func
from sqlalchemy import text

from shared.sql_io import get_engine

app = func.Blueprint()

TARGET_SERVER   = str(os.getenv("SQL_TARGET_SERVER"))
TARGET_DB       = str(os.getenv("SQL_TARGET_DATABASE"))
TARGET_USER     = str(os.getenv("SQL_TARGET_USER"))
TARGET_PASSWORD = str(os.getenv("SQL_TARGET_PASSWORD"))

@app.timer_trigger(schedule="59 15 * * *", arg_name="timer", run_on_startup=False)
def enable_constraints(timer: func.TimerRequest):

    with get_engine(TARGET_SERVER, TARGET_DB, TARGET_USER, TARGET_PASSWORD).begin() as conn:
        conn.execute(
            text(
                """
                ALTER TABLE erp.categoria_produto CHECK CONSTRAINT ALL;
                ALTER TABLE erp.cliente CHECK CONSTRAINT ALL;
                ALTER TABLE erp.entrega CHECK CONSTRAINT ALL;
                ALTER TABLE erp.estoque_movimentacao CHECK CONSTRAINT ALL;
                ALTER TABLE erp.estoque_saldo CHECK CONSTRAINT ALL;
                ALTER TABLE erp.pedido CHECK CONSTRAINT ALL;
                ALTER TABLE erp.pedido_item CHECK CONSTRAINT ALL;
                ALTER TABLE erp.regiao CHECK CONSTRAINT ALL;
                ALTER TABLE erp.representante CHECK CONSTRAINT ALL;
                ALTER TABLE erp.titulo_receber CHECK CONSTRAINT ALL;
                ALTER TABLE erp.transportadora CHECK CONSTRAINT ALL;
                """
            ))
