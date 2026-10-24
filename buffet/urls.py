from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('cozinha/', views.cozinha_view, name='cozinha'),
    path(
        'equipe/', views.equipe_view, name='equipe'
    ),
    path(
        'financeiro/', views.financeiro_view, name='financeiro'
    ),
]