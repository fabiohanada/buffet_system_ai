from django.db import models

class Ingrediente(models.Model):
  nome = models.CharField(max_length=100)
  unidade_medida = models.CharField(max_length=10)  # kg, L, un, pct
  custo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
  quantidade_estoque = models.DecimalField(
      max_digits=10, decimal_places=2, default=0.00
  )
  estoque_minimo = models.DecimalField(
      max_digits=10, decimal_places=2, default=0.00
  )

  @property
  def status_estoque(self):
    if self.quantidade_estoque <= self.estoque_minimo:
      return 'Crítico / Baixo'
    return 'Normal'

  def __str__(self):
    return f'{self.nome} ({self.unidade_medida})'


class Receita(models.Model):
  nome = models.CharField(max_length=150)
  rendimento_porcoes = models.PositiveIntegerField()
  modo_preparo = models.TextField(blank=True, null=True)

  def custo_total_receita(self):
    return sum(item.custo_parcial for item in self.itens.all())

  def custo_por_porcao(self):
    if self.rendimento_porcoes and self.rendimento_porcoes > 0:
      return self.custo_total_receita() / self.rendimento_porcoes
    return 0

  def __str__(self):
    return self.nome


class ItemReceita(models.Model):
  receita = models.ForeignKey(
      Receita, related_name='itens', on_delete=models.CASCADE
  )
  ingrediente = models.ForeignKey(Ingrediente, on_delete=models.PROTECT)
  quantidade = models.DecimalField(max_digits=10, decimal_places=3)

  @property
  def custo_parcial(self):
    return self.quantidade * self.ingrediente.custo_unitario


class Colaborador(models.Model):
  nome = models.CharField(max_length=150)
  funcao = models.CharField(max_length=50)  # Garçom, Cozinheira, Segurança
  diaria_padrao = models.DecimalField(max_digits=10, decimal_places=2)
  telefone = models.CharField(max_length=20, blank=True, null=True)

  def __str__(self):
    return f'{self.nome} ({self.funcao})'


class Evento(models.Model):
  nome_cliente = models.CharField(max_length=150)
  nome_evento = models.CharField(
      max_length=150
  )  # Ex: Aniversário 15 anos / Casamento
  data_hora = models.DateTimeField()
  numero_convidados = models.PositiveIntegerField()
  cardapio = models.ManyToManyField(Receita, blank=True)
  markup_aplicado = models.DecimalField(max_digits=5, decimal_places=2, default=2.50)
  preco_contrato = models.DecimalField(
      max_digits=10, decimal_places=2, blank=True, null=True
  )
  status = models.CharField(max_length=50, default='Em Negociação')

  def custo_total_insumos(self):
    custo = 0
    for receita in self.cardapio.all():
      custo += receita.custo_por_porcao() * self.numero_convidados
    return custo

  def __str__(self):
    return f'{self.nome_evento} - {self.nome_cliente}'


class EscalaEvento(models.Model):
  colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE)
  evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
  funcao = models.CharField(
      max_length=100
  )  # ou max_length se for CharField
  valor_diaria = models.DecimalField(
      max_digits=10, decimal_places=2, default=0.00
  )

  def __str__(self):
    return (
        f"{self.colaborador.nome} - {self.evento.nome_evento} ({self.funcao})"
    )


class TransacaoFinanceira(models.Model):
  vencimento = models.DateField()
  descricao = models.CharField(max_length=200)
  valor = models.DecimalField(max_digits=10, decimal_places=2)
  tipo = models.CharField(
      max_length=10, choices=[('entrada', 'Entrada'), ('saida', 'Saída')]
  )
  status = models.CharField(max_length=30, default='A Pagar / A Receber')
  evento = models.ForeignKey(
      Evento, blank=True, null=True, on_delete=models.SET_NULL
  )

  def __str__(self):
    return f'{self.descricao} - R$ {self.valor}'

class TransacaoFinanceira(models.Model):
  TIPO_CHOICES = (
      ('RECEITA', 'Receita'),
      ('DESPESA', 'Despesa'),
  )

  descricao = models.CharField(max_length=200)
  tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
  valor = models.DecimalField(max_digits=10, decimal_places=2)
  data = models.DateField()
  evento = models.ForeignKey(
      Evento, on_delete=models.SET_NULL, null=True, blank=True
  )

  def __str__(self):
    return f'{self.tipo}: {self.descricao} - R$ {self.valor}'