import logging
import azure.functions as func
from triggers.extract_cliente import app as extract_cliente
from triggers.extract_entrega import app as extract_entrega
from triggers.extract_pedido import app as extract_pedido

app = func.FunctionApp()
