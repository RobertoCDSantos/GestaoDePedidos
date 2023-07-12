from django.contrib.auth.models import User, Group
from rest_framework import routers,serializers,viewsets
from .models import Pedido,LinhaHorario

class LinhaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinhaHorario
        fields = ['titulo', 'descricao']

class PedidoSerializer(serializers.HyperlinkedModelSerializer):
    linhas = LinhaSerializer(read_only=True, many=True)
    class Meta:
        model = Pedido
        fields = ['id', 'titulo', 'descricao','linhas']