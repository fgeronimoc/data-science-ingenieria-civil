# Guía de Replicación — Dashboard Geoespacial SENAMHI
**Autor:** Fernando Geronimo Ccoillor Soto  
**Fecha:** Abril 2026  
**Proyecto:** Data Science aplicado a Ingeniería Civil — Perú

---

## ¿Qué construimos y por qué?

Construimos una **aplicación web profesional con Streamlit** que permite a cualquier persona de la empresa —sin saber Python— ingresar las coordenadas de un proyecto de infraestructura civil y obtener instantáneamente:

- Las 5 estaciones meteorológicas SENAMHI activas más cercanas
- Un mapa interactivo con distancias y datos de cada estación
- Gráficos de precipitación histórica de la zona
- Exportación a Excel, HTML y texto

La decisión de usar Streamlit (en lugar de un notebook o script) fue estratégica: convierte el análisis en una **herramienta de empresa** que se puede mostrar a gerencia, compartir con colegas y escalar con nuevas funciones.

---

## Estructura de archivos

```
PROYECTO_DATA_CIVIL_INGENIERIA/
│
├── 07_proyectos/riesgo_geoespacial/notebooks/
│   └── buscador_estaciones_senamhi.py    ← Módulo base (catálogo + funciones)
│
└── 08_dashboards/senamhi_app/
    ├── app.py                            ← App Streamlit principal
    ├── requirements.txt                  ← Dependencias del proyecto
    └── GUIA_REPLICACION.md               ← Este archivo
```

**Principio clave:** `app.py` importa funciones de `buscador_estaciones_senamhi.py`.  
Nunca duplicamos código — si hay que actualizar el catálogo de estaciones, se edita solo en un lugar.

---

## Paso 1 — Entorno de Python

### 1.1 Crear entorno virtual (recomendado)

```bash
# Crear entorno llamado "data-civil"
conda create -n data-civil python=3.11
conda activate data-civil

# O con venv puro:
python -m venv data-civil
data-civil\Scripts\activate        # Windows
source data-civil/bin/activate     # Linux/Mac
```

**¿Por qué un entorno virtual?**  
Evita conflictos entre versiones de librerías. Si un proyecto necesita pandas 2.0 y otro pandas 1.5, los entornos los mantienen separados.

### 1.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instala exactamente:

| Librería | Para qué sirve |
|---|---|
| `streamlit` | Framework para la aplicación web |
| `streamlit-folium` | Insertar mapas Folium dentro de Streamlit |
| `folium` | Generar mapas interactivos HTML con Leaflet.js |
| `pandas` | Manejo de tablas y datos |
| `numpy` | Cálculos matemáticos (Haversine) |
| `plotly` | Gráficos interactivos de precipitación |
| `pyproj` | Conversión de coordenadas UTM ↔ Geográficas |
| `openpyxl` | Exportar resultados a Excel |

---

## Paso 2 — El módulo base: buscador_estaciones_senamhi.py

Este archivo es el **corazón técnico** del proyecto. Contiene:

### 2.1 El catálogo de estaciones

```python
ESTACIONES_SENAMHI = [
    {
        "codigo":  "000401",       # Código oficial SENAMHI
        "nombre":  "Otuzco",       # Nombre de la estación
        "tipo":    "CO",           # Tipo: CO/CP/PLU/HLG/DCP
        "dpto":    "La Libertad",  # Departamento
        "prov":    "Otuzco",       # Provincia
        "dist":    "Otuzco",       # Distrito
        "lat":     -7.897,         # Latitud en grados decimales (negativo = sur)
        "lon":     -78.575,        # Longitud en grados decimales (negativo = oeste)
        "elev":    2641,           # Elevación en metros sobre el nivel del mar
        "activa":  True            # ¿La estación sigue operando?
    },
    # ... 147 estaciones más
]
```

**Tipos de estación:**
- `CP` — Climatológica Principal: mide temperatura, humedad, viento, lluvia, evaporación. La más completa.
- `CO` — Climatológica Ordinaria: igual que CP pero con menos variables o frecuencia.
- `PLU` — Pluviométrica: solo mide lluvia (precipitación). La más común en zonas rurales.
- `HLG` — Hidrológica: mide caudal de ríos.
- `DCP` — Automática: envía datos por satélite en tiempo real.

### 2.2 La función de distancia Haversine

```python
def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia en km entre dos puntos sobre la superficie
    de la Tierra, usando la fórmula Haversine.
    
    La Tierra no es plana, entonces no podemos usar Pitágoras directamente.
    Haversine tiene en cuenta la curvatura terrestre.
    """
    R = 6371.0  # Radio de la Tierra en km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat/2)**2
         + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2)
    return R * 2 * np.arcsin(np.sqrt(a))
```

**Precisión:** El error es < 0.3% para distancias menores a 1000 km — suficiente para nuestro uso.

### 2.3 Conversión UTM ↔ Geográficas

