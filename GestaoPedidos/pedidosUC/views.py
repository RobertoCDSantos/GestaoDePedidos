from django.shortcuts import render,redirect
from django.urls import reverse
from django.forms import formset_factory,inlineformset_factory
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from custom_users.models import Docente
from .forms import PedidosDisciplinaForm
from .models import Pedido,PedidoUC,AnoLetivo,Linha,Disciplina
from .tables import PedidoTable
from .serializers import PedidoSerializer
from datetime import date, datetime  
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import generics
from django.db.models import Q
from django.contrib.auth.decorators import permission_required


#############
## Inicio  ##
#############

@permission_required('custom_users.docente_rights')
def index(request):
    opcoes = request.GET.getlist('opcao')
    id_estado = request.GET.get('id_estado')
    pesquisa = request.GET.get('pesquisa')
    pedidos = Pedido.objects.select_subclasses(PedidoUC).order_by('datacriacao')

    if 'Titulo' in opcoes:
        pedidos = pedidos.filter(titulo__isnull=False)
    if 'Descricao' in opcoes:
        pedidos = pedidos.filter(descricao__isnull=False)
    if 'Estado' in opcoes:
        pedidos = pedidos.filter(estado__isnull=False)
    if 'ID' in opcoes:
        pedidos = pedidos.filter(id__isnull=False)

    if pesquisa:
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
    
    pedidos = [p for p in pedidos if isinstance(p, PedidoUC)]
    pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    return render(request, 'pedidosUC/index_uc.html',{'pedidos': pedidos, 'table': table, 'name': pesquisa})

def empty_field(pedido_form):
    return pedido_form['titulo'].value() == '' or pedido_form['descricao'].value() == '' or pedido_form['dataalvo'].value() == ''

##################
## Criar pedido ##
##################
def save_pedido(pedido_form,request):
    pedido = pedido_form.save(commit=False)
    pedido.estado = 'espera'
    pedido.docente = Docente.objects.get(customuser_ptr=request.user)
    if pedido.dataalvo == None:
        pedido.dataalvo = datetime.now()
    pedido.save()
    return pedido

def duplicate(pedido):
    pedidos = Pedido.objects.all()
    for p in pedidos:
        if(p.titulo == pedido.titulo and p.descricao == pedido.descricao and p.dataalvo == pedido.dataalvo):
            return True
    return False

def render_criar_pedido(request,message,sucesso):
    pedido_form = PedidosDisciplinaForm()
    anos  = AnoLetivo.objects.all()
    disciplinas = Disciplina.objects.all()
    linha_formset = inlineformset_factory(Pedido, Linha, fields=('descricao','uc'), extra=0)
    if not sucesso:
        colorBack = '#FF0000'
        color = '#FFFFFF'
        mensagem = message
        return render(request, 'pedidosUC/criar_pedidos.html', {'mensagem': mensagem, 'colorBack': colorBack , 'color': color, 'pedido_form': pedido_form, 
            'anos': anos,
            'disciplinas': disciplinas,
            'linha_formset': linha_formset()})
    else:
        colorBack = '#d4edda'
        color = '#155724'
        mensagem = message
        return render(request, 'pedidosUC/criar_pedidos.html', {'mensagem': mensagem, 'colorBack': colorBack , 'color': color, 'pedido_form': pedido_form, 
            'anos': anos,
            'disciplinas': disciplinas,
            'linha_formset': linha_formset()})
    
# to render
def render_index_uc(request,message,sucesso):
    pedidos = Pedido.objects.select_subclasses(PedidoUC).order_by('datacriacao')
    pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
    pedidos = [p for p in pedidos if isinstance(p, PedidoUC)]
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    if not sucesso:
        colorBack = '#FF0000'
        color = '#FFFFFF'
        mensagem = message
        return render(request, 'pedidosUC/index_uc.html', {'mensagem': mensagem, 'table': table, 'colorBack': colorBack , 'color': color})
    else:
        colorBack = '#d4edda'
        color = '#155724'
        mensagem = message
        return render(request, 'pedidosUC/index_uc.html', {'mensagem': mensagem, 'table': table, 'colorBack': colorBack , 'color': color})


