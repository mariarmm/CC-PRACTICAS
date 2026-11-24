# Hito 2 — Empaquetado Cloud Native, Entorno Local e Integración Continua (CI)

En este hito se implementa la arquitectura de microservicios definida para el proyecto de gestión agrícola.

El sistema está compuesto por tres microservicios:

- `auth-service`: gestión de usuarios, autenticación y autorización.
- `geo-service`: gestión de parcelas agrícolas.
- `treatments-service`: gestión de tratamientos.

Cada microservicio dispone de su propia base de datos y se ejecuta de forma independiente mediante contenedores Docker.

La API se prueba mediante la documentación interactiva de FastAPI (`/docs`) o mediante herramientas como Postman y `curl`, sin necesidad de una interfaz gráfica.

---

## Arquitectura

| Servicio | Responsabilidad | Base de datos | Puerto |
|---|---|---|---|
| auth-service | Registro, login y emisión de tokens JWT con el rol del usuario | auth-db (PostgreSQL) | 8001 |
| geo-service | Gestión de parcelas | geo-db (PostgreSQL) | 8002 |
| treatments-service | Gestión de tratamientos | treatments-db (PostgreSQL) | 8003 |


- Cada microservicio tiene **su propia base de datos**, en un contenedor y un volumen separados. Si cambia un servicio, solo se toca su base de datos.

- La comunicación con el cliente es una API REST sobre HTTP con JSON. No hay interfaz gráfica: la API se prueba con la documentación interactiva que genera FastAPI (`/docs`) o con herramientas como Postman o `curl`.

- Los servicios están hechos con **Python 3.12, FastAPI y SQLAlchemy**. Las bases de datos usan la imagen oficial `postgres:16-alpine`.

---

## Estructura del repositorio

```text
CC-PRACTICAS/
├── .github/workflows/ci.yml    # integración continua
├── auth-service/               # microservicio de autenticación
├── geo-service/                # microservicio geográfico
├── treatments-service/         # microservicio de tratamientos
├── tests/e2e.sh                # pruebas de integración de extremo a extremo
├── hitos/                      # documentación de los hitos
├── compose.yaml                # orquestación local de todo el sistema
├── .env.example                # plantilla de variables de entorno (sin credenciales)
├── ruff.toml                   # configuración del linter
└── README.md
```

---

# Microservicios

## `auth-service`: autenticación y roles

Gestiona los usuarios y emite los tokens JWT con los que se accede al resto del sistema.

### Endpoints

| Método | Endpoint | Descripción | Acceso |
|---|---|---|---|
| POST | `/auth/register` | Registra un usuario. Siempre se crea con el rol `encargado`; el cliente no puede elegir el rol | Público |
| POST | `/auth/login` | Comprueba las credenciales y devuelve un token JWT | Público |
| GET | `/auth/me` | Devuelve los datos del usuario dueño del token | Token |
| GET | `/health` | Indica que el servicio está activo | Público |

### Roles y JWT

Existen tres roles:

- `admin`: administrador del sistema.
- `encargado`: gestiona su finca.
- `trabajador`: registra tratamientos.

El token JWT contiene el id del usuario, su email, su rol, las fechas de emisión y caducidad y, solo en el caso de los trabajadores, el id de su encargado (encargado_id).

Los demás servicios leen estos datos directamente del token, sin consultar a `auth-service`.

### Persistencia

La tabla `usuarios` guarda el email (único), el nombre, el **hash** de la contraseña (nunca la contraseña en texto plano), el rol, el encargado (solo para trabajadores) y la fecha de creación.

---

## `geo-service`: parcelas

Gestiona las parcelas de las explotaciones.

**No consulta a `auth-service`**: valida por sí mismo la firma y la caducidad del token con el secreto compartido.

### Endpoints

| Método | Endpoint | Descripción | Acceso |
|---|---|---|---|
| POST | `/parcelas` | Crea una parcela. El id del propietario se obtiene del token, no de la petición | `admin`, `encargado` |
| GET | `/parcelas` | Lista parcelas según el rol: el encargado ve las suyas, el trabajador las de su encargado y el admin todas | Token |
| GET | `/health` | Indica que el servicio está activo | Público |

### Persistencia

La tabla `parcelas` guarda el nombre, la descripción, el id del propietario y la fecha de creación.

