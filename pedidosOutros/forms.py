from django import forms
from pedidos.models import *
from django.forms import inlineformset_factory
from pedidosOutros.models import PedidoOutros


class PedidosOutrosForm(forms.ModelForm):
    #titulo = forms.CharField(widget=forms.TextInput(), max_length=100)
    #dataalvo = forms.DateField()
    #descricao = forms.CharField(widget=forms.Textarea, max_length=255)
    class Meta:
        model = PedidoOutros
        fields = ['descricao', 'titulo', 'dataalvo','anoletivo']

class LinhaForm(forms.ModelForm):
    class Meta:
        model = LinhaOutros
        fields = ['descricao']