@permission_required('custom_users.docente_rights')
def criar_pedido(request):
    anos  = AnoLetivo.objects.all()
    disciplinas = Disciplina.objects.all()
    linha_formset = inlineformset_factory(Pedido, Linha, fields=('descricao','uc'), extra=0)
    if request.method == 'POST':
        pedido_form = PedidosDisciplinaForm(request.POST)
        if pedido_form.is_valid():
            pedido = save_pedido(pedido_form,request)
            formset = linha_formset(request.POST, request.FILES, instance=pedido)
            if formset.is_valid():
                formset.save()
                linhas = pedido.linha_set.all()
                ano_letivo = AnoLetivo.objects.filter(estado='ativo').first()
                if Pedido.objects.filter(titulo=pedido.titulo,descricao=pedido.descricao,dataalvo=pedido.dataalvo).count() > 1:
                    Pedido.objects.filter(id=pedido.id).delete()
                    return render_criar_pedido(request,"O pedido não pode ser duplicado!",False)
                if(len(linhas) == 0):
                    Pedido.objects.filter(id=pedido.id).delete()
                    return render_criar_pedido(request,"O pedido não tem linhas!",False)
                if (pedido.dataalvo < date.today()):
                    Pedido.objects.filter(id=pedido.id).delete()
                    return render_criar_pedido(request,"A data alvo tem de ser superior à do dia de hoje!",False)
                if not (ano_letivo.datainicio <= pedido.dataalvo <= ano_letivo.datafim):
                    Pedido.objects.filter(id=pedido.id).delete()
                    return render_criar_pedido(request,"A data alvo não está dentro do período válido do ano letivo!",False)
                if ano_letivo is None:
                    Pedido.objects.filter(id=pedido.id).delete()
                    return render_criar_pedido(request,"Não há AnoLetivo ativo!",False)
                if empty_field(pedido_form):
                    Pedido.objects.filter(id=pedido.id).delete()
                    return render_criar_pedido(request,"Os campos 'Título', 'Descrição' e 'Data Alvo' são obrigatórios!",False)
                return render_index_uc(request,"Pedido criado com sucesso",True)
        else:
            print(pedido_form.errors)
    else:
        pedido_form = PedidosDisciplinaForm()
        context = {
            'pedido_form': pedido_form, 
            'anos': anos,
            'disciplinas': disciplinas,
            'linha_formset': linha_formset()
        }
    return render(request, 'pedidosUC/criar_pedidos.html', context)


########################
##  Editar Pedido     ##
########################
        
