# Muestra de recepción ACARS

[`recepcion_acars.jsonl`](recepcion_acars.jsonl) conserva los nueve mensajes de la sesión del 20 de octubre de 2026 en 131.725 MHz. El archivo se obtuvo de la captura guardada por `acarsdec` en la estación Dragon26. Cada línea contiene un registro JSON con su hora original, matrícula, vuelo, nivel, ruido, errores y texto.

| Matrícula | Vuelo | Registros |
|---|---|---:|
| CC-BFO | LP2055 | 1 |
| CC-BFW | LP2267 | 2 |
| CC-CPJ | LP2205 | 1 |
| CC-BAH | LP2067 | 5 |
| Total | 4 matrículas | 9 |

Tres registros incluyen texto: LSRES, INIT y WXRQ. Los nueve indican `error=0`. La [lectura comentada de los datos](../docs/RESULTADOS.md) explica lo que significan sus campos.

## Explorar la muestra sin un RTL-SDR

Se necesitan **Python 3**, **Docker Compose**, **Loki** y **Grafana**. Python utiliza únicamente su biblioteca estándar. La recepción por radio y `acarsdec` no son necesarios para este procedimiento.

Los comandos se ejecutan desde la raíz del repositorio. Primero compruebe el archivo, sin enviar nada a la red:

```bash
python3 scripts/cargar_muestra.py --check
```

El resultado esperado es `9 registros, 4 matrículas, 3 con texto`. Si el archivo falta o no coincide con la muestra, el programa se detiene e informa del problema.

En un despliegue nuevo, inicie los servicios necesarios:

```bash
docker compose -f docker-compose.yml -f docker-compose.acars.yml up -d loki grafana
curl -i http://localhost:3100/ready
```

Espere a recibir `200 OK` y `ready`. Si la estación ya tiene los servicios en ejecución, utilice esos servicios y omita el arranque de otra copia.

Cargue la muestra una vez:

```bash
python3 scripts/cargar_muestra.py
```

El programa envía las nueve líneas directamente a la [API de ingestión de Loki](https://grafana.com/docs/loki/latest/reference/loki-http-api/#post-lokiapiv1push). Las identifica con `job="acarsdec-demo"`, separado del `job="acarsdec"` que usa la recepción real mediante Alloy. La carpeta `ejemplos/` no está vigilada por Alloy y este procedimiento no copia registros a `data/acars/`.

## Ver los resultados en Grafana

1. Abra `http://localhost:3000` y configure la fuente Loki con URL `http://loki:3100`, como explica la [guía de uso](../docs/GUIA_DE_USO.md#configurar-grafana-y-consultar-loki).
2. Importe el archivo `acars-dashboard.json` actualizado. Si ya existe el dashboard con el mismo identificador, confirme el reemplazo.
3. En **Origen de datos**, seleccione **acarsdec-demo**.
4. Elija **Last 30 minutes** y actualice inmediatamente después de cargar. Con una sola carga, los contadores deben mostrar **9 mensajes, 4 matrículas y 3 mensajes con texto**.

En Explore, esta consulta permite ver los registros originales:

```logql
{job="acarsdec-demo"} | json | __error__=""
```

## Fechas y diferencia entre muestra y recepción actual

El cargador conserva la línea JSON original, incluido su campo `timestamp`. Para evitar que una captura histórica quede fuera del intervalo reciente o del límite de antigüedad de Loki, desplaza **solo las horas usadas para la ingestión**: el último mensaje queda unos segundos antes del momento de la carga y se mantienen las separaciones temporales entre los nueve mensajes.

Por tanto, la fecha mostrada por Loki en la reproducción corresponde a la carga desplazada; el `timestamp` que permanece dentro del JSON documenta la recepción original. Reproducir la muestra no significa que esas aeronaves estén transmitiendo ahora.

Ejecute el cargador una sola vez para comparar los conteos. Si vuelve a ejecutarlo, crea otra reproducción con horas de ingestión nuevas y los conteos pueden acumularse si el intervalo contiene ambas cargas. Para volver a las recepciones de la estación, seleccione `acarsdec` en el dashboard.
