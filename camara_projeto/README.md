# Acompanhamento de Projetos de Lei – Câmara dos Deputados

## Por que API e não Selenium?

A Câmara dos Deputados disponibiliza uma **API REST pública e gratuita** sem necessidade de autenticação:
`https://dadosabertos.camara.leg.br/api/v2`

✅ API REST → usada neste projeto  
❌ Selenium → desnecessário (o site permite e a API é completa)

---

## Arquitetura

```
Browser (seu HTML existente)
        │  fetch()
        ▼
┌─────────────────────────┐
│   Django (este projeto) │
│                         │
│  /api/proposicoes/…     │──┐
│  /api/votacoes/…        │  │  requests
│                         │  ▼
│  camara_app/services/   │  API Dados Abertos
│  camara_api.py          │◄─┘ dadosabertos.camara.leg.br
└─────────────────────────┘
```

---

## Estrutura de Arquivos

```
camara_projeto/
├── core/
│   ├── settings.py          # Configurações (CAMARA_API_BASE, cache)
│   └── urls.py              # Roteamento raiz
│
├── camara_app/
│   ├── services/
│   │   └── camara_api.py    # ★ Toda a lógica de acesso à API da Câmara
│   ├── templates/
│   │   └── camara_app/
│   │       └── index.html   # Exemplo de integração com seu HTML
│   ├── static/
│   │   └── camara_app/js/
│   │       └── camara_api.js  # ★ Cliente JS para suas páginas HTML
│   ├── views.py             # Serve os HTMLs existentes
│   └── urls.py
│
├── proposicoes/
│   ├── views.py             # Endpoints REST de proposições
│   └── urls.py
│
├── votacoes/
│   ├── views.py             # Endpoints REST de votações + votos
│   └── urls.py
│
└── requirements.txt
```

---

## Instalação

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Endpoints da API Interna

### Proposições
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/proposicoes/buscar/` | Busca por keyword, tipo, número, ano |
| GET | `/api/proposicoes/<id>/` | Detalhe completo |
| GET | `/api/proposicoes/<id>/tramitacao/` | Histórico de tramitação |

**Parâmetros de busca:**
- `keywords` – texto livre (ex: `reforma tributária`)
- `siglaTipo` – `PL`, `PEC`, `MPV`, `PDL`, etc.
- `numero` – número da proposição
- `ano` – ano (ex: `2024`)
- `pagina`, `itens` – paginação

### Votações
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/votacoes/buscar/` | Lista votações por proposição ou período |
| GET | `/api/votacoes/<id>/` | Detalhe de uma votação |
| GET | `/api/votacoes/<id>/votos/` | Votos nominais + resumo Sim/Não/Abstenção |

**Parâmetros de busca:**
- `idProposicao` – filtra votações de uma proposição específica
- `dataInicio`, `dataFim` – período (`AAAA-MM-DD`)

---

## Integração com seu HTML Existente

Adicione em todas as suas páginas, antes de `</body>`:

```html
<script src="{% static 'camara_app/js/camara_api.js' %}"></script>
```

Depois chame normalmente:

```js
// Buscar projetos de lei
const { dados } = await camaraAPI.buscarProposicoes({ keywords: 'meio ambiente' });

// Tramitação
const { dados: tramitacoes } = await camaraAPI.tramitacaoProposicao(2345678);

// Votações de um projeto
const { dados: votacoes } = await camaraAPI.buscarVotacoes({ idProposicao: 2345678 });

// Votos nominais + placar
const { dados: votos, resumo } = await camaraAPI.votosVotacao('2345678-99');
console.log(resumo); // { Sim: 312, Não: 145, Abstenção: 7, Outros: 0 }
```

---

## Cache

O Django usa cache em memória por padrão (5 min).  
Em produção, substitua por Redis em `settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```
