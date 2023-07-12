from django.urls import path
from . import views
from rest_framework import routers

app_name = 'pedidosHorario'
urlpatterns = [
    path('',views.index, name = "pedido_horario"),
    path('', views.index, name='index'),
    path('criar-pedido/', views.criar_pedido_horario, name='criar_pedido_horario'),
    path('editar-pedido/<int:pedido_id>', views.editar_pedido_horario, name='editar_pedido_horario'),
    path('eliminar-pedido/<int:pedido_id>', views.eliminar_pedido_horario, name='eliminar_pedido_horario'),
    path('alterar-estado-pedido/<int:pedido_id>', views.alterar_estado_pedido_horario, name='alterar_estado_pedido_horario'),
    path('view-pedido/<int:pedido_id>', views.view_pedido, name='view_pedido_horario'),
    path('sucesso/',views.sucesso, name = "sucesso"),

    # API Functions
    #path('pedidos/', views.pedidos, name = "pedidos"),
    #path('pedidos/<int:pk>/', views.pedido, name = "pedido"),

    # API Classes
    path('pedidos/',  views.PedidoList.as_view(), name = "pedidos"),
    path('pedidos/<int:pk>/',  views.PedidoDetail.as_view(), name = "pedido"),
]