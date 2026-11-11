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
    r = client.post("/auth/register", json={"email": "ana@example.com", "nombre": "Ana", "password": "s"})
    assert r.status_code == 422
