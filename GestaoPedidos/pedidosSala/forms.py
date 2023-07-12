from django.forms import ModelForm
from django import forms
from .models import PedidoSala
from pedidos.models import LinhaSala
from django.forms import inlineformset_factory


class PedidosSalaForm(forms.ModelForm):
    class Meta:
        model = PedidoSala
        fields = ['titulo','descricao','dataalvo','anoletivo']

class LinhaForm(forms.ModelForm):
    class Meta:
        model = LinhaSala
        fields = ['detalhe','sala', 'horainicio', 'horafim', 'horainicioantigo', 'horafimantigo', 'tipopedido', 'categoriatemporal']


LinhaFormSet = inlineformset_factory(
    PedidoSala, LinhaSala,fields=['detalhe','sala', 'horainicio', 'horafim', 'horainicioantigo', 'horafimantigo', 'tipopedido', 'categoriatemporal'],extra=1
)