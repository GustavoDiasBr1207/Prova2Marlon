# Sistema de Recomendação de Filmes — Prova2Marlon

Projeto simples em Flask para a disciplina: motor de recomendação leve integrado com TMDB e SQLite. Feito para testar via Postman (sem frontend).

**Principais componentes:**
- `app.py` — API Flask com endpoints: `/user/preferences`, `/movies/rate`, `/movies/recommend`.
- `init_db.py` — script para criar o banco SQLite (`movies.db`).
- `postman_collection.json` — coleção com exemplos para testar no Postman.
- `.env.example` — variáveis de ambiente (copie para `.env`).

## Instalação rápida

1. Criar ambiente (recomendado) e instalar dependências:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Copie e edite `.env`:

```powershell
copy .env.example .env
# edite .env e coloque sua TMDB_KEY
```

3. Inicialize o banco:

```powershell
python init_db.py
```

4. Rode o servidor Flask:

```powershell
python app.py
```

O servidor ficará disponível em `http://localhost:5000`.

## Testando com Postman

Importe `postman_collection.json` e execute as requisições na ordem:

1. `Save Preferences` — cadastra os gêneros favoritos e filmes assistidos.
2. `Rate Movie` — registra uma avaliação do usuário.
3. `Get Recommendations` — obtém a lista gerada pelo motor de recomendação.

## Endpoints

- `POST /user/preferences` — payload:

```
{
	"user_id": 1,
	"favorite_genres": ["Action","Sci-Fi"],
	"watched": [603, 550]
}
```

- `POST /movies/rate` — payload:

```
{
	"user_id": 1,
	"movie_id": 603,
	"rating": 4
}
```

- `GET /movies/recommend?user_id=1` — retorna JSON com recomendações (title, overview, poster, vote_average, popularity, score).

## Como funciona (resumo técnico)

- O backend guarda preferências e ratings em SQLite.
- Para recomendar, busca filmes na API TMDB filtrando por gênero (usa `genre/movie/list` + `discover/movie` quando possível) e ordena por uma pontuação simples (baseada em `vote_average` e `popularity`).
- Filtra filmes já assistidos.

## Apresentação (vídeo)

No vídeo, siga este roteiro curto:
1. Apresente a ideia e o diagrama de arquitetura (Flask ↔ SQLite ↔ TMDB ↔ JSON → Usuário/Postman).
2. Mostre o Postman: cadastrar preferências, dar uma nota e pedir recomendações.
3. Explique brevemente o motor de recomendação (filtra por gêneros, exclui assistidos, ordena por score/popularidade).

Boa sorte com a entrega — se quiser, eu posso gerar um `README` em PDF, slides simples ou um roteiro detalhado para o vídeo.
