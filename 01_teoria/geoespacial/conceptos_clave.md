# Análisis Geoespacial aplicado a la Construcción

El análisis geoespacial permite responder preguntas que tienen una dimensión espacial: ¿dónde está el mayor riesgo de deslizamiento en la ruta del proyecto? ¿Qué zonas de la traza vial cruzan áreas inundables? ¿Cómo se distribuyen los accidentes de obra en el espacio?

En infraestructura vial y de puentes, el dónde es tan importante como el qué.

---

## 1. Conceptos fundamentales

### Sistema de coordenadas (CRS)
Todo dato geoespacial tiene un sistema de referencia que define cómo se representan las ubicaciones en la Tierra.

- **WGS84 (EPSG:4326):** El más común. Es el que usa el GPS. Coordenadas en grados (longitud, latitud).
- **UTM (Universal Transverse Mercator):** Proyección en metros. Perú usa las zonas UTM 17S, 18S y 19S. Ideal para cálculos de área y distancia.
- **PSAD56:** Sistema antiguo usado en cartografía peruana anterior. Todavía aparece en documentos del IGN.

**Regla práctica:** Antes de cualquier análisis, asegúrate de que todos tus datos estén en el mismo CRS.

### Tipos de datos geoespaciales

**Datos vectoriales:** Representan geometrías discretas.
- **Puntos:** Ubicación de accidentes, estaciones meteorológicas, calicatas
- **Líneas:** Ejes de carreteras, ríos, trazas de puentes
- **Polígonos:** Zonas de riesgo, cuencas hidrográficas, distritos

**Datos raster:** Grilla regular de celdas con valores numéricos.
- Modelos digitales de elevación (DEM): altitud en cada punto del terreno
- Imágenes satelitales: valores de reflectancia por banda espectral
- Mapas de precipitación: lluvia acumulada por celda

---

## 2. Herramientas principales

### GeoPandas
Extiende Pandas para trabajar con datos geoespaciales vectoriales. Si sabes Pandas, ya casi sabes GeoPandas.

```python
import geopandas as gpd

# Leer shapefile de zonas de riesgo del CENEPRED
zonas_riesgo = gpd.read_file('zonas_riesgo_lima.shp')

# Reproyectar a UTM para cálculos en metros
zonas_riesgo_utm = zonas_riesgo.to_crs(epsg=32718)  # UTM zona 18S

# Filtrar zonas de riesgo alto
riesgo_alto = zonas_riesgo[zonas_riesgo['nivel'] == 'MUY ALTO']
```

### Folium
Genera mapas interactivos en HTML, visualizables en cualquier navegador o celular.

```python
import folium

mapa = folium.Map(location=[-12.046374, -77.042793], zoom_start=10)  # Lima

# Agregar marcador de proyecto
folium.Marker(
    location=[-11.98, -76.85],
    popup="Proyecto Puente Río Rimac",
    icon=folium.Icon(color='red')
).add_to(mapa)

mapa.save('mapa_proyecto.html')
```

### Rasterio
Para leer y procesar datos raster (DEMs, imágenes satelitales).

```python
import rasterio
import numpy as np

with rasterio.open('dem_lima.tif') as src:
    elevacion = src.read(1)  # Banda 1 = elevación en metros
    print(f"Elevación máxima: {elevacion.max()} m")
    print(f"Elevación mínima: {elevacion.min()} m")
```

### Google Earth Engine (Python API)
Acceso a décadas de imágenes satelitales y datos climáticos globales sin descargar nada. Corre en la nube de Google.

```python
import ee
ee.Initialize()

# Obtener imagen Landsat de la zona del proyecto
imagen = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
    .filterBounds(ee.Geometry.Point([-76.85, -11.98])) \
    .filterDate('2023-01-01', '2023-12-31') \
    .first()
```

---

## 3. Operaciones espaciales esenciales

### Buffer
Crear una zona de influencia alrededor de una geometría.
```python
# Zona de 500m alrededor del eje del puente
zona_influencia = eje_puente.buffer(500)  # en metros si el CRS es UTM
```

### Intersección espacial
Encontrar qué geometrías se superponen.
```python
# ¿Qué tramos de carretera cruzan zonas inundables?
tramos_en_riesgo = gpd.overlay(carretera, zonas_inundables, how='intersection')
```

### Spatial Join (unión espacial)
Combinar atributos de dos capas basándose en su relación espacial.
```python
# Asignar el nivel de riesgo del CENEPRED a cada punto de calicata
calicatas_con_riesgo = gpd.sjoin(calicatas, zonas_riesgo, how='left', predicate='within')
```

### Análisis de pendiente
A partir de un DEM, calcular la pendiente del terreno — crítica para diseño vial.

---

## 4. Fuentes de datos geoespaciales para Perú

| Fuente | Datos disponibles | URL |
|--------|------------------|-----|
| IGN | Cartografía base, curvas de nivel, hidrografía | geoportal.igm.gob.pe |
| CENEPRED | Zonas de riesgo por peligro natural | sigrid.cenepred.gob.pe |
| MINAM / GeoServidor | Cobertura vegetal, ecosistemas, clima | geoservidor.minam.gob.pe |
| SENAMHI | Estaciones meteorológicas, datos climáticos | senamhi.gob.pe |
| MTC | Red vial nacional, puentes inventariados | portal.mtc.gob.pe |
| INEI | Límites distritales, datos socioeconómicos | inei.gob.pe |
| Google Earth Engine | Imágenes satelitales, datos globales | earthengine.google.com |
| OpenTopography | DEMs globales (SRTM, ALOS) | opentopography.org |

---

## 5. Caso de uso: análisis de riesgo para traza vial

**Escenario:** Tienes la traza propuesta de una carretera en la sierra de Lima. Quieres identificar qué segmentos tienen mayor riesgo antes de iniciar el diseño.

**Proceso:**
1. Importar la traza en formato shapefile o KML
2. Descargar DEM (SRTM 30m) de la zona desde OpenTopography
3. Calcular pendiente del terreno a lo largo de la traza
4. Cruzar con mapa de zonas de riesgo del CENEPRED (deslizamientos, huaicos)
5. Cruzar con datos de precipitación histórica de SENAMHI
6. Generar mapa de calor de riesgo acumulado por segmento
7. Exportar a HTML con Folium para compartir con el equipo de diseño

---

## Conexión con proyectos de este repositorio

- `07_proyectos/riesgo_geoespacial/` — implementación completa del análisis de riesgo
- `04_fuentes_de_datos/datos_geoespaciales.md` — catálogo detallado de fuentes
