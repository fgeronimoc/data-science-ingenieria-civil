# Fuentes de Datos Geoespaciales

Datos de ubicación, terreno, riesgo y cobertura del suelo disponibles gratuitamente para análisis de proyectos de infraestructura en Perú.

---

## IGN — Instituto Geográfico Nacional del Perú

**URL:** geoportal.igm.gob.pe
**Datos disponibles:**
- Cartografía base nacional (escala 1:100,000 y 1:25,000)
- Curvas de nivel (topografía)
- Red hidrográfica (ríos, quebradas, lagos)
- Límites políticos (departamentos, provincias, distritos)
- Puntos geodésicos de control

**Formato:** Shapefile, KMZ, WMS (servicio de mapa web)
**Acceso:** Gratuito, descarga directa desde el geoportal

**Cómo usarlo en Python:**
```python
import geopandas as gpd

# Cargar red hidrográfica de una región
rios = gpd.read_file('rios_lima.shp')
rios.plot(figsize=(10,8), color='blue')
```

---

## CENEPRED — Centro Nacional de Estimación, Prevención y Reducción del Riesgo de Desastres

**URL:** sigrid.cenepred.gob.pe
**Datos disponibles:**
- Zonas de susceptibilidad a deslizamientos
- Zonas de susceptibilidad a inundaciones
- Zonas de susceptibilidad a huaicos (flujos de detritos)
- Peligro sísmico
- Vulnerabilidad social

**Formato:** Shapefile, visualización en visor web
**Acceso:** Gratuito

**Uso directo en proyectos:** Cruzar la traza de una carretera o la ubicación de un puente con estos mapas de peligro es la aplicación más inmediata y valiosa para obras de infraestructura.

```python
import geopandas as gpd

traza_carretera = gpd.read_file('traza_proyecto.shp').to_crs(epsg=32718)
zonas_huaico = gpd.read_file('susceptibilidad_huaico.shp').to_crs(epsg=32718)

# Intersección: qué tramos están en zona de huaico
tramos_en_riesgo = gpd.overlay(traza_carretera, zonas_huaico, how='intersection')
print(f"Longitud en zona de huaico: {tramos_en_riesgo.geometry.length.sum()/1000:.2f} km")
```

---

## GeoServidor MINAM

**URL:** geoservidor.minam.gob.pe
**Datos disponibles:**
- Cobertura vegetal y uso del suelo
- Ecosistemas del Perú
- Áreas naturales protegidas
- Zonas de amortiguamiento
- Datos de cambio climático

**Formato:** Shapefile, GeoTIFF, WMS
**Acceso:** Gratuito

**Relevancia para proyectos de infraestructura:** Identificar si la traza de una vía cruza áreas protegidas o ecosistemas frágiles — información crítica para los estudios de impacto ambiental (EIA).

---

## SRTM y ALOS — Modelos Digitales de Elevación

**Fuentes:**
- **SRTM (NASA):** Resolución 30m global. Acceso via OpenTopography o EarthExplorer.
- **ALOS PALSAR:** Resolución 12.5m. Mejor calidad en zonas montañosas.
- **Copernicus DEM:** Resolución 30m y 90m. La opción más actualizada.

**URL:** opentopography.org | earthexplorer.usgs.gov

**Uso en proyectos:**
```python
import rasterio
import numpy as np
from rasterio.plot import show

with rasterio.open('dem_proyecto.tif') as src:
    dem = src.read(1)
    perfil = src.profile

# Calcular pendiente
from scipy.ndimage import sobel
dx = sobel(dem, axis=1)
dy = sobel(dem, axis=0)
pendiente = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))

print(f"Pendiente máxima en la zona: {pendiente.max():.1f}°")
print(f"Pendiente promedio: {pendiente.mean():.1f}°")
```

---

## MTC — Ministerio de Transportes y Comunicaciones

**URL:** portal.mtc.gob.pe → SIG vial
**Datos disponibles:**
- Red vial nacional (rutas, clasificación, estado de conservación)
- Inventario de puentes (ubicación, tipo, estado)
- Datos de accidentes de tránsito por tramo

**Formato:** Shapefile, KML, visualización web
**Acceso:** Gratuito

**Relevancia directa:** El inventario de puentes del MTC es un dataset inmediato para análisis de estado de infraestructura y priorización de mantenimiento.

---

## ANA — Autoridad Nacional del Agua

**URL:** ana.gob.pe
**Datos disponibles:**
- Red hidrográfica oficial del Perú
- Cuencas hidrográficas delimitadas
- Datos de caudales históricos en estaciones hidrológicas
- Zonas de inundación históricas

**Relevancia:** Para proyectos de puentes, el caudal máximo del río es el parámetro de diseño crítico. Los datos históricos del ANA permiten validar los parámetros hidráulicos del diseño.

---

## Google Earth Engine — Imágenes satelitales

**URL:** earthengine.google.com
**Datos disponibles:**
- Landsat (1972 - presente): imágenes multiespectrales cada 16 días
- Sentinel-2 (2015 - presente): resolución 10m, cada 5 días
- MODIS: resolución 250m-1km, diaria
- Datos de cobertura del suelo, vegetación (NDVI), humedad del suelo

**Acceso:** Gratuito con cuenta Google (para uso no comercial)

```python
import ee
ee.Initialize()

# NDVI (Índice de Vegetación) en zona del proyecto
# Útil para evaluar cobertura vegetal antes de deforestar
sentinel = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filterDate('2024-01-01', '2024-06-30') \
    .filterBounds(ee.Geometry.Point([-76.85, -11.98])) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
    .first()

ndvi = sentinel.normalizedDifference(['B8', 'B4']).rename('NDVI')
```

---

## Tabla resumen de fuentes geoespaciales

| Fuente | Tipo de dato | Escala/Resolución | Formato | Acceso |
|--------|-------------|-------------------|---------|--------|
| IGN | Vectorial | 1:25,000 | SHP, KMZ | Gratuito |
| CENEPRED | Vectorial raster | Variable | SHP, TIF | Gratuito |
| MINAM GeoServidor | Vectorial raster | Variable | SHP, WMS | Gratuito |
| SRTM (NASA) | Raster DEM | 30m | GeoTIFF | Gratuito |
| ALOS DEM | Raster DEM | 12.5m | GeoTIFF | Gratuito |
| MTC SIG Vial | Vectorial | 1:100,000 | SHP, KML | Gratuito |
| ANA | Vectorial | Variable | SHP | Gratuito |
| Sentinel-2 (GEE) | Raster imagen | 10m | via API | Gratuito |
| Landsat (GEE) | Raster imagen | 30m | via API | Gratuito |
