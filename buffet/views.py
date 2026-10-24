from django.shortcuts import get_object_or_404, render
from .models import EscalaEvento, Evento, Ingrediente

from django.db.models import Sum
from django.shortcuts import render
from .models import TransacaoFinanceira


def dashboard_view(request):  # Corrigido o argumento de 'views' para 'request'
  eventos = Evento.objects.all().order_by('data_hora')

  # CORREÇÃO AQUI: Adicionado o '.objects'
  ingredientes_criticos = [
      i for i in Ingrediente.objects.all() if i.status_estoque == 'Crítico / Baixo'
  ]

  context = {
      'eventos': eventos,
      'ingredientes_criticos': ingredientes_criticos,
  }
  return render(request, 'buffet/dashboard.html', context)

def cozinha_view(request):
  eventos = Evento.objects.all().order_by('-data_hora')
  evento_selecionado = None
  lista_compras = []

  # Se o usuário escolheu um evento no select da tela
  evento_id = request.GET.get('evento_id')
  if evento_id:
    evento_selecionado = get_object_or_404(Evento, id=evento_id)
    convidados = evento_selecionado.numero_convidados

    # Dicionário para acumular os ingredientes de todas as receitas do cardápio
    controlador_insumos = {}

    for receita in evento_selecionado.cardapio.all():
      for item_receita in receita.itens.all():
        ing = item_receita.ingrediente
        # Quantidade necessária = (Qtd na receita / rendimento da receita) * número de convidados do evento
        # Para simplificar no MVP, assumimos a proporção linear da receita padrão por pessoa ou por porção
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

    # Converter o dicionário em lista para exibir na tabela
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

def equipe_view(request):
  escalas = EscalaEvento.objects.all().order_by('-evento__data_hora')

  # Filtro opcional por evento
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
  transacoes = TransacaoFinanceira.objects.all().order_by('-data')

  # Calcular totais para o DRE / Resumo
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