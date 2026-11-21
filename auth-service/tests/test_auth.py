import jwt

# Usuario de prueba
USER = {"email": "ana@example.com", "nombre": "Ana", "password": "supersecreta1"}


# Comprueba que el endpoint GET /health funciona correctamente
def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


# Comprueba que un usuario se registra con éxito y que no se devuelve su contraseña en la respuesta
def test_register_exito(client):

    r = client.post("/auth/register", json=USER)
    assert r.status_code == 201
    body = r.json()

    # email recibido coincide con el que se manda
    assert body["email"] == USER["email"]

    assert body["rol"] == "encargado"

    # en la respuesta no aparece ninguna contraseña
    assert "password" not in body and "password_hash" not in body


# Comprueba que un usuario puede iniciar sesión
def test_login(client):

    # Crea el usuario
    client.post("/auth/register", json=USER)

    # Petición
    r = client.post("/auth/login",json={"email": USER["email"], "password": USER["password"]},)
    assert r.status_code == 200

    # Decodifica el token
    datos = jwt.decode(r.json()["access_token"], "secreto-de-tests", algorithms=["HS256"])
    assert datos["email"] == USER["email"]
    assert datos["rol"] == "encargado"


# Comprueba que no se registran dos usuarios con el mismo correo
def test_register_email_duplicado(client):

    # Crea el usuario
    client.post("/auth/register", json=USER).status_code == 201

    #Lo vuelve a crear
    r = client.post("/auth/register", json=USER)
    assert r.status_code == 409


# Comprueba el inicio de sesión con una contraseña incorrecta
def test_login_password_incorrecta(client):

    # Crea el usuario
    client.post("/auth/register", json=USER)
    
    # Petición
    r = client.post("/auth/login",json={"email": USER["email"], "password": "contraseña_incorrecta"},)
    assert r.status_code == 401


# Comprueba el intento de inicio de sesión con un usuario que no esté registrado
def test_login_usuario_inexistente(client):
    # Petición
    r = client.post("/auth/login",json={"email": USER["email"], "password": USER["password"]},)
    assert r.status_code == 401


# Comprueba un intento de registro con una contraseña que no llega al mínimo de carácteres (no cumple el formato)
def test_register_password_corta(client):
    # Intenta crear el usuario
    r = client.post("/auth/register", json={"email": USER["email"], "nombre": USER["nombre"], "password": "s"})
    assert r.status_code == 422


# Comprueba que se registre un usuario con rol encargado aunque se indique su rol es admin (desde el endpoint publico solo se pueden crear encargados)
def test_register_ignora_rol(client):
    # Intenta crear el usuario
    r = client.post("/auth/register", json={"email": USER["email"], "nombre": USER["nombre"], "password": USER["password"], "rol": "admin"})
    assert r.status_code == 201

    # El servidor ignora ese campo
    assert r.json()["rol"] == "encargado"       



# Función auxiliar: registra a USER y devuelve su token
def obtener_token(client):

    client.post("/auth/register", json=USER)
    r = client.post("/auth/login",json={"email": USER["email"], "password": USER["password"]},)
    return r.json()["access_token"]


# Comprueba que el usuario devuelto es el dueño del token y que su rol es encargado
def test_me_con_token_valido(client):
    token = obtener_token(client)

    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

    assert r.json()["email"] == USER["email"]
    assert r.json()["rol"] == "encargado"


# Comprueba que, al no mandar la cabecera, da error la funcion get_usuario_actual
def test_me_sin_token(client):
    assert client.get("/auth/me").status_code == 401


# Comprueba que de error cuando se inyecta un código inválido
def test_me_token_incorrecto(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer esto-no-es-un-jwt"})
    assert r.status_code == 401


# Comprueba que de error cuando se fabrica un token con otro secreto
def test_me_token_firmado_con_otro_secreto(client):

    client.post("/auth/register", json=USER)

    # Un token bien formado, pero firmado por un atacante con otro secreto
    falso = jwt.encode({"sub": "1", "rol": "admin"}, "otro-secreto", algorithm="HS256")
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {falso}"})
    assert r.status_code == 401