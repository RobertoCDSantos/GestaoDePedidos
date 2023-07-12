from django.db import models
from pedidos.models import *
# Create your models here.

class PedidoOutros(Pedido):
    #tipopedido = models.ForeignKey(TipoPedido, on_delete=models.CASCADE, db_column='tipoPedidoID', default=4)  # Field name made lowercase.

    class Meta:
        db_table = 'PedidoOutros'

