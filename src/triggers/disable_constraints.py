import os

import azure.functions as func
from sqlalchemy import text

from shared.sql_io import get_engine

app = func.Blueprint()

TARGET_SERVER   = str(os.getenv("SQL_TARGET_SERVER"))
TARGET_DB       = str(os.getenv("SQL_TARGET_DATABASE"))
TARGET_USER     = str(os.getenv("SQL_TARGET_USER"))
TARGET_PASSWORD = str(os.getenv("SQL_TARGET_PASSWORD"))

@app.timer_trigger(schedule="0 15 * * *", arg_name="timer", run_on_startup=False)
def disable_constraints(timer: func.TimerRequest):

    with get_engine(TARGET_SERVER, TARGET_DB, TARGET_USER, TARGET_PASSWORD).begin() as conn:
        conn.execute(
            text(
                """
                ALTER TABLE erp.categoria_produto NOCHECK CONSTRAINT ALL;
                ALTER TABLE erp.cliente NOCHECK CONSTRAINT ALL;
                ALTER TABLE erp.entrega NOCHECK CONSTRAINT ALL;
                ALTER TABLE erp.estoque_movimentacao NOCHECK CONSTRAINT ALL;
                ALTER TABLE erp.estoque_saldo NOCHECK CONSTRAINT ALL;
                ALTER TABLE erp.pedido NOCHECK CONSTRAINT ALL;
                ALTER TABLE erp.pedido_item NOCHECK CONSTRAINT ALL;
                ALTER TABLE erp.regiao NOCHECK CONSTRAINT ALL;
                ALTER TABLE erp.representante NOCHECK CONSTRAINT ALL;
                ALTER TABLE erp.titulo_receber NOCHECK CONSTRAINT ALL;
                ALTER TABLE erp.transportadora NOCHECK CONSTRAINT ALL;
                """
            ))