```python
def utm_a_geograficas(zona_utm, este, norte, hemisferio='S'):
    """
    Convierte UTM WGS84 → Latitud/Longitud.
    
    En Perú hay 3 zonas:
      17S → Piura, Tumbes (longitudes ~81° a ~75°W)
      18S → Lima, Cusco, Puno, mayoría del país (~75° a ~69°W)  
      19S → Extremo este de Madre de Dios (~69° a ~63°W)
    
    El código EPSG para cada zona es: 32700 + número de zona
      Zona 17S → EPSG:32717
      Zona 18S → EPSG:32718
      Zona 19S → EPSG:32719
    """
    epsg = 32700 + int(zona_utm)
    transformer = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(este, norte)
    return round(lat, 6), round(lon, 6)
```

**¿Por qué pyproj?** Es la librería estándar de la industria para conversiones cartográficas. Internamente usa PROJ, el mismo motor que usa QGIS y ArcGIS.

### 2.4 La función principal de búsqueda

```python
def buscar_estaciones(lat, lon, n=5, solo_activas=True):
    df = df_estaciones.copy()
    if solo_activas:
        df = df[df['activa'] == True]
    
    # Aplica Haversine a cada estación del catálogo
    df['distancia_km'] = df.apply(
        lambda row: haversine(lat, lon, row['lat'], row['lon']), axis=1
    )
    
    # Ordena por distancia y toma las N más cercanas
    return df.sort_values('distancia_km').head(n).reset_index(drop=True)
```

**Complejidad computacional:** O(n) — recorre las 148 estaciones una sola vez. En hardware moderno esto toma menos de 1 milisegundo.

---

## Paso 3 — La app Streamlit: app.py

### 3.1 Configuración inicial

```python
st.set_page_config(
    page_title="Dashboard SENAMHI — Perú",
    page_icon="🌦️",
    layout="wide",          # Usa todo el ancho de la pantalla
    initial_sidebar_state="expanded"
)
```

Esta es la primera línea que Streamlit ejecuta. Debe ir antes de cualquier otro elemento visual.

### 3.2 Estructura general de la app

```
app.py
│
├── CSS personalizado (st.markdown con <style>)
├── Datos de precipitación por región (diccionario)
├── Funciones auxiliares
│   ├── get_precip_data(dpto)      → datos climáticos según departamento
│   ├── generar_mapa_folium(...)   → mapa Leaflet con estaciones
│   └── exportar_excel(...)        → archivo .xlsx con resultados
│
├── SIDEBAR (panel izquierdo)
│   ├── Radio: Geográficas o UTM
│   ├── Inputs de coordenadas
│   ├── Nombre del proyecto
│   └── Botón "Analizar"
│
├── Estado de sesión (st.session_state)
│   → Guarda el último resultado para que no se borre al interactuar
│
├── Header con métricas rápidas (4 columnas)
│
└── Tabs principales
    ├── Tab 1: Mapa Folium interactivo
    ├── Tab 2: Tabla de estaciones (con buscador)
    ├── Tab 3: Gráficos de precipitación (Plotly)
    └── Tab 4: Exportar (Excel + HTML + TXT)
```

### 3.3 El concepto de st.session_state

```python
# ❌ Sin session_state — los resultados se pierden cada vez que
#    el usuario hace clic en cualquier cosa de la interfaz:
df = buscar_estaciones(lat, lon)   # Se re-ejecuta con cada interacción

# ✅ Con session_state — los resultados persisten hasta que
#    el usuario presione "Analizar" explícitamente:
if 'df_result' not in st.session_state:
    st.session_state.df_result = None

if btn_analizar or st.session_state.df_result is None:
    st.session_state.df_result = buscar_estaciones(lat, lon)

df = st.session_state.df_result   # Usa el resultado guardado
```

**¿Por qué importa?** Streamlit re-ejecuta todo el script de arriba hacia abajo cada vez que el usuario interactúa. Sin session_state, el mapa se regeneraría al hacer clic en un tab, lo cual es lento y confuso.

### 3.4 Cómo funciona el mapa dentro de Streamlit

```python
# Genera el mapa Folium normalmente (es un objeto Python)
mapa_f = generar_mapa_folium(lat, lon, nombre, df)

# streamlit-folium lo inserta dentro de la app como un iframe
st_folium(mapa_f, width=None, height=520, returned_objects=[])
```

`streamlit-folium` convierte el mapa Folium en HTML y lo incrusta. `returned_objects=[]` evita que el mapa envíe datos de vuelta a Python (lo que causaría re-ejecuciones innecesarias).

### 3.5 Cómo funciona la exportación a Excel

```python
def exportar_excel(df_cercanas, lat, lon, nombre):
    output = io.BytesIO()    # Buffer en memoria (no crea archivo en disco)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_cercanas.to_excel(writer, sheet_name='Estaciones Cercanas', index=False)
        info.to_excel(writer, sheet_name='Info Proyecto', index=False)
    return output.getvalue()  # Bytes del archivo Excel

# En la app:
excel_data = exportar_excel(df, lat, lon, nombre)
st.download_button(
    label="⬇️ Descargar Excel",
    data=excel_data,                    # Los bytes del archivo
    file_name="estaciones_sauco.xlsx",  # Nombre al descargar
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
```

