# ACARS SDR Observatory

### Observación ACARS en 131.725 MHz con DragonOS, Grafana Alloy y Loki

Este proyecto documenta una recepción real de mensajes ACARS con un RTL-SDR Blog V4 y la presenta en un dashboard de Grafana. La estación conservó los mensajes JSON de `acarsdec`, los envió a Loki con Grafana Alloy y los exploró por tiempo, matrícula, texto, nivel y ruido.

![Antena y receptor RTL-SDR Blog V4 de la estación](imagenes/1.png)

*Antena y receptor empleados durante la observación: RTL-SDR Blog V4 con sintonizador R828D.*

![Vista de SDR# en torno a 131.725 MHz](imagenes/2.png)

*La señal observada en SDR# corresponde a la frecuencia de recepción ACARS de 131.725 MHz. SDR# se utilizó para inspección visual de la señal; la decodificación documentada se realizó con `acarsdec` en DragonOS.*

![Medición S11 de la antena con NanoVNA](imagenes/3.png)

*Medición S11 de la antena usada para la estación.*

![Medición SWR de la antena con NanoVNA](imagenes/4.png)

*Medición de la relación de onda estacionaria (SWR) de la antena, con el marcador en 131.725 MHz.*

## Resumen del proyecto

La sesión tuvo lugar el **20 de octubre de 2026**, entre **19:14 y 19:27 UTC** (**14:14–14:27, hora de Lima**). Se registraron **9 mensajes**, de **4 matrículas**; **3 mensajes** contenían texto. La captura final de Grafana muestra estos mismos conteos y los registros con `error=0` clasificados visualmente como INFO.

El objetivo fue crear una vista histórica y consultable de los mensajes ACARS recibidos por una estación SDR. El dashboard reúne el conteo de mensajes, aeronaves distintas, mensajes con texto, actividad por minuto, nivel y ruido por matrícula, registros completos, registros con texto y los mensajes que contienen marcadores `INIT` o `WXRQ`.

![Versiones de software observadas en la estación](imagenes/5.png)

*Versiones de software registradas durante la recepción y la integración.*

| Componente | Versión o equipo observado |
|---|---|
| Sistema | DragonOS 26.1 |
| Decodificador | `acarsdec` v4.6-1-g0b7ba27 |
| Biblioteca ACARS | libacars 2.2.1 |
| Receptor SDR | RTL-SDR Blog V4, R828D |
| Colector de logs | Grafana Alloy v1.21.0 |
| Almacenamiento de logs | Loki v3.7.8 |
| Interfaz de visualización | Grafana v13.2.3 |

## Recepción y captura

`acarsdec` recibió la señal del RTL-SDR y produjo, en paralelo, salida de texto y JSONL. Los archivos JSON se conservaron como registros originales y sirvieron como fuente para la ingestión en Loki. Los datos observados incluyen la estación, frecuencia, canal, nivel, ruido, errores, modo, código de etiqueta, matrícula, identificador de vuelo y texto cuando esos campos estaban presentes.

![Mensajes ACARS decodificados en terminal](imagenes/6.png)

*La terminal muestra las líneas de mensajes entregadas por `acarsdec` durante la recepción.*

![Ejemplo de payload JSON generado por acarsdec](imagenes/7.png)

*El JSON conserva los campos decodificados que usan las consultas del dashboard. Los mensajes con etiqueta `_d` de esta muestra tienen el campo `text` vacío y se conservan en el conteo total.*

![Archivos JSONL de la recepción](imagenes/8.png)

*Los mensajes se conservaron en archivos locales con rotación diaria UTC.*

La señal se recibió en **131.725 MHz**, con una ganancia del receptor configurada en **28 dB**.

## Esquema de datos e interpretación

Los nombres de campo mantienen separadas las distintas clases de información que entrega el decodificador:

| Campo | Interpretación en este proyecto |
|---|---|
| `tail` | Matrícula o identificador de aeronave presente en el mensaje |
| `flight` | Identificador de vuelo; puede diferir de `tail` |
| `label` | Etiqueta/código del protocolo ACARS, por ejemplo `80` o `5U` |
| `mode` | Identificador del modo ACARS; en esta muestra aparece `2` |
| `level` | Nivel de señal relativo que reporta el decodificador |
| `noise` | Nivel de ruido relativo que reporta el decodificador |
| `error` | Conteo de errores que acompaña a cada mensaje recibido |
| `text` | Contenido decodificado cuando el mensaje incluye texto legible |

En particular, `CC-BAH` es el tail y `LP2067` el flight del mismo registro; no son valores intercambiables. De igual forma, `label=80` identifica el código de protocolo y no es un indicador de nivel RF. Los campos vacíos se conservan en contexto y no se convierten automáticamente en fallas de procesamiento.

## Recorrido de los datos

El flujo de observación está compuesto por la antena y el RTL-SDR, `acarsdec`, archivos JSONL, Grafana Alloy, Loki y Grafana. La salida StatsD hacia Graphite está configurada en el stack base; las series ACARS concretas de Graphite no forman parte de los resultados verificados aquí.

![Servicios del stack de observabilidad](imagenes/9.png)

*Vista de los servicios que participaron en la observación y el almacenamiento.*

![Estado listo de Loki](imagenes/10.png)

*Loki respondió como servicio disponible durante la validación.*

![Grafana Alloy leyendo la salida ACARS](imagenes/11.png)

*Alloy leyó los archivos JSONL y envió los eventos a Loki, preservando el contenido y el timestamp del mensaje.*

La configuración de Alloy indexa etiquetas de baja cardinalidad para identificar el trabajo, la estación y la frecuencia. Matrícula, vuelo, nivel, ruido, error y texto se extraen al consultar el JSON; no se convierten en etiquetas indexadas. Esto permite agrupar registros por matrícula sin crear una serie Loki por cada valor de alta cardinalidad.

## Exploración en Grafana

![Conexión de Grafana con la fuente de datos Loki](imagenes/12.png)

*La fuente de datos Loki conecta Grafana con los eventos de la estación.*

![Consulta de mensajes ACARS en Explore](imagenes/13.png)

*Explore permite consultar los registros ACARS conservados por Loki dentro de un intervalo temporal.*

Los eventos del intervalo aparecen en Grafana usando su timestamp de ACARS. La selección de un rango de tiempo que cubra la sesión permite consultar los registros del 20 de octubre de 2026. La búsqueda puede filtrar los mensajes por contenido, además de mostrar el payload junto con los campos extraídos.

![Importación del dashboard ACARS](imagenes/14.png)

*El dashboard se integra como una vista de Grafana vinculada a la fuente de datos Loki.*

## Dashboard y resultados

![Dashboard ACARS v4 con resultados 9, 4 y 3](imagenes/15.png)

*Resultado observado: nueve mensajes, cuatro matrículas distintas y tres mensajes con texto. Los registros sin errores de decodificación se presentan como INFO.*

El dashboard final contiene nueve paneles:

| Vista | Qué muestra |
|---|---|
| Mensajes en el rango | Total de registros ACARS en el intervalo elegido |
| Aeronaves distintas | Matrículas `tail` no vacías y distintas |
| Mensajes con texto | Registros con contenido no vacío en `text` |
| Mensajes por minuto | Conteo en ventanas fijas de un minuto |
| Nivel por matrícula | Promedio de `level` en ventanas de cinco minutos |
| Ruido por matrícula | Promedio de `noise` en ventanas de cinco minutos |
| Todos los mensajes | Campos principales y texto cuando existe |
| Mensajes con texto | Vista enfocada en payloads no vacíos |
| WXRQ e INIT | Registros cuyo texto contiene esos marcadores |

Las series de nivel y ruido se presentan en **dB relativos** reportados por el decodificador. No son medidas calibradas en dBm. Los paneles omiten valores que no puedan convertirse a número y separan los valores por matrícula. Los intervalos sin registros aparecen como huecos en la actividad, no como ceros observados.

La severidad mostrada en los paneles de logs se deriva del campo ACARS `error`: `error=0` se presenta como INFO, un valor no vacío distinto de cero como WARN y un campo ausente como UNKNOWN. El nivel RF se conserva por separado como `signal_db`; las etiquetas INFO/WARN/UNKNOWN describen el conteo de errores del mensaje, no la intensidad de señal.

![Detalle de los mensajes INIT, WXRQ y LSRES](imagenes/16.png)

*Detalle de los tipos de mensaje observados, junto con sus matrículas, identificadores de vuelo y texto disponible.*

Entre los datos de la sesión se observaron estos pares matrícula/vuelo:

| Matrícula (`tail`) | Vuelo (`flight`) | Evidencia de la sesión |
|---|---|---|
| CC-BFO | LP2055 | Mensaje recibido |
| CC-BFW | LP2267 | Mensaje recibido |
| CC-CPJ | LP2205 | Mensaje `LSRES`, `label=80` |
| CC-BAH | LP2067 | Mensajes `INIT` y `WXRQ`; también se observó `label=5U` |

### Qué significan los mensajes recibidos

La recepción permitió leer información operativa, además de contar mensajes. ACARS es un enlace de datos entre aeronaves y tierra utilizado para intercambiar información de operación y meteorología, entre otros usos. [SITA: aplicaciones de los mensajes ACARS](https://www.sita.aero/globalassets/docs/infographics/aircom-r-cockpit-services-acars-infographic.pdf).

En el mensaje de **CC-BAH**, vuelo **LP2067**, se recibió:

```text
3G01 INIT   2067/20 SPJC/SPTN .CC-BAH/001
```

`CC-BAH` identifica la aeronave y `LP2067` el vuelo. `INIT` se interpreta aquí como un mensaje de inicialización de datos del vuelo: reúne el número `2067`, el valor `20` que coincide con el día de la recepción, dos aeropuertos y la matrícula. Es una lectura del texto recibido; no se asigna un significado a los campos internos `3G01` y `/001`.

| Código OACI recibido | Ciudad | Aeropuerto |
|---|---|---|
| `SPJC` | Lima / Callao | Internacional Jorge Chávez |
| `SPTN` | Tacna | Internacional Coronel FAP Carlos Ciriani Santa Rosa |
| `SPSO` | Pisco | Capitán FAP Renán Elías Olivera |
| `SPQU` | Arequipa | Internacional Alfredo Rodríguez Ballón |

Las correspondencias se contrastan con el [listado de aeropuertos del MTC](https://cdn.www.gob.pe/uploads/document/file/7419112/6322184-listado-de-aeropuertos%282%29.pdf) y las estaciones meteorológicas de NOAA para [Tacna](https://tgftp.nws.noaa.gov/data/observations/metar/decoded/SPTN.TXT), [Pisco](https://tgftp.nws.noaa.gov/data/observations/metar/decoded/SPSO.TXT) y [Arequipa](https://tgftp.nws.noaa.gov/data/observations/metar/decoded/SPQU.TXT).

Por tanto, **`SPJC/SPTN` se lee como Lima / Tacna**. Si el par está escrito como origen/destino, el sentido indicado es **Lima → Tacna**. Esta interpretación procede del orden del texto; los códigos identifican aeropuertos, pero no indican dónde estaba el avión al transmitir.

Unos segundos después, la misma aeronave envió:

```text
01 WXRQ   2067/20 SPJC/SPTN .CC-BAH
/TYP 1/STA SPTN/STA SPSO/STA SPQU
```

**`WXRQ` significa “Weather request”, solicitud meteorológica**, según el [manual del decodificador AOR ARD-2](https://www.aorja.com/support/discontinued/m/ARD-2_operating_manual.pdf). Las entradas `STA` enumeran Tacna, Pisco y Arequipa: se interpreta como una solicitud de información meteorológica para esas estaciones. La lista no demuestra escalas ni aeropuertos alternos del vuelo. El valor `TYP 1` se conserva sin atribuirle un producto meteorológico concreto.

También llegó `LSRES` seguido de `0001/10`, asociado a CC-CPJ/LP2205. Se conserva como contenido observado, sin asignarle una expansión no verificada. Los seis mensajes restantes tenían el texto vacío: siguen aportando matrícula, vuelo, hora y datos de recepción.

La [lectura detallada de los registros](docs/RESULTADOS.md) explica estos campos, los números de mensaje, `Nak`, el nivel de señal y el ruido con ejemplos de la sesión.

![Ampliación de las gráficas de nivel y ruido](imagenes/17.png)

*Detalle de las series temporales por matrícula. Los valores reflejan los campos relativos de la salida del decodificador.*

## Alcance de la observación

La captura permite describir los nueve mensajes conservados y los campos que aparecen en ellos. No permite concluir que todos los paquetes transmitidos fueron recibidos, calcular una tasa de pérdida, deducir la cobertura de la antena ni localizar el receptor. Una línea con `text` vacío puede seguir siendo un frame ACARS válido.

La visualización presentada se basa en los mensajes ACARS almacenados en Loki. La salida StatsD hacia Graphite queda disponible como rama de métricas; los resultados documentados corresponden al flujo JSONL → Alloy → Loki → Grafana.

![Diagrama del flujo ACARS desde la recepción hasta Grafana](imagenes/18.png)

*Resumen visual de la cadena de recepción, almacenamiento JSONL, transporte por Alloy, consulta en Loki y presentación en Grafana.*

## Componentes del proyecto

| Archivo o carpeta | Propósito |
|---|---|
| `acars.alloy` | Lectura de JSONL, asignación de timestamp y etiquetas de baja cardinalidad |
| `docker-compose.acars.yml` | Servicio auxiliar de Alloy para el stack existente |
| `acars-dashboard.json` | Dashboard de nueve paneles para Grafana |
| `start-acars.sh` | Configuración del decodificador y salida JSONL/StatsD |
| [Arquitectura](docs/ARQUITECTURA.md) | Qué hace cada programa y cómo circula un mensaje |
| [Lectura de los datos](docs/RESULTADOS.md) | Ejemplos comentados de los mensajes de la sesión |
| [Guía de uso](docs/GUIA_DE_USO.md) | Programas necesarios, recepción y visualización paso a paso |
| `imagenes/` | Fotografías, capturas y diagrama del proyecto |

## Créditos

Proyecto de [Josueeeoo-0](https://github.com/Josueeeoo-0). La decodificación se realizó con [`acarsdec`](https://github.com/f00b4r0/acarsdec), de Thierry Leconte y Thibaut VARENE. La integración propia se publica bajo MIT; `acarsdec` conserva su licencia GPL-2.0-only. Las atribuciones de la configuración y los logotipos se detallan en [NOTICE.md](NOTICE.md).
