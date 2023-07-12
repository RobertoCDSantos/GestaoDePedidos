from custom_users.models import Docente
from .forms import PedidosHorarioForm ,LinhaForm,LinhaFormSet
from django.shortcuts import render,redirect
from django.urls import reverse
from django.forms import formset_factory,inlineformset_factory
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import Pedido, PedidoHorario, AnoLetivo, LinhaHorario, Funcionario
from .tables import PedidoTable
from .serializers import PedidoSerializer
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import generics
from django.db.models import Q
from http.client import HTTPResponse
from django.shortcuts import render
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
import datetime
from django.contrib.auth.decorators import permission_required
# Create your views here.

@permission_required('custom_users.docente_rights')
def index(request):
    opcoes = request.GET.getlist('opcao')
    id_estado = request.GET.get('id_estado')
    pesquisa = request.GET.get('pesquisa')
    pedidos = Pedido.objects.select_subclasses(PedidoHorario).order_by('datacriacao')

    if 'Titulo' in opcoes:
        pedidos = pedidos.filter(titulo__isnull=False)
    if 'Descricao' in opcoes:
        pedidos = pedidos.filter(descricao__isnull=False)
    if 'ID' in opcoes:
        pedidos = pedidos.filter(id__isnull=False)

    if pesquisa:
        print("if")
        filtros = Q()
        if 'Titulo' in opcoes:
            filtros |= Q(titulo__icontains=pesquisa)
        if 'Descricao' in opcoes:
            filtros |= Q(descricao__icontains=pesquisa)
        if id_estado != 'todos':
            pedidos = pedidos.filter(estado__iexact=id_estado)
        pedidos = pedidos.filter(filtros)
        pedidos = pedidos.order_by('datacriacao')
    elif id_estado != None and id_estado != 'todos':
        pedidos = pedidos.filter(estado__iexact=id_estado)


    pedidos = [p for p in pedidos if isinstance(p, PedidoHorario)]
    pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    return render(request, 'pedidosHorario/indexHorario.html',{'pedidos': pedidos, 'table': table, 'name': pesquisa, 'opcao': opcoes, 'id_estado': id_estado})