propietario_id **no es una clave foránea**: los usuarios viven en otra base de datos y cada microservicio solo conoce la suya.

---

## `treatments-service`: tratamientos

Este servicio está preparado pero sin funcionalidad todavía. Tiene su propio
Dockerfile, su base de datos PostgreSQL (`treatments-db`), su red aislada, su
volumen y su configuración en el compose, y se valida y publica con el CI igual
que los demás. De momento solo expone:

| Método | Endpoint | Descripción | Acceso |
|---|---|---|---|
| GET | `/health` | Indica que el servicio está activo | Público |

Está previsto que registre los tratamientos aplicados a cada planta y permita
consultar su historial. Ya incluye `security.py` y `dependencies.py` para validar tokens, igual que `geo-service`, de modo que los endpoints que se añadan podrán protegerse con los roles existentes. He decidido dejar la infraestructura para centrarme en los siguientes hitos en la implementación y en las pruebas.

---

## Estructura común de los servicios

Los tres servicios tienen la misma organización de archivos:

```text
<servicio>/
├── app/
│   ├── main.py          # aplicación FastAPI y endpoints
│   ├── config.py        # configuración leída de variables de entorno
│   ├── database.py      # conexión a la base de datos y sesiones
│   ├── models.py        # tablas
│   ├── schemas.py       # contrato de la API: JSON que se acepta y se devuelve
│   ├── security.py      # funciones de seguridad (contraseñas y tokens)
│   ├── dependencies.py  # identificación del usuario y comprobación de roles
│   └── roles.py         # roles permitidos
├── tests/
│   ├── conftest.py      # configuración común de las pruebas
│   └── test_*.py        # pruebas de la API
├── Dockerfile            # imagen del servicio
├── .dockerignore         # qué no se copia a la imagen
├── requirements.txt      # dependencias de producción (versiones fijadas)
├── requirements-dev.txt  # dependencias de desarrollo (tests y linter)
└── pytest.ini            # configuración de pytest
```

### Contenido de `app/`

| Archivo | Propósito |
|---|---|
| `main.py` | Crea la aplicación, crea las tablas al arrancar y define los endpoints |
| `config.py` | Lee `DATABASE_URL` y `JWT_SECRET` del entorno. Si falta una variable obligatoria, la aplicación no arranca |
| `database.py` | Crea la conexión (*engine*), la fábrica de sesiones y la dependencia `get_db`, que da una sesión a cada petición y la cierra al terminar |
| `models.py` | Define las tablas de la base de datos |
| `schemas.py` | Valida los datos de entrada y filtra los de salida |
| `security.py` | En `auth-service`, cifra contraseñas con bcrypt y crea y valida tokens. En `geo-service` y `treatments-service` solo se validan tokens, porque no los emiten |
| `dependencies.py` | Lee el token de la cabecera `Authorization`, identifica al usuario y comprueba su rol: 401 si no hay token válido, 403 si el rol no basta |
| `roles.py` | Lista cerrada de roles (`admin`, `encargado`, `trabajador`) |

La principal diferencia de contenido entre los microservicios, aparte de la funcionalidad de cada uno, está en cómo identifican al usuario:

- `auth-service` busca al usuario en su base de datos en cada petición, por lo que un usuario borrado deja de poder usar su token.
- `geo-service` y `treatments-service` leen los datos del usuario directamente del token, sin consultar ninguna base de datos. Así funciona aunque `auth-service` esté caído, a costa de que un token siga siendo válido hasta que caduque.

Archivos como `config.py`, `database.py` y `roles.py` están **duplicados a propósito** en los tres servicios. Compartirlos obligaría a los servicios a desplegarse juntos, lo que rompería su independencia.

---

## Pruebas de los microservicios

Cada servicio dispone de sus propias pruebas automáticas.

| Archivo | Propósito |
|---|---|
| `conftest.py` | Prepara el entorno de pruebas. Fija `DATABASE_URL` (SQLite en memoria) y `JWT_SECRET` **antes** de importar la aplicación, porque `config.py` los lee al importarse. Define la fixture `client`, que borra y recrea las tablas antes de cada prueba y entrega un cliente HTTP de pruebas, de modo que cada test parte de una base de datos vacía y ninguno depende de otro |
| `test_auth.py` (`auth-service`) | Pruebas de la API de autenticación |
| `test_parcelas.py` (`geo-service`) | Pruebas de la API de parcelas y de los permisos por rol |
| `test_treatments.py` (`treatments-service`) | Pruebas de la API de tratamientos y de los permisos por rol |

