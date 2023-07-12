from django.db import models
from pedidos.models import *
# Create your models here.

class PedidoHorario(Pedido):
    #tipopedido = models.ForeignKey(TipoPedido, on_delete=models.CASCADE, db_column='tipoPedidoID')  # Field name made lowercase.

    class Meta:
        db_table = 'PedidoHorario'

