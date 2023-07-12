from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Docente, Funcionario

class RegistrationFormDocente(UserCreationForm):

    class Meta:
        model = Docente
        fields = ('username', 'password1', 'password2', 'email',
                  'first_name', 'last_name','codigo')


class RegistrationFormFuncionario(UserCreationForm):

    class Meta:
        model = Funcionario
        fields = ('username', 'password1', 'password2', 'email',
                  'first_name', 'last_name','codigo')

