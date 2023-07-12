from django.shortcuts import render, redirect

from pedidos.models import Pedido
from pedidos.tables import PedidoTable
from pedidosHorario.models import PedidoHorario
from pedidosOutros.models import PedidoOutros
from pedidosSala.models import PedidoSala
from pedidosUC.models import PedidoUC
from .forms import RegistrationFormDocente, RegistrationFormFuncionario
from django.contrib.auth.models import Group

def register_docente(request):
    if request.method == 'POST':
        form = RegistrationFormDocente(request.POST)
        if form.is_valid():
            docente = form.save(commit=False)
            docente.is_docente = True
            docente.save()
            group = Group.objects.get(name='docente')
            print(group)
            docente.groups.add(group)
            pedidos = Pedido.objects.select_subclasses(PedidoUC, PedidoHorario, PedidoOutros, PedidoSala).order_by('datacriacao')
            table = PedidoTable(pedidos)
            table.paginate(page=request.GET.get("page", 1), per_page=10)
            mensagem = "Utilizador registado com sucesso!"
            colorBack = '#d4edda'
            color = '#155724'
            return render(request, 'index_pedidos.html', {'pedidos': pedidos, 'table': table, 'mensagem': mensagem, 'colorBack': colorBack , 'color': color})
    else:
        form = RegistrationFormDocente()
    return render(request, 'registration/register.html', {'form': form})


def register_funcionario(request):
    if request.method == 'POST':
        form = RegistrationFormFuncionario(request.POST)
        if form.is_valid():
            funcionario = form.save(commit=False)
            funcionario.is_funcionario = True
            funcionario.save()
            group = Group.objects.get(name='funcionario')  
            funcionario.groups.add(group)
            pedidos = Pedido.objects.select_subclasses(PedidoUC, PedidoHorario, PedidoOutros, PedidoSala).order_by('datacriacao')
            table = PedidoTable(pedidos)
            table.paginate(page=request.GET.get("page", 1), per_page=10)
            mensagem = "Utilizador registado com sucesso"
            colorBack = '#d4edda'
            color = '#155724'
            return render(request, 'index_pedidos.html', {'pedidos': pedidos, 'table': table, 'mensagem': mensagem, 'colorBack': colorBack , 'color': color})
    else:
        form = RegistrationFormFuncionario()
    return render(request, 'registration/register.html', {'form': form})