# Fuentes de Datos Climáticos

El clima es la variable externa con mayor impacto en la ejecución de obras de infraestructura en Perú. Estas son las fuentes disponibles, gratuitas y confiables.

---

## SENAMHI — Servicio Nacional de Meteorología e Hidrología del Perú

**URL:** senamhi.gob.pe
**Tipo de datos:** Precipitación, temperatura, humedad, viento, radiación solar
**Cobertura:** Red de estaciones meteorológicas en todo Perú
**Frecuencia:** Diaria, horaria en algunas estaciones
**Formato:** CSV descargable desde el portal

**Cómo acceder:**
1. Ir a senamhi.gob.pe → Datos Históricos
2. Seleccionar la estación más cercana al proyecto
3. Seleccionar variables y rango de fechas
4. Descargar en CSV

**Código de descarga programática:**
```python
# SENAMHI no tiene API oficial documentada
# Opción 1: Descarga manual del portal
# Opción 2: Usar el paquete senamhi-data (Python)
# pip install senamhidata

import senamhidata as sh
# Listar estaciones disponibles
estaciones = sh.get_stations()
# Descargar datos de una estación
datos = sh.get_data(station_id='000401', variable='Precipitacion')
```

**Limitaciones:** No todas las estaciones tienen datos completos ni continuos. Es normal encontrar períodos con datos faltantes que requieren imputación.

---

## ERA5 — ECMWF Reanalysis

**URL:** cds.climate.copernicus.eu
**Tipo de datos:** Reanálisis climático global — reconstrucción histórica de condiciones atmosféricas desde 1940
**Cobertura:** Global, con resolución de ~31km
**Frecuencia:** Horaria
**Formato:** NetCDF (requiere librería xarray para procesar)

**Por qué usarlo:** Cuando SENAMHI no tiene datos para una zona remota, ERA5 ofrece datos históricos consistentes para cualquier punto del planeta.

**Cómo acceder:**
1. Crear cuenta gratuita en Copernicus CDS
2. Instalar el paquete cdsapi
3. Descargar via API

```python
import cdsapi

c = cdsapi.Client()
c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': 'total_precipitation',
        'year': '2023',
        'month': ['01', '02', '03'],
        'day': [f'{d:02d}' for d in range(1, 32)],
        'time': '12:00',
        'area': [-8, -82, -18, -68],  # [Norte, Oeste, Sur, Este] — Perú
        'format': 'netcdf',
    },
    'precipitacion_peru_2023.nc'
)
```

---

## OpenWeather API

**URL:** openweathermap.org
**Tipo de datos:** Pronóstico climático (hasta 7 días) y datos históricos
**Cobertura:** Global
**Frecuencia:** Horaria
**Formato:** JSON via API REST

**Plan gratuito:** 1,000 llamadas/día — suficiente para un sistema de monitoreo básico.

```python
import requests

API_KEY = 'tu_api_key_aqui'
lat, lon = -12.046374, -77.042793  # Lima

url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=es'
response = requests.get(url)
datos = response.json()

# Extraer precipitación de los próximos 5 días
for item in datos['list']:
    fecha = item['dt_txt']
    lluvia = item.get('rain', {}).get('3h', 0)
    print(f"{fecha}: {lluvia} mm")
```

---

## Google Earth Engine — Datos climáticos satelitales

**URL:** earthengine.google.com
**Tipo de datos:** CHIRPS (precipitación), MODIS (temperatura superficie), ERA5 en GEE
**Cobertura:** Global
**Acceso:** Gratuito con cuenta académica o personal

```python
import ee
ee.Initialize()

# Precipitación CHIRPS para Lima, 2023
precipitacion = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY') \
    .filterDate('2023-01-01', '2023-12-31') \
    .filterBounds(ee.Geometry.Point([-77.04, -12.05]))

# Obtener serie de tiempo
def extraer_valor(image):
    valor = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=ee.Geometry.Point([-77.04, -12.05]),
        scale=5000
    )
    return image.set('date', image.date().format()).set(valor)

serie = precipitacion.map(extraer_valor)
```

---

## Tabla resumen de fuentes climáticas

| Fuente | Costo | Cobertura | Resolución | Mejor uso |
|--------|-------|-----------|------------|-----------|
| SENAMHI | Gratuito | Perú | Estación puntual | Datos históricos de zona específica |
| ERA5 | Gratuito | Global | ~31 km | Zonas sin estación SENAMHI |
| OpenWeather | Gratuito (básico) | Global | Ciudad | Pronóstico en tiempo real |
| CHIRPS (GEE) | Gratuito | Global | ~5 km | Series de tiempo de lluvia consistentes |
| Tomorrow.io | Freemium | Global | 1 km | Pronóstico de alta resolución |

---

## Variables climáticas críticas para construcción

| Variable | Umbral crítico | Impacto en obra |
|----------|---------------|-----------------|
| Precipitación | > 10 mm/día | Paralización de movimiento de tierras y vaciados |
| Temperatura | < 5°C o > 35°C | Afecta hidratación del concreto |
| Viento | > 50 km/h | Peligro en trabajos en altura, izaje |
| Humedad relativa | > 85% | Afecta tiempos de fraguado y pintura |
| Temperatura de superficie | Variable | Control de curado de asfalto |
