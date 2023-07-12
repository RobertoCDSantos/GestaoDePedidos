import django_tables2 as tables
from .models import Pedido

class PedidosTable(tables.Table):
    titulo = tables.Column(attrs={"td": {"class": "my-class"}})

    class Meta:
        model = Pedido
        template_name = "pedidosOutros/indexOutrosTabela.html"
        fields = ('titulo', 'descricao', 'estado', 'dataalvo')
        row_attrs = {
            'data-pk': lambda record: record.pk
        }