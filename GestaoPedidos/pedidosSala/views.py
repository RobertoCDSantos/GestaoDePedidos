from custom_users.models import Docente
from .forms import PedidosSalaForm, LinhaForm, LinhaFormSet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import formset_factory, inlineformset_factory
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Pedido, AnoLetivo, LinhaSala, Edificio, Sala, PedidoSala
from .tables import PedidoTable
from .serializers import PedidoSerializer
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import generics
from django.db.models import Q
from django.contrib.auth.decorators import permission_required
# Create your views here.

@permission_required('custom_users.docente_rights')
def index(request):
    opcoes = request.GET.getlist('opcao')
    id_estado = request.GET.get('id_estado')
    pesquisa = request.GET.get('pesquisa')
    pedidos = Pedido.objects.select_subclasses(PedidoSala).order_by('datacriacao')

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


    pedidos = [p for p in pedidos if isinstance(p, PedidoSala)]
    pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    return render(request, 'pedidosSala/indexSala.html',{'pedidos': pedidos, 'table': table, 'name': pesquisa, 'opcao': opcoes, 'id_estado': id_estado})


##################
## Criar pedido ##
##################
@permission_required('custom_users.docente_rights')
def criar_pedido_sala(request):
    campus = Edificio.objects.values_list('localizacao', flat=True).distinct()
    edificios = Edificio.objects.all()
    salas = Sala.objects.all()
    pedidos = Pedido.objects.select_subclasses(PedidoSala).order_by('datacriacao')
    pedidos = [p for p in pedidos if isinstance(p, PedidoSala)]
    pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    
    anos = AnoLetivo.objects.all()
    colorBack = '#FF0000'
    color = '#FFFFFF'
    context = {
        'mensagem': "",
        'colorBack': colorBack,
        'color': color,
        'anos': anos,
        'pedidos': pedidos,
        'table': table,
        'salas': list(salas.values()),
        'campus': list(campus),
        'edificios': list(edificios.values()),
    }
    linha_formset = inlineformset_factory(
        Pedido, LinhaSala, fields=('detalhe','sala', 'horainicio', 'horafim', 'horainicioantigo', 'horafimantigo', 'tipopedido', 'categoriatemporal'), extra=0)
    if request.method == 'POST':
        pedido_form = PedidosSalaForm(request.POST)
        if pedido_form.is_valid():
            pedido = pedido_form.save(commit=False)
            pedido.docente = Docente.objects.get(customuser_ptr=request.user)
            pedido.estado = "espera"
            if pedido.dataalvo == None:
                pedido.dataalvo = datetime.now()
            pedido.save()
            formset = linha_formset(
                request.POST, request.FILES, instance=pedido)
            if formset.is_valid():
                formset.save()
                linhas = pedido.linhasala_set.all()
                if (len(linhas) <= 0):
                    Pedido.objects.filter(id=pedido.id).delete()
                    context['mensagem'] = "Não foi possível criar o pedido! Sem linhas"
                    return render(request, 'pedidosSala/criar_pedidos_sala.html', context)
                ano_letivo = AnoLetivo.objects.get(id=request.POST.get('anoletivo'))
                if not ano_letivo.datainicio <= pedido.dataalvo <= ano_letivo.datafim:
                    Pedido.objects.filter(id=pedido.id).delete()
                    context['mensagem'] = "Não foi possível criar o pedido! Data Alvo fora da periodo do ano letivo selecionado!"
                    return render(request, 'pedidosSala/criar_pedidos_sala.html', context)
                if Pedido.objects.filter(titulo=pedido.titulo,descricao=pedido.descricao,dataalvo=pedido.dataalvo).count() > 1:
                    Pedido.objects.filter(id=pedido.id).delete()
                    context['mensagem'] = "Não foi possível criar o pedido! Pedido duplicado!"
                    return render(request, 'pedidosSala/criar_pedidos_sala.html', context)                    
                context['mensagem'] = "Pedido Sala criado com sucesso"
                context['colorBack'] = '#d4edda'
                context['color'] = '#155724'
                context['pedidos'] = Pedido.objects.all().order_by('datacriacao')
                return render(request, 'pedidosSala/indexSala.html', context)
            else:
                Pedido.objects.filter(id=pedido.id).delete()
                context['mensagem'] = "Não foi possível criar o pedido!"
                return render(request, 'pedidosSala/criar_pedidos_sala.html', context)
        else:
            context['mensagem'] = "Não foi possível criar o pedido! Todos os espaços devem ser preenchidos!"
            return render(request, 'pedidosSala/criar_pedidos_sala.html', context)
    else:
        pedido_form = PedidosSalaForm()
        context['pedido_form']: pedido_form
        context['anos']: anos
        context['linha_formset']: linha_formset()
        return render(request, 'pedidosSala/criar_pedidos_sala.html', context)
    
