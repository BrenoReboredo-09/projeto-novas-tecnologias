"""
votacoes/views.py
──────────────────
API REST interna — Votações.

Rotas:
  GET /api/votacoes/buscar/          → lista por proposição ou período
  GET /api/votacoes/<id>/            → detalhe de uma votação
  GET /api/votacoes/<id>/votos/      → votos nominais dos deputados
"""

from django.http import JsonResponse
from django.views import View

from camara_app.services.camara_api import (
    buscar_votacoes,
    detalhe_votacao,
    votos_votacao,
    CamaraAPIError,
)


def _json_error(msg: str, status: int = 500) -> JsonResponse:
    return JsonResponse({'erro': msg}, status=status)


class BuscarVotacoesView(View):
    """
    GET /api/votacoes/buscar/?idProposicao=12345&dataInicio=2024-01-01&dataFim=2024-12-31
    """

    def get(self, request):
        q = request.GET
        try:
            resultado = buscar_votacoes(
                id_proposicao=q.get('idProposicao'),
                data_inicio=q.get('dataInicio'),
                data_fim=q.get('dataFim'),
                pagina=int(q.get('pagina', 1)),
                itens=int(q.get('itens', 20)),
            )
        except CamaraAPIError as e:
            return _json_error(str(e))

        return JsonResponse({'dados': resultado['dados'], 'total': len(resultado['dados'])})


class DetalheVotacaoView(View):
    """
    GET /api/votacoes/<id>/
    """

    def get(self, request, id_votacao: str):
        try:
            resultado = detalhe_votacao(id_votacao)
        except CamaraAPIError as e:
            return _json_error(str(e))

        return JsonResponse({'dados': resultado['dados']})


class VotosView(View):
    """
    GET /api/votacoes/<id>/votos/
    Retorna os votos nominais + resumo (sim/não/abstenção).
    """

    def get(self, request, id_votacao: str):
        try:
            resultado = votos_votacao(id_votacao)
        except CamaraAPIError as e:
            return _json_error(str(e))

        votos = resultado['dados']

        # Resumo automático do placar
        resumo = {'Sim': 0, 'Não': 0, 'Abstenção': 0, 'Outros': 0}
        for v in votos:
            voto_str = v.get('tipoVoto', '')
            if voto_str in resumo:
                resumo[voto_str] += 1
            else:
                resumo['Outros'] += 1

        return JsonResponse({'dados': votos, 'resumo': resumo, 'total': len(votos)})
