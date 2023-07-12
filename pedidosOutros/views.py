import pytz
from custom_users.models import Docente
import xlwt
from django.utils import timezone
from .forms import PedidosOutrosForm
from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from .models import Pedido, PedidoOutros, AnoLetivo, LinhaOutros
from django.contrib.auth.decorators import permission_required
from .tables import PedidosTable

@permission_required('custom_users.docente_rights')
def indexOutros(request):
    opcoes = request.GET.getlist('opcao')
    id_estado = request.GET.get('id_estado')
    pesquisa = request.GET.get('pesquisa')
    pedidos = Pedido.objects.select_subclasses(PedidoOutros).order_by('datacriacao')

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

    pedidos = [p for p in pedidos if isinstance(p, PedidoOutros)]
    pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
    table = PedidosTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    return render(request, 'pedidosOutros/indexOutros.html', {'pedidos': pedidos, 'table': table, 'name': pesquisa, 'opcao': opcoes, 'id_estado': id_estado})
'''
    opcoes = request.GET.getlist('opcao')
    pesquisa = request.GET.get('pesquisa')

    pedidos = Pedido.objects.all()

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
        if 'Estado' in opcoes:
            filtros |= Q(estado__icontains=pesquisa)
        pedidos = pedidos.filter(filtros)
        pedidos = pedidos.order_by('datacriacao')
    else:
        pedidos = Pedido.objects.all().order_by('datacriacao')

    linhas = Linha.objects.all()
    table = PedidosTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=numPage)
    return render(request, 'pedidosOutros/indexOutros.html',
                  {'pedidos': pedidos, 'table': table, 'name': pesquisa, 'opcao': opcoes})'''


@permission_required('custom_users.docente_rights')
def criar_pedido(request):
    anos = AnoLetivo.objects.all()
    linha_formset = inlineformset_factory(Pedido, LinhaOutros, fields=('descricao',), extra=0)
    pedidos = Pedido.objects.all().order_by('datacriacao')
    table = PedidosTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    if request.method == 'POST':
        pedido_form = PedidosOutrosForm(request.POST)
        if pedido_form.is_valid():
            pedido = pedido_form.save(commit=False)
            pedido.docente = Docente.objects.get(customuser_ptr=request.user)
            pedido.estado = "espera"
            if pedido.dataalvo == None:
                pedido.dataalvo = datetime.now()
            pedido.save()
            formset = linha_formset(request.POST, request.FILES, instance=pedido)
            if formset.is_valid():
                formset.save()
                linhas = pedido.linhaoutros_set.all()
                if (len(linhas) == 0):
                    Pedido.objects.filter(id=pedido.id).delete()
                    pedidos = Pedido.objects.all().order_by('datacriacao')
                    table = PedidosTable(pedidos)
                    table.paginate(page=request.GET.get("page", 1), per_page=10)
                    colorBack = '#FF0000'
                    color = '#FFFFFF'
                    mensagem = "O pedido nÃ£o tem linhas!"
                    return render(request, 'pedidosOutros/indexOutros.html',
                                  {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})
                table = PedidosTable(pedidos)
                table.paginate(page=request.GET.get("page", 1), per_page=10)
                colorBack = '#d4edda'
                color = '#155724'
                mensagem = "Pedido criado com sucesso"
                #return render(request, 'pedidosOutros/indexOutros.html',
                             # {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})
                return redirect('/pedidoOutros')
            else:
                return JsonResponse({'status': 'error', 'errors': formset.errors})
        else:
            return JsonResponse({'status': 'error', 'errors_pedido_form': pedido_form.errors})
    else:
        pedido_form = PedidosOutrosForm()
        context = {
            'pedido_form': pedido_form,
            'anos': anos,
            'linha_formset': linha_formset()
        }
        return render(request, 'pedidosOutros/criarPedidosOutros.html', context)


@permission_required('custom_users.docente_rights')
def editar_pedido(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    linha_formset = inlineformset_factory(Pedido, LinhaOutros, fields=('descricao',), extra=0)
    pedidos = Pedido.objects.select_subclasses(PedidoOutros).order_by('datacriacao')
    pedidos = [p for p in pedidos if isinstance(p, PedidoOutros)]
    pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
    table = PedidosTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    if request.method == 'POST':
        print(str(request.POST))
        pedido.titulo = request.POST['titulo']
        pedido.descricao = request.POST['descricao']
        pedido.save()
        formset = linha_formset(request.POST, request.FILES, instance=pedido)
        if formset.is_valid():
            linhas = pedido.linhaoutros_set.all()
            if (len(linhas) == 0):
                Pedido.objects.filter(id=pedido.id).delete()
                pedidos = Pedido.objects.select_subclasses(PedidoOutros).order_by('datacriacao')
                pedidos = [p for p in pedidos if isinstance(p, PedidoOutros)]
                pedidos = [p for p in pedidos if (p.docente.codigo == request.user.codigo)]
                table = PedidosTable(pedidos)
                table.paginate(page=request.GET.get("page", 1), per_page=10)
                colorBack = '#FF0000'
                color = '#FFFFFF'
                mensagem = "O pedido não tem linhas!"
                context = {
                    'linha_formset': linha_formset(),
                    'pedido_form': pedido,
                    'mensagem': mensagem,
                    'colorBack': colorBack,
                    'color': color
                }
                return render(request, 'pedidosOutros/criarPedidosOutros.html', context)
            formset.save()
            if (pedido.estado != "espera"):
                return JsonResponse({'status': 'error', 'errors': formset.errors})

            colorBack = '#d4edda'
            color = '#155724'
            mensagem = "Pedido alterado com sucesso"
            return render(request, 'pedidosOutros/indexOutros.html',
                          {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})
        else:
            return JsonResponse({'status': 'error', 'errors': formset.errors})
    else:
        linhas_data = pedido.linhaoutros_set.all()
        pedido_form = PedidosOutrosForm()
        context = {
            'pedido_form': pedido_form,
            'titulo': pedido.titulo,
            'descricao': pedido.descricao,
            'pedi': pedido,
            'linhas_data': linhas_data,
            'linha_formset': linha_formset(instance=pedido),
            'inicial': len(linhas_data)
        }
        return render(request, 'pedidosOutros/editarPedidosOutros.html', context)


@permission_required('custom_users.any_rights')
def view_pedido(request, pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    pedidos = Pedido.objects.select_subclasses(PedidoOutros).order_by('datacriacao')
    p = [p for p in pedidos if (p.id == pedido.id)][0]
    linhas = pedido.linha_set.all()
    if isinstance(p,PedidoOutros):
        return render(request, 'view_pedido.html', {'pedido': p, 'linhas_data': pedido.linhaoutros_set.all(), 'tipo': 'outros'})

@permission_required('custom_users.docente_rights')
def eliminarPedidosOutros(request, id):
    pedidos = Pedido.objects.all().order_by('datacriacao')
    table = PedidosTable(pedidos)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    Pedido.objects.filter(id=id).delete()
    colorBack = '#FF0000'
    color = '#FFFFFF'
    mensagem = "O pedido foi eliminado com sucesso"
    return render(request, 'pedidosOutros/indexOutros.html',
                  {'mensagem': mensagem, 'table': table, 'colorBack': colorBack, 'color': color})
