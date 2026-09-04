#!/usr/bin/env bash
#
# start.sh — Sobe o Argus (Simulador de Defeito de Máquina Rotativa) via Docker Compose.
#
# Faz o setup do ambiente quando necessário:
#   1. valida docker / docker compose;
#   2. cria o arquivo .env a partir de .env.example (se não existir);
#   3. constrói as imagens apenas se ainda não existirem (ou com --build);
#   4. sobe os serviços db, backend e frontend;
#   5. aguarda o health do back-end;
#   6. cria um Ponto demo na hierarquia (Planta>Área>Máquina>Ponto) se não houver nenhum.
#
# Uso:
#   ./start.sh            # sobe usando as imagens já construídas
#   ./start.sh --build    # força a reconstrução das imagens antes de subir
#   ./start.sh --no-seed  # não cria o Ponto demo automaticamente
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

FORCE_BUILD=0
SEED=1
for arg in "$@"; do
  case "$arg" in
    --build) FORCE_BUILD=1 ;;
    --no-seed) SEED=0 ;;
    --help | -h)
      sed -n '2,20p' "$0"
      exit 0
      ;;
    *) echo "Argumento desconhecido: $arg (use --help)"; exit 1 ;;
  esac
done

echo "==> Argus — Simulador de Defeito de Máquina Rotativa"

# 1) Pré-requisitos -----------------------------------------------------------
command -v docker >/dev/null 2>&1 || { echo "ERRO: docker não encontrado. Instale o Docker."; exit 1; }
if ! docker compose version >/dev/null 2>&1; then
  echo "ERRO: comando 'docker compose' (v2) não disponível."
  exit 1
fi

# 2) Arquivo de ambiente ------------------------------------------------------
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "=> .env criado a partir de .env.example (ajuste os valores se necessário)."
  else
    echo "AVISO: .env.example não encontrado — usando os valores padrão do docker-compose."
  fi
else
  echo "=> .env já existe (usando configurações atuais)."
fi

# Carrega as variáveis do .env (POSTGRES_*, ARGUS_*, etc.) para os passos seguintes.
set -a
# shellcheck disable=SC1091
[ -f .env ] && . ./.env
set +a

POSTGRES_USER="${POSTGRES_USER:-argus}"
POSTGRES_DB="${POSTGRES_DB:-argus}"

# 3) Imagens ------------------------------------------------------------------
if [ "$FORCE_BUILD" = "1" ]; then
  echo "=> --build informado: reconstruindo imagens..."
  docker compose build
else
  missing=0
  while IFS= read -r img; do
    [ -z "$img" ] && continue
    if ! docker image inspect "$img" >/dev/null 2>&1; then
      missing=1
    fi
  done < <(docker compose config --images)

  if [ "$missing" = "1" ]; then
    echo "=> alguma imagem ainda não existe: construindo (primeira execução)..."
    docker compose build
  else
    echo "=> imagens já presentes (use --build para reconstruir)."
  fi
fi

# 4) Subir serviços -----------------------------------------------------------
echo "=> subindo serviços (db, backend, frontend)..."
docker compose up -d

# 5) Aguardar health do back-end ----------------------------------------------
echo -n "=> aguardando o back-end responder (http://localhost:8000/health)"
ok=0
if command -v curl >/dev/null 2>&1; then
  for _ in $(seq 1 60); do
    if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
      ok=1
      break
    fi
    echo -n "."
    sleep 1
  done
else
  echo " (curl não encontrado — aguardando 10s)"
  sleep 10
  ok=1
fi
echo
if [ "$ok" != "1" ]; then
  echo "ERRO: o back-end não respondeu em 60s. Diagnóstico:"
  echo "  docker compose logs --tail=50 backend"
  exit 1
fi
echo "=> back-end saudável."

# 6) Seed do Ponto demo --------------------------------------------------------
if [ "$SEED" = "1" ]; then
  count=$(docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA \
    -c "SELECT count(*) FROM pontos;" 2>/dev/null || echo "0")
  count=$(echo "$count" | tr -d '[:space:]')

  if [ "${count:-0}" = "0" ]; then
    echo "=> nenhum Ponto cadastrado: criando hierarquia demo (Planta>Área>Máquina>Ponto)..."
    ponto_id=$(docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA \
      -c "WITH p AS (INSERT INTO plantas(id,nome) VALUES (gen_random_uuid(),'Planta Demo') RETURNING id), \
                 a AS (INSERT INTO areas(id,planta_id,nome) SELECT gen_random_uuid(), id, 'Área Demo' FROM p RETURNING id), \
                 m AS (INSERT INTO maquinas(id,area_id,nome) SELECT gen_random_uuid(), id, 'Máquina Demo' FROM a RETURNING id) \
           INSERT INTO pontos(id,maquina_id,nome) SELECT gen_random_uuid(), id, 'Ponto Demo' FROM m RETURNING id;" | head -n 1)
    ponto_id=$(echo "$ponto_id" | tr -d '[:space:]')
    echo "=> Ponto demo criado: $ponto_id"
  else
    echo "=> já existem Ponto(s) cadastrado(s); nenhum seed necessário."
    ponto_id=$(docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA \
      -c "SELECT id FROM pontos ORDER BY nome LIMIT 1;" 2>/dev/null | tr -d '[:space:]' || true)
  fi
else
  echo "=> --no-seed informado: nenhum Ponto demo foi criado."
  ponto_id=""
fi

# 7) Resumo --------------------------------------------------------------------
echo
echo "==> Ambiente pronto!"
echo "   Painel web  : http://localhost:5173"
echo "   API         : http://localhost:8000"
echo "   OpenAPI     : http://localhost:8000/docs"
if [ -n "$ponto_id" ]; then
  echo "   Ponto (use no painel): $ponto_id"
fi
echo
echo "Para parar: ./stop.sh   |   Para remover também os dados do banco: ./stop.sh --volumes"
