from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('agenda/', views.agenda_view, name='agenda'),
    path('cozinha/', views.cozinha_view, name='cozinha'),
    path('estoque/', views.estoque_view, name='estoque'),
    path('equipe/', views.equipe_view, name='equipe'),
    path('financeiro/', views.financeiro_view, name='financeiro'),
    path(
        'evento/<int:evento_id>/',
        views.evento_detalhe_view,
        name='evento_detalhe',
    ),
]