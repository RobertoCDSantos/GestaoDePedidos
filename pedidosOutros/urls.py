from django.contrib import admin
from django.urls import path, include
from pedidosOutros import views

app_name = 'pedidosOutros'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.indexOutros, name='pedido_outros'),
    path('criarPedidoOutros/', views.criar_pedido, name='criar_pedido_outros'),
    path('editarPedidoOutros/<int:pedido_id>/', views.editar_pedido, name='editar_pedido_outros'),
    path('eliminarPedidoOutros/<int:id>/', views.eliminarPedidosOutros, name='eliminar_pedido_outros'),
    path('view-pedido/<int:pedido_id>', views.view_pedido, name='view_pedido_outros'),
    path('api-auth', include('rest_framework.urls'))
]
