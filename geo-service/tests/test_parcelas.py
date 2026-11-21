from datetime import datetime, timedelta, timezone

import jwt

SECRETO = "secreto-de-tests"

# Parcela de prueba
PARCELA = {"nombre": "Olivar norte", "descripcion": "Parcela de olivos"}

# Función auxiliar para fabricar un token (imita lo que harái auth-service)
def token(user_id=1, rol="encargado", encargado_id=None, secreto=SECRETO):

    payload = {
        "sub": str(user_id),
        "email": f"usuario{user_id}@example.com",
        "rol": rol,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }

    if encargado_id is not None:
        payload["encargado_id"] = encargado_id

    return jwt.encode(payload, secreto, algorithm="HS256")


# Función auxiliar que devuelve la cabecera Authorization... con el token
def auth(**kwargs):
    return {"Authorization": f"Bearer {token(**kwargs)}"}

# Comprueba que el endpoint GET /health funciona correctamente
def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

# Test para intentar crear una parcela sin indicar el token del usuario que la crea
def test_crear_parcela_sin_token(client):
    assert client.post("/parcelas", json=PARCELA).status_code == 401


# Test para intentar crear una parcela con un token incorrecto
def test_token_firmado_con_otro_secreto(client):
    r = client.post("/parcelas", json=PARCELA, headers=auth(secreto="otro-secreto"))
    assert r.status_code == 401


# Test para intentar crear una parcela un usuario sin permiso
def test_trabajador_no_puede_crear_parcelas(client):
    r = client.post(
        "/parcelas", json=PARCELA, headers=auth(user_id=5, rol="trabajador", encargado_id=1)
    )
    assert r.status_code == 403


# Test para comprobar que un encargado puede crear una parcela
def test_encargado_crea_parcela(client):
    r = client.post("/parcelas", json=PARCELA, headers=auth(user_id=1))
   
    assert r.status_code == 201
    assert r.json()["nombre"] == PARCELA["nombre"]
    assert r.json()["propietario_id"] == 1


# Test para intentar mandar otro propietario
def test_el_cliente_no_elige_el_propietario(client):
    r = client.post(
        "/parcelas", json={**PARCELA, "propietario_id": 99}, headers=auth(user_id=1)
    )
    assert r.status_code == 201
    assert r.json()["propietario_id"] == 1


# Test para comprobar que un encargado solo ve sus parcelas
def test_encargado_solo_ve_sus_parcelas(client):
    client.post("/parcelas", json=PARCELA, headers=auth(user_id=1))
    client.post("/parcelas", json=PARCELA, headers=auth(user_id=2))

    r = client.get("/parcelas", headers=auth(user_id=1))
    assert r.status_code == 200
    assert [p["propietario_id"] for p in r.json()] == [1]


# Test para comprobar que un trabajador solo ve las parcelas de su encargado asociado
def test_trabajador_ve_las_parcelas_de_su_encargado(client):
    client.post("/parcelas", json=PARCELA, headers=auth(user_id=1))
    client.post("/parcelas", json=PARCELA, headers=auth(user_id=2))

    r = client.get(
        "/parcelas", headers=auth(user_id=5, rol="trabajador", encargado_id=2)
    )
    assert [p["propietario_id"] for p in r.json()] == [2]


# Test para comprobar que el admin puede ver todas las parcelas
def test_admin_ve_todas_las_parcelas(client):
    client.post("/parcelas", json=PARCELA, headers=auth(user_id=1))
    client.post("/parcelas", json=PARCELA, headers=auth(user_id=2))

    r = client.get("/parcelas", headers=auth(user_id=9, rol="admin"))
    assert len(r.json()) == 2
