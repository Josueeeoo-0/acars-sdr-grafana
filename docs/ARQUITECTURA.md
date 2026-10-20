# Arquitectura de la integración ACARS

## Flujo de datos

```text
Antena → RTL-SDR → acarsdec (DragonOS) → JSONL en data/acars/
                                           ↓ montaje de solo lectura
                                   Alloy (Docker) → Loki → Grafana
                                   └── estado Alloy en volumen nombrado

acarsdec ── StatsD/UDP 8125 ──→ Graphite (configurado; recepción no validada)
```

`start-acars.sh` ejecuta `acarsdec` en el host DragonOS. Muestra la salida de texto en terminal y escribe JSON en `data/acars/`; la salida JSON configura rotación diaria (`rotate=daily`). El archivo fuente de Alloy (`acars.alloy`) descubre `*.jsonl`, empieza desde el inicio (`tail_from_end = false`), vuelve a buscar archivos cada cinco segundos y entrega cada línea JSON a Loki. Alloy extrae `timestamp`, `station_id` y `freq`; la hora de evento usa `timestamp` Unix. La línea original permanece intacta. El montaje `/logs` está marcado como solo lectura.

## Red y puertos

El colector Alloy corre en Docker Compose. Dentro de la red Compose, publica a Loki por el nombre de servicio `loki` en `http://loki:3100/loki/api/v1/push`. Para las comprobaciones desde DragonOS, el procedimiento documentado consulta Loki en `http://localhost:3100/ready`; requiere que el puerto 3100 esté publicado por el stack existente. Grafana se abre en `http://localhost:3000`, según la publicación del stack base.

El launcher configura el destino StatsD en `127.0.0.1:8125/UDP` por defecto. Esa opción está presente en el comando de `acarsdec`, pero no se verificó la recepción ni el nombre o los valores de las series resultantes en Graphite. El puerto TCP 2003 es la entrada Carbon del servicio Graphite y no se utiliza para enviar los JSON ACARS.

## Archivos y estado persistente

- `data/acars/` conserva los JSONL del decodificador y se monta como solo lectura en Alloy. La rotación diaria se solicita a `acarsdec`; el descubrimiento de Alloy incluye los archivos rotados que terminan en `.jsonl`.
- `acars-alloy-data` es un volumen nombrado para `--storage.path=/var/lib/alloy/data`. Alloy guarda allí las posiciones de lectura y puede retomar después de reiniciar.
- La extensión no añade volúmenes de persistencia a Grafana, Loki ni Graphite. El estado y los datos de esos servicios base siguen dependiendo de su Compose original. Antes de recrearlos, hay que respaldar y migrar sus datos.

La estación usa un RTL-SDR: solo un proceso puede abrir el dispositivo a la vez. Para iniciar `acarsdec`, hay que cerrar SDR#, `rtl_power`, `dumpvdl2` u otro lector del mismo receptor. Las capturas de SDR# documentan una observación visual separada; no son parte de la recepción continua de esta arquitectura.

## Consultas y severidad visual

Los streams usan las etiquetas de baja cardinalidad `job`, `station` y `freq`. Campos variables como `tail`, `flight`, `label`, `level`, `noise` y `text` se mantienen en el JSON y se extraen en las consultas del dashboard, no se usan como etiquetas indexadas.

En el dashboard v4, los paneles de logs presentan `error=0` como `INFO`, un `error` no vacío distinto de cero como `WARN` y un campo ausente como `UNKNOWN`. El nivel RF original se renombra en la consulta a `signal_db`; el conteo original de errores se conserva como `errores_acars`. La normalización de `detected_level` evita que metadatos estructurados anteriores contradigan esa clasificación en esos paneles. Esto es una regla de presentación de consultas; no reescribe el JSON almacenado ni cambia la severidad de Loki para otras consultas. La captura final de DragonOS confirma la presentación INFO, con 9 mensajes, 4 matrículas y 3 mensajes con texto en el intervalo documentado.

La documentación oficial explica el [lector de archivos de Alloy](https://grafana.com/docs/alloy/latest/reference/components/loki/loki.source.file/) y las [etiquetas y la cardinalidad de Loki](https://grafana.com/docs/loki/latest/get-started/labels/). El decodificador upstream es [f00b4r0/acarsdec](https://github.com/f00b4r0/acarsdec); este proyecto integra su ejecución y el flujo de observabilidad sin modificar su código.