@permission_required('custom_users.docente_rights')
def editar_pedido(request, pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    if pedido.anoletivo.estado == "inativo":
        return render_index_uc(request,"Ano do pedido está inativo",False)
    if pedido.estado != "espera":
        return render_index_uc(request,"Pedido já está a ser tratado",False)
    disciplinas = Disciplina.objects.all()
    linha_formset = inlineformset_factory(Pedido, Linha, fields=('descricao','uc'), extra=0)
    if request.method == 'POST':
        pedido.titulo = request.POST['titulo']
        pedido.descricao = request.POST['descricao']
        pedido.save()
        formset = linha_formset(request.POST, request.FILES, instance=pedido)
        if formset.is_valid():
            formset.save()
            return render_index_uc(request,"Pedido editado com sucesso",True)
    else:
        linhas = pedido.linha_set.all()
        pedido_form = PedidosDisciplinaForm()
        linhas_data = [{'id': linha.id, 'descricao': linha.descricao} for linha in linhas]
        context = {
            'pedido_form': pedido_form,
            'pedidoID' : pedido.id,
            'titulo': pedido.titulo,
            'descricao': pedido.descricao,  
            'pedi': pedido,
            'linhas_data': linhas_data,
            'linha_formset': linha_formset(instance=pedido),
            'disciplinas' : disciplinas
        }
        return render(request, 'pedidosUC/editar_pedidos.html', context)

########################
##  View   Pedido     ##
########################
    
@permission_required('custom_users.any_rights')
def view_pedido(request, pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    linhas = pedido.linha_set.all()
    linhas_data = [{'id': linha.id, 'descricao': linha.descricao, 'uc': linha.uc} for linha in linhas]
    return render(request, 'pedidosUC/view_pedido.html', {'pedido': pedido, 'linhas_data': linhas_data, 'tipo': 'uc'})

########################
##  Eliminar Pedido   ##
########################
@permission_required('custom_users.docente_rights')
def eliminar_pedido_uc(request,pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    if(pedido.estado == "espera"):
        Pedido.objects.filter(id=pedido_id).delete()
        return render_index_uc(request,"O pedido foi eliminado com sucesso",True)
    else:
        return render_index_uc(request,"O pedido Já está a ser tratado",False)

def sucesso(request):
    return render(request, 'pedidosUC/success.html')

########################
##  Validar Pedido    ##
########################


def validar_pedido_uc(request,pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    if(pedido.estado == "analise"):
        pedido.estado = "validado"
        print(pedido.estado)
        pedido.save()
        pedidos = Pedido.objects.select_subclasses(PedidoUC).order_by('datacriacao')
        pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
        pedidos = [p for p in pedidos if isinstance(p, PedidoUC)]
        table = PedidoTable(pedidos)
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        colorBack = '#d4edda'
        color = '#155724'
        mensagem = "O estado do pedido foi actualizado com sucesso, pelo funcionário"
        return render(request, 'pedidosUC/index_uc.html',{'mensagem': mensagem,'table': table, 'colorBack': colorBack, 'color': color})
    else:
        pedidos = Pedido.objects.select_subclasses(PedidoUC).order_by('datacriacao')
        pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
        pedidos = [p for p in pedidos if isinstance(p, PedidoUC)]
        table = PedidoTable(pedidos)
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        return render(request, 'pedidosUC/index_uc.html',{'table': table})
    

def rejeitar_pedido_uc(request,pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    if(pedido.estado == "analise"):
        pedido.estado = "cancelado"
        print(pedido.estado)
        pedido.save()
        pedidos = Pedido.objects.select_subclasses(PedidoUC).order_by('datacriacao')
        pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
        pedidos = [p for p in pedidos if isinstance(p, PedidoUC)]
        table = PedidoTable(pedidos)
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        colorBack = '#FF0000'
        color = '#FFFFFF'
        mensagem = "O estado do pedido foi actualizado com sucesso, pelo funcionário "
        return render(request, 'pedidosUC/index_uc.html',{'mensagem': mensagem,'table': table, 'colorBack': colorBack, 'color': color})
    else:
        pedidos = Pedido.objects.select_subclasses(PedidoUC).order_by('datacriacao')
        pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
        pedidos = [p for p in pedidos if isinstance(p, PedidoUC)]
        table = PedidoTable(pedidos)
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        return render(request, 'pedidosUC/index_uc.html',{'table': table})
    

def alterar_estado_pedido_uc(request, pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    if request.method == 'POST':
        pedido.estado = request.POST['estado']
        pedido.save()
        pedidos = Pedido.objects.select_subclasses(PedidoUC).order_by('datacriacao')
        pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
        pedidos = [p for p in pedidos if isinstance(p, PedidoUC)]
        table = PedidoTable(pedidos)
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        colorBack = '#d4edda'
        color = '#155724'
        mensagem = "Estado de pedido alterado com sucesso"
        return render(request, 'pedidosUC/index_uc.html', {'mensagem': mensagem, 'table': table, 'colorBack': colorBack , 'color': color})
    else:
        form = PedidosDisciplinaForm()
    return render(request, 'pedidosUC/editar_pedidos.html',
                  {'form': form, 'titulo': pedido.titulo, 'descricao': pedido.descricao})

