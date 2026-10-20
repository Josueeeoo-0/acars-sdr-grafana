# Guía de uso y reproducción

Esta guía describe cómo usar el proyecto en una estación Linux con un RTL-SDR, conservar la salida de `acarsdec` como JSONL y consultarla en Grafana. Los comandos suponen que la terminal está situada en el directorio raíz del repositorio.

## Requisitos

- Linux; la captura documentada se hizo con DragonOS.
- Para recepción por radio: Bash y `acarsdec` v4.6 con soporte moderno para `--rtlsdr` y `--output` en formatos de texto y JSON. La salida JSON debe admitir `path` y `rotate=daily`. Consulte el proyecto [acarsdec](https://github.com/f00b4r0/acarsdec) para conocer el decodificador.
- Un RTL-SDR compatible y una antena para la banda recibida, conectados a la estación y disponibles para `acarsdec`.
- Docker Engine y el complemento Docker Compose con el comando `docker compose` (v2 o posterior).
- `curl` para comprobar la respuesta de Loki y un navegador para abrir Grafana.
- Para explorar la muestra sin receptor: Python 3 y su biblioteca estándar; no requiere módulos de `pip`, `acarsdec` ni RTL-SDR.
- Acceso a Grafana en el puerto 3000 y a Loki en el puerto 3100. El stack publica también Graphite en 8080, 2003 y 8125/UDP.

El stack fija Grafana 13.2.3, Loki 3.7.8 y Alloy 1.21.0. Graphite es opcional para la exploración ACARS de esta guía: la configuración StatsD existe, pero sus métricas ACARS no se validaron. SDR# es una herramienta opcional de observación visual independiente; NanoVNA es opcional para medir la antena. Ninguno es necesario para la ingestión JSONL en Loki.

La guía describe la recepción en directo. Para probar los mensajes y el dashboard sin hardware, siga la [reproducción de la muestra incluida](../ejemplos/README.md).

## Preparar la captura

Antes de iniciar Compose, cree el directorio que se montará en Alloy:

```bash
mkdir -p data/acars
```

La ruta del host se monta como solo lectura en el contenedor. Si el usuario que ejecuta `acarsdec` no puede escribir allí, no se generarán archivos que Alloy pueda leer.

Puede crear `.env` a partir del ejemplo sin sobrescribir un archivo existente y cambiar la contraseña inicial para una instalación nueva:

```bash
cp --update=none .env.example .env
```

Compose lee `.env` para interpolar las imágenes y `GRAFANA_ADMIN_PASSWORD`. En cambio, `start-acars.sh` **no** carga `.env`: las opciones del receptor se toman del entorno de la terminal que ejecuta el script.

Los valores predeterminados del script son dispositivo `0`, nombre de estación del sistema, ganancia `28` y frecuencia `131.725` MHz. También admite `STATSD_HOST` (predeterminado `127.0.0.1`) y `STATSD_PORT` (predeterminado `8125`).

## Iniciar los servicios

Elija la situación que corresponde a la estación. Si ya hay servicios activos con los nombres `grafana`, `loki` y `graphite`, use la alternativa para un despliegue existente que aparece al final de esta sección; no inicie otra copia en paralelo.

**En un despliegue nuevo**, valide la configuración y arranque Loki, Grafana, Graphite y el colector Alloy:

```bash
docker compose -f docker-compose.yml -f docker-compose.acars.yml config --quiet
docker compose -f docker-compose.yml -f docker-compose.acars.yml up -d
```

Espere a que Loki acepte consultas:

```bash
curl -i http://localhost:3100/ready
```

Una respuesta `503` puede ser temporal durante el arranque. Repita la consulta hasta recibir `200`. Para revisar el lector ACARS:

```bash
docker compose -f docker-compose.yml -f docker-compose.acars.yml logs -f acars-collector
```

`Ctrl+C` termina el seguimiento de los logs; el colector continúa ejecutándose.

Para una estación que ya ejecuta este stack con los nombres fijos `grafana`, `loki` y `graphite`, no levante una segunda copia: los nombres y puertos entrarían en conflicto. Desde el mismo directorio y usando el mismo proyecto Compose existente, añada únicamente el colector, sin recrear sus dependencias:

```bash
docker compose -f docker-compose.yml -f docker-compose.acars.yml up -d --no-deps acars-collector
```

## Recibir mensajes

Abra una terminal para la captura y ejecútela desde la raíz del repositorio:

```bash
RTL_DEVICE=0 STATION_ID=estacion-1 RTL_GAIN=28 ACARS_FREQ=131.725 bash start-acars.sh
```

El ejemplo fija explícitamente dispositivo, estación, ganancia y frecuencia. También puede ejecutar `bash start-acars.sh` para usar los valores predeterminados. Solo debe ejecutarse una instancia por receptor; cierre la aplicación SDR que lo esté utilizando antes de capturar.

El script ejecuta `acarsdec` con `--rtlsdr` y escribe texto en terminal y JSONL en paralelo. La opción `rotate=daily` incorpora la fecha UTC al nombre desde el primer archivo: por ejemplo, `data/acars/acars_20261020.jsonl`. El nombre base `acars.jsonl` que aparece en el script no es el nombre final del archivo rotado. Para revisar archivos y seguir la salida en otra terminal:

```bash
ls -lh data/acars/
tail -f "data/acars/acars_$(date -u +%Y%m%d).jsonl"
```

El archivo se crea al escribir el primer mensaje. Si `tail` dice que aún no existe, espere una recepción y compruebe de nuevo con `ls`. Al cambiar de día UTC, vuelva a ejecutar `tail` para seguir el archivo nuevo. La carpeta `data/acars` conserva los JSONL en el host. El servicio Alloy conserva su estado de lectura en el volumen nombrado `acars-alloy-data`. La configuración base no declara volúmenes persistentes para Loki, Grafana ni Graphite; recrear esos contenedores requiere un respaldo o persistencia adicional para conservar sus datos internos.

## Configurar Grafana y consultar Loki

Abra `http://localhost:3000` e inicie sesión como `admin`. En una instalación nueva, la contraseña es la definida por `GRAFANA_ADMIN_PASSWORD` en `.env`, o `admin` si se usa el valor predeterminado.

La configuración no aprovisiona automáticamente la fuente de datos ni el dashboard. En Grafana:

1. Abra **Connections → Data sources → Add data source** y elija **Loki**.
2. En **URL**, escriba `http://loki:3100`, seleccione **Save & test** y confirme que la conexión responde correctamente.
3. Abra **Dashboards → New → Import**. Seleccione `acars-dashboard.json`, elija la fuente de datos Loki cuando Grafana lo solicite e importe el dashboard. Consulte la [documentación de importación de dashboards](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/import-dashboards/).

En **Origen de datos**, mantenga `acarsdec` para la recepción en directo. La opción `acarsdec-demo` muestra la reproducción de la muestra. Si actualiza un dashboard importado anteriormente, vuelva a importar el JSON y confirme su reemplazo para incorporar ese selector.

En **Explore**, elija la fuente Loki, cambie a **Code**, introduzca esta consulta y ejecútela:

```logql
{job="acarsdec"} | json | __error__=""
```

Para ver solo los mensajes con texto de una matrícula:

```logql
{job="acarsdec"} | json | __error__="" | tail="CC-BAH" | text != ""
```

Sustituya la matrícula por una de su propia recepción. Use un intervalo que cubra los eventos, por ejemplo **Last 30 minutes**, y active la actualización periódica si la necesita. Para archivos antiguos seleccione su fecha real. Alloy conserva el `timestamp` de cada evento; el [dashboard](../acars-dashboard.json) añade la clasificación INFO/WARN/UNKNOWN a sus paneles de mensajes.

## Detener y solucionar problemas

Para terminar la recepción, use `Ctrl+C` en la terminal que ejecuta `start-acars.sh`. Para detener los contenedores y conservar archivos y volúmenes:

```bash
docker compose -f docker-compose.yml -f docker-compose.acars.yml stop
```

`RTL busy` suele indicar que otro proceso ya está usando el receptor; cierre ese proceso antes de iniciar `acarsdec`. Si no aparecen frames, compruebe antena, dispositivo, frecuencia y ganancia. Si `start-acars.sh` informa opciones incompatibles, confirme que la versión de `acarsdec` admite `--rtlsdr` y la sintaxis JSON `--output` empleada por el script. Si Alloy no ve datos, revise que existan JSONL legibles en `data/acars/` y consulte los logs de `acars-collector`. Un `503` de `/ready` inmediatamente después de arrancar Loki puede desaparecer cuando termine de inicializarse.

Si el archivo contiene mensajes pero Grafana muestra **No data**, compruebe el intervalo de tiempo, la fuente Loki seleccionada y su URL `http://loki:3100`. En otra ubicación puede no existir actividad ACARS en 131.725 MHz; el valor de la guía es el canal observado en esta estación.

## Sobre la muestra incluida

Los nueve registros de la sesión se incluyen en [`ejemplos/recepcion_acars.jsonl`](../ejemplos/recepcion_acars.jsonl). Conservan las matrículas, vuelos, textos, niveles y fechas originales. El [cargador de la muestra](../ejemplos/README.md) permite explorar esos datos sin receptor y usa un origen separado de las nuevas recepciones. Los conteos 9/4/3 describen esta muestra; una recepción propia puede tener otros resultados.
