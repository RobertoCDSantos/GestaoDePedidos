from django.urls import include, path
from . import views

app_name = 'users'
urlpatterns = [
    path('register/docente',views.register_docente, name="register-docente"),
    path('register/funcionario',views.register_funcionario, name="register-funcionario"),
    path('accounts/', include('django.contrib.auth.urls')),
]