@permission_required('custom_users.docente_rights')
def criar_pedido_horario(request):
    anos = AnoLetivo.objects.all()
    linha_formset = inlineformset_factory(Pedido, LinhaHorario, fields=('tipodepedido',
    'diadasemana', 'horainicio', 'horafim', 'datainicio', 'datafim', 'novadiadasemana',
    'novahorainicio', 'novahorafim', 'novadatainicio', 'novadatafim' ), extra=0)
    if request.method == 'POST':
        pedido_form = PedidosHorarioForm(request.POST)
        if pedido_form.is_valid():
            pedido = pedido_form.save(commit=False)
            pedido.docente = Docente.objects.get(customuser_ptr=request.user)

            if pedido_form['titulo'].value() == '' or pedido_form['descricao'].value() == '' or pedido_form[
                'dataalvo'].value() == '':
                # Campos obrigatórios estão vazios
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "Os campos 'Título', 'Descrição' e 'Data Alvo' são obrigatórios!"
                context = {
                    'anos': anos,
                    'linha_formset': linha_formset,
                    'pedido_form': pedido,
                    'mensagem': mensagem,
                    'colorBack': colorBack,
                    'color': color
                }
                return render(request, 'pedidosHorario/criar_pedidos_horario.html', context)

            if Pedido.objects.filter(dataalvo=pedido.dataalvo, titulo=pedido.titulo, descricao=pedido.descricao).exists():
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "Já existe um pedido com esse formato!"
                context = {
                    'pedido_form': pedido,
                    'anos': anos,
                    'linha_formset': linha_formset,
                    'mensagem': mensagem, 'colorBack': colorBack, 'color': color
                }
                return render(request, 'pedidosHorario/criar_pedidos_horario.html', context)

            ano_letivo = AnoLetivo.objects.filter(estado='ativo').first()
            if ano_letivo is None:
                # No active AnoLetivo found
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "Não há AnoLetivo ativo!"
                context = {
                    'pedido_form': pedido,
                    'anos': anos,
                    'linha_formset': linha_formset,
                    'mensagem': mensagem,
                    'colorBack': colorBack,
                    'color': color
                }
                return render(request, 'pedidosHorario/criar_pedidos_horario.html', context)
            # Check if dataalvo is within the active AnoLetivo's range
            now = datetime.datetime.now()
            if not (ano_letivo.datainicio <= pedido.dataalvo <= ano_letivo.datafim):
                # Invalid dataalvo
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "A data alvo não está dentro do período válido do ano letivo!"
                context = {
                    'pedido_form': pedido,
                    'anos': anos,
                    'linha_formset': linha_formset,
                    'mensagem': mensagem,
                    'colorBack': colorBack,
                    'color': color
                }
                return render(request, 'pedidosHorario/criar_pedidos_horario.html', context)

            if (pedido.dataalvo < now.date()):
                # Invalid dataalvo
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "A data alvo tem de ser superior à do dia de hoje!"
                context = {
                    'pedido_form': pedido,
                    'anos': anos,
                    'linha_formset': linha_formset,
                    'mensagem': mensagem,
                    'colorBack': colorBack,
                    'color': color
                }
                return render(request, 'pedidosHorario/criar_pedidos_horario.html', context)
            pedido.estado = 'espera'
            formset = linha_formset(request.POST, request.FILES, instance=pedido)
            if formset.is_valid():
                linhas = formset.save(commit=False)

                has_invalid_lines = False
                data_less_now = False
                data_endless = False
                data_dataalvo = False
                for linha in linhas:
                    if linha.tipodepedido == 'Criar' or linha.tipodepedido == 'Remover':
                        if not linha.diadasemana or not linha.horainicio or not linha.horafim or not linha.datainicio or not linha.datafim:
                            has_invalid_lines = True
                            break
                        if linha.datainicio < now.date() or linha.datafim < now.date():
                            data_less_now = True
                            break
                        if linha.datainicio > linha.datafim:
                            data_endless = True
                            break
                        if pedido.dataalvo > linha.datainicio:
                            data_dataalvo = True
                            break
                    elif linha.tipodepedido == 'Editar':
                        if not linha.diadasemana or not linha.horainicio or not linha.horafim or not linha.datainicio or not linha.datafim or not linha.novadiadasemana or not linha.novahorainicio or not linha.novahorafim or not linha.novadatainicio or not linha.novadatafim:
                            has_invalid_lines = True
                            break
                        if linha.datainicio < now.date() or linha.datafim < now.date() or linha.novadatainicio < now.date() or linha.novadatafim < now.date():
                            data_less_now = True
                            break
                        if linha.datainicio > linha.datafim or linha.novadatafim < linha.novadatainicio:
                            data_endless = True
                            break
                        if pedido.dataalvo > linha.datainicio or linha.novadatainicio < pedido.dataalvo:
                            data_dataalvo = True
                            break

                if has_invalid_lines:
                    colorBack = '#FF0000'
                    color = '#FFFFFF'
                    mensagem = "Alguns parametros nas linhas estão incompletos!"
                    context = {
                        'pedido_form': pedido,
                        'anos': anos,
                        'linha_formset': linha_formset,
                        'mensagem': mensagem,
                        'colorBack': colorBack,
                        'color': color
                    }
                    return render(request, 'pedidosHorario/criar_pedidos_horario.html', context)

                if data_dataalvo:
                    colorBack = '#FF0000'
                    color = '#FFFFFF'
                    mensagem = "A data inicial tem de ser maior que a data alvo!"
                    context = {
                        'pedido_form': pedido,
                        'anos': anos,
                        'linha_formset': linha_formset,
                        'mensagem': mensagem,
                        'colorBack': colorBack,
                        'color': color
                    }
                    return render(request, 'pedidosHorario/criar_pedidos_horario.html', context)

                if data_less_now:
                    colorBack = '#FF0000'
                    color = '#FFFFFF'
                    mensagem = "As datas tem de ser superiores à do dia de hoje!"
                    context = {
                        'pedido_form': pedido,
                        'anos': anos,
                        'linha_formset': linha_formset,
                        'mensagem': mensagem,
                        'colorBack': colorBack,
                        'color': color
                    }
                    return render(request, 'pedidosHorario/criar_pedidos_horario.html', context)

                if data_endless:
                    colorBack = '#FF0000'
                    color = '#FFFFFF'
                    mensagem = "As datas do fim tem de ser superiores às do inicio!"
                    context = {
                        'pedido_form': pedido,
                        'anos': anos,
                        'linha_formset': linha_formset,
                        'mensagem': mensagem,
                        'colorBack': colorBack,
                        'color': color
                    }
                    return render(request, 'pedidosHorario/criar_pedidos_horario.html', context)
                pedido.save()
                formset.save()
                pedidos = Pedido.objects.select_subclasses(PedidoHorario).order_by('datacriacao')
                pedidos = [p for p in pedidos if isinstance(p, PedidoHorario)]
                pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
                table = PedidoTable(pedidos)
                table.paginate(page=request.GET.get("page", 1), per_page=10)
                colorBack = '#d4edda'
                color = '#155724'
                mensagem = "Pedido criado com sucesso"
                return render(request, 'pedidosHorario/indexHorario.html',
                              {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})
            else:
                return JsonResponse({'status': 'error', 'errors': formset.errors})
        else:
            return JsonResponse({'status': 'error', 'errors_pedido_form': pedido_form.errors})
    else:
        context = {
            'anos': anos,
            'linha_formset': linha_formset()
        }
        return render(request, 'pedidosHorario/criar_pedidos_horario.html', context)





