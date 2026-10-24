from django.contrib import admin
from .models import (
    Colaborador,
    EscalaEvento,
    Evento,
    Ingrediente,
    ItemReceita,
    Receita,
    TransacaoFinanceira,
)

# Registrando os modelos para aparecerem no Django Admin
admin.site.register(Ingrediente)
admin.site.register(Receita)
admin.site.register(ItemReceita)
admin.site.register(Colaborador)
admin.site.register(Evento)
admin.site.register(EscalaEvento)
admin.site.register(TransacaoFinanceira)