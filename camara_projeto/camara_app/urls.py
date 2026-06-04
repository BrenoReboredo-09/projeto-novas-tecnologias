from django.urls import path
from . import views

urlpatterns = [
    # Páginas
    path('',                        views.pagina_principal, name='principal'),
    path('cadastro/',               views.pagina_cadastro,  name='cadastro'),
    path('login/',                  views.pagina_login,     name='login'),
    path('logout/',                 views.pagina_logout,    name='logout'),
    path('perfil/',                 views.pagina_perfil,    name='perfil'),
    path('proposicao/<int:id_proposicao>/', views.pagina_detalhe, name='detalhe'),

    # Favoritos (AJAX)
    path('favoritos/adicionar/<int:id_proposicao>/', views.adicionar_favorito, name='adicionar-favorito'),
    path('favoritos/remover/<int:id_proposicao>/',   views.remover_favorito,   name='remover-favorito'),
    path('favoritos/desfavoritar/<int:id_proposicao>/', views.desfavoritar_perfil, name='desfavoritar'),
]
