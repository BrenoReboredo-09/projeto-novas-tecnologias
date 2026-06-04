from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('camara_app.urls')),
    path('api/proposicoes/', include('proposicoes.urls')),
    path('api/votacoes/',    include('votacoes.urls')),
]
