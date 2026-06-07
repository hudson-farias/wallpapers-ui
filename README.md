# wallpaper-ui

Interface web para browsear wallpapers, escolher monitor, crop (MVP) e aplicar no KDE Plasma.

## Stack

- **Frontend:** SvelteKit + Vite
- **Backend:** FastAPI (Python) + SQLAlchemy
- **Cache:** `gallery-dl` em runtime (Pinterest → cache local)
- **Banco:** PostgreSQL (Docker) ou SQLite (dev local)
- **Container:** Docker Compose

## Fluxo de dados

```
URL original (Pinterest) → cache em runtime (gallery-dl) → UI
```

1. Fonte cadastrada no banco (URL do board)
2. Ao abrir a fonte na UI, o backend baixa para `backend/cache/<slug>/` (se cache vazio)
3. A UI lê o cache; favoritos são **cópias permanentes** em `backend/favorites/<slug>/`

## Pré-requisitos

- `gallery-dl` (instalado via `pip install -r requirements.txt` no venv)
- Boards privados: login no Vivaldi (`GALLERY_DL_BROWSER=vivaldi`)
- Docker + Docker Compose (opcional para dev local)

## Subir com Docker

```bash
cd wallpaper-ui
docker compose up --build
```

- UI: http://localhost:5173
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

Volumes:

| Volume | Uso |
|--------|-----|
| `cache-data` | cache runtime (`/app/cache`) |
| `favorites-data` | favoritos permanentes (`/app/favorites`) |
| `applied-data` | crops aplicados |
| `pg-data` | PostgreSQL |

## Banco de dados

| Ambiente | Padrão |
|----------|--------|
| Docker Compose | PostgreSQL |
| Dev local | SQLite em `backend/data/sources.db` |

## Desenvolvimento local (sem Docker)

### Backend (asdf → venv)

```bash
asdf install
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run.sh
```

Cache local: `backend/cache/<slug>/`  
Favoritos: `backend/favorites/<slug>/`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Rotas (UI)

| Rota | Página |
|------|--------|
| `/` | Home (redireciona para primeira fonte) |
| `/sources/{slug}` | Board + cache + atualizar |
| `/favorites` | Lista de subpastas |
| `/favorites/{pasta}` | Imagens favoritas da pasta |

Favoritos: `favorites/{pasta}/{board}__{arquivo}` — cópia permanente, sobrevive a refresh do board.

## API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/health` | Health check |
| GET | `/api/sources` | Lista fontes |
| POST | `/api/sources` | Adiciona fonte `{ "source": "https://..." }` |
| DELETE | `/api/sources/{id}` | Remove fonte + cache |
| GET | `/api/sources/{slug}/images` | Sincroniza cache (se vazio) e lista imagens |
| POST | `/api/sources/{slug}/refresh` | Rebaixa cache da fonte |
| GET | `/api/images/{slug}/{file}` | Serve imagem do cache |
| GET | `/api/favorites/folders` | Lista subpastas |
| POST | `/api/favorites/folders` | Cria subpasta |
| DELETE | `/api/favorites/folders/{pasta}` | Remove subpasta |
| GET | `/api/favorites/folders/{pasta}/images` | Imagens da subpasta |
| POST | `/api/favorites` | Copia `{ folder, slug, filename }` |
| DELETE | `/api/favorites/{pasta}/{arquivo}` | Remove favorito |
| GET | `/api/favorites/images/{pasta}/{arquivo}` | Serve imagem favorita |
| GET | `/api/monitors` | Desktops Plasma |
| POST | `/api/apply` | Aplica imagem (`from_favorites: true` opcional) |
| POST | `/api/apply/crop` | Crop + aplica (PNG) |

## Estrutura (backend — padrão portfolio-api)

```
backend/
├── main.py
├── env.py
├── database/
│   ├── __init__.py
│   └── sources.py
├── models/
├── routers/
├── services/
│   ├── cache.py
│   ├── favorites.py
│   ├── sources.py
│   ├── plasma.py
│   └── images.py
├── cache/            # runtime (gitignored)
├── favorites/        # cópias permanentes (gitignored)
└── data/
    └── sources.db
```

## Próximos passos

- [ ] Crop interativo no browser (Cropper.js)
- [ ] Suporte GIF animado
- [ ] Lock screen
- [ ] Build produção (frontend estático servido pelo FastAPI)
