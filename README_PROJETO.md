
## Resumo

Microsserviço REST em Python com FastAPI para cadastro e busca de documentos, com:

- busca textual usando PostgreSQL Full Text Search;
- busca por frase (`busca`) e por termo (`palavraChave`);
- ordenação geográfica por proximidade (PostGIS);
- observabilidade (logs estruturados + métricas);
- testes automatizados sem depender de banco para o fluxo principal.

---

## Stack

- Python 3.x
- FastAPI
- SQLAlchemy 2 + psycopg
- Alembic
- PostgreSQL + PostGIS
- Prometheus client
- Pytest + pytest-cov

---

## Arquitetura e estratégia adotada

A implementação segue um estilo **DDD + ports/adapters**:

- `src/domain`: entidade, objetos de valor, serviços de domínio e exceções de negócio;
- `src/application`: casos de uso, comandos/queries e contratos (`Repository`, `UnitOfWork`);
- `src/infrastructure`: SQLAlchemy, migrações, banco e observabilidade;
- `src/api`: endpoints, DTOs, middlewares, mapeamentos e error handlers.

### Por que DDD neste contexto

Como o cliente é a **Sicredi** (setor financeiro), foquei em uma estrutura que deixa regra clara e reduz risco de comportamento inesperado ao evoluir.

Os motivos principais da escolha:

- separar regra de negócio de framework e SQL;
- deixar invariantes do problema explícitas (ex.: `palavraChave` XOR `busca`, validação de coordenadas, limite de termo);
- facilitar testes de regra sem depender de Postgres em cada execução;
- manter o projeto legível para evolução futura (novas regras, novos filtros, outro repositório).

### Arquiteturas consideradas (e por que não escolhi)

- **MVC**: é rápido de montar, mas tende a misturar regra de negócio no controller/service com o tempo.
- **Clean/Hexagonal**: costumo gostar, mas para este escopo adicionaria camadas/boilerplate além do necessário.
- **Event-driven**: faz sentido em cenários distribuídos; para este desafio síncrono aumentaria complexidade operacional sem ganho proporcional.
- **Monólito por feature**: simples no começo, mas costuma misturar bagunçar API/infra conforme cresce.

DDD deu um bom equilíbrio entre organização, velocidade de entrega e manutenção.

---

## Execução local

### 1) Pré-requisitos

- Python instalado
- PostgreSQL em execução
- PostGIS instalado no mesmo PostgreSQL (necessário para a migração geo)

### 2) Ambiente e dependências

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3) Configuração

Crie `.env` na raiz (exemplo):

```env
DATABASE_URL=postgresql+psycopg://postgres:895623@localhost:5432/documentos
ENVIRONMENT=development
```
Tem um env de exemplo, caso quero usá-lo, só o renomeie para *.env*

### 4) Migrações

```powershell
python -m alembic upgrade head
```

### 5) Subir API

```powershell
uvicorn src.main:app --reload --no-server-header
```

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `GET /health/live` e `GET /health/ready`
- Métricas: `GET /metrics`

---

## Testes

A suíte principal foi construída para não exigir banco real:

- usa fakes em memória nos casos de uso;
- usa override de dependências na API;
- evita dependência de Postgres para validar regra de negócio.

Comando:

```powershell
python -m pytest tests -q --cov=src --cov-config=.coveragerc --cov-report=term-missing
```

Resultado de referência atual: **39 testes, ~81% de cobertura**.

---

## Endpoints

### POST `/documentos`

Cria documento com:

- `titulo`
- `autor`
- `conteudo`
- `data`
- `latitude`
- `longitude`

### GET `/documentos`

Busca com **exatamente um** entre:

- `palavraChave` (token)
- `busca` (frase)

Parâmetros opcionais:

- `latitude` e `longitude` para ordenação geográfica;
- `limit`, `offset`;
- `conteudoPreview`.

---

## Considerações de performance

- Full-text com `to_tsvector`/`ts_rank` e índice GIN.
- Campo geográfico com PostGIS + índice GiST para ordenação por distância.
- Paginação com `limit`/`offset`.
- Pool de conexões configurável.
- Métrica de duração da busca e logs estruturados por request.

---

## Decisões importantes da implementação

### 1) Contrato de busca

Escolhi validar essa regra no domínio (e não só no controller) para evitar comportamento ambíguo em qualquer ponto de entrada.  
Na prática, isso deixa a regra centralizada e impede que ela seja quebrada quando o endpoint evoluir.

### 2) Coordenadas obrigatórias no cadastro

Como o bônus de ordenação geográfica era requisito relevante para o desafio, optei por pedir `latitude` e `longitude` no `POST`.  
Isso simplifica o modelo, evita documento “incompleto” para busca por proximidade e reduz tratamento condicional espalhado.

### 3) FTS no PostgreSQL em vez de busca textual simples

Usei Full Text Search nativo (`to_tsvector`, `@@`, `ts_rank`) porque ele escala melhor que `ILIKE` em massa e mantém a solução dentro da restrição do desafio (sem Elastic/Solr).  
Com índice GIN, o custo de consulta cai bastante quando a base cresce.

### 4) Por que PostGIS

Eu poderia calcular distância no Python, mas isso desloca custo para a aplicação e piora conforme aumenta volume de dados/concurrency.  
Com PostGIS, o banco faz o trabalho geoespacial com tipo/operadores próprios e índice GiST, mantendo a ordenação geográfica mais eficiente e previsível.

Em resumo, a escolha do GIS no foi por:

- performance melhor em ordenação por proximidade;
- uso de índice espacial real (em vez de cálculo linha a linha no app);
- menor custo de CPU na API;
- solução robusta e padrão de mercado para dado geográfico em banco relacional.

### 5) Testes sem serviço externo

A suíte principal usa fakes em memória e override de dependências para garantir feedback rápido e cobertura de regra de negócio sem depender de ambiente.  
Teste de integração com banco pode existir depois, mas não foi obrigatório para validar o core da lógica.

---
