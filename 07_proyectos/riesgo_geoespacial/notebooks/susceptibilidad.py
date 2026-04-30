"""
=============================================================================
MÓDULO DE SUSCEPTIBILIDAD A DESLIZAMIENTOS DE TIERRA
Modelo multicriterio ponderado — Metodología CENEPRED Perú
=============================================================================
Autor  : Fernando Geronimo Ccoillor Soto
Fecha  : Abril 2026

METODOLOGÍA:
  Análisis multicriterio ponderado (WLC – Weighted Linear Combination)
  basado en la guía técnica del CENEPRED (Centro Nacional de Estimación,
  Prevención y Reducción del Riesgo de Desastres) para evaluación de
  susceptibilidad a movimientos en masa en el Perú.

  Factores y pesos default:
    - Pendiente     40%  (factor geomorfológico dominante)
    - Precipitación 30%  (detonante principal de deslizamientos)
    - Elevación     15%  (contexto altitudinal y climático)
    - Curvatura     15%  (concentración del flujo hídrico)

  Índice = Σ(peso_i × score_i), normalizado a escala 1–5

  Clases de susceptibilidad:
    1.0–1.8 → Muy Baja   (verde oscuro)
    1.8–2.6 → Baja       (amarillo)
    2.6–3.4 → Moderada   (naranja)
    3.4–4.2 → Alta       (rojo)
    4.2–5.0 → Muy Alta   (rojo oscuro)

FUNCIONES:
  calcular_susceptibilidad()    → índice, clasificación y estadísticas
  generar_figura_susceptibilidad() → figura matplotlib lista para Streamlit
  generar_mapa_susceptibilidad()   → mapa Folium con overlay de riesgo
  susceptibilidad_completo()    → pipeline completo en una llamada
=============================================================================
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
from scipy.ndimage import sobel, gaussian_filter
import io
import base64
import warnings
warnings.filterwarnings('ignore')

try:
    import folium
    FOLIUM_OK = True
except ImportError:
    FOLIUM_OK = False

# =============================================================================
# CONSTANTES
# =============================================================================

CLASES_SUSCEPTIBILIDAD = {
    "Muy Baja":  {"rango": (1.0, 1.8), "color": "#1a9850"},
    "Baja":      {"rango": (1.8, 2.6), "color": "#fee08b"},
    "Moderada":  {"rango": (2.6, 3.4), "color": "#fdae61"},
    "Alta":      {"rango": (3.4, 4.2), "color": "#d73027"},
    "Muy Alta":  {"rango": (4.2, 5.1), "color": "#4a0000"},
}

NOMBRES_CLASES = list(CLASES_SUSCEPTIBILIDAD.keys())
COLORES_CLASES = [CLASES_SUSCEPTIBILIDAD[n]["color"] for n in NOMBRES_CLASES]


# =============================================================================
# 1. CÁLCULO DEL ÍNDICE DE SUSCEPTIBILIDAD
# =============================================================================

def calcular_susceptibilidad(dem_data, precip_anual_mm=800,
                              w_pendiente=0.40, w_precip=0.30,
                              w_elevacion=0.15, w_curvatura=0.15):
    """
    Calcula el índice de susceptibilidad a deslizamientos de tierra.

    Metodología: WLC (Weighted Linear Combination) basado en CENEPRED.
    Cada factor se evalúa en escala 1–5 y se combina con pesos.

    Parámetros:
        dem_data         : dict retornado por generar_dem() o cargar_dem_srtm()
        precip_anual_mm  : precipitación media anual del sitio (mm/año)
                           Referencia: estación SENAMHI más cercana
        w_pendiente      : peso para pendiente   (default 0.40)
        w_precip         : peso para precipitación (default 0.30)
        w_elevacion      : peso para elevación   (default 0.15)
        w_curvatura      : peso para curvatura   (default 0.15)

    Retorna:
        dict con:
          indice         : array 2D, escala 1–5
          clasificacion  : array 2D int, 0=Muy Baja … 4=Muy Alta
          stats          : dict por clase con porcentaje y área
          slope_deg      : mapa de pendiente (grados)
          factores       : dict con arrays de cada factor (1–5)
          indice_medio   : valor promedio del índice
          lat_grid, lon_grid : coordenadas de la grilla
    """
    dem  = dem_data["dem"]
    cell = dem_data["cell_size_m"]
    lat_g = dem_data["lat_grid"]
    lon_g = dem_data["lon_grid"]

    # ── Factor 1: PENDIENTE (Sobel, grados) ──────────────────────────────
    # Pendiente alta → mayor probabilidad de deslizamiento
    dz_dx = sobel(dem, axis=1) / (8.0 * cell)
    dz_dy = sobel(dem, axis=0) / (8.0 * cell)
    slope_deg = np.degrees(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))

    f_pend = np.ones_like(slope_deg)
    f_pend[slope_deg >= 5]  = 2   # Suave
    f_pend[slope_deg >= 15] = 3   # Moderada
    f_pend[slope_deg >= 30] = 4   # Escarpada
    f_pend[slope_deg >= 45] = 5   # Muy escarpada

    # ── Factor 2: PRECIPITACIÓN (escalar uniforme en la grilla) ──────────
    # La precipitación es un detonante: mayor lluvia → mayor riesgo
    # Se usa la precipitación anual de la estación SENAMHI más cercana.
    # Costa árida: <250 mm | Sierra: 500-1000 mm | Selva: >2000 mm
    if   precip_anual_mm < 250:  pv = 1
    elif precip_anual_mm < 500:  pv = 2
    elif precip_anual_mm < 1000: pv = 3
    elif precip_anual_mm < 2000: pv = 4
    else:                        pv = 5
    f_precip = np.full_like(dem, float(pv))

    # ── Factor 3: ELEVACIÓN (m.s.n.m.) ───────────────────────────────────
    # La Sierra alta tiene más inestabilidad por permafrost y precipitaciones
    f_elev = np.ones_like(dem)
    f_elev[dem >= 500]  = 2
    f_elev[dem >= 1500] = 3
    f_elev[dem >= 3000] = 4
    f_elev[dem >= 4500] = 5

    # ── Factor 4: CURVATURA (Laplaciano — convergencia del flujo) ─────────
    # Curvatura cóncava (negativa) = acumula agua → mayor saturación del suelo
    d2z_dx2 = np.gradient(np.gradient(dem, axis=1), axis=1) / (cell ** 2)
    d2z_dy2 = np.gradient(np.gradient(dem, axis=0), axis=0) / (cell ** 2)
    curv = -(d2z_dx2 + d2z_dy2)          # Laplaciano negativo = cóncavo
    rng = curv.max() - curv.min() + 1e-9
    f_curv = 1.0 + ((curv - curv.min()) / rng) * 4.0   # mapear a 1–5
    f_curv = np.clip(f_curv, 1.0, 5.0)
    f_curv = gaussian_filter(f_curv, sigma=1)           # suavizar bordes

    # ── Índice ponderado ──────────────────────────────────────────────────
    indice = (w_pendiente * f_pend  +
              w_precip    * f_precip +
              w_elevacion * f_elev  +
              w_curvatura * f_curv)
    indice = np.clip(indice, 1.0, 5.0)

    # ── Clasificación (0=Muy Baja … 4=Muy Alta) ───────────────────────────
    clf = np.zeros(dem.shape, dtype=np.int8)
    for i, nombre in enumerate(NOMBRES_CLASES):
        lo, hi = CLASES_SUSCEPTIBILIDAD[nombre]["rango"]
        clf[(indice >= lo) & (indice < hi)] = i

    # ── Estadísticas por clase ─────────────────────────────────────────────
    total = indice.size
    stats = {}
    for i, nombre in enumerate(NOMBRES_CLASES):
        n    = int(np.sum(clf == i))
        area = n * (cell / 1000) ** 2
        stats[nombre] = {
            "n_celdas":   n,
            "porcentaje": round(100 * n / total, 1),
            "area_km2":   round(area, 3),
            "color":      CLASES_SUSCEPTIBILIDAD[nombre]["color"],
        }

    return {
        "indice":           indice,
        "clasificacion":    clf,
        "stats":            stats,
        "slope_deg":        slope_deg,
        "factores": {
            "pendiente":      f_pend,
            "precipitacion":  f_precip,
            "elevacion":      f_elev,
            "curvatura":      f_curv,
        },
        "indice_medio":     float(np.mean(indice)),
        "precip_anual_mm":  precip_anual_mm,
        "nombres_clases":   NOMBRES_CLASES,
        "lat_grid":         lat_g,
        "lon_grid":         lon_g,
        "pesos": {
            "pendiente": w_pendiente, "precipitacion": w_precip,
            "elevacion": w_elevacion, "curvatura": w_curvatura,
        },
    }


# =============================================================================
# 2. FIGURA MATPLOTLIB
# =============================================================================

def generar_figura_susceptibilidad(susc_data, dem_data, nombre_proyecto="Proyecto"):
    """
    Genera figura matplotlib con:
      - Mapa de susceptibilidad (imagen clasificada con leyenda)
      - Gráfico de barras horizontales por clase
      - Tabla de factores y pesos utilizados

    Retorna figura lista para st.pyplot() en Streamlit.
    """
    clf    = susc_data["clasificacion"]
    stats  = susc_data["stats"]
    indice = susc_data["indice"]
    pesos  = susc_data["pesos"]

    fig = plt.figure(figsize=(16, 6), facecolor="#f8f9fa")
    gs  = fig.add_gridspec(1, 3, wspace=0.35)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])

    # ── Panel 1: Mapa de susceptibilidad ──────────────────────────────────
    cmap  = mcolors.ListedColormap(COLORES_CLASES)
    norm  = mcolors.BoundaryNorm(range(len(NOMBRES_CLASES) + 1), cmap.N)
    ax1.imshow(clf, cmap=cmap, norm=norm, interpolation='nearest', origin='lower')
    ax1.set_title(f"Susceptibilidad a Deslizamientos\n{nombre_proyecto}",
                  fontsize=11, fontweight='bold', pad=8)
    ax1.set_xticks([]); ax1.set_yticks([])

    # Marcador del punto central
    ny, nx = clf.shape
    ax1.plot(nx // 2, ny // 2, 'w*', markersize=12, zorder=5)

    leyenda = [Patch(facecolor=COLORES_CLASES[i], label=NOMBRES_CLASES[i],
                     edgecolor='white')
               for i in range(len(NOMBRES_CLASES))]
    ax1.legend(handles=leyenda, loc='lower right', fontsize=7.5,
               framealpha=0.9, edgecolor='#ccc')
    ax1.text(0.02, 0.98, f"Precip. anual: {susc_data['precip_anual_mm']} mm",
             transform=ax1.transAxes, fontsize=8, va='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.75))

    # ── Panel 2: Barras horizontales ───────────────────────────────────────
    ax2.set_facecolor('white')
    pcts  = [stats[n]["porcentaje"] for n in NOMBRES_CLASES]
    areas = [stats[n]["area_km2"]   for n in NOMBRES_CLASES]
    bars  = ax2.barh(NOMBRES_CLASES, pcts, color=COLORES_CLASES,
                     edgecolor='white', linewidth=0.6, height=0.6)
    for bar, pct, area in zip(bars, pcts, areas):
        ax2.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height() / 2,
                 f"{pct:.1f}%  ({area:.2f} km²)",
                 va='center', fontsize=8.5)

    ax2.set_xlabel("% del área de análisis", fontsize=9)
    ax2.set_title("Distribución por clase", fontsize=11, fontweight='bold')
    ax2.set_xlim(0, max(pcts) * 1.6)
    ax2.invert_yaxis()
    for spine in ['top', 'right']:
        ax2.spines[spine].set_visible(False)
    ax2.grid(axis='x', alpha=0.3)

    clase_dom = max(stats, key=lambda k: stats[k]["porcentaje"])
    ax2.text(0.02, 0.02,
             f"Clase dominante: {clase_dom}\n"
             f"Índice promedio: {susc_data['indice_medio']:.2f} / 5.00",
             transform=ax2.transAxes, fontsize=8.5, va='bottom',
             bbox=dict(boxstyle='round', facecolor='#f0f4f8', alpha=0.9))

    # ── Panel 3: Tabla de factores ─────────────────────────────────────────
    ax3.set_facecolor('white')
    ax3.axis('off')
    ax3.set_title("Factores del Modelo (CENEPRED)", fontsize=11,
                  fontweight='bold')

    filas = [
        ["Factor", "Peso", "Score prom."],
        ["Pendiente",      f"{pesos['pendiente']*100:.0f}%",
         f"{susc_data['factores']['pendiente'].mean():.2f}"],
        ["Precipitación",  f"{pesos['precipitacion']*100:.0f}%",
         f"{susc_data['factores']['precipitacion'].mean():.2f}"],
        ["Elevación",      f"{pesos['elevacion']*100:.0f}%",
         f"{susc_data['factores']['elevacion'].mean():.2f}"],
        ["Curvatura",      f"{pesos['curvatura']*100:.0f}%",
         f"{susc_data['factores']['curvatura'].mean():.2f}"],
        ["ÍNDICE FINAL",   "100%", f"{susc_data['indice_medio']:.2f}"],
    ]
    colores_tabla = [["#2c3e50"] * 3] + \
                    [["#f8f9fa", "#eaf0fb", "#eaf0fb"]] * 4 + \
                    [["#2980b9", "#2980b9", "#2980b9"]]
    tabla = ax3.table(cellText=filas[1:], colLabels=filas[0],
                      cellLoc='center', loc='center',
                      cellColours=colores_tabla[1:])
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9)
    tabla.scale(1, 1.8)

    # Estilo encabezado
    for j in range(3):
        tabla[(0, j)].set_facecolor("#2c3e50")
        tabla[(0, j)].set_text_props(color='white', fontweight='bold')
    # Estilo fila total
    for j in range(3):
        tabla[(5, j)].set_facecolor("#2980b9")
        tabla[(5, j)].set_text_props(color='white', fontweight='bold')

    ax3.text(0.5, 0.05,
             "Ref: CENEPRED — Manual para Evaluación\n"
             "de Riesgos originados por Movimientos en Masa",
             transform=ax3.transAxes, fontsize=7, ha='center', color='#666')

    fig.suptitle(
        f"Análisis de Susceptibilidad a Movimientos en Masa — {nombre_proyecto}",
        fontsize=13, fontweight='bold', y=1.01
    )
    return fig


# =============================================================================
# 3. MAPA FOLIUM
# =============================================================================

def generar_mapa_susceptibilidad(susc_data, dem_data, nombre_proyecto):
    """
    Genera mapa Folium interactivo con overlay semitransparente de
    susceptibilidad a deslizamientos sobre imagen satelital.

    Incluye:
      - Capa de susceptibilidad (5 colores, 70% opacidad)
      - Marcador del punto del proyecto con popup informativo
      - Leyenda HTML fija en esquina inferior izquierda
      - Control de capas (base cartográfica / satelital)
    """
    if not FOLIUM_OK:
        return None

    lat_c = dem_data["lat_centro"]
    lon_c = dem_data["lon_centro"]
    clf   = susc_data["clasificacion"]
    lat_g = susc_data["lat_grid"]
    lon_g = susc_data["lon_grid"]
    stats = susc_data["stats"]

    # ── Imagen RGBA del mapa de susceptibilidad ────────────────────────────
    cmap  = mcolors.ListedColormap(COLORES_CLASES)
    norm  = mcolors.BoundaryNorm(range(len(NOMBRES_CLASES) + 1), cmap.N)
    rgba  = cmap(norm(clf)).astype(float)
    rgba[..., 3] = 0.70   # 70% opacidad

    buf = io.BytesIO()
    plt.imsave(buf, rgba[::-1], format='png')   # flip vertical para Leaflet
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()
    img_url = f"data:image/png;base64,{img_b64}"

    bounds_box = [[lat_g.min(), lon_g.min()], [lat_g.max(), lon_g.max()]]

    # ── Mapa base ──────────────────────────────────────────────────────────
    m = folium.Map(location=[lat_c, lon_c], zoom_start=13,
                   tiles="CartoDB positron", name="Cartográfico")

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satélite",
        overlay=False
    ).add_to(m)

    # ── Overlay de susceptibilidad ─────────────────────────────────────────
    folium.raster_layers.ImageOverlay(
        image=img_url,
        bounds=bounds_box,
        opacity=0.75,
        name="Susceptibilidad a Deslizamientos",
        interactive=False,
        cross_origin=False,
        zindex=1
    ).add_to(m)

    # ── Marcador del proyecto ──────────────────────────────────────────────
    clase_dom  = max(stats, key=lambda k: stats[k]["porcentaje"])
    color_dom  = CLASES_SUSCEPTIBILIDAD[clase_dom]["color"]
    area_riesgo_alto = sum(
        stats[n]["area_km2"]
        for n in ["Alta", "Muy Alta"]
        if n in stats
    )

    popup_html = f"""
    <div style="font-family:Arial,sans-serif;width:240px;font-size:13px">
      <div style="background:#2c3e50;color:white;padding:6px 10px;
                  border-radius:4px 4px 0 0;font-weight:bold">
        {nombre_proyecto}
      </div>
      <div style="padding:8px 10px;border:1px solid #ddd;border-radius:0 0 4px 4px">
        <table style="width:100%;border-collapse:collapse">
          <tr><td style="color:#666">Clase dominante</td>
              <td style="text-align:right">
                <span style="background:{color_dom};color:white;
                             padding:2px 8px;border-radius:10px;font-size:11px">
                  {clase_dom}
                </span>
              </td></tr>
          <tr><td style="color:#666">Índice promedio</td>
              <td style="text-align:right"><b>{susc_data['indice_medio']:.2f} / 5.00</b></td></tr>
          <tr><td style="color:#666">Área Alta+Muy Alta</td>
              <td style="text-align:right"><b>{area_riesgo_alto:.2f} km²</b></td></tr>
          <tr><td style="color:#666">Precipitación anual</td>
              <td style="text-align:right">{susc_data['precip_anual_mm']} mm</td></tr>
        </table>
      </div>
    </div>
    """
    folium.Marker(
        location=[lat_c, lon_c],
        popup=folium.Popup(popup_html, max_width=260),
        tooltip=f"{nombre_proyecto} — clic para detalles",
        icon=folium.Icon(color="red", icon="exclamation-sign", prefix="glyphicon")
    ).add_to(m)

    # ── Leyenda HTML ───────────────────────────────────────────────────────
    leyenda = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:9999;
                background:white;padding:10px 14px;border-radius:8px;
                box-shadow:0 2px 10px rgba(0,0,0,0.25);
                font-family:Arial,sans-serif;font-size:12px">
      <div style="font-weight:bold;margin-bottom:6px;color:#2c3e50">
        Susceptibilidad a Deslizamientos
      </div>
    """
    for nombre, info in CLASES_SUSCEPTIBILIDAD.items():
        pct = stats.get(nombre, {}).get("porcentaje", 0)
        leyenda += (
            f'<div style="display:flex;align-items:center;margin:3px 0">'
            f'<span style="display:inline-block;width:16px;height:16px;'
            f'background:{info["color"]};border-radius:3px;margin-right:8px;'
            f'flex-shrink:0"></span>'
            f'<span>{nombre}</span>'
            f'<span style="margin-left:auto;padding-left:12px;color:#666">'
            f'{pct:.1f}%</span></div>'
        )
    leyenda += '<div style="margin-top:6px;font-size:10px;color:#999">Ref: CENEPRED Perú</div>'
    leyenda += '</div>'
    m.get_root().html.add_child(folium.Element(leyenda))

    folium.LayerControl(position='topright').add_to(m)
    return m


# =============================================================================
# 4. PIPELINE COMPLETO
# =============================================================================

def susceptibilidad_completo(dem_data, nombre_proyecto="Proyecto",
                              precip_anual_mm=800,
                              w_pendiente=0.40, w_precip=0.30,
                              w_elevacion=0.15, w_curvatura=0.15):
    """
    Pipeline completo de susceptibilidad a deslizamientos:
      1. Calcula índice multicriterio (CENEPRED)
      2. Genera figura matplotlib (mapa + barras + tabla factores)
      3. Genera mapa Folium interactivo

    Parámetros:
        dem_data        : dict de generar_dem() o cargar_dem_srtm()
        nombre_proyecto : nombre del proyecto
        precip_anual_mm : precipitación anual (mm) — de estación SENAMHI
        w_*             : pesos para cada factor

    Retorna:
        dict con susc_data, figura, mapa
    """
    print(f"[1/3] Calculando índice de susceptibilidad...")
    susc_data = calcular_susceptibilidad(
        dem_data, precip_anual_mm=precip_anual_mm,
        w_pendiente=w_pendiente, w_precip=w_precip,
        w_elevacion=w_elevacion, w_curvatura=w_curvatura
    )

    print(f"[2/3] Generando figura...")
    figura = generar_figura_susceptibilidad(susc_data, dem_data, nombre_proyecto)

    print(f"[3/3] Generando mapa Folium...")
    mapa = generar_mapa_susceptibilidad(susc_data, dem_data, nombre_proyecto)

    # Reporte en consola
    stats = susc_data["stats"]
    clase_dom = max(stats, key=lambda k: stats[k]["porcentaje"])
    print(f"\n{'='*55}")
    print(f"  SUSCEPTIBILIDAD — {nombre_proyecto}")
    print(f"{'='*55}")
    print(f"  Método          : WLC multicriterio (CENEPRED)")
    print(f"  Precipitación   : {precip_anual_mm} mm/año")
    print(f"  Índice promedio : {susc_data['indice_medio']:.2f} / 5.00")
    print(f"  Clase dominante : {clase_dom}")
    print(f"\n  Distribución:")
    for nombre in NOMBRES_CLASES:
        d   = stats[nombre]
        bar = chr(9608) * int(d["porcentaje"] / 4)
        print(f"    {nombre:<14}: {d['porcentaje']:5.1f}%  {d['area_km2']:.2f} km²  {bar}")
    print(f"{'='*55}\n")

    return {
        "susc_data": susc_data,
        "figura":    figura,
        "mapa":      mapa,
    }


# =============================================================================
# TEST RÁPIDO
# =============================================================================
if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    import dem_analysis as d

    print("Generando DEM sintético para prueba...")
    dem_data = d.generar_dem(-8.018, -78.568, radio_km=5, elev_base=3180, n_puntos=80)

    resultado = susceptibilidad_completo(
        dem_data,
        nombre_proyecto="Proyecto Sauco",
        precip_anual_mm=620
    )
    resultado["figura"].savefig("/tmp/susceptibilidad_sauco.png", dpi=100, bbox_inches="tight")
    print("Figura guardada en /tmp/susceptibilidad_sauco.png")
    if resultado["mapa"]:
        resultado["mapa"].save("/tmp/mapa_susceptibilidad_sauco.html")
        print("Mapa guardado en /tmp/mapa_susceptibilidad_sauco.html")
