# Créditos y alcance de la licencia

**ACARS SDR Observatory** es una integración de recepción y observación preparada para [Josueeeoo-0](https://github.com/Josueeeoo-0). Sus aportaciones son la configuración ACARS/Alloy, el dashboard, el script de recepción, la documentación y la figura de arquitectura. La licencia MIT de este repositorio se aplica a esas aportaciones.

El diseño de partida procede de [alphafox02/dumphfdl-grafana-stack](https://github.com/alphafox02/dumphfdl-grafana-stack), cuyo README atribuye el stack a cemaxecuter y declara licencia MIT. La configuración base incluida se adapta de ese stack para utilizar Alloy en el flujo ACARS. Se conserva aquí la referencia y atribución al proyecto original.

El decodificador es [f00b4r0/acarsdec](https://github.com/f00b4r0/acarsdec), copyright Thierry Leconte y Thibaut VARENE, publicado bajo GPL-2.0-only según su documentación. Se utiliza como dependencia instalada en DragonOS; este repositorio no redistribuye su código ni sus binarios.

Grafana, Loki, Alloy, Graphite, Docker, DragonOS y SDR# son proyectos de sus respectivos autores. Sus nombres se utilizan para identificar componentes. Las dependencias conservan sus propias licencias; no se atribuye a esta integración su desarrollo.

Las fotos y capturas de la estación corresponden a las evidencias incorporadas por el autor. La figura 18 es una representación técnica del flujo, no una medición del espectro ni una fotografía de la estación.

## Logotipos de la figura 18

Se incorporan como identificación de los componentes, conservando su diseño y autoría:

- [Grafana](https://github.com/grafana/grafana/blob/main/public/img/grafana_icon.svg).
- [Grafana Alloy](https://github.com/grafana/alloy/blob/main/docs/sources/assets/logo_alloy_dark.svg).
- [Loki](https://grafana.com/static/img/logos/logo-loki.svg).
- [Docker, desde su repositorio de documentación](https://github.com/docker-library/docs/blob/c350af05d3fac7b5c3f6327ac82fe4d990d8729c/docker/logo.png).
- [Graphite, desde su repositorio Graphite-Web](https://github.com/graphite-project/graphite-web/blob/master/webapp/content/img/graphite.png).

Los símbolos de antena, receptor, terminal y archivo son pictogramas del esquema, no logotipos oficiales de esos componentes.