########################
##  Editar Pedido     ##
########################

@permission_required('custom_users.docente_rights')
def editar_pedido_horario(request, pedido_id):
    anos = AnoLetivo.objects.all()
    pedido = Pedido.objects.get(id=pedido_id)
    linha_formset = inlineformset_factory(Pedido, LinhaHorario, fields=('tipodepedido',
    'diadasemana', 'horainicio', 'horafim', 'datainicio', 'datafim', 'novadiadasemana',
    'novahorainicio', 'novahorafim', 'novadatainicio', 'novadatafim' ), extra=0)

    pedidos = Pedido.objects.select_subclasses(PedidoHorario).order_by('datacriacao')
    pedidos = [p for p in pedidos if isinstance(p, PedidoHorario)]
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    linhas = pedido.linhahorario_set.all()
    pedido_form_save = PedidosHorarioForm()
    linhas_data_save = [{'id': linha.id, 'tipodepedido': linha.tipodepedido, 'diadasemana': linha.diadasemana,
                    'horainicio': linha.horainicio, 'horafim': linha.horafim, 'datainicio': linha.datainicio
                       , 'datafim': linha.datafim, 'novadiadasemana': linha.novadiadasemana,
                    'novahorainicio': linha.novahorainicio, 'novahorafim': linha.novahorafim,
                    'novadatainicio': linha.novadatainicio, 'novadatafim': linha.novadatafim} for linha in linhas]

    if (pedido.estado == 'espera'):
        if request.method == 'POST':
            pedido.titulo = request.POST['titulo']
            pedido.descricao = request.POST['descricao']
            pedido.dataalvo = request.POST['dataalvo']
            pedido.dataalvo = datetime.datetime.strptime(pedido.dataalvo, "%Y-%m-%d").date()
            if pedido.titulo == '' or pedido.descricao == '' or pedido.dataalvo == '':
                # Campos obrigatórios estão vazios
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "Os campos 'Título', 'Descrição' e 'Data Alvo' são obrigatórios!"
                context = {
                    'inicial': len(linhas),
                    'pedido_form': pedido_form_save,
                    'titulo': pedido.titulo,
                    'dataalvo': pedido.dataalvo,
                    'descricao': pedido.descricao,
                    'pedi': pedido,
                    'anos': anos,
                    'linhas_data': linhas_data_save,
                    'linha_formset': linha_formset(instance=pedido),
                    'mensagem': mensagem,
                    'colorBack': colorBack,
                    'color': color
                }
                return render(request, 'pedidosHorario/editar_pedidos_horario.html', context)

            pedidos_iguais = Pedido.objects.filter(dataalvo=pedido.dataalvo, titulo=pedido.titulo,
                                                   descricao=pedido.descricao)

            if pedidos_iguais.exists() and pedidos_iguais.count() > 1:
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "Já existe um pedido com esse formato!"
                context = {
                    'inicial': len(linhas),
                    'pedido_form': pedido_form_save,
                    'titulo': pedido.titulo,
                    'dataalvo': pedido.dataalvo,
                    'descricao': pedido.descricao,
                    'pedi': pedido,
                    'anos': anos,
                    'linhas_data': linhas_data_save,
                    'linha_formset': linha_formset(instance=pedido),
                    'mensagem': mensagem,
                    'colorBack': colorBack,
                    'color': color
                }
                return render(request, 'pedidosHorario/editar_pedidos_horario.html', context)

            ano_letivo = AnoLetivo.objects.filter(estado='ativo').first()
            if ano_letivo is None:
                # No active AnoLetivo found
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "Não há AnoLetivo ativo!"
                context = {
                    'inicial': len(linhas),
                    'pedido_form': pedido_form_save,
                    'titulo': pedido.titulo,
                    'dataalvo': pedido.dataalvo,
                    'descricao': pedido.descricao,
                    'pedi': pedido,
                    'anos': anos,
                    'linhas_data': linhas_data_save,
                    'linha_formset': linha_formset(instance=pedido),
                    'mensagem': mensagem,
                    'colorBack': colorBack,
                    'color': color
                }
                return render(request, 'pedidosHorario/editar_pedidos_horario.html', context)
            # Check if dataalvo is within the active AnoLetivo's range
            now = datetime.datetime.now()

            if not (ano_letivo.datainicio <= pedido.dataalvo <= ano_letivo.datafim):
                # Invalid dataalvo
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "A data alvo não está dentro do período válido do ano letivo!"
                context = {
                    'inicial': len(linhas),
                    'pedido_form': pedido_form_save,
                    'titulo': pedido.titulo,
                    'dataalvo': pedido.dataalvo,
                    'descricao': pedido.descricao,
                    'pedi': pedido,
                    'anos': anos,
                    'linhas_data': linhas_data_save,
                    'linha_formset': linha_formset(instance=pedido),
                    'mensagem': mensagem,
                    'colorBack': colorBack,
                    'color': color
                }
                return render(request, 'pedidosHorario/editar_pedidos_horario.html', context)

            if (pedido.dataalvo < now.date()):
                # Invalid dataalvo
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "A data alvo tem de ser superior à do dia de hoje!"
                context = {
                    'inicial': len(linhas),
                    'pedido_form': pedido_form_save,
                    'titulo': pedido.titulo,
                    'dataalvo': pedido.dataalvo,
                    'descricao': pedido.descricao,
                    'pedi': pedido,
                    'anos': anos,
                    'linhas_data': linhas_data_save,
                    'linha_formset': linha_formset(instance=pedido),
                    'mensagem': mensagem,
                    'colorBack': colorBack,
                    'color': color
                }
                return render(request, 'pedidosHorario/editar_pedidos_horario.html', context)

            formset = linha_formset(request.POST, request.FILES, instance=pedido)
            if formset.is_valid():
                linhas = formset.cleaned_data

                has_invalid_lines = False
                data_less_now = False
                data_endless = False

                for linha in linhas:
                    print(linha)
                    if linha.get('tipodepedido') == 'Criar' or linha.get('tipodepedido') == 'Remover':
                        if not linha.get('diadasemana') or not linha.get('horainicio') or not linha.get(
                                'horafim') or not linha.get('datainicio') or not linha.get('datafim'):
                            has_invalid_lines = True
                            break

                        if linha.get('datainicio') < now.date() or linha.get('datafim') < now.date():
                            data_less_now = True
                        if linha.get('datainicio') > linha.get('datafim'):
                            data_endless = True
                        if pedido.dataalvo > linha.get('datainicio'):
                            data_endless = True
                    elif linha.get('tipodepedido') == 'Editar':
                        if not linha.get('diadasemana') or not linha.get('horainicio') or not linha.get(
                                'horafim') or not linha.get('datainicio') or not linha.get('datafim') or not linha.get(
                                'novadiadasemana') or not linha.get('novahorainicio') or not linha.get(
                                'novahorafim') or not linha.get('novadatainicio') or not linha.get('novadatafim'):
                            has_invalid_lines = True
                            break
                        if linha.get('datainicio') < now.date() or linha.get('datafim') < now.date() or linha.get(
                                'novadatainicio') < now.date() or linha.get('novadatafim') < now.date():
                            data_less_now = True
                        if linha.get('datainicio') < linha.get('datafim') or linha.get('novadatafim') < linha.get(
                                'novadatainicio'):
                            data_endless = True
                        if pedido.dataalvo > linha.get('datainicio') or pedido.dataalvo > linha.get('novadatainicio'):
                            data_endless = True

                if has_invalid_lines:
                    colorBack = '#FF0000'
                    color = '#FFFFFF'
                    mensagem = "Alguns parametros nas linhas estão incompletos!"
                    context = {
                        'inicial': len(linhas),
                        'pedido_form': pedido_form_save,
                        'titulo': pedido.titulo,
                        'dataalvo': pedido.dataalvo,
                        'descricao': pedido.descricao,
                        'pedi': pedido,
                        'anos': anos,
                        'linhas_data': linhas_data_save,
                        'linha_formset': linha_formset(instance=pedido),
                        'mensagem': mensagem,
                        'colorBack': colorBack,
                        'color': color
                    }
                    return render(request, 'pedidosHorario/editar_pedidos_horario.html', context)

                if data_less_now:
                    colorBack = '#FF0000'
                    color = '#FFFFFF'
                    mensagem = "As datas tem de ser superiores à do dia de hoje!"
                    context = {
                        'inicial': len(linhas),
                        'pedido_form': pedido_form_save,
                        'titulo': pedido.titulo,
                        'dataalvo': pedido.dataalvo,
                        'descricao': pedido.descricao,
                        'pedi': pedido,
                        'anos': anos,
                        'linhas_data': linhas_data_save,
                        'linha_formset': linha_formset(instance=pedido),
                        'mensagem': mensagem,
                        'colorBack': colorBack,
                        'color': color
                    }
                    return render(request, 'pedidosHorario/editar_pedidos_horario.html', context)

                if data_endless:
                    colorBack = '#FF0000'
                    color = '#FFFFFF'
                    mensagem = "As datas do fim tem de ser superiores as do inicio!"
                    context = {
                        'inicial': len(linhas),
                        'pedido_form': pedido_form_save,
                        'titulo': pedido.titulo,
                        'dataalvo': pedido.dataalvo,
                        'descricao': pedido.descricao,
                        'pedi': pedido,
                        'anos': anos,
                        'linhas_data': linhas_data_save,
                        'linha_formset': linha_formset(instance=pedido),
                        'mensagem': mensagem,
                        'colorBack': colorBack,
                        'color': color
                    }
                    return render(request, 'pedidosHorario/editar_pedidos_horario.html', context)
                pedido.save()
                formset.save()
                pedidos = Pedido.objects.select_subclasses(PedidoHorario).order_by('datacriacao')
                pedidos = [p for p in pedidos if isinstance(p, PedidoHorario)]
                pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
                table = PedidoTable(pedidos)
                table.paginate(page=request.GET.get("page", 1), per_page=10)
                colorBack = '#d4edda'
                color = '#155724'
                mensagem = "Pedido alterado com sucesso"
                return render(request, 'pedidosHorario/indexHorario.html',
                          {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})
            else:
                return JsonResponse({'status': 'error', 'errors': formset.errors})
        else:
            context = {
                'pedido_form': pedido_form_save,
                'titulo': pedido.titulo,
                'dataalvo': pedido.dataalvo,
                'descricao': pedido.descricao,
                'pedi': pedido,
                'anos': anos,
                'linhas_data': linhas_data_save,
                'linha_formset': linha_formset(instance=pedido),
                'inicial': len(linhas)
            }
            return render(request, 'pedidosHorario/editar_pedidos_horario.html', context)
    else:
        colorBack = '#FF0000'
        color = '#FFFFFF'
        mensagem = "O pedido não pode ser alterado, pois ja se encontra em processo"
        return render(request, 'pedidosHorario/indexHorario.html', {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})
