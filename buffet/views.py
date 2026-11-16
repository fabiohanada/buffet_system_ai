from django.db.models import Sum
from django.shortcuts import get_object_or_404, render, redirect
from .models import Colaborador, EscalaEvento, Evento, Ingrediente, TransacaoFinanceira


def dashboard_view(request):
    eventos = Evento.objects.all().order_by('data_hora')
    ingredientes_criticos = [
        i for i in Ingrediente.objects.all() if i.status_estoque == 'Crítico / Baixo'
    ]

    context = {
        'eventos': eventos,
        'ingredientes_criticos': ingredientes_criticos,
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