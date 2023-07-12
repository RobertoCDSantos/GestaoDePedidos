import django_tables2 as tables
from .models import AnoLetivo,Pedido

class AnoLetivoTable(tables.Table):
    #id = tables.Column(empty_values=())
    #titulo = tables.Column(attrs={"td": {"class": "my-class"}})

    class Meta:
        model = AnoLetivo
        #template_name = "pedidosUC/semantic.html"
        template_name = "index_anos_tabela.html"
        fields = ('ano', 'datainicio', 'datafim','estado')
        row_attrs = {
            'data-pk': lambda record: record.pk
        }



class PedidoTable(tables.Table):
    #id = tables.Column(empty_values=())
    titulo = tables.Column(attrs={"td": {"class": "my-class"}})

    class Meta:
        model = Pedido
        #template_name = "pedidosUC/semantic.html"
        template_name = "index_pedidos_tabela.html"
        fields = ('titulo', 'descricao', 'estado', 'dataalvo')
        row_attrs = {
            'data-pk': lambda record: record.pk
        }