---

# Ejecución del proyecto

## Requisitos

Se necesita Docker con el plugin Compose.

Para el script de pruebas de extremo a extremo son necesarios además `curl` y `python3`.

## Variables de entorno

Se definen en un archivo `.env` (no versionado) a partir de `.env.example`.

| Variable | Uso |
|---|---|
| `AUTH_DB_NAME`, `AUTH_DB_USER`, `AUTH_DB_PASSWORD` | Base de datos, usuario y contraseña de `auth-db`. PostgreSQL los crea la primera vez que arranca |
| `GEO_DB_NAME`, `GEO_DB_USER`, `GEO_DB_PASSWORD` | Lo mismo para `geo-db` |
| `TREAT_DB_NAME`, `TREAT_DB_USER`, `TREAT_DB_PASSWORD` | Lo mismo para `treatments-db` |
| `JWT_SECRET` | Secreto con el que `auth-service` firma los tokens y `geo-service` y `treatments-service` los valida |

`.env.example` contiene solo valores de relleno y sí se versiona. El `.env` real, con las credenciales, está en `.gitignore`.


## Arranque

```bash
cp .env.example .env
# Sustituir los valores "cambiame" por los valores correspondientes

docker compose up --build
```

Una vez arrancado, la documentación interactiva de cada servicio está en:

- `auth-service`: `http://localhost:8001/docs`
- `geo-service`: `http://localhost:8002/docs`
- `treatments-service`: `http://localhost:8003/docs`

---

## Cómo usar la API desde `/docs`

1. En `auth-service`, ejecuta `POST /auth/register` y después `POST /auth/login`.
   Copia el valor de `access_token` de la respuesta.

2. En `geo-service`, pulsa el botón **Authorize** (arriba a la derecha), pega el token (solo el token, sin la palabra `Bearer`) y ya puedes usar `POST /parcelas` y `GET /parcelas`.

3. En `treatments-service`, ejecuta `GET /health`.

También se puede utilizar Postman o `curl` para realizar las mismas peticiones HTTP.

---

# Contenerización

## Dockerfiles

Un `Dockerfile` contiene las instrucciones para construir la imagen de un servicio, es decir, el paquete que contiene todo lo necesario para ejecutarlo dentro de un contenedor.

Cada microservicio tiene el suyo, en su propia carpeta, y los tres siguen la misma estructura.

### Qué hace el Dockerfile, paso a paso

La imagen se construye en **dos etapas**:

1. **Etapa `builder` (preparación).** Parte de una imagen de Python, copia el archivo `requirements.txt` e instala las librerías que necesita el servicio.

2. **Etapa `runner` (imagen final).** Parte de nuevo de una imagen de Python limpia y:
   - crea un usuario sin privilegios llamado `app`,
   - copia desde `builder` las librerías ya instaladas,
   - copia el código del servicio,
   - indica el puerto en el que escucha, una comprobación de salud y el comando que arranca la aplicación.

Solo la imagen final se utiliza. Todo lo de la etapa `builder` se descarta.

### Decisiones y por qué se tomaron

| Decisión | Qué se hace | Para qué sirve |
|---|---|---|
| **Imagen base** | Uso `python:3.12-slim` | Es una versión de Python reducida, con solo lo necesario. Pesa mucho menos que la completa y se descarga más rápido. Existe otra opción aún más ligera, Alpine, pero algunas de las librerías que se utilizan (`bcrypt`, `psycopg`) vienen ya preparadas para el sistema que usa `slim`. En Alpine habría que prepararlas durante la construcción, lo que complica y alarga el proceso |
| **Dos etapas** | Separar la preparación de la ejecución | Las herramientas que solo hacen falta para construir se quedan fuera de la imagen final. Así la imagen contiene únicamente lo necesario para ejecutar el servicio |
| **Usuario sin privilegios** | El programa se ejecuta con el usuario `app`, no como administrador (`root`) | Si alguien consiguiera aprovechar un fallo de la aplicación, tendría muy pocos permisos dentro del contenedor. Es el principio de mínimo privilegio |
| **Orden de copia** | Primero se copia `requirements.txt` y se instalan las librerías; el código se copia al final | Docker guarda cada paso de la construcción y reutiliza los que no han cambiado. Si solo se cambia el código, no hace falta reinstalar las librerías y la construcción tarda segundos |
| **Versiones fijadas** | La imagen base y las librerías tienen una versión concreta | Cada construcción da el mismo resultado, y la imagen no cambia por sorpresa |
| **`.dockerignore`** | Lista de archivos que no se copian a la imagen (tests, cachés, `.env`, bases de datos locales...) | La imagen es más pequeña y las contraseñas locales nunca pueden acabar dentro de ella |
| **Puerto** | `EXPOSE 8000` | Indica en qué puerto escucha la aplicación. Qué puertos se abren hacia el exterior se decide en el `compose.yaml` |
| **Comprobación de salud** | Cada 10 segundos, Docker pregunta al servicio por `/health` si está bien | Docker Compose la usa para saber cuándo un servicio está listo. Se hace con Python porque la imagen `slim` no incluye `curl` y así no hay que instalar nada más |

**Tamaño.** Las imágenes finales ocupan unos 288 MB (`auth-service`) y 283 MB (`geo-service` y `treatments-service`). Las imágenes intermedias de la etapa builder ocupan 301 MB para auth-service y 296 MB para geo-service y treatments-service. Aunque la reducción de tamaño no es tan grande en este caso, el uso de multi-stage builds permite mantener la imagen final separada de las herramientas y dependencias utilizadas únicamente durante la construcción.

---

# Orquestación con Docker Compose

Docker Compose permite levantar todos los contenedores a la vez a partir de un único archivo, `compose.yaml`, que está en la raíz del repositorio.

Con un solo comando (`docker compose up --build`) se crean **seis contenedores**, cuatro redes y tres volúmenes.

| Elemento | Cómo está hecho |
|---|---|
| **Servicios** | `auth-service`, `auth-db`, `geo-service` , `geo-db` , `treatments-service` y `treatments-db` |
| **Bases de datos** | Imagen oficial `postgres:16-alpine`; no se crea ninguna imagen propia |
| **Una base de datos por servicio** | Cada servicio solo conoce la suya. Ninguna tabla se comparte |
| **Redes aisladas** | `auth-net` , `geo-net` y `treatments-net` unen cada servicio únicamente con su base de datos, y no tienen salida a internet. `backend-net` conecta los servicios entre sí (para la comunicación entre servicios de los próximos hitos) |
| **Volúmenes** | `auth-db-data` , `geo-db-data` y `treatments-db-data` son carpetas gestionadas por Docker donde PostgreSQL guarda sus datos. Los datos se conservan aunque se borren y se vuelvan a crear los contenedores |
| **Orden de arranque** | Cada servicio espera a que su base de datos esté lista antes de arrancar |
| **Configuración** | Las contraseñas y el resto de variables se leen del archivo `.env`. Si falta alguna obligatoria, Compose avisa y no arranca |
| **Puertos hacia el exterior** | El 8001 (`auth-service`), el 8002 (`geo-service`) y el 8003 (`treatments-service`). Las bases de datos no se pueden alcanzar desde fuera |
| **Reinicio automático** | Si un contenedor se cae, Docker lo vuelve a arrancar |

### Aislamiento de redes

Ningún servicio comparte red con la base de datos de otro servicio. Cada base de datos solo es accesible para su propio servicio.

El script `tests/e2e.sh` lo comprueba.

### Persistencia

Se puede parar el sistema con:

```bash
docker compose down
```

y volver a levantarlo con:

```bash
docker compose up
```

sin perder los datos.

Para borrar también los volúmenes:

```bash
docker compose down -v
```

---

# Seguridad

- **Contraseñas cifradas**: nunca se guarda la contraseña, solo su *hash*, un resultado del que no se puede recuperar el original. Se calcula con bcrypt.

- **Error genérico en el login**: se responde lo mismo si el email no existe o si la contraseña es incorrecta, para no revelar qué emails están registrados.

- **Respuestas sin datos sensibles**: las respuestas de la API nunca incluyen el hash de la contraseña.

- **Tokens firmados y con caducidad**: nadie puede modificar un token sin conocer el secreto con el que se firma. Un token se puede leer, pero no manipular, por lo que no contiene datos sensibles.

