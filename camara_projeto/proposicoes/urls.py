from django.urls import path
from . import views

urlpatterns = [
    path('buscar/',                         views.BuscarProposicoesView.as_view(),    name='buscar-proposicoes'),
    path('<int:id_proposicao>/',            views.DetalheProposicaoView.as_view(),    name='detalhe-proposicao'),
    path('<int:id_proposicao>/tramitacao/', views.TramitacaoProposicaoView.as_view(), name='tramitacao-proposicao'),
]
