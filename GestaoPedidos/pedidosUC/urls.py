from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
#router.register('pedidos', test_api)


app_name = 'pedidosUC'
urlpatterns = [
    path('',views.index, name = "pedido_uc"),
    path('criar-pedido/', views.criar_pedido, name='criar_pedido_uc'),
    path('editar-pedido/<int:pedido_id>', views.editar_pedido, name='editar_pedido_uc'),
    path('eliminar-pedido/<int:pedido_id>', views.eliminar_pedido_uc, name='eliminar_pedido_uc'),
    path('view-pedido/<int:pedido_id>', views.view_pedido, name='view_pedido_uc'),
    path('alterar-estado-pedido/<int:pedido_id>', views.alterar_estado_pedido_uc, name='alterar_estado_pedido_uc'),
    path('sucesso/',views.sucesso, name = "sucesso"),
]