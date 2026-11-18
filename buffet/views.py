from django.db.models import Sum
from django.shortcuts import get_object_or_404, render, redirect
from .models import Colaborador, EscalaEvento, Evento, Ingrediente, TransacaoFinanceira
from .forms import EventoForm
import calendar
from datetime import datetime
from django.shortcuts import render
from django.db import models

def dashboard_view(request):
  hoje = datetime.now()
  ano = int(request.GET.get('ano', hoje.year))
  mes = int(request.GET.get('mes', hoje.month))

  # Cálculo para as setas de navegação de meses (Anterior / Próximo)
  mes_ant = mes - 1
  ano_ant = ano
  if mes_ant < 1:
    mes_ant = 12
    ano_ant = ano - 1

  mes_prox = mes + 1
  ano_prox = ano
  if mes_prox > 12:
    mes_prox = 1
    ano_prox = ano + 1

  # Instancia o calendário
  cal = calendar.Calendar(firstweekday=6)  # Começa no Domingo
  dias_mes = cal.monthdayscalendar(ano, mes)

  # Busca eventos do mês para marcar no calendário
  eventos_mes = Evento.objects.filter(
      data_hora__year=ano, data_hora__month=mes
  )

  # Mapeia os dias que possuem eventos
  eventos_por_dia = {}
  for ev in eventos_mes:
    dia = ev.data_hora.day
    if dia not in eventos_por_dia:
      eventos_por_dia[dia] = []
    eventos_por_dia[dia].append(ev)

  eventos = Evento.objects.all().order_by('data_hora')[:5]

  context = {
      'eventos': eventos,
      'ano': ano,
      'mes': mes,
      'mes_ant': mes_ant,
      'ano_ant': ano_ant,
      'mes_prox': mes_prox,
      'ano_prox': ano_prox,
      'nome_mes': calendar.month_name[mes],
      'dias_mes': dias_mes,
      'eventos_por_dia': eventos_por_dia,
  }
  return render(request, 'buffet/dashboard.html', context)

def agenda_view(request):
    """Página 3: Agenda de Eventos"""
    eventos = Evento.objects.all().order_by('data_hora')
    context = {
        'eventos': eventos,
    }
    return render(request, 'buffet/agenda.html', context)


def cozinha_view(request):
    """Página 4: Explosão de Cardápio e Cozinha"""
    eventos = Evento.objects.all().order_by('-data_hora')
    evento_selecionado = None
    lista_compras = []

    evento_id = request.GET.get('evento_id')
    if evento_id:
        evento_selecionado = get_object_or_404(Evento, id=evento_id)
        convidados = evento_selecionado.numero_convidados

        controlador_insumos = {}

        for receita in evento_selecionado.cardapio.all():
            for item_receita in receita.itens.all():
                ing = item_receita.ingrediente
                quantidade_total = (
                    float(item_receita.quantidade)
                    / float(receita.rendimento_porcoes)
                    * convidados
                )

                if ing.id in controlador_insumos:
                    controlador_insumos[ing.id]['qtd_necessaria'] += quantidade_total
                else:
                    controlador_insumos[ing.id] = {
                        'ingrediente': ing.nome,
                        'unidade': ing.unidade_medida,
                        'qtd_necessaria': quantidade_total,
                        'estoque_atual': float(ing.quantidade_estoque),
                    }

        for dados in controlador_insumos.values():
            falta = dados['qtd_necessaria'] - dados['estoque_atual']
            status = 'OK'
            if falta > 0:
                status = f'Faltam {falta:.2f} {dados["unidade"]}'

            lista_compras.append({
                'ingrediente': dados['ingrediente'],
                'unidade': dados['unidade'],
                'qtd_necessaria': round(dados['qtd_necessaria'], 2),
                'estoque_atual': round(dados['estoque_atual'], 2),
                'status': status,
            })

    context = {
        'eventos': eventos,
        'evento_selecionado': evento_selecionado,
        'lista_compras': lista_compras,
    }
    return render(request, 'buffet/cozinha.html', context)


def estoque_view(request):
    """Página 5: Gestão de Estoque"""
    ingredientes = Ingrediente.objects.all().order_by('nome')
    context = {
        'ingredientes': ingredientes,
    }
    return render(request, 'buffet/estoque.html', context)


def equipe_view(request):
    """Página 6: Escala de Equipe"""
    escalas = EscalaEvento.objects.all().order_by('-evento__data_hora')
    evento_id = request.GET.get('evento_id')
    if evento_id:
        escalas = escalas.filter(evento_id=evento_id)

    eventos = Evento.objects.all().order_by('-data_hora')

    context = {
        'escalas': escalas,
        'eventos': eventos,
        'evento_selecionado': evento_id,
    }
    return render(request, 'buffet/equipe.html', context)


def financeiro_view(request):
    """Página 7: Financeiro & DRE"""
    transacoes = TransacaoFinanceira.objects.all().order_by('-data')

    total_receitas = (
        TransacaoFinanceira.objects.filter(tipo='RECEITA').aggregate(
            Sum('valor')
        )['valor__sum']
        or 0
    )
    total_despesas = (
        TransacaoFinanceira.objects.filter(tipo='DESPESA').aggregate(
            Sum('valor')
        )['valor__sum']
        or 0
    )
    lucro_liquido = total_receitas - total_despesas

    context = {
        'transacoes': transacoes,
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'lucro_liquido': lucro_liquido,
    }
    return render(request, 'buffet/financeiro.html', context)

def evento_detalhe_view(request, evento_id):
  """Página 2 e 3 do Wireframe: Detalhes, Logística e Fechamento Pós-Evento"""
  evento = get_object_or_404(Evento, id=evento_id)
  escalas = EscalaEvento.objects.filter(evento=evento)

  # Ação POST para concluir o fechamento pós-evento
  if request.method == 'POST':
    acao = request.POST.get('acao')
    if acao == 'concluir_fechamento':
      evento.status = 'Realizado / Fechado'
      evento.save()

      # Opcional: Gerar automaticamente a transação financeira de receita do evento se houver preço de contrato
      if evento.preco_contrato:
        TransacaoFinanceira.objects.get_or_create(
            descricao=(
                f'Receita Evento: {evento.nome_evento} - {evento.nome_cliente}'
            ),
            tipo='RECEITA',
            valor=evento.preco_contrato,
            data=evento.data_hora.date(),
            evento=evento,
        )
      return redirect('evento_detalhe', evento_id=evento.id)

  context = {
      'evento': evento,
      'escalas': escalas,
  }
  return render(request, 'buffet/evento_detalhe.html', context)

def evento_criar_view(request):
  """Página para cadastrar um novo evento"""
  if request.method == 'POST':
    form = EventoForm(request.POST)
    if form.is_valid():
      evento = form.save()
      return redirect('evento_detalhe', evento_id=evento.id)
  else:
    form = EventoForm()

  context = {
      'form': form,
  }
  return render(request, 'buffet/evento_form.html', context)