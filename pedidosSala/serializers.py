from django.contrib.auth.models import User, Group
from rest_framework import routers,serializers,viewsets
from .models import Pedido

class PedidoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'titulo', 'descricao']