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
- Importar olivos desde un archivo geográfico
- Registrar un tratamiento sobre un olivo.
- Consultar el historial de tratamientos de un olivo.
- Consultar solo la información de las explotaciones a las que se tiene acceso.


## Justificación NIST SP 800-145