@permission_required('custom_users.docente_rights')
def editar_pedido_sala(request, pedido_id):
    campus = Edificio.objects.values_list('localizacao', flat=True).distinct()
    edificios = Edificio.objects.all()
    salas = Sala.objects.all()
    pedidos = Pedido.objects.all().order_by('datacriacao')
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    
    colorBack = '#FF0000'
    color = '#FFFFFF'
    context = {
        'mensagem': "",
        'colorBack': colorBack,
        'color': color,
        'pedidos': pedidos,
        'table': table,
        'salas': list(salas.values()),
        'campus': list(campus),
        'edificios': list(edificios.values()),
    }
    
    pedido = Pedido.objects.get(id=pedido_id)
    linha_formset = inlineformset_factory(
        Pedido, LinhaSala, fields=('detalhe','sala', 'horainicio', 'horafim', 'tipopedido', 'categoriatemporal'), extra=0)
    if request.method == 'POST':
        pedido.titulo = request.POST['titulo']
        pedido.descricao = request.POST['descricao']
        pedido.dataalvo = request.POST['dataalvo']
        pedido.save()
        formset = linha_formset(request.POST, request.FILES, instance=pedido)
        if formset.is_valid():
            formset.save()
            if (pedido.estado != "espera"):
                return render(request, 'pedidosSala/indexSala.html', context)
            context['mensagem'] = "Pedido editado com sucesso"
            context['colorBack'] = '#d4edda'
            context['color'] = '#155724'
            return render(request, 'pedidosSala/indexSala.html', context)
        else:
            print("170!!!!!!")
            print(formset.data)
            context['mensagem'] = "Erro"
            linhas = pedido.linhasala_set.all()
            pedido_form = PedidosSalaForm()
            
            context['pedido_form'] = pedido_form
            context['titulo'] = pedido.titulo
            context['descricao'] = pedido.descricao
            context['pedi'] = pedido
            context['dataalvo'] = pedido.dataalvo
            context['linhas_data'] = linhas
            context['linha_formset'] = linha_formset(instance=pedido)
            context['inicial'] = len(linhas)
            return render(request, 'pedidosSala/editar_pedidos_sala.html', context)
    else:
        pedido_form = PedidosSalaForm()
        linhas = pedido.linhasala_set.all()
        
        context['pedido_form'] = pedido_form
        context['titulo'] = pedido.titulo
        context['descricao'] = pedido.descricao
        context['pedi'] = pedido
        context['dataalvo'] = pedido.dataalvo.strftime('%Y-%m-%d') if pedido.dataalvo else ''
        context['linhas_data'] = linhas
        context['linha_formset'] = linha_formset(instance=pedido)
        context['inicial'] = len(linhas)
        return render(request, 'pedidosSala/editar_pedidos_sala.html', context)


########################
##  Editar Pedido     ##
########################

def alterar_estado_pedido_sala(request, pedido_id):
    pedidos = Pedido.objects.all().order_by('datacriacao').order_by('datacriacao')
    pedido = Pedido.objects.get(pk=pedido_id)
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    if request.method == 'POST':
        pedido.estado = request.POST['estado']
        pedido.save()
        colorBack = '#d4edda'
        color = '#155724'
        mensagem = "Estado de pedido alterado com sucesso"
        return render(request, 'pedidosSala/indexSala.html', {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})
    else:
        form = PedidosSalaForm()
        # form.fields['titulo'].initial = pedido.titulo
        # form.fields['descricao'].initial = pedido.descricao
    return render(request, 'pedidosSala/editar_pedidos_sala.html',
                  {'form': form, 'titulo': pedido.titulo, 'descricao': pedido.descricao})


########################
##  Eliminar Pedido   ##
########################
@permission_required('custom_users.docente_rights')
def eliminar_pedido_sala(request, pedido_id):
    pedidos = Pedido.objects.all().order_by('datacriacao').order_by('datacriacao')
    table = PedidoTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    Pedido.objects.filter(id=pedido_id).delete()
    colorBack = '#FF0000'
    color = '#FFFFFF'
    mensagem = "O pedido foi eliminado com sucesso"
    return render(request, 'pedidosSala/indexSala.html',
                  {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})

@permission_required('custom_users.any_rights')
def ver_pedido_sala(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    linhas = pedido.linhasala_set.all()
    salas = Sala.objects.all()
    
    context = {
        'mensagem': "",
        'titulo': pedido.titulo,
        'descricao': pedido.descricao,
        'pedi': pedido,
        'salas': list(salas.values()),
        'dataalvo': pedido.dataalvo.strftime('%Y-%m-%d') if pedido.dataalvo else '',
        'linhas_data': linhas,
    }
    return render(request, 'pedidosSala/ver_pedido_sala.html', context)

def sucesso(request):
    return render(request, 'pedidosSala/success.html')


##############################
###         API            ###
##############################
class PedidoList(generics.ListCreateAPIView):
    queryset = Pedido.objects.all().order_by('datacriacao')
    serializer_class = PedidoSerializer


class PedidoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pedido.objects.all().order_by('datacriacao')
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
        pedidos = Pedido.objects.all().order_by('datacriacao')
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


def criar_pedido_sala_formset(request):
    Pedidoformset = formset_factory(PedidosSalaForm)
    if request.method == 'POST':
        formset = Pedidoformset(request.POST, request.FILES)
        pedidos_sala = formset.save(commit=False)
        for pedido_sala in pedidos_sala:
            pedido_sala.estado = 0
            if pedido_sala.dataalvo == None:
                pedido_sala.dataalvo = datetime.now()
            pedido_sala.save()
        if formset.is_valid():
            return render(request, 'pedidosSala/success.html', {'mensagem': "Pedido criado com sucesso"})
    else:
        formset = Pedidoformset()
    return render(request, 'pedidosSala/criar_pedidos_sala.html', {'formset': formset})
