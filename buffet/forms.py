from django import forms
from .models import Evento


class EventoForm(forms.ModelForm):

  class Meta:
    model = Evento
    fields = [
        'nome_cliente',
        'nome_evento',
        'data_hora',
        'numero_convidados',
        'cardapio',
        'markup_aplicado',
        'preco_contrato',
        'status',
    ]
    widgets = {
        'nome_cliente': forms.TextInput(
            attrs={
                'class': 'border border-gray-300 p-2 rounded w-full',
                'placeholder': 'Ex: Ana & Carlos',
            }
        ),
        'nome_evento': forms.TextInput(
            attrs={
                'class': 'border border-gray-300 p-2 rounded w-full',
                'placeholder': 'Ex: Casamento / Aniversário 15 anos',
            }
        ),
        'data_hora': forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'border border-gray-300 p-2 rounded w-full',
            }
        ),
        'numero_convidados': forms.NumberInput(
            attrs={
                'class': 'border border-gray-300 p-2 rounded w-full',
                'placeholder': '180',
            }
        ),
        'cardapio': forms.SelectMultiple(
            attrs={
                'class': (
                    'border border-gray-300 p-2 rounded w-full h-32'
                )
            }
        ),
        'markup_aplicado': forms.NumberInput(
            attrs={
                'class': 'border border-gray-300 p-2 rounded w-full',
                'step': '0.01',
            }
        ),
        'preco_contrato': forms.NumberInput(
            attrs={
                'class': 'border border-gray-300 p-2 rounded w-full',
                'placeholder': 'Ex: 15000.00',
            }
        ),
        'status': forms.TextInput(
            attrs={
                'class': 'border border-gray-300 p-2 rounded w-full',
                'value': 'Em Negociação',
            }
        ),
    }