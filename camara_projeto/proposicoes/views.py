"""
proposicoes/views.py
─────────────────────
API REST interna para o frontend HTML existente.

Rotas:
  GET /api/proposicoes/buscar/          → busca por keyword, número, tipo, ano
  GET /api/proposicoes/<id>/            → detalhe de uma proposição
  GET /api/proposicoes/<id>/tramitacao/ → histórico de tramitação
"""

import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from camara_app.services.camara_api import (
    buscar_proposicoes,
    detalhe_proposicao,
    tramitacao_proposicao,
    CamaraAPIError,
)


def _json_error(msg: str, status: int = 500) -> JsonResponse:
    return JsonResponse({'erro': msg}, status=status)


class BuscarProposicoesView(View):
    """
    GET /api/proposicoes/buscar/?keywords=reforma&siglaTipo=PL&ano=2024&pagina=1
    """

    def get(self, request):
        q = request.GET
        try:
            resultado = buscar_proposicoes(
                keywords=q.get('keywords'),
                numero=q.get('numero'),
                sigla_tipo=q.get('siglaTipo'),
                ano=q.get('ano'),
                pagina=int(q.get('pagina', 1)),
                itens=int(q.get('itens', 20)),
            )
        except CamaraAPIError as e:
            return _json_error(str(e))

        return JsonResponse({
            'dados': resultado['dados'],
            'links': resultado['links'],
            'total': len(resultado['dados']),
        })


class DetalheProposicaoView(View):
    """
    GET /api/proposicoes/<id>/
    """

    def get(self, request, id_proposicao: int):
        try:
            resultado = detalhe_proposicao(id_proposicao)
        except CamaraAPIError as e:
            return _json_error(str(e))

        return JsonResponse({'dados': resultado['dados']})


class TramitacaoProposicaoView(View):
    """
    GET /api/proposicoes/<id>/tramitacao/
    Retorna o histórico de tramitação em ordem cronológica (mais recente primeiro).
    """

    def get(self, request, id_proposicao: int):
        try:
            resultado = tramitacao_proposicao(id_proposicao)
        except CamaraAPIError as e:
            return _json_error(str(e))

        # Inverte para mostrar mais recente no topo
        tramitacoes = list(reversed(resultado['dados']))
        return JsonResponse({'dados': tramitacoes, 'total': len(tramitacoes)})
