"""
camara_app/services/camara_api.py
──────────────────────────────────
Camada de acesso à API Dados Abertos da Câmara dos Deputados.
Base URL: https://dadosabertos.camara.leg.br/api/v2

Endpoints usados:
  GET /proposicoes                  – busca por palavra-chave / número / tipo
  GET /proposicoes/{id}             – detalhe de uma proposição
  GET /proposicoes/{id}/tramitacoes – histórico de tramitação
  GET /votacoes                     – lista de votações (filtros: idProposicao, dataInicio…)
  GET /votacoes/{id}                – detalhe de uma votação
  GET /votacoes/{id}/votos          – votos nominais dos deputados
"""

import requests
from django.conf import settings
from django.core.cache import cache

BASE = settings.CAMARA_API_BASE
TIMEOUT = settings.CAMARA_API_TIMEOUT


# ── helpers ───────────────────────────────────────────────────────────────────

def _get(path: str, params: dict = None, cache_key: str = None, ttl: int = 300):
    """
    Faz GET na API da Câmara com cache opcional.

    Retorna o dict já deserializado (campo 'dados') ou levanta CamaraAPIError.
    """
    if cache_key:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    url = f"{BASE}{path}"
    headers = {'Accept': 'application/json'}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        raise CamaraAPIError("API da Câmara não respondeu a tempo.")
    except requests.exceptions.HTTPError as e:
        raise CamaraAPIError(f"Erro HTTP {resp.status_code}: {e}")
    except requests.exceptions.RequestException as e:
        raise CamaraAPIError(f"Erro de conexão: {e}")

    payload = resp.json()
    result = {
        'dados': payload.get('dados', []),
        'links': payload.get('links', []),
    }

    if cache_key:
        cache.set(cache_key, result, ttl)

    return result


class CamaraAPIError(Exception):
    """Erro ao acessar a API de Dados Abertos da Câmara."""


# ── Proposições ───────────────────────────────────────────────────────────────

def buscar_proposicoes(
    keywords: str = None,
    numero: int = None,
    sigla_tipo: str = None,   # PL, PEC, MPV, PDL…
    ano: int = None,
    pagina: int = 1,
    itens: int = 20,
) -> dict:
    """
    GET /proposicoes
    Retorna lista de proposições com filtros opcionais.
    """
    params = {
        'pagina': pagina,
        'itens': itens,
        'ordem': 'DESC',
        'ordenarPor': 'id',
    }
    if keywords:
        params['keywords'] = keywords
    if numero:
        params['numero'] = numero
    if sigla_tipo:
        params['siglaTipo'] = sigla_tipo
    if ano:
        params['ano'] = ano

    cache_key = f"proposicoes:{keywords}:{numero}:{sigla_tipo}:{ano}:p{pagina}"
    return _get('/proposicoes', params=params, cache_key=cache_key)


def detalhe_proposicao(id_proposicao: int) -> dict:
    """
    GET /proposicoes/{id}
    Retorna dados completos de uma proposição.
    """
    cache_key = f"proposicao:{id_proposicao}"
    return _get(f'/proposicoes/{id_proposicao}', cache_key=cache_key, ttl=600)


def tramitacao_proposicao(id_proposicao: int) -> dict:
    """
    GET /proposicoes/{id}/tramitacoes
    Retorna o histórico de tramitação (ordem cronológica).
    """
    cache_key = f"tramitacao:{id_proposicao}"
    return _get(f'/proposicoes/{id_proposicao}/tramitacoes', cache_key=cache_key, ttl=180)


# ── Votações ──────────────────────────────────────────────────────────────────

def buscar_votacoes(
    id_proposicao: int = None,
    data_inicio: str = None,    # 'AAAA-MM-DD'
    data_fim: str = None,
    pagina: int = 1,
    itens: int = 20,
) -> dict:
    """
    GET /votacoes
    Lista votações, opcionalmente filtradas por proposição ou período.
    """
    params = {
        'pagina': pagina,
        'itens': itens,
        'ordem': 'DESC',
        'ordenarPor': 'dataHoraInicio',
    }
    if id_proposicao:
        params['idProposicao'] = id_proposicao
    if data_inicio:
        params['dataInicio'] = data_inicio
    if data_fim:
        params['dataFim'] = data_fim

    cache_key = f"votacoes:{id_proposicao}:{data_inicio}:{data_fim}:p{pagina}"
    return _get('/votacoes', params=params, cache_key=cache_key)


def detalhe_votacao(id_votacao: str) -> dict:
    """
    GET /votacoes/{id}
    Retorna dados de uma votação (resultado, placar, proposição votada…).
    """
    cache_key = f"votacao:{id_votacao}"
    return _get(f'/votacoes/{id_votacao}', cache_key=cache_key, ttl=600)


def votos_votacao(id_votacao: str) -> dict:
    """
    GET /votacoes/{id}/votos
    Retorna os votos nominais de cada deputado.
    """
    cache_key = f"votos:{id_votacao}"
    return _get(f'/votacoes/{id_votacao}/votos', cache_key=cache_key, ttl=600)
