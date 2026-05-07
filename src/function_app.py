import logging
import azure.functions as func
from triggers.extract_cliente import app as extract_cliente
from triggers.extract_entrega import app as extract_entrega
from triggers.extract_pedido import app as extract_pedido
from triggers.extract_categoria_produto import app as extract_categoria_produto
from triggers.extract_estoque_movimentacao import app as extract_estoque_movimentacao
from triggers.extract_estoque_saldo import app as extract_estoque_saldo


app = func.FunctionApp()
app.register_functions(extract_cliente)
app.register_functions(extract_entrega)
app.register_functions(extract_pedido)
app.register_functions(extract_categoria_produto)
app.register_functions(extract_estoque_movimentacao)
app.register_functions(extract_estoque_saldo)