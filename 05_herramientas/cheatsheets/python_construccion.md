# Cheatsheet — Python para Construcción

Comandos y patrones de uso frecuente en proyectos de data science aplicados a construcción.

---

## Manejo de fechas (crítico para cronogramas)
```python
import pandas as pd

# Convertir columna de fechas
df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True)

# Calcular duración entre fechas
df['duracion_dias'] = (df['fecha_fin'] - df['fecha_inicio']).dt.days

# Semana del año
df['semana'] = df['fecha'].dt.isocalendar().week

# Mes y año
df['mes'] = df['fecha'].dt.month
df['anio'] = df['fecha'].dt.year

# Filtrar por rango de fechas
obra_2024 = df[(df['fecha'] >= '2024-01-01') & (df['fecha'] <= '2024-12-31')]

# Resamplear a frecuencia semanal
semanal = df.set_index('fecha').resample('W').agg({'avance': 'sum', 'lluvia': 'sum'})
```

---

## Lectura de archivos comunes en construcción
```python
# Excel con múltiples hojas (valorización, cronograma)
excel = pd.ExcelFile('valorización_marzo.xlsx')
print(excel.sheet_names)
df = pd.read_excel('valorización_marzo.xlsx', sheet_name='Avance')

# CSV con encoding peruano (tildes)
df = pd.read_csv('parte_diario.csv', encoding='latin1', sep=';')

# Shapefile geoespacial
import geopandas as gpd
zonas = gpd.read_file('zonas_riesgo.shp')
```

---

## Limpieza rápida de datos de obra
```python
# Eliminar filas vacías y duplicados
df = df.dropna(how='all').drop_duplicates()

# Limpiar nombres de columnas
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Estandarizar texto (tildes, mayúsculas)
df['actividad'] = df['actividad'].str.strip().str.title()

# Ver datos faltantes
print(df.isnull().sum())
print(df.isnull().mean() * 100)  # Porcentaje de nulos
```

---

## Análisis de avance de obra
```python
# Calcular SPI (Schedule Performance Index)
df['spi'] = df['avance_real_pct'] / df['avance_planificado_pct']
df['estado'] = df['spi'].apply(lambda x: 'Adelantado' if x > 1.05 else ('Retrasado' if x < 0.95 else 'En plazo'))

# Proyección de fecha de término
avance_semanal_promedio = df['avance_semanal'].mean()
avance_restante = 1 - df['avance_real_pct'].iloc[-1]
semanas_restantes = avance_restante / avance_semanal_promedio
```

---

## Pronóstico rápido con Prophet
```python
from prophet import Prophet
import pandas as pd

# Preparar datos (columnas obligatorias: ds y y)
df_prophet = df[['fecha', 'lluvia_mm']].rename(columns={'fecha': 'ds', 'lluvia_mm': 'y'})

# Entrenar modelo
modelo = Prophet(yearly_seasonality=True, weekly_seasonality=False)
modelo.fit(df_prophet)

# Pronosticar 30 días hacia adelante
futuro = modelo.make_future_dataframe(periods=30)
pronostico = modelo.predict(futuro)

# Ver resultados
print(pronostico[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30))
```

---

## Mapa interactivo rápido con Folium
```python
import folium

# Coordenadas del proyecto (ejemplo: obra en Huarochirí)
lat, lon = -11.98, -76.60

mapa = folium.Map(location=[lat, lon], zoom_start=13)

# Marcador de la obra
folium.Marker(
    [lat, lon],
    popup='Proyecto Puente Río Santa Eulalia',
    tooltip='Click para info',
    icon=folium.Icon(color='red', icon='info-sign')
).add_to(mapa)

# Círculo de zona de influencia (500m)
folium.Circle([lat, lon], radius=500, color='orange', fill=True, fillOpacity=0.2).add_to(mapa)

# Guardar
mapa.save('mapa_proyecto.html')
print("Mapa guardado. Abrir en navegador.")
```

---

## YOLO — Detección rápida en imagen
```python
from ultralytics import YOLO

# Cargar modelo
modelo = YOLO('yolov8n.pt')  # nano: rápido | yolov8x.pt: más preciso

# Detectar en imagen
resultados = modelo('foto_obra.jpg', conf=0.5)
resultados[0].show()
resultados[0].save('deteccion_resultado.jpg')

# Detectar en video
modelo.predict(source='video_obra.mp4', save=True, conf=0.4, show=True)

# Ver clases detectadas
for r in resultados:
    for box in r.boxes:
        clase = modelo.names[int(box.cls)]
        confianza = float(box.conf)
        print(f"{clase}: {confianza:.2%}")
```
