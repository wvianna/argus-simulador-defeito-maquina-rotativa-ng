#!/usr/bin/env bash
#
# stop.sh — Para os serviços do Argus (Simulador de Defeito de Máquina Rotativa).
#
# Uso:
#   ./stop.sh             # para e remove os contêineres (mantém o volume do banco)
#   ./stop.sh --volumes   # também remove o volume (apaga todos os dados persistidos)
#   ./stop.sh -v          # atalho para --volumes
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

VOLUMES=0
for arg in "$@"; do
  case "$arg" in
    --volumes | -v) VOLUMES=1 ;;
    --help | -h)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *) echo "Argumento desconhecido: $arg (use --help)"; exit 1 ;;
  esac
done

command -v docker >/dev/null 2>&1 || { echo "ERRO: docker não encontrado."; exit 1; }

down_args=()
if [ "$VOLUMES" = "1" ]; then
  down_args+=("-v")
  echo "==> Parando e removendo contêineres E o volume de dados..."
else
  echo "==> Parando e removendo contêineres (dados do banco preservados no volume)..."
fi

# `docker compose down` é idempotente; repete uma vez se sobrar contêiner/rede
# do projeto (parada lenta do frontend/nginx pode atrasar a remoção).
docker compose down "${down_args[@]}" || true
if docker compose ps -q 2>/dev/null | grep -q .; then
  echo "==> contêineres ainda presentes; repetindo o down..."
  docker compose down "${down_args[@]}"
fi

if [ "$VOLUMES" = "1" ]; then
  echo "==> Pronto. Dados do banco foram apagados (use ./start.sh para subir de novo)."
else
  echo "==> Pronto. Para subir novamente: ./start.sh"
fi
