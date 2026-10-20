# Captura original de la sesión

[`recepcion_acars.jsonl`](recepcion_acars.jsonl) contiene los nueve registros originales de la recepción ACARS del **20 de octubre de 2026**, en **131.725 MHz**, con la estación **Dragon26**. Se publica como evidencia de los datos que sustentan las capturas de terminal y el dashboard.

El archivo fue generado por `acarsdec`. Se conservan sus líneas JSON, marcas de tiempo, campos y textos; no se modifican las horas ni se generan mensajes adicionales. Puede abrirse directamente en GitHub, descargarse como archivo Raw o leerse en un editor de texto.

| Matrícula | Vuelo | Registros |
|---|---|---:|
| CC-BFO | LP2055 | 1 |
| CC-BFW | LP2267 | 2 |
| CC-CPJ | LP2205 | 1 |
| CC-BAH | LP2067 | 5 |
| Total | 4 matrículas | 9 |

Tres registros contienen texto: LSRES, INIT y WXRQ. Los nueve indican `error=0`. Las fechas abarcan aproximadamente **19:14:34–19:27:35 UTC**, equivalentes a **14:14:34–14:27:35 en Lima**.

JSONL significa un objeto JSON por línea. Los saltos de línea que forman parte de un mensaje aparecen escapados dentro del campo `text`, por ejemplo como `\r\n`; no representan registros adicionales.

La [explicación de los datos](../docs/RESULTADOS.md) permite interpretar matrículas, vuelos, aeropuertos, texto y niveles. La carpeta `muestras/` conserva la evidencia publicada; las nuevas recepciones se guardan aparte en `data/acars/` y permanecen excluidas de Git.
