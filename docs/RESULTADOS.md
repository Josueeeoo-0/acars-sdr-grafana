# Cómo leer los datos recibidos

El dashboard resume una sesión; este documento explica los registros que hay detrás de sus números. Los ejemplos proceden de la recepción del **20 de octubre de 2026 en 131.725 MHz**. Los nueve mensajes se conservan en [la muestra JSONL](../ejemplos/recepcion_acars.jsonl) y pueden [reproducirse sin receptor](../ejemplos/README.md). Para iniciar una recepción propia, véase la [guía de uso](GUIA_DE_USO.md).

## Una aeronave y un vuelo son identificadores distintos

En los registros se leen, entre otros, estos dos campos:

```text
Aircraft reg: CC-BAH    Flight id: LP2067
```

`CC-BAH` es la matrícula que identifica la aeronave en el mensaje. `LP2067` es el identificador del vuelo comunicado. La misma matrícula puede aparecer en otros vuelos; varios mensajes con esa matrícula no representan varios aviones. Por eso el dashboard cuenta por separado mensajes y matrículas distintas.

Los cuatro pares observados fueron CC-BFO/LP2055, CC-BFW/LP2267, CC-CPJ/LP2205 y CC-BAH/LP2067. La distribución de mensajes fue 1, 2, 1 y 5, respectivamente. Estos campos proceden de la [salida JSON documentada por acarsdec](https://github.com/f00b4r0/acarsdec#output-formats-examples).

## INIT: datos asociados al vuelo

Este es el texto recibido de CC-BAH/LP2067:

```text
3G01 INIT   2067/20 SPJC/SPTN .CC-BAH/001
```

| Fragmento | Lectura del ejemplo |
|---|---|
| `INIT` | Se interpreta como inicialización de datos del vuelo |
| `2067` | Coincide con la parte numérica de `LP2067` |
| `/20` | Coincide con el día 20 de la sesión; es una inferencia por el contexto |
| `SPJC/SPTN` | Par de aeropuertos Lima / Tacna |
| `.CC-BAH` | Repite la matrícula; el punto forma parte del formato del texto |
| `3G01` y `/001` | Campos internos que se conservan sin asignarles un significado no verificado |

`SPJC` identifica el aeropuerto Jorge Chávez de Lima/Callao, de acuerdo con el [listado del Ministerio de Transportes y Comunicaciones](https://cdn.www.gob.pe/uploads/document/file/7419112/6322184-listado-de-aeropuertos%282%29.pdf). `SPTN` corresponde a Tacna, como también muestra la [estación de NOAA](https://tgftp.nws.noaa.gov/data/observations/metar/decoded/SPTN.TXT); el aeropuerto es el [Internacional Coronel FAP Carlos Ciriani Santa Rosa](https://aap.com.pe/sedes/tacna/).

Si el formato usa el orden origen/destino, **SPJC/SPTN apunta a Lima → Tacna**. Esa lectura es una interpretación del texto del mensaje, no una comprobación independiente del itinerario. Tampoco proporciona la posición del avión al transmitir. La inicialización se explica aquí por los datos visibles; no se pretende documentar todos los campos internos del software de la aerolínea.

## WXRQ: una solicitud meteorológica

El siguiente mensaje de la misma matrícula y vuelo contenía:

```text
01 WXRQ   2067/20 SPJC/SPTN .CC-BAH
/TYP 1/STA SPTN/STA SPSO/STA SPQU
```

`WXRQ` abrevia **Weather request**, es decir, solicitud meteorológica. La abreviatura figura en el [manual del fabricante AOR para el ARD-2](https://www.aorja.com/support/discontinued/m/ARD-2_operating_manual.pdf). El intercambio de información meteorológica es uno de los usos de ACARS descritos por [SITA](https://www.sita.aero/globalassets/docs/infographics/aircom-r-cockpit-services-acars-infographic.pdf).

Las entradas `STA` se interpretan como las estaciones solicitadas:

| Fragmento | Ciudad identificada | Fuente para el código |
|---|---|---|
| `/STA SPTN` | Tacna | [NOAA: SPTN](https://tgftp.nws.noaa.gov/data/observations/metar/decoded/SPTN.TXT) |
| `/STA SPSO` | Pisco | [NOAA: SPSO](https://tgftp.nws.noaa.gov/data/observations/metar/decoded/SPSO.TXT) |
| `/STA SPQU` | Arequipa | [NOAA: SPQU](https://tgftp.nws.noaa.gov/data/observations/metar/decoded/SPQU.TXT) |

En lenguaje cotidiano: **el mensaje pide información meteorológica para Tacna, Pisco y Arequipa**. Enumera estaciones de interés; no demuestra que el avión vaya a aterrizar en las tres. Las páginas de NOAA se enlazan para identificar los códigos, no como evidencia del tiempo meteorológico de nuestra sesión.

`TYP 1` y el prefijo `01` quedan conservados tal como llegaron. Sin una especificación del formato de aplicación no se les atribuye un producto concreto, como METAR o TAF. Lo recibido es la solicitud; en la muestra no se identificó su respuesta meteorológica.

## LSRES: contenido conservado sin interpretación añadida

CC-CPJ/LP2205 envió:

```text
LSRES
0001/10
```

El registro permite asociar ese texto a una hora, aeronave y vuelo. No se dispone de una fuente verificada para expandir `LSRES` ni interpretar `0001/10` en este formato. El proyecto conserva el contenido para su consulta y evita convertir una abreviatura desconocida en una conclusión.

## Los mensajes sin texto también cuentan

Seis de los nueve registros tenían `text` vacío y etiqueta `_d`. Aun así, incluían datos de identificación y recepción, por lo que forman parte del total de mensajes. La [ayuda de acarsdec](https://github.com/f00b4r0/acarsdec#common-options) incluye expresamente los mensajes `_d` entre los ejemplos de mensajes vacíos que pueden filtrarse con `-e`. El script de este proyecto conserva esos registros.

Los campos `label=80` y `label=5U` son códigos de mensaje ACARS. No son una potencia, una frecuencia ni el número de errores. `mode=2` es el identificador de modo ACARS que apareció en los registros de esta sesión.

## Nivel, ruido y errores: tres cosas diferentes

Un registro de CC-BAH/LP2067 mostró:

```text
L:-15.3/-51.2 E:0
```

| Valor | Qué expresa |
|---|---|
| `level=-15.3` | Nivel relativo de la señal recibido por el decodificador |
| `noise=-51.2` | Estimación relativa del ruido que acompaña al registro |
| `error=0` | Cero errores reportados por el decodificador para ese mensaje |

En la misma escala, un nivel de `-15.3` es mayor que uno de `-34.1`. La diferencia puede deberse a las condiciones de recepción; por sí sola no determina distancia ni potencia del transmisor. Estos valores se presentan como **dB relativos**, sin convertirlos a dBm calibrados.

El [formateador de salida de acarsdec](https://github.com/f00b4r0/acarsdec/blob/master/output.c) entrega estos valores en los campos JSON `level`, `noise` y `error`. El dashboard conserva el nivel RF como `signal_db` en las vistas de mensajes y utiliza `error` para la clasificación visual: cero → INFO; un valor presente distinto de cero → WARN; ausente → UNKNOWN. Los nueve registros de la sesión tenían cero errores reportados.

## Qué significan No, Nak y Reassembly

- **`No: M50A` o `S66A`:** identificador/número del mensaje (`msgno`), útil para distinguir registros. No es un contador del dashboard.
- **`Nak`:** es un valor del campo de reconocimiento del protocolo. No sustituye al contador de errores local: en la muestra aparece junto a `E:0`.
- **`Reassembly: skipped`:** estado de la reconstrucción de fragmentos. No significa, por sí solo, que el mensaje mostrado se haya perdido o esté mal decodificado.

La [implementación de la salida](https://github.com/f00b4r0/acarsdec/blob/master/output.c) mantiene separados el reconocimiento, el número de mensaje, los errores y el estado de reconstrucción.

## Qué representan los contadores

**9 mensajes** significa nueve registros dentro del intervalo consultado. **4 aeronaves distintas** significa cuatro valores distintos y no vacíos de `tail`. **3 mensajes con texto** significa tres registros con contenido en `text`; los otros seis siguen dentro del total.

La actividad por minuto cuenta mensajes en ventanas de un minuto. Las curvas de nivel y ruido promedian los registros de cada matrícula en ventanas de cinco minutos. Un hueco indica ausencia de muestras en esa consulta, sin demostrar una avería o una pérdida de paquetes.

Estos números describen la muestra documentada. Una recepción propia puede tener otros conteos, matrículas y textos, según la actividad local y el intervalo seleccionado.