**Clave:** Usamos `io.BytesIO()` para generar el archivo en memoria RAM, no en disco. Streamlit lo sirve directamente al navegador del usuario.

---

## Paso 4 — Ejecutar la app

### En tu máquina (desarrollo)

```bash
# 1. Activar el entorno
conda activate data-civil

# 2. Ir a la carpeta de la app
cd C:\Users\ferge\Downloads\PROYECTO_DATA_CIVIL_INGENIERIA\08_dashboards\senamhi_app

# 3. Ejecutar
streamlit run app.py

# Streamlit abre automáticamente el navegador en:
# http://localhost:8501
```

### En red local (compartir con colegas)

```bash
# Ejecutar escuchando en todas las interfaces de red
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

# Tus colegas acceden desde su navegador con:
# http://TU_IP_LOCAL:8501
# (ej: http://192.168.1.100:8501)
```

Para encontrar tu IP local en Windows: `ipconfig` → "Dirección IPv4"

### En internet (deploy gratuito con Streamlit Cloud)

```bash
# 1. Subir el proyecto a GitHub (repositorio público o privado)
git push origin main

# 2. Ir a share.streamlit.io
# 3. Conectar tu repositorio de GitHub
# 4. Especificar la ruta: 08_dashboards/senamhi_app/app.py
# 5. Deploy — Streamlit asigna una URL pública gratis

# Resultado: https://tu-usuario-senamhi-app.streamlit.app
```

---

## Paso 5 — Cómo agregar una nueva estación al catálogo

Editar `buscador_estaciones_senamhi.py` y agregar una entrada al diccionario `ESTACIONES_SENAMHI`:

```python
{"codigo":"000413","nombre":"Nueva Estación", "tipo":"CO",
 "dpto":"La Libertad","prov":"Otuzco","dist":"Agallpampa",
 "lat":-7.850,"lon":-78.520,"elev":3100,"activa":True},
```

Los datos los encuentras en: **senamhi.gob.pe → Datos Históricos → Catálogo de Estaciones**

---

## Paso 6 — Cómo agregar nuevas secciones a la app

La estructura de tabs hace fácil agregar nuevas funciones:

```python
# En app.py, agregar un tab nuevo:
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Mapa Interactivo",
    "📊 Tabla de Estaciones", 
    "🌧️ Análisis Climático",
    "📥 Exportar",
    "⛰️ Análisis DEM"      # ← Nuevo tab
])

with tab5:
    st.markdown("#### Análisis de terreno con DEM NASA SRTM")
    # ... nuevo código aquí
```

---

## Decisiones técnicas tomadas y por qué

| Decisión | Alternativa descartada | Razón |
|---|---|---|
| Streamlit | Flask / Django | Streamlit no requiere HTML/CSS/JS. Ideal para data science. |
| Folium + streamlit-folium | Plotly Maps | Folium tiene más control sobre capas WMS y marcadores personalizados. |
| Catálogo local (dict) | API SENAMHI en vivo | La API de SENAMHI no tiene CORS libre. El catálogo local funciona offline. |
| pyproj para UTM | Fórmulas manuales | pyproj tiene precisión milimétrica y cubre todos los datums (WGS84, PSAD56). |
| io.BytesIO para Excel | Guardar a disco | Más limpio: no genera archivos temporales en el servidor. |
| st.session_state | Sin estado | Evita re-ejecuciones costosas al interactuar con tabs o botones. |
| Plotly para gráficos | Matplotlib | Plotly es interactivo (zoom, hover). Matplotlib genera imágenes estáticas. |

---

## Próximos módulos a agregar (roadmap)

1. **Capas WMS oficiales** → agregar en Tab 1, sección de capas CENEPRED/ANA
2. **Análisis DEM** → nuevo Tab con pendiente, cuencas, perfil real de elevación
3. **Modelo de susceptibilidad** → Tab con mapa de riesgo calculado
4. **Datos en tiempo real** → sismos USGS + alertas SENAMHI vía API
5. **Multi-proyecto** → comparar varias coordenadas simultáneamente

---

## Recursos para seguir aprendiendo

| Recurso | URL |
|---|---|
| Documentación Streamlit | docs.streamlit.io |
| Galería de ejemplos Streamlit | streamlit.io/gallery |
| Folium documentación | python-visualization.github.io/folium |
| Catálogo estaciones SENAMHI | senamhi.gob.pe/main.php?dp=meteorologia&p=estaciones |
| SIGRID CENEPRED (WMS) | sigrid.cenepred.gob.pe |
| DEM NASA SRTM gratuito | earthexplorer.usgs.gov |
| Copernicus DEM 30m | copernicus.eu/en/access-data |

---

*Documento generado como parte del proyecto "Data Science en Ingeniería Civil — Perú"*  
*Fernando Geronimo Ccoillor Soto — Abril 2026*
