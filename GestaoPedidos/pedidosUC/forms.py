from django.forms import ModelForm
from django import forms
from .models import PedidoUC,Pedido
from pedidos.models import Disciplina, Linha
from datetime import datetime
from django.forms import inlineformset_factory


class PedidosDisciplinaForm(forms.ModelForm):
    class Meta:
        model = PedidoUC
        fields = ['titulo','descricao','dataalvo','anoletivo']


class LinhaForm(forms.ModelForm):
    class Meta:
        model = Linha
        fields = ['descricao','uc']

LinhaFormSet = inlineformset_factory(
    PedidoUC, Linha, LinhaForm, extra=0
)