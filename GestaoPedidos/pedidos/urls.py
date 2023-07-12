from django.urls import include, path

import pedidosHorario
from . import views

app_name = 'pedidos'
urlpatterns = [
    path('',views.app, name="app"),
    path('lista/',views.index, name="pedidos"),
    path('criar-ano-letivo/',views.criar_ano_letivo, name="criar-ano-letivo"),
    path('ativar-ano-letivo/<int:ano_id>',views.ativar_ano_letivo, name="ativar-ano-letivo"),
    path('editar_ano_letivo/<int:ano_id>',views.editar_ano_letivo, name="editar_ano_letivo"),
    path('eliminar-ano-letivo/<int:ano_id>',views.eliminar_ano_letivo, name="eliminar-ano-letivo"),
    path('listar-ano-letivo/',views.listar_ano_letivo, name="listar-ano-letivo"),
    path('criar-semestre/',views.criar_semestre, name="criar-semestre"),
    path('criar-disciplina/',views.criar_disciplina, name="criar-disciplina"),
    path('estatisticas1/', views.estatisticas1, name="estatisticas1"),
    path('estatisticas2/', views.estatisticas2, name="estatisticas2"),
    path('estatisticas3/', views.estatisticas3, name="estatisticas3"),
    path('pedidos_processados/', views.pedidos_processados, name="pedidos_processados"),
    path('media-pedidos_processados/', views.media_pedidos_processados, name="media_pedidos_processados"),
    path('numero-pedidos_processados/', views.numero_pedidos_processados, name="numero_pedidos_processados"),
    path('pedidos_processados_funcionario/', views.pedidos_processados_funcionario, name="pedidos_processados_funcionario"),
    path('upload-docente/',views.upload_docentes, name="upload-docente"),
    path('import_excel_pandas/', views.import_dsd,name="import_dsd"),
    path('import_sala', views.import_salas, name='import_sala'),
    path('importar_ruc', views.importar_ruc, name='importar_ruc'),
    path('associar_pedido/<int:pedido_id>', views.associar_pedido, name='associar_pedido'),
    path('validar-pedido/<int:pedido_id>', views.validar_pedido, name='validar_pedido'),
    path('rejeitar-pedido/<int:pedido_id>', views.rejeitar_pedido, name='rejeitar_pedido'),
    path('view-pedido/<int:pedido_id>', views.view_pedido, name='view_pedido'),
    path('export-pedidos/', views.export_pedidos_to_excel, name='export_pedidos'),
    path('editar_ano_letivo/<int:ano_id>',views.editar_ano_letivo, name="editar_ano_letivo"),

]