########################
##  Alterar estado Pedido     ##
########################
def alterar_estado_pedido_horario(request, pedido_id):
    pedidos = Pedido.objects.all().order_by('datacriacao')
    pedido = Pedido.objects.get(pk=pedido_id)
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)

    if request.method == 'POST':
        pedido.estado = request.POST['estado']
        pedido.save()
        pedidos = Pedido.objects.select_subclasses(PedidoHorario).order_by('datacriacao')
        pedidos = [p for p in pedidos if isinstance(p, PedidoHorario)]
        table = PedidoTable(pedidos)
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        colorBack = '#d4edda'
        color = '#155724'
        mensagem = "Estado de pedido alterado com sucesso"
        return render(request, 'pedidosHorario/indexHorario.html', {'mensagem': mensagem , 'table': table, 'colorBack': colorBack , 'color': color})
    else:
        form = PedidosHorarioForm()
        # form.fields['titulo'].initial = pedido.titulo
        # form.fields['descricao'].initial = pedido.descricao
    return render(request, 'pedidosHorario/editar_pedidos_horario.html',
                  {'form': form, 'titulo': pedido.titulo, 'descricao': pedido.descricao})


########################
##  Eliminar Pedido   ##
########################
@permission_required('custom_users.docente_rights')
def eliminar_pedido_horario(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    pedidos = Pedido.objects.select_subclasses(PedidoHorario).order_by('datacriacao')
    pedidos = [p for p in pedidos if isinstance(p, PedidoHorario)]
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)

    if( pedido.estado == 'espera'):
        Pedido.objects.filter(id=pedido_id).delete()
        pedidos = Pedido.objects.select_subclasses(PedidoHorario).order_by('datacriacao')
        pedidos = [p for p in pedidos if isinstance(p, PedidoHorario)]
        table = PedidoTable(pedidos)
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        colorBack = '#d4edda'
        color = '#155724'
        mensagem = "O pedido foi eliminado com sucesso"
        return render(request, 'pedidosHorario/indexHorario.html',
                      {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})
    else:
        colorBack = '#FF0000'
        color = '#FFFFFF'
        mensagem = "O pedido não pode ser eliminado, pois ja se encontra em processo"
        return render(request, 'pedidosHorario/indexHorario.html', {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})




