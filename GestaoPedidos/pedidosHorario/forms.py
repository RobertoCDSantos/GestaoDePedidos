from django.forms import ModelForm
from django import forms
from .models import PedidoHorario,Pedido
from pedidos.models import LinhaHorario
from django.forms import inlineformset_factory


class PedidosHorarioForm(forms.ModelForm):
    class Meta:
        model = PedidoHorario
        fields = ['titulo','descricao','dataalvo','anoletivo']

class LinhaForm(forms.ModelForm):
    class Meta:
        model = LinhaHorario
        fields = ['tipodepedido', 'diadasemana', 'horainicio', 'horafim', 'datainicio', 'datafim' , 'novadiadasemana', 'novahorainicio', 'novahorafim', 'novadatainicio', 'novadatafim' ]


LinhaFormSet = inlineformset_factory(
    PedidoHorario, LinhaHorario,LinhaForm,extra=1
)