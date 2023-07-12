from django.urls import path
from . import views
from rest_framework import routers

app_name = 'pedidosSala'
urlpatterns = [
    path('',views.index, name = "pedido_sala"),
    path('', views.index, name='index'),
    path('criar-pedido/', views.criar_pedido_sala, name='criar_pedido_sala'),
    path('criar-pedido/<int:pedido_id>', views.criar_pedido_sala, name='criar_pedido_sala'),
    path('editar-pedido/<int:pedido_id>', views.editar_pedido_sala, name='editar_pedido_sala'),
    path('eliminar-pedido/<int:pedido_id>', views.eliminar_pedido_sala, name='eliminar_pedido_sala'),
    path('ver_pedido_sala/<int:pedido_id>', views.ver_pedido_sala, name='ver_pedido_sala'),
    path('alterar-estado-pedido/<int:pedido_id>', views.alterar_estado_pedido_sala, name='alterar_estado_pedido_sala'),
    path('sucesso/',views.sucesso, name = "sucesso"),

    # API Functions
    #path('pedidos/', views.pedidos, name = "pedidos"),
    #path('pedidos/<int:pk>/', views.pedido, name = "pedido"),

    # API Classes
    path('pedidos/',  views.PedidoList.as_view(), name = "pedidos"),
    path('pedidos/<int:pk>/',  views.PedidoDetail.as_view(), name = "pedido"),
]