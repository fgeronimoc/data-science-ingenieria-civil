"""
=============================================================================
MÓDULO DE ANÁLISIS DEM (Digital Elevation Model)
Análisis de terreno profesional para proyectos de infraestructura civil
=============================================================================
Autor  : Fernando Geronimo Ccoillor Soto
Fecha  : Abril 2026

FUNCIONES PRINCIPALES:
  generar_dem()            → Crea grilla de elevación (sintética o real)
  calcular_pendiente()     → Mapa de pendiente en grados (algoritmo Sobel)
  calcular_aspecto()       → Orientación de laderas (N/S/E/O)
  calcular_hillshade()     → Sombra de relieve (visual 3D)
  calcular_flujo_d8()      → Dirección de flujo (algoritmo D8)
  acumulacion_flujo()      → Acumulación de flujo (red de drenaje)
  delimitar_cuenca()       → Delimitación de cuenca hidrográfica
  perfil_elevacion()       → Perfil topográfico entre dos puntos
  clasificar_pendiente()   → Clasificación técnica de pendiente
  generar_figuras_dem()    → Figuras matplotlib listas para Streamlit
  generar_mapa_folium_dem()→ Mapa Folium con capas DEM

SOBRE EL DEM SINTÉTICO:
  Usa ruido fractal multicapa (suma de ondas senoidales a distintas
  frecuencias) + suavizado gaussiano para simular terreno Andino realista.
  La elevación base, amplitud y rugosidad se ajustan automáticamente
  según la altitud del punto ingresado.

PARA USAR CON DATOS SRTM REALES:
  Ver función cargar_dem_srtm() al final del archivo.
  Requiere: pip install elevation rasterio
=============================================================================
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LightSource
from scipy.ndimage import gaussian_filter, sobel, label, generate_binary_structure
from scipy.interpolate import RegularGridInterpolator
import io
import base64
import warnings
warnings.filterwarnings('ignore')

# Intento de importar folium (opcional para algunos contextos)
try:
    import folium
    FOLIUM_OK = True
except ImportError:
    FOLIUM_OK = False

# =============================================================================
# CONSTANTES
# =============================================================================
KM_POR_GRADO_LAT = 111.0        # 1° lat ≈ 111 km (constante)
COLORES_PENDIENTE = {
    "Plano"      : ("#FFFFCC", 0,  5),
    "Suave"      : ("#A1D99B", 5, 15),
    "Moderada"   : ("#FEC44F", 15, 30),
    "Escarpada"  : ("#F03B20", 30, 45),
    "Muy Escarpada": ("#99000D", 45, 90),
}

# =============================================================================
# 1. GENERACIÓN DEL DEM
# =============================================================================

def generar_dem(lat, lon, radio_km=5.0, elev_base=None,
                n_puntos=150, seed=42):
    """
    Genera una grilla DEM realista para el área alrededor del punto dado.

    Usa ruido fractal multicapa que simula la topografía Andina:
    ondas de baja frecuencia (crestas y valles principales) sumadas a
    ondas de alta frecuencia (microrrelieve) con suavizado gaussiano.

    Parámetros:
        lat, lon   : coordenadas del centro
        radio_km   : radio del área en km (default 5 km)
        elev_base  : elevación base en m.s.n.m. (None = estima por latitud)
        n_puntos   : resolución de la grilla (default 150×150)
        seed       : semilla aleatoria para reproducibilidad

    Retorna:
        dict con:
          lat_grid, lon_grid : grillas 2D de coordenadas
          dem                : grilla 2D de elevación (metros)
          cell_size_m        : tamaño de celda en metros
          radio_km           : radio usado
          elev_base          : elevación base usada
    """
    rng = np.random.default_rng(seed)

    # Elevación base según latitud (si no se especifica)
    if elev_base is None:
        lat_abs = abs(lat)
        if lat_abs < 5:    elev_base = 150    # Selva baja
        elif lat_abs < 8:  elev_base = 800    # Selva alta / ceja de selva
        elif lat_abs < 12: elev_base = 2500   # Sierra media
        else:              elev_base = 3200   # Sierra sur

    # Grilla de coordenadas
    km_per_deg_lon = KM_POR_GRADO_LAT * np.cos(np.radians(lat))
    rango_lat = radio_km / KM_POR_GRADO_LAT
    rango_lon = radio_km / km_per_deg_lon

    lats = np.linspace(lat - rango_lat, lat + rango_lat, n_puntos)
    lons = np.linspace(lon - rango_lon, lon + rango_lon, n_puntos)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Coordenadas normalizadas [-1, 1]
    x = (lon_grid - lon) / rango_lon
    y = (lat_grid - lat) / rango_lat

    # Tamaño de celda en metros
    cell_size_m = (2 * radio_km * 1000) / n_puntos

    # ── TERRENO FRACTAL MULTICAPA ────────────────────────────────────────────
    # Cada capa: frecuencia más alta = amplitud más pequeña (1/f noise)
    # Esto imita la textura real del terreno: valles/crestas + microrrelieve
    dem = np.full_like(x, float(elev_base))

    capas = [
        (1,   0.40),   # Valles y crestas principales (baja freq, alta amp)
        (2,   0.20),   # Ondulaciones secundarias
        (3,   0.12),   # Laderas
        (6,   0.06),   # Microrrelieve
        (12,  0.03),   # Rugosidad fina
        (24,  0.015),  # Textura muy fina
    ]

    # Amplitud total = ~35% de elevación base (típico Andes)
    amp_total = elev_base * 0.35

    for freq, peso in capas:
        angulo = rng.uniform(0, np.pi)
        fase_x = rng.uniform(0, 2 * np.pi)
        fase_y = rng.uniform(0, 2 * np.pi)

        # Onda en dirección aleatoria (simula crestas orientadas)
        eje = x * np.cos(angulo) + y * np.sin(angulo)
        dem += amp_total * peso * np.sin(freq * np.pi * eje + fase_x)

        # Segunda onda perpendicular (valles transversales)
        eje_perp = -x * np.sin(angulo) + y * np.cos(angulo)
        dem += amp_total * peso * 0.4 * np.cos(freq * np.pi * eje_perp + fase_y)

    # ── SUAVIZADO GAUSSIANO (simula erosión natural) ──────────────────────
    sigma = max(1, n_puntos // 50)
    dem = gaussian_filter(dem, sigma=sigma)

    # ── ASEGURAR MÍNIMO REALISTA ─────────────────────────────────────────
    dem = np.maximum(dem, elev_base * 0.3)

    # ── NORMALIZAR PARA CONTROLAR EL RANGO DE ELEVACIÓN ─────────────────
    # Escalar el DEM sintético para que tenga desnivel realista Andino
    dem_min, dem_max = dem.min(), dem.max()
    desnivel_objetivo = elev_base * 0.20   # ~20% de la elevación base
    dem = (dem - dem_min) / (dem_max - dem_min + 1e-9) * desnivel_objetivo
    dem += elev_base - desnivel_objetivo * 0.4   # centrar en elev_base

    # ── VALLE GARANTIZADO EN EL PUNTO CENTRAL ────────────────────────────
    # Estrategia: restar una cuenca hidrográfica sintética centrada en el
    # punto del proyecto. Usamos distancias desde el centro para crear
    # un relieve tipo "olla" con quebradas que drenen hacia el centro.
    dist2 = x**2 + y**2

    # Depresión principal (fondo del valle)
    profundidad = desnivel_objetivo * 0.60
    dem -= profundidad * np.exp(-dist2 / 0.08)

    # Dos quebradas tributarias (aguas arriba del centro)
    for angulo_q in [rng.uniform(0.3, 1.2), rng.uniform(1.8, 2.8)]:
        qx = np.cos(angulo_q); qy = np.sin(angulo_q)
        # Distancia al eje de la quebrada
        eje_q = x * qx + y * qy          # componente a lo largo de la quebrada
        perp_q = np.abs(-x * qy + y * qx)  # perpendicular al eje
        # Solo aguas arriba (eje_q > 0) y cerca del eje
        mask_q = (eje_q > 0) & (perp_q < 0.18)
        prof_q = profundidad * 0.35 * np.exp(-perp_q**2 / 0.01)
        # Gradiente: más profundo en el centro, sube hacia arriba
        grad_q = 1.0 / (1.0 + eje_q * 2)
        dem[mask_q] -= prof_q[mask_q] * grad_q[mask_q]

    # ── GARANTIZAR QUE EL CENTRO ES EL MÍNIMO GLOBAL ─────────────────────
    # Esto es clave para el algoritmo D8: el outlet (punto del proyecto)
    # debe ser el punto de menor elevación para que todo drene hacia él.
    # Estrategia: asignar directamente la celda central al valor mínimo
    # global menos un margen. Así D8 garantiza que los 8 vecinos drenen
    # al centro y la cuenca se puede trazar correctamente.
    cy_c, cx_c = n_puntos // 2, n_puntos // 2
    dem[cy_c, cx_c] = dem.min() - 5.0

    return {
        "lat_grid":    lat_grid,
        "lon_grid":    lon_grid,
        "dem":         dem,
        "cell_size_m": cell_size_m,
        "radio_km":    radio_km,
        "elev_base":   elev_base,
        "n_puntos":    n_puntos,
        "lat_centro":  lat,
        "lon_centro":  lon,
    }


# =============================================================================
# 2. PENDIENTE (SLOPE)
# =============================================================================

def calcular_pendiente(dem, cell_size_m):
    """
    Calcula la pendiente en grados para cada celda del DEM.

    Algoritmo: operador Sobel (estándar ESRI/ArcGIS) — calcula el
    gradiente en X e Y con una ventana 3×3 centrada en cada celda.

    Fórmula:
        dz_dx = gradiente este-oeste / 8*cell_size
        dz_dy = gradiente norte-sur  / 8*cell_size
        pendiente = atan(sqrt(dz_dx² + dz_dy²)) en grados

    Parámetros:
        dem         : array 2D de elevación
        cell_size_m : tamaño de celda en metros

    Retorna:
        slope_deg : array 2D de pendiente en grados (0-90°)
    """
    dz_dx = sobel(dem, axis=1) / (8.0 * cell_size_m)
    dz_dy = sobel(dem, axis=0) / (8.0 * cell_size_m)
    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    return np.degrees(slope_rad)


# =============================================================================
# 3. ASPECTO (ASPECT)
# =============================================================================

def calcular_aspecto(dem, cell_size_m):
    """
    Calcula la orientación de las laderas (aspecto) en grados (0-360°).
    0° = Norte, 90° = Este, 180° = Sur, 270° = Oeste.

    En análisis de riesgo por huaicos: las laderas orientadas al norte
    (en el hemisferio sur) reciben más lluvia orográfica.
    """
    dz_dx = sobel(dem, axis=1) / (8.0 * cell_size_m)
    dz_dy = sobel(dem, axis=0) / (8.0 * cell_size_m)

    aspecto = np.degrees(np.arctan2(-dz_dy, dz_dx))
    aspecto = 90 - aspecto
    aspecto = np.where(aspecto < 0, aspecto + 360, aspecto)
    return aspecto


# =============================================================================
# 4. HILLSHADE (SOMBRA DE RELIEVE)
# =============================================================================

def calcular_hillshade(dem, cell_size_m, azimuth=315.0, altitud_sol=45.0):
    """
    Calcula el hillshade (sombra de relieve) para visualización 3D.

    El hillshade simula la iluminación de un sol virtual en un ángulo dado,
    resaltando la topografía. Es el fondo de la mayoría de mapas ArcGIS Pro.

    Parámetros:
        azimuth     : dirección del sol en grados (0=N, 90=E, 315=NW estándar)
        altitud_sol : ángulo de elevación del sol (45° estándar)

    Retorna:
        hillshade : array 2D de 0-255 (0=sombra, 255=máxima iluminación)
    """
    az_rad  = np.radians(360 - azimuth + 90)
    alt_rad = np.radians(altitud_sol)

    dz_dx = sobel(dem, axis=1) / (8.0 * cell_size_m)
    dz_dy = sobel(dem, axis=0) / (8.0 * cell_size_m)

    slope_rad  = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    aspecto_rad = np.arctan2(-dz_dy, dz_dx)

    hillshade = (
        np.cos(alt_rad) * np.cos(slope_rad)
        + np.sin(alt_rad) * np.sin(slope_rad) * np.cos(az_rad - aspecto_rad)
    )
    hillshade = np.clip(hillshade, 0, 1) * 255
    return hillshade.astype(np.uint8)


# =============================================================================
# 5. FLUJO D8 (DIRECCIÓN DE FLUJO)
# =============================================================================

def calcular_flujo_d8(dem):
    """
    Calcula la dirección de flujo usando el algoritmo D8 (Eight-Direction).

    D8 es el algoritmo estándar en hidrología GIS (ArcGIS, QGIS, GRASS).
    Para cada celda, el agua fluye hacia el vecino con la mayor pendiente
    descendente entre las 8 celdas adyacentes.

    Retorna:
        flow_dir : array 2D con índice del vecino al que fluye (0-7)
                   0=E, 1=SE, 2=S, 3=SW, 4=W, 5=NW, 6=N, 7=NE
    """
    ny, nx = dem.shape
    flow_dir = np.zeros((ny, nx), dtype=np.int8)

    # Los 8 vecinos: (dy, dx) y distancia
    vecinos = [
        (0,  1,  1.0),    # E
        (1,  1,  1.414),  # SE
        (1,  0,  1.0),    # S
        (1, -1,  1.414),  # SW
        (0, -1,  1.0),    # W
        (-1,-1,  1.414),  # NW
        (-1, 0,  1.0),    # N
        (-1, 1,  1.414),  # NE
    ]

    # Padding para manejar bordes
    dem_pad = np.pad(dem, 1, mode='edge')

    for i in range(ny):
        for j in range(nx):
            max_slope = -np.inf
            best_dir  = 0
            for k, (di, dj, dist) in enumerate(vecinos):
                slope = (dem_pad[i+1, j+1] - dem_pad[i+1+di, j+1+dj]) / dist
                if slope > max_slope:
                    max_slope = slope
                    best_dir  = k
            flow_dir[i, j] = best_dir

    return flow_dir


def acumulacion_flujo(flow_dir, dem):
    """
    Calcula la acumulación de flujo: cuántas celdas drenan hacia cada celda.
    Las celdas con alta acumulación forman la red de drenaje (ríos y quebradas).

    Parámetros:
        flow_dir : salida de calcular_flujo_d8()
        dem      : array 2D de elevación

    Retorna:
        acc : array 2D de acumulación (0 = divisoria de aguas, alto = río)
    """
    ny, nx = dem.shape
    acc = np.ones((ny, nx), dtype=np.int32)

    # Vectores de movimiento para cada dirección D8
    dy = [0,  1,  1,  1,  0, -1, -1, -1]
    dx = [1,  1,  0, -1, -1, -1,  0,  1]

    # Ordenar celdas de mayor a menor elevación (procesar desde crestas)
    orden = np.argsort(dem.ravel())[::-1]

    for idx in orden:
        i, j = divmod(idx, nx)
        if 0 < i < ny-1 and 0 < j < nx-1:
            d  = int(flow_dir[i, j])
            ni = i + dy[d]
            nj = j + dx[d]
            if 0 <= ni < ny and 0 <= nj < nx:
                acc[ni, nj] += acc[i, j]

    return acc


# =============================================================================
# 6. DELIMITACIÓN DE CUENCA
# =============================================================================

def delimitar_cuenca(dem_data, umbral_flujo=300):
    """
    Delimita la cuenca hidrográfica que drena hacia el punto central del DEM.

    Proceso:
      1. Calcula flujo D8
      2. Calcula acumulación de flujo
      3. La cuenca = todas las celdas que eventualmente drenan al punto central
      4. La red de drenaje = celdas con acumulación > umbral

    Parámetros:
        dem_data    : dict de salida de generar_dem()
        umbral_flujo: mínima acumulación para considerar un cauce (default 300)

    Retorna:
        dict con flow_dir, acc, cuenca_mask, red_drenaje_mask, area_km2
    """
    dem = dem_data["dem"]
    cell_size_m = dem_data["cell_size_m"]
    ny, nx = dem.shape
    cy, cx = ny // 2, nx // 2   # Punto central = ubicación del proyecto

    # Calcular flujo
    flow_dir = calcular_flujo_d8(dem)
    acc      = acumulacion_flujo(flow_dir, dem)

    # ── Trazar cuenca desde el punto de salida (outlet) ─────────────────────
    # Una celda pertenece a la cuenca si su flujo llega al outlet
    dy = [0,  1,  1,  1,  0, -1, -1, -1]
    dx = [1,  1,  0, -1, -1, -1,  0,  1]
    # Dirección inversa para trazar aguas arriba
    inv = [4,  5,  6,  7,  0,  1,  2,  3]

    cuenca = np.zeros((ny, nx), dtype=bool)
    cuenca[cy, cx] = True
    cola = [(cy, cx)]

    while cola:
        i, j = cola.pop()
        for k in range(8):
            ni, nj = i + dy[k], j + dx[k]
            if 0 <= ni < ny and 0 <= nj < nx and not cuenca[ni, nj]:
                if flow_dir[ni, nj] == inv[k]:
                    cuenca[ni, nj] = True
                    cola.append((ni, nj))

    # Red de drenaje (celdas con alta acumulación dentro de la cuenca)
    red_drenaje = (acc > umbral_flujo) & cuenca

    # Área de la cuenca en km²
    area_celdas = np.sum(cuenca)
    area_km2    = area_celdas * (cell_size_m / 1000) ** 2

    return {
        "flow_dir":       flow_dir,
        "acc":            acc,
        "cuenca_mask":    cuenca,
        "red_drenaje":    red_drenaje,
        "area_km2":       round(area_km2, 2),
        "n_celdas":       int(area_celdas),
    }


# =============================================================================
# 7. PERFIL DE ELEVACIÓN
# =============================================================================

def perfil_elevacion(dem_data, angulo_grados=45, n_puntos=200):
    """
    Extrae el perfil de elevación a lo largo de una línea que pasa por el
    punto central del DEM en la dirección dada.

    Parámetros:
        dem_data      : dict de salida de generar_dem()
        angulo_grados : ángulo del transecto (0=E-O, 45=NE-SO, 90=N-S)
        n_puntos      : resolución del perfil

    Retorna:
        dict con distancias_km, elevaciones, stats
    """
    dem      = dem_data["dem"]
    lat_grid = dem_data["lat_grid"]
    lon_grid = dem_data["lon_grid"]
    ny, nx   = dem.shape

    lats = lat_grid[:, 0]
    lons = lon_grid[0, :]

    interpolador = RegularGridInterpolator(
        (lats[::-1], lons), dem[::-1, :],
        method='linear', bounds_error=False, fill_value=None
    )

    lat_c = dem_data["lat_centro"]
    lon_c = dem_data["lon_centro"]
    radio = dem_data["radio_km"]

    km_per_lon = KM_POR_GRADO_LAT * np.cos(np.radians(lat_c))
    ang_rad    = np.radians(angulo_grados)

    t = np.linspace(-0.9, 0.9, n_puntos)
    lats_linea = lat_c + t * radio / KM_POR_GRADO_LAT * np.sin(ang_rad)
    lons_linea = lon_c + t * radio / km_per_lon * np.cos(ang_rad)

    puntos = np.column_stack([lats_linea, lons_linea])
    elevs  = interpolador(puntos)

    # Distancias acumuladas en km
    dlat_km = np.diff(lats_linea) * KM_POR_GRADO_LAT
    dlon_km = np.diff(lons_linea) * km_per_lon
    dists   = np.concatenate([[0], np.cumsum(np.sqrt(dlat_km**2 + dlon_km**2))])

    return {
        "distancias_km": dists,
        "elevaciones":   elevs,
        "lats":          lats_linea,
        "lons":          lons_linea,
        "stats": {
            "elev_min":    float(np.nanmin(elevs)),
            "elev_max":    float(np.nanmax(elevs)),
            "elev_media":  float(np.nanmean(elevs)),
            "desnivel_m":  float(np.nanmax(elevs) - np.nanmin(elevs)),
            "longitud_km": float(dists[-1]),
            "pendiente_media_pct": float(
                np.nanmean(np.abs(np.diff(elevs))) /
                (dists[1] * 1000) * 100 if len(dists) > 1 else 0
            ),
        }
    }


# =============================================================================
# 8. CLASIFICACIÓN DE PENDIENTE
# =============================================================================

def clasificar_pendiente(slope_deg):
    """
    Clasifica la pendiente según estándares técnicos usados en ingeniería
    civil peruana y análisis de riesgo por movimientos en masa.

    Clases:
        Plano         :  0° -  5°  → Sin riesgo de deslizamiento
        Suave         :  5° - 15°  → Riesgo bajo
        Moderada      : 15° - 30°  → Riesgo moderado (zona de atención)
        Escarpada     : 30° - 45°  → Riesgo alto, posibles deslizamientos
        Muy Escarpada : > 45°      → Riesgo muy alto, deslizamientos activos

    Retorna:
        clasificacion : array 2D de enteros (0-4)
        stats         : dict con porcentaje de cada clase
    """
    clf = np.zeros_like(slope_deg, dtype=np.int8)
    clf[slope_deg >= 5]  = 1
    clf[slope_deg >= 15] = 2
    clf[slope_deg >= 30] = 3
    clf[slope_deg >= 45] = 4

    total = slope_deg.size
    stats = {}
    nombres = list(COLORES_PENDIENTE.keys())
    for i, nombre in enumerate(nombres):
        n = np.sum(clf == i)
        stats[nombre] = {
            "n_celdas": int(n),
            "porcentaje": round(100 * n / total, 1)
        }
    return clf, stats


# =============================================================================
# 9. GENERACIÓN DE FIGURAS MATPLOTLIB
# =============================================================================

def _fig_a_base64(fig, dpi=110):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return b64


def generar_figuras_dem(dem_data, cuenca_data, perfil_data, nombre_proyecto=""):
    """
    Genera 4 figuras matplotlib para el análisis DEM:
      1. Hillshade con elevación superpuesta
      2. Mapa de pendiente clasificado
      3. Red de drenaje y cuenca
      4. Perfil de elevación

    Retorna:
        dict con fig_hillshade, fig_pendiente, fig_cuenca, fig_perfil
        (cada uno como objeto Figure de matplotlib)
    """
    dem      = dem_data["dem"]
    cell_m   = dem_data["cell_size_m"]
    lat_g    = dem_data["lat_grid"]
    lon_g    = dem_data["lon_grid"]
    ny, nx   = dem.shape
    cy, cx   = ny // 2, nx // 2

    slope    = calcular_pendiente(dem, cell_m)
    hillshade= calcular_hillshade(dem, cell_m)
    aspecto  = calcular_aspecto(dem, cell_m)
    clf, stats = clasificar_pendiente(slope)

    ext = [lon_g[0,0], lon_g[0,-1], lat_g[-1,0], lat_g[0,0]]

    # ── FIG 1: Hillshade + Elevación ─────────────────────────────────────────
    fig1, ax1 = plt.subplots(figsize=(7, 5.5))
    ax1.imshow(hillshade, cmap='gray', extent=ext, aspect='auto',
               alpha=0.6, origin='upper')
    im1 = ax1.imshow(dem, cmap='terrain', extent=ext, aspect='auto',
                     alpha=0.65, origin='upper',
                     vmin=dem.min(), vmax=dem.max())
    ax1.plot(dem_data["lon_centro"], dem_data["lat_centro"],
             '*', color='red', ms=12, zorder=5, label='Proyecto')
    plt.colorbar(im1, ax=ax1, label='Elevación (m.s.n.m.)', shrink=0.8)
    ax1.set_title(f'Modelo Digital de Elevación (DEM)\n{nombre_proyecto}',
                  fontsize=11, fontweight='bold')
    ax1.set_xlabel('Longitud'); ax1.set_ylabel('Latitud')
    ax1.legend(loc='lower right', fontsize=9)
    _agregar_norte_escala(ax1, dem_data)
    fig1.tight_layout()

    # ── FIG 2: Mapa de Pendiente ─────────────────────────────────────────────
    colores_cls = [v[0] for v in COLORES_PENDIENTE.values()]
    cmap_pend   = mcolors.ListedColormap(colores_cls)
    bounds_pend = [0, 5, 15, 30, 45, 90]
    norm_pend   = mcolors.BoundaryNorm(bounds_pend, cmap_pend.N)

    fig2, ax2 = plt.subplots(figsize=(7, 5.5))
    im2 = ax2.imshow(slope, cmap=cmap_pend, norm=norm_pend, extent=ext,
                     aspect='auto', origin='upper')
    ax2.plot(dem_data["lon_centro"], dem_data["lat_centro"],
             '*', color='blue', ms=12, zorder=5, label='Proyecto')

    cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.8)
    cbar2.set_ticks([2.5, 10, 22.5, 37.5, 67.5])
    cbar2.set_ticklabels(['Plano\n(0-5°)', 'Suave\n(5-15°)',
                          'Moderada\n(15-30°)', 'Escarpada\n(30-45°)',
                          'Muy Escarp.\n(>45°)'])

    # Estadísticas en el mapa
    y0 = 0.97
    for nombre, d in stats.items():
        ax2.text(0.02, y0, f'{nombre}: {d["porcentaje"]}%',
                 transform=ax2.transAxes, fontsize=8,
                 va='top', color='black',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
        y0 -= 0.085

    ax2.set_title(f'Mapa de Pendiente — Clasificación de Riesgo\n{nombre_proyecto}',
                  fontsize=11, fontweight='bold')
    ax2.set_xlabel('Longitud'); ax2.set_ylabel('Latitud')
    ax2.legend(loc='lower right', fontsize=9)
    fig2.tight_layout()

    # ── FIG 3: Cuenca + Red de Drenaje ───────────────────────────────────────
    fig3, ax3 = plt.subplots(figsize=(7, 5.5))
    ax3.imshow(hillshade, cmap='gray', extent=ext, aspect='auto',
               alpha=0.5, origin='upper')

    # Cuenca en azul transparente
    cuenca_rgba = np.zeros((*cuenca_data["cuenca_mask"].shape, 4))
    cuenca_rgba[cuenca_data["cuenca_mask"]] = [0.2, 0.4, 0.8, 0.35]
    ax3.imshow(cuenca_rgba, extent=ext, aspect='auto', origin='upper')

    # Red de drenaje
    red = cuenca_data["red_drenaje"]
    ys, xs = np.where(red)
    if len(ys) > 0:
        lat_red = lat_g[ys, 0]
        lon_red = lon_g[0, xs]
        ax3.scatter(lon_red, lat_red, c='#1E90FF', s=1.5,
                    alpha=0.8, linewidths=0, label='Red de drenaje')

    # Divisoria de aguas (contorno de la cuenca)
    from matplotlib.contour import QuadContourSet
    cuenca_float = cuenca_data["cuenca_mask"].astype(float)
    try:
        ax3.contour(lon_g, lat_g, cuenca_float,
                    levels=[0.5], colors=['#1A5276'], linewidths=2)
    except Exception:
        pass

    ax3.plot(dem_data["lon_centro"], dem_data["lat_centro"],
             'v', color='red', ms=10, zorder=6, label='Punto de proyecto')

    ax3.set_title(
        f'Cuenca Hidrográfica — Área: {cuenca_data["area_km2"]:.1f} km²\n{nombre_proyecto}',
        fontsize=11, fontweight='bold')
    ax3.set_xlabel('Longitud'); ax3.set_ylabel('Latitud')
    ax3.legend(loc='lower right', fontsize=9)
    fig3.tight_layout()

    # ── FIG 4: Perfil de Elevación ────────────────────────────────────────────
    dists = perfil_data["distancias_km"]
    elevs = perfil_data["elevaciones"]
    s     = perfil_data["stats"]
    dist_medio = dists[-1] / 2

    fig4, ax4 = plt.subplots(figsize=(9, 4))
    ax4.fill_between(dists, elevs, elevs.min() - 50,
                     alpha=0.3, color='sienna', label='Terreno')
    ax4.plot(dists, elevs, '-', color='#5D4E37', linewidth=2)
    ax4.axvline(dist_medio, color='red', linestyle='--',
                linewidth=1.5, alpha=0.8, label='Ubicación del proyecto')

    # Anotaciones
    ax4.annotate(f'Máx: {s["elev_max"]:.0f} m',
                 xy=(dists[np.argmax(elevs)], np.max(elevs)),
                 xytext=(dists[np.argmax(elevs)], np.max(elevs) + 40),
                 fontsize=8, ha='center',
                 arrowprops=dict(arrowstyle='->', color='gray'))

    info_txt = (f"Rango: {s['elev_min']:.0f} – {s['elev_max']:.0f} m.s.n.m.\n"
                f"Desnivel: {s['desnivel_m']:.0f} m\n"
                f"Longitud: {s['longitud_km']:.1f} km\n"
                f"Pendiente media: {s['pendiente_media_pct']:.1f}%")
    ax4.text(0.02, 0.97, info_txt, transform=ax4.transAxes,
             fontsize=9, va='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

    ax4.set_title(f'Perfil de Elevación Transversal\n{nombre_proyecto}',
                  fontsize=11, fontweight='bold')
    ax4.set_xlabel('Distancia (km)')
    ax4.set_ylabel('Elevación (m.s.n.m.)')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    fig4.tight_layout()

    return {
        "fig_hillshade": fig1,
        "fig_pendiente": fig2,
        "fig_cuenca":    fig3,
        "fig_perfil":    fig4,
        "stats_pendiente": stats,
        "stats_cuenca":    cuenca_data,
        "stats_perfil":    perfil_data["stats"],
    }


def _agregar_norte_escala(ax, dem_data):
    """Agrega flecha norte y barra de escala al mapa."""
    radio = dem_data["radio_km"]
    lat_c = dem_data["lat_centro"]
    lon_c = dem_data["lon_centro"]
    km_lon = KM_POR_GRADO_LAT * np.cos(np.radians(lat_c))

    # Flecha norte (esquina superior derecha)
    ax.annotate('N', xy=(0.95, 0.90), xytext=(0.95, 0.80),
                xycoords='axes fraction', textcoords='axes fraction',
                fontsize=10, ha='center', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='black', lw=2))

    # Barra de escala (1 km)
    escala_deg = 1.0 / km_lon
    x0 = ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05
    y0 = ax.get_ylim()[0] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05
    ax.plot([x0, x0 + escala_deg], [y0, y0], 'k-', linewidth=3)
    ax.text(x0 + escala_deg / 2, y0 + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.02,
            '1 km', ha='center', fontsize=8, fontweight='bold')


# =============================================================================
# 10. MAPA FOLIUM CON DEM
# =============================================================================

def generar_mapa_folium_dem(dem_data, cuenca_data, perfil_data, nombre_proyecto=""):
    """
    Genera un mapa Folium con las capas del análisis DEM superpuestas.
    Las imágenes raster (hillshade, pendiente, cuenca) se convierten a PNG
    y se incrustan como ImageOverlay en el mapa.
    """
    if not FOLIUM_OK:
        raise ImportError("Instala folium: pip install folium")

    lat_c = dem_data["lat_centro"]
    lon_c = dem_data["lon_centro"]
    dem   = dem_data["dem"]
    cell  = dem_data["cell_size_m"]
    lat_g = dem_data["lat_grid"]
    lon_g = dem_data["lon_grid"]

    slope    = calcular_pendiente(dem, cell)
    hillshade= calcular_hillshade(dem, cell)
    clf, _   = clasificar_pendiente(slope)

    # Bounds del raster [S, W, N, E]
    bounds = [
        [lat_g[-1, 0], lon_g[-1, 0]],
        [lat_g[0, -1],  lon_g[0, -1]]
    ]

    m = folium.Map(location=[lat_c, lon_c], zoom_start=12)

    # Capa base
    folium.TileLayer('CartoDB positron', name='Mapa base').add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='🛰️ Satelital', overlay=False, control=True
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='🗻 Topográfico', overlay=False, control=True
    ).add_to(m)

    # ── Hillshade como ImageOverlay ──────────────────────────────────────────
    hs_rgba = np.stack([hillshade, hillshade, hillshade,
                        (hillshade * 0.6).astype(np.uint8)], axis=-1)
    hs_b64 = _array_a_base64_png(hs_rgba)
    folium.raster_layers.ImageOverlay(
        image=f"data:image/png;base64,{hs_b64}",
        bounds=bounds, opacity=0.6, name="⛰️ Hillshade"
    ).add_to(m)

    # ── Pendiente como ImageOverlay ──────────────────────────────────────────
    colores = ['#FFFFCC','#A1D99B','#FEC44F','#F03B20','#99000D']
    slope_norm = np.digitize(slope, [5, 15, 30, 45])
    slope_rgb  = np.zeros((*slope.shape, 4), dtype=np.uint8)
    for i, c in enumerate(colores):
        r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        mask = slope_norm == i
        slope_rgb[mask] = [r, g, b, 160]
    pend_b64 = _array_a_base64_png(slope_rgb)
    folium.raster_layers.ImageOverlay(
        image=f"data:image/png;base64,{pend_b64}",
        bounds=bounds, opacity=0.7, name="📐 Pendiente"
    ).add_to(m)

    # ── Cuenca como ImageOverlay ─────────────────────────────────────────────
    cuenca_rgb = np.zeros((*cuenca_data["cuenca_mask"].shape, 4), dtype=np.uint8)
    cuenca_rgb[cuenca_data["cuenca_mask"]] = [51, 102, 204, 80]
    cuenca_rgb[cuenca_data["red_drenaje"]] = [30, 144, 255, 200]
    cuenca_b64 = _array_a_base64_png(cuenca_rgb)
    folium.raster_layers.ImageOverlay(
        image=f"data:image/png;base64,{cuenca_b64}",
        bounds=bounds, opacity=0.8, name="💧 Cuenca hidrográfica"
    ).add_to(m)

    # ── Perfil de elevación como línea ───────────────────────────────────────
    capa_perfil = folium.FeatureGroup(name="📏 Transecto de perfil")
    coords_perfil = list(zip(perfil_data["lats"], perfil_data["lons"]))
    folium.PolyLine(
        coords_perfil, color='#FF6B35', weight=2.5,
        dash_array='6 3', tooltip='Transecto del perfil de elevación'
    ).add_to(capa_perfil)
    capa_perfil.add_to(m)

    # ── Marcador del proyecto ────────────────────────────────────────────────
    s = perfil_data["stats"]
    c_data = cuenca_data
    popup_html = f"""
    <div style='font-family:Arial;font-size:12px;width:230px'>
      <b style='color:#1A5276'>🏗️ {nombre_proyecto}</b>
      <hr style='margin:5px 0'>
      <b>📐 Terreno</b><br>
      Elevación base: <b>~{dem_data['elev_base']:,.0f} m.s.n.m.</b><br>
      Rango perfil: {s['elev_min']:.0f} – {s['elev_max']:.0f} m<br>
      Desnivel: <b>{s['desnivel_m']:.0f} m</b><br>
      Pendiente media perfil: {s['pendiente_media_pct']:.1f}%
      <hr style='margin:5px 0'>
      <b>💧 Cuenca</b><br>
      Área de cuenca: <b>{c_data['area_km2']:.1f} km²</b>
    </div>"""

    folium.Marker(
        [lat_c, lon_c],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"📍 {nombre_proyecto}",
        icon=folium.Icon(color='darkblue', icon='home', prefix='glyphicon')
    ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def _array_a_base64_png(arr):
    """Convierte array numpy RGBA a string base64 PNG."""
    buf = io.BytesIO()
    plt.imsave(buf, arr, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


# =============================================================================
# 12. DEM REAL — DESCARGA AUTOMÁTICA NASA SRTM
# =============================================================================

def cargar_dem_srtm(lat, lon, radio_km=5.0, n_puntos=120,
                    cache_dir=None, suavizado=0.8):
    """
    Descarga datos de elevación REALES del satélite NASA SRTM y construye
    una grilla DEM para el área del proyecto.

    Resolución: SRTM3 = 3 arcseg ≈ 90 m/pixel. Cobertura: todo Perú.

    Parámetros:
        lat, lon    : coordenadas del centro
        radio_km    : radio del área (km)
        n_puntos    : resolución de la grilla de salida (N×N)
        cache_dir   : carpeta local para cachear tiles descargados
        suavizado   : sigma para suavizado gaussiano (elimina artefactos)

    Retorna dict compatible con generar_dem() — mismo formato de salida.
    Requiere: pip install srtm.py
    """
    try:
        import srtm as _srtm
    except ImportError:
        raise ImportError(
            "Librería srtm.py no instalada.\n"
            "Ejecuta:  pip install srtm.py"
        )

    # ── Grilla de coordenadas ─────────────────────────────────────────────
    km_per_deg_lon = KM_POR_GRADO_LAT * np.cos(np.radians(lat))
    rango_lat      = radio_km / KM_POR_GRADO_LAT
    rango_lon      = radio_km / km_per_deg_lon

    lats_arr = np.linspace(lat - rango_lat, lat + rango_lat, n_puntos)
    lons_arr = np.linspace(lon - rango_lon, lon + rango_lon, n_puntos)
    lon_grid, lat_grid = np.meshgrid(lons_arr, lats_arr)
    cell_size_m = (2 * radio_km * 1000) / n_puntos

    # ── Descargar tiles SRTM (cachea localmente tras la primera descarga) ─
    print("  Conectando con NASA SRTM...")
    kwargs = {"local_cache_dir": cache_dir} if cache_dir else {}
    srtm_data = _srtm.get_data(**kwargs)

    # Pre-cargar los tiles necesarios (1 o 2 tiles de 1°×1°)
    tile_lats = set(int(np.floor(la)) for la in [lats_arr[0], lats_arr[-1]])
    tile_lons = set(int(np.floor(lo)) for lo in [lons_arr[0], lons_arr[-1]])
    for tl in tile_lats:
        for tlo in tile_lons:
            srtm_data.get_file(float(tl) + 0.5, float(tlo) + 0.5)
    print(f"  Tiles cargados: {len(tile_lats) * len(tile_lons)}")

    # ── Leer elevaciones en la grilla ─────────────────────────────────────
    dem = np.full((n_puntos, n_puntos), np.nan, dtype=float)
    for i in range(n_puntos):
        for j in range(n_puntos):
            e = srtm_data.get_elevation(float(lats_arr[i]), float(lons_arr[j]))
            if e is not None and e != -32768:
                dem[i, j] = float(e)

    # ── Rellenar vacíos (océano, sombras de radar) ────────────────────────
    nan_mask = np.isnan(dem)
    if nan_mask.any():
        from scipy.ndimage import distance_transform_edt
        _, nearest_idx = distance_transform_edt(
            nan_mask, return_distances=True, return_indices=True
        )
        dem[nan_mask] = dem[tuple(nearest_idx[:, nan_mask])]

    # ── Suavizado leve para eliminar aliasing del grid de 90 m ───────────
    if suavizado > 0:
        dem = gaussian_filter(dem, sigma=suavizado)

    elev_base = float(np.median(dem))
    print(f"  DEM SRTM: {dem.min():.0f}–{dem.max():.0f} m, mediana {elev_base:.0f} m")

    return {
        "lat_grid":    lat_grid,
        "lon_grid":    lon_grid,
        "dem":         dem,
        "cell_size_m": cell_size_m,
        "radio_km":    radio_km,
        "elev_base":   elev_base,
        "n_puntos":    n_puntos,
        "lat_centro":  lat,
        "lon_centro":  lon,
        "fuente":      "SRTM3 (NASA, resolución 90m)",
    }


def _intentar_srtm(lat, lon, radio_km, n_puntos):
    """
    Intenta descargar DEM SRTM real.
    Devuelve (dem_data, True) si tiene éxito, (None, False) si falla.
    """
    try:
        dem_data = cargar_dem_srtm(lat, lon, radio_km=radio_km, n_puntos=n_puntos)
        return dem_data, True
    except ImportError as e:
        print(f"  [SRTM] Librería no instalada: {e}")
    except Exception as e:
        print(f"  [SRTM] Error al descargar: {e}")
    return None, False


# =============================================================================
# 11. PIPELINE COMPLETO (función de conveniencia)
# =============================================================================

def analisis_dem_completo(lat, lon, nombre_proyecto="Proyecto",
                           radio_km=5.0, elev_base=None,
                           angulo_perfil=45, umbral_flujo=300,
                           usar_srtm="auto", n_puntos=120):
    """
    Ejecuta el pipeline completo de análisis DEM:
      1. Genera / descarga DEM (SRTM real o sintético)
      2. Calcula cuenca hidrográfica
      3. Extrae perfil de elevación
      4. Genera todas las figuras matplotlib
      5. Genera mapa Folium

    Parámetros:
        lat, lon        : coordenadas del proyecto
        nombre_proyecto : nombre descriptivo
        radio_km        : radio del área de análisis
        elev_base       : elevación del punto (None = automático)
        angulo_perfil   : ángulo del transecto (0=E-O, 90=N-S, 45=diagonal)
        umbral_flujo    : celdas mínimas de acumulación para red de drenaje
        usar_srtm       : "auto"     → intenta SRTM, cae a sintético si falla
                          "srtm"     → fuerza SRTM (lanza error si falla)
                          "sintetico"→ siempre usa DEM sintético
        n_puntos        : resolución de la grilla (default 120×120)

    Retorna:
        dict completo con dem_data, cuenca_data, perfil_data, figuras, mapa
        Incluye 'fuente_dem': "SRTM3 (NASA, 90m)" o "Sintético"
    """
    # ── PASO 1: Obtener DEM ────────────────────────────────────────────────
    fuente_usada = "Sintético (fractal Andino)"
    dem_data     = None   # se asigna abajo según la fuente elegida

    if usar_srtm in ("auto", "srtm"):
        print(f"[1/4] Descargando DEM SRTM real para {nombre_proyecto}...")
        dem_data, srtm_ok = _intentar_srtm(lat, lon, radio_km, n_puntos)
        if srtm_ok:
            fuente_usada = dem_data.get("fuente", "SRTM3 (NASA, 90m)")
        else:
            if usar_srtm == "srtm":
                raise RuntimeError(
                    "No se pudo descargar datos SRTM. "
                    "Verifica conexión a internet y que srtm.py esté instalado."
                )
            print(f"[1/4] SRTM no disponible — usando DEM sintético...")
            dem_data = None

    if dem_data is None:
        print(f"[1/4] Generando DEM sintético para {nombre_proyecto}...")
        dem_data = generar_dem(lat, lon, radio_km=radio_km,
                               elev_base=elev_base, n_puntos=n_puntos)
        fuente_usada = "Sintético (fractal Andino)"

    print(f"[2/4] Delimitando cuenca hidrográfica...")
    cuenca_data = delimitar_cuenca(dem_data, umbral_flujo=umbral_flujo)

    print(f"[3/4] Extrayendo perfil de elevación...")
    perfil_data = perfil_elevacion(dem_data, angulo_grados=angulo_perfil)

    print(f"[4/4] Generando figuras y mapa...")
    figuras = generar_figuras_dem(dem_data, cuenca_data, perfil_data, nombre_proyecto)

    if FOLIUM_OK:
        mapa = generar_mapa_folium_dem(dem_data, cuenca_data, perfil_data, nombre_proyecto)
    else:
        mapa = None

    # Reporte en consola
    s  = perfil_data["stats"]
    sp = figuras["stats_pendiente"]
    c  = cuenca_data
    print(f"\n{'='*55}")
    print(f"  ANALISIS DEM --- {nombre_proyecto}")
    print(f"{'='*55}")
    print(f"  Fuente DEM        : {fuente_usada}")
    print(f"  Radio de analisis : {radio_km} km")
    print(f"  Elevacion base    : ~{dem_data['elev_base']:,.0f} m.s.n.m.")
    print(f"  Rango elevacion   : {s['elev_min']:.0f} - {s['elev_max']:.0f} m")
    print(f"  Desnivel          : {s['desnivel_m']:.0f} m")
    print(f"  Area de cuenca    : {c['area_km2']:.1f} km2")
    print(f"\n  Distribucion de pendiente:")
    for nomb, dd in sp.items():
        bar = chr(9608) * int(dd['porcentaje'] / 4)
        print(f"    {nomb:<16}: {dd['porcentaje']:5.1f}% {bar}")
    print(f"{'='*55}\n")

    return {
        "dem_data":    dem_data,
        "cuenca_data": cuenca_data,
        "perfil_data": perfil_data,
        "figuras":     figuras,
        "mapa":        mapa,
        "fuente_dem":  fuente_usada,
    }
