from django.forms import ModelForm
from django import forms
from .models import AnoLetivo,Semestre,Disciplina
from django.forms import inlineformset_factory


class AnoLetivoForm(forms.ModelForm):
    class Meta:
        model = AnoLetivo
        fields = ['ano','datainicio','datafim']


class SemestreForm(forms.ModelForm):
    class Meta:
        model = Semestre
        fields = ['inicio_data','fim_data','nr_horas_service']


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nome','semestreid']


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Selecione o ficheiro Excel')

    def clean_excel_file(self):
        excel_file = self.cleaned_data['excel_file']
        if not excel_file.name.endswith('.xlsx'):
            raise forms.ValidationError('Só ficheiros são permitidos Excel (.xlsx)')
        return excel_file