##############################
###         API            ###
##############################
class PedidoList(generics.ListCreateAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer


class PedidoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer


def test_api(request):
    data = [{"Key": "Value"}]
    return JsonResponse(data, safe=False)


""" @csrf_exempt
def pedidos(request):
    '''
    List all task snippets
    '''
    if(request.method == 'GET'):
        pedidos = Pedido.objects.all()
        serializer = PedidoSerializer(pedidos, many=True)
        return JsonResponse(serializer.data,safe=False)
    elif(request.method == 'POST'):
        #data = JSONParser().parse(request)
        serializer = PedidoSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def pedido(request, pk):

    try:
        pedido = Pedido.objects.get(pk=pk)
    except Pedido.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer =  PedidoSerializer(pedido)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PedidoSerializer(pedido, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        pedido.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
 """


def criar_pedido_horario_formset(request):
    Pedidoformset = formset_factory(PedidosHorarioForm)
    if request.method == 'POST':
        formset = Pedidoformset(request.POST, request.FILES)
        pedidos_horario = formset.save(commit=False)
        for pedido_horario in pedidos_horario:
            pedido_horario.estado = 0
            if pedido_horario.dataalvo == None:
                pedido_horario.dataalvo = datetime.now()
            pedido_horario.save()
        if formset.is_valid():
            return render(request, 'pedidosHorario/success.html', {'mensagem': "Pedido criado com sucesso"})
    else:
        formset = Pedidoformset()
    return render(request, 'pedidosHorario/criar_pedidos_horario.html', {'formset': formset})


@permission_required('custom_users.docente_rights')
def view_pedido(request, pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    return render(request, 'pedidosHorario/view_pedido.html', {'pedido': pedido, 'linhas_data': pedido.linhahorario_set.all(), 'tipo': 'horario'})

def sucesso(request):
    return render(request, 'pedidosHorario/success.html')
