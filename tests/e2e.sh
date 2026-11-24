#!/usr/bin/env bash
# Prueba de extremo a extremo: requiere el sistema levantado con docker compose
set -euo pipefail

AUTH=http://localhost:8001
GEO=http://localhost:8002
TREAT=http://localhost:8003
EMAIL="e2e-$(date +%s)@example.com"   # único en cada ejecución
PASSWORD="supersecreta1"

ok()    { echo "OK    $1"; }
fallo() { echo "FALLO $1"; exit 1; }

# Devuelve solo el código HTTP de una petición
codigo() { curl -s -o /dev/null -w '%{http_code}' "$@"; }

echo "== Servicios arriba =="
[ "$(codigo $AUTH/health)" = 200 ]  || fallo "auth-service no responde"
[ "$(codigo $GEO/health)" = 200 ]   || fallo "geo-service no responde"
[ "$(codigo $TREAT/health)" = 200 ] || fallo "treatments-service no responde"
ok "los tres servicios responden en /health"

echo "== Autenticación =="
c=$(codigo -X POST $AUTH/auth/register -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"nombre\":\"E2E\",\"password\":\"$PASSWORD\"}")
[ "$c" = 201 ] || fallo "registro: esperado 201, recibido $c"
ok "registro de usuario (201)"

TOKEN=$(curl -sf -X POST $AUTH/auth/login -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  | python3 -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')
[ -n "$TOKEN" ] || fallo "login: no se recibió token"
ok "login y obtención del token"

echo "== Comunicación entre servicios =="
c=$(codigo $GEO/parcelas)
[ "$c" = 401 ] || fallo "parcelas sin token: esperado 401, recibido $c"
ok "geo-service rechaza peticiones sin token (401)"

c=$(codigo -X POST $GEO/parcelas -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"nombre":"Olivar e2e"}')
[ "$c" = 201 ] || fallo "crear parcela: esperado 201, recibido $c"
ok "geo-service acepta el token de auth-service y crea la parcela (201)"

curl -sf $GEO/parcelas -H "Authorization: Bearer $TOKEN" | grep -q "Olivar e2e" \
  || fallo "la parcela creada no aparece en el listado"
ok "la parcela aparece en el listado"

echo "== Aislamiento de redes =="
# Ningún servicio debe poder ni encontrar las bases de datos de los demás.
# $1 = servicio desde el que se prueba, $2 = nombre que se intenta resolver
no_resuelve() {
  if docker compose exec -T "$1" python -c \
    "import socket; socket.gethostbyname('$2')" 2>/dev/null; then
    fallo "$1 puede ver $2: las redes no están aisladas"
  fi
  ok "$1 no puede alcanzar $2"
}

no_resuelve auth-service geo-db
no_resuelve auth-service treatments-db
no_resuelve geo-service auth-db
no_resuelve geo-service treatments-db
no_resuelve treatments-service auth-db
no_resuelve treatments-service geo-db

echo "Todas las pruebas de integración han pasado"
