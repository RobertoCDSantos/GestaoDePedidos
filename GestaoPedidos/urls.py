"""GestaoPedidos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from pedidos import urls as pedidos_urls
from pedidosUC import urls as pedidos_uc_urls
from pedidosHorario import urls as pedidos_horario_urls
from pedidosSala import urls as pedidos_sala_urls
from pedidosOutros import urls as pedidos_outros_urls
from custom_users import urls as users

urlpatterns = [
    path('pedidos/', include(pedidos_urls)),
    path('pedidoHorario/', include(pedidos_horario_urls)),
    path('pedidoUC/', include(pedidos_uc_urls)),
    path('pedidoSala/', include(pedidos_sala_urls)),
    path('pedidoOutros/', include(pedidos_outros_urls)),
    path('users/',include(users)),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
