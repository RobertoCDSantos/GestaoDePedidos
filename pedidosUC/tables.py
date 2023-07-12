import django_tables2 as tables
from .models import Pedido

class PedidoTable(tables.Table):
    #id = tables.Column(empty_values=())
    titulo = tables.Column(attrs={"td": {"class": "my-class"}})

    class Meta:
        model = Pedido
        #template_name = "pedidosUC/semantic.html"
        template_name = "pedidosUC/index_uc_tabela.html"
        fields = ('titulo', 'descricao', 'estado', 'dataalvo')
        row_attrs = {
            'data-pk': lambda record: record.pk
        }
        