# Documentación Hito 1
## Descripción del dominio

### Problema
  Las explotaciones agrícolas necesitan mantener un historial de tratamientos, enfermedades y otras actualizaciones realizadas sobre cada planta para mejorar la trazabilidad, consultar intervenciones anteriores y mantener la información de cada parcela actualizada. 
  
Actualmente, estos datos se almacenan mediante hojas de cálculo o anotaciones manuales, lo que dificulta la localización de una planta concreta y conocer qué tratamientos o actuaciones se han sobre ella.

  La idea de este proyecto surge de observar este problema en una explotación agrícola de olivar. Sin embargo, la aplicación se desarrollará de forma general para que pueda adaptarse a cualquier tipo de plantación.

### Objetivo
  El objetivo es desarrollar una aplicación distribuida que permita gestionar la información geográfica de las plantas y registrar y consultar su historial de tratamientos y actuaciones, mediante una arquitectura basada en microservicios desacoplados.
  
La aplicación permitirá: 
- Gestionar explotaciones y parcelas agrícolas.
- Importar las coordenadas de las plantas de una parcela.
- Visualizar un listado de las plantas registradas.
- Registrar tratamientos y actuaciones asociados a las plantas concretas.
- Consultar el historial de tratamientos y actuaciones de cada planta.
- Controlar el acceso a la información según los permisos de cada usuario.

### Usuarios y casos de uso
Los principales usuarios serán los responsables y trabajadores de las explotaciones agrícolas.

Los casos de usos principales son:
- Registrarse e iniciar sesión
- Registrar una explotación.
- Importar plantas desde un archivo geográfico
- Registrar un tratamiento/actuación sobre una planta.
- Consultar el historial de tratamientos y actuaciones de una planta.
- Consultar solo la información de las explotaciones a las que se tiene acceso.


## Justificación NIST SP 800-145
La aplicación se plantea como un sistema basado en servicios cloud que cumple las cinco características definidas por NIST SP 800-145:

| Característica | Justificación |
|---|---|
| Autoservicio bajo demanda | Los usuarios pueden gestionar parcelas, plantas y tratamientos desde la aplicación sin necesitar la intervención del proveedor cloud para cada operación.| 
| Acceso amplio a la red| La plataforma será accesible mediante una conexión de red desde distintos dispositivos, como ordenadores, tabletas y móviles.|
| Asignación común de recursos | La infraestructura cloud podrá compartirse entre distintas explotaciones, manteniendo aislados sus datos y permisos. |
| Rápida elasticidad | La capacidad de los servicios podrá ampliarse o reducirse según la demanda, dependiendo de la infraestructura y la configuración del despliegue. |
| Servicio medido | Se podrán monitorizar el consumo de almacenamiento, CPU, tráfico y peticiones para controlar los recursos utilizados. |

## Mapeo de actores NIST SP 500-292 

| Actor | Aplicación en AgroTrace | Impacto económico |
|---|---|---|
| Consumidor | Explotaciones agrícolas que utilizan la plataforma. | Asume el coste de la suscripción para utilizar la plataforma. | 
| Proveedor  | Empresa que proporciona la infraestructura y los servicios cloud donde se ejecuta la aplicación. | Cobra por los recursos y servicios proporcionados. | 
| Intermediario | Entidad que gestiona servicios de uno o varios proveedores de cloud (opcional). | Puede añadir costes de gestión, pero simplificar la administración de los servicios. | 
| Auditor | Entidad independiente que evalúa la seguridad, los controles y el cumplimiento de los servicios cloud utilizados. | Puede generar costes de auditoría, pero contribuir a reducir riesgos e identificar deficiencias. | 
| Operador | Proveedor de conectividad que permite la comunicación entre los usuarios y la infraestructura cloud. | Los costes dependen del servicio de conectividad contratado.


## Diagrama de arquitectura


## Especificación API REST

 | Método HTTP | Endpoint | Descripción | 
 |---|---|---|
 | POST | /auth/register | Registrar un nuevo usuario. | 
 | POST | /auth/login | Iniciar sesión. | 
 | POST | /parcelas | Crear una nueva parcela agrícola. | 
 | GET | /parcelas | Consultar las parcelas accesibles para el usuario autenticado. | 
 | POST | /plantas/importar | Importar plantas y sus coordenadas desde un archivo. | 
 | GET | /parcelas/{id}/plantas | Obtener las plantas de una parcela determinada. | 
 | GET | /plantas/{id} | Consultar los datos de una planta concreta. | 
 | POST | /tratamientos | Registrar un tratamiento aplicado a una planta. | 
 | GET | /plantas/{id}/historial | Consultar el historial de tratamientos de una olanta. | 
 | GET | /tratamientos?parcelaId={id} | Consultar los tratamientos asociados a una parcela. | 

Las peticiones que requieran autenticación utilizarán un token de acceso. El servidor comprobará los permisos del usuario antes de permitir el acceso o la modificación de los datos.

