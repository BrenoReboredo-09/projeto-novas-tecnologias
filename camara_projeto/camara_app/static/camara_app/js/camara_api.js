/**
 * camara_api.js
 * ─────────────
 * Cliente JS para a API interna do Django.
 * Importe este script nas suas páginas HTML existentes.
 *
 * Uso:
 *   const api = new CamaraAPI();
 *   const { dados } = await api.buscarProposicoes({ keywords: 'reforma tributária' });
 */

class CamaraAPI {
  constructor(baseUrl = '/api') {
    this.base = baseUrl;
  }

  async _fetch(path, params = {}) {
    const url = new URL(path, window.location.origin);
    Object.entries(params).forEach(([k, v]) => {
      if (v !== null && v !== undefined && v !== '') url.searchParams.set(k, v);
    });

    const resp = await fetch(url.toString(), {
      headers: { 'Accept': 'application/json' },
    });

    const data = await resp.json();

    if (!resp.ok) {
      throw new Error(data.erro || `Erro ${resp.status}`);
    }
    return data;
  }

  // ── Proposições ─────────────────────────────────────────────────────────────

  /**
   * Busca proposições.
   * @param {Object} opts - keywords, numero, siglaTipo, ano, pagina, itens
   */
  buscarProposicoes(opts = {}) {
    return this._fetch('/api/proposicoes/buscar/', opts);
  }

  /**
   * Detalhe de uma proposição.
   * @param {number} id
   */
  detalheProposicao(id) {
    return this._fetch(`/api/proposicoes/${id}/`);
  }

  /**
   * Histórico de tramitação (mais recente primeiro).
   * @param {number} id
   */
  tramitacaoProposicao(id) {
    return this._fetch(`/api/proposicoes/${id}/tramitacao/`);
  }

  // ── Votações ─────────────────────────────────────────────────────────────────

  /**
   * Lista votações.
   * @param {Object} opts - idProposicao, dataInicio, dataFim, pagina, itens
   */
  buscarVotacoes(opts = {}) {
    return this._fetch('/api/votacoes/buscar/', opts);
  }

  /**
   * Detalhe de uma votação.
   * @param {string} id
   */
  detalheVotacao(id) {
    return this._fetch(`/api/votacoes/${id}/`);
  }

  /**
   * Votos nominais + resumo (Sim/Não/Abstenção).
   * @param {string} id
   */
  votosVotacao(id) {
    return this._fetch(`/api/votacoes/${id}/votos/`);
  }
}

// Instância global — use `camaraAPI` nas suas páginas
const camaraAPI = new CamaraAPI();
