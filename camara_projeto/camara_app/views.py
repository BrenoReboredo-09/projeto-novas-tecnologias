"""
camara_app/views.py
────────────────────
Views de páginas HTML + autenticação + favoritos.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ProposicaoFavorita


# ── Páginas HTML ──────────────────────────────────────────────────────────────

def pagina_cadastro(request):
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1:
            messages.error(request, 'Preencha todos os campos.')
        elif password1 != password2:
            messages.error(request, 'As senhas não coincidem.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Esse nome de usuário já existe.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            messages.success(request, f'Conta criada! Bem-vindo, {username}.')
            return redirect('principal')

    return render(request, 'camara_app/cadastro.html')


def pagina_login(request):
    if request.user.is_authenticated:
        return redirect('principal')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'principal'))
        else:
            messages.error(request, 'Usuário ou senha incorretos.')

    return render(request, 'camara_app/login.html')


def pagina_logout(request):
    logout(request)
    return redirect('login')


def pagina_principal(request):
    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(
            ProposicaoFavorita.objects.filter(usuario=request.user)
            .values_list('id_proposicao', flat=True)
        )
    return render(request, 'camara_app/principal.html', {
        'favoritos_ids': favoritos_ids,
    })


@login_required
def pagina_perfil(request):
    favoritos = ProposicaoFavorita.objects.filter(usuario=request.user)
    return render(request, 'camara_app/perfil.html', {'favoritos': favoritos})


def pagina_detalhe(request, id_proposicao: int):
    ja_favoritado = False
    if request.user.is_authenticated:
        ja_favoritado = ProposicaoFavorita.objects.filter(
            usuario=request.user, id_proposicao=id_proposicao
        ).exists()
    return render(request, 'camara_app/detalhe.html', {
        'id_proposicao': id_proposicao,
        'ja_favoritado': ja_favoritado,
    })


# ── Favoritos (AJAX) ──────────────────────────────────────────────────────────

@login_required
@require_POST
def adicionar_favorito(request, id_proposicao: int):
    obj, criado = ProposicaoFavorita.objects.get_or_create(
        usuario=request.user,
        id_proposicao=id_proposicao,
        defaults={
            'sigla_tipo': request.POST.get('sigla_tipo', ''),
            'numero':     request.POST.get('numero') or None,
            'ano':        request.POST.get('ano') or None,
            'ementa':     request.POST.get('ementa', ''),
            'situacao':   request.POST.get('situacao', ''),
        }
    )
    return JsonResponse({'ok': True, 'criado': criado})


@login_required
@require_POST
def remover_favorito(request, id_proposicao: int):
    ProposicaoFavorita.objects.filter(
        usuario=request.user, id_proposicao=id_proposicao
    ).delete()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def desfavoritar_perfil(request, id_proposicao: int):
    """Remove favorito vindo do formulário no perfil (redirect)."""
    ProposicaoFavorita.objects.filter(
        usuario=request.user, id_proposicao=id_proposicao
    ).delete()
    messages.success(request, 'Projeto removido dos favoritos.')
    return redirect('perfil')
