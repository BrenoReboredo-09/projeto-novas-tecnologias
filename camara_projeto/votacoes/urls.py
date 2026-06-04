from django.urls import path
from . import views

urlpatterns = [
    path('buscar/',             views.BuscarVotacoesView.as_view(),  name='buscar-votacoes'),
    path('<str:id_votacao>/',   views.DetalheVotacaoView.as_view(),  name='detalhe-votacao'),
    path('<str:id_votacao>/votos/', views.VotosView.as_view(),       name='votos-votacao'),
]