- **El rol y el propietario salen del token**, no de lo que envíe el cliente. Un usuario no puede registrarse con un rol que no le corresponde ni crear parcelas a nombre de otro.

- **Sin credenciales en el código ni en las imágenes**: las contraseñas y el secreto llegan por variables de entorno. El archivo `.env` real no se sube a GitHub (`.gitignore`) ni entra en las imágenes (`.dockerignore`).

- **Contenedores sin permisos de administrador**, y bases de datos en redes internas, sin puertos accesibles desde fuera.

---

# Pruebas

Las pruebas automáticas de cada servicio y el script de extremo a extremo se explican en la sección de microservicios.

## Pruebas de cada servicio

Para ejecutarlas en local:

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r auth-service/requirements-dev.txt -r geo-service/requirements-dev.txt -r treatments-service/requirements-dev.txt

# Pruebas y revisión de código de cada servicio
cd auth-service && pytest && ruff check . && cd ..
cd geo-service && pytest && ruff check . && cd ..
cd treatments-service && pytest && ruff check . && cd ..

```

## Prueba de extremo a extremo

Necesita el sistema levantado:

```bash
docker compose up -d --build --wait
./tests/e2e.sh
```

La prueba de extremo a extremo comprueba el registro, login, creación de parcelas con el token, que el servicio de tratamientos esté activo y el aislamiento de redes.

---

# Integración continua

La integración continua comprueba automáticamente el proyecto cada vez que cambia.

El workflow `.github/workflows/ci.yml` se ejecuta en GitHub con cada `push` y con cada `pull_request` hacia `main`.

Se trabaja en ramas (`feature/...`) que se llevan a `main` mediante Pull Request, de modo que cada cambio pasa por estas comprobaciones antes de entrar.

## Flujo del pipeline

```text
lint ──► test ──► integration ──► publish
```

## Jobs

| Job | Qué hace |
|---|---|
| `lint` | Revisa el estilo y los errores comunes para cada servicio. **hadolint** revisa los Dockerfiles y **ruff** revisa el código Python |
| `test` | Ejecuta las pruebas automáticas (`pytest`) de cada servicio |
| `integration` | Levanta todo el sistema con Docker Compose y ejecuta `tests/e2e.sh`, que comprueba que los servicios funcionan juntos. Si algo falla, muestra los logs; al terminar, lo apaga y lo limpia |
| `publish` | Construye la imagen de cada servicio y la sube a **GitHub Container Registry**. Solo se ejecuta cuando el cambio llega a `main`, nunca en un Pull Request |

### Detalles importantes

- **Si algo falla, no se publica nada**, porque `publish` solo se ejecuta si todos los trabajos anteriores han pasado.

- **Etiquetas de las imágenes**: cada imagen se publica con la etiqueta `latest` (la última versión) y con una etiqueta `sha-xxxxxxx`, que indica el commit exacto del que procede. Así se sabe siempre qué código contiene cada imagen.

- **Límite de tiempo** en cada job, para que uno atascado no consuma minutos durante horas.

- El job de integración usa `.env.example`, así que además comprueba que esa plantilla de variables está completa.

## Imágenes publicadas

Cada cambio que llega a `main` y pasa todas las pruebas publica las imágenes en **GitHub Container Registry**, etiquetadas con `latest` y con el hash del commit (`sha-xxxxxxx`).

```bash
docker pull ghcr.io/mariarmm/agrotrace-auth-service:latest
docker pull ghcr.io/mariarmm/agrotrace-geo-service:latest
docker pull ghcr.io/mariarmm/agrotrace-treatments-service:latest
```

---

# Alcance actual y trabajo futuro

El hito 2 se centra en el empaquetado, la orquestación y el CI, por lo que se
han implementado solo los endpoints imprescindibles para demostrar el
funcionamiento de los tres microservicios. El hito 1 describe una API más amplia. De ella **ya existe**: registro, login, consulta de usuario, y creación y listado de parcelas. **Queda pendiente**:

- **Servicio de tratamientos funcional** :
  registro de tratamientos y consulta del historial por planta.
- **Importación de plantas** desde un archivo geográfico y listado de plantas por
  parcela.
- **Gestión de trabajadores**: crear, listar y eliminar trabajadores desde un
  encargado.
- **Creación del admin inicial**, mediante variables de entorno o un script, nunca
  por la API pública.
- **Interfaz sencilla**, si hay tiempo.

