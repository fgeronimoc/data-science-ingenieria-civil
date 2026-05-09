"""
=============================================================================
DASHBOARD GEOESPACIAL — SENAMHI PERÚ
Análisis de estaciones meteorológicas para proyectos de infraestructura civil
=============================================================================
Autor  : Fernando Geronimo Ccoillor Soto
Fecha  : Abril 2026
Uso    : streamlit run app.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import io
import sys
import os
import zipfile
import re
import xml.etree.ElementTree as ET

# ── Ruta al módulo de estaciones ─────────────────────────────────────────────
# Agrega la carpeta del buscador al path de Python
NOTEBOOKS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..",
    "07_proyectos", "riesgo_geoespacial", "notebooks"
)
sys.path.insert(0, os.path.abspath(NOTEBOOKS_DIR))
from buscador_estaciones_senamhi import (
    ESTACIONES_SENAMHI, TIPOS_ESTACION,
    buscar_estaciones, buscar_estaciones_utm,
    generar_mapa_estaciones, haversine, geograficas_a_utm,
    gms_a_decimal, decimal_a_gms,
)

# ── Módulo de análisis DEM ────────────────────────────────────────────────────
try:
    import dem_analysis as dem_mod
    DEM_OK = True
except Exception as _dem_err:
    DEM_OK = False
    _dem_err_msg = str(_dem_err)

# ── Módulo de susceptibilidad ─────────────────────────────────────────────────
try:
    import susceptibilidad as susc_mod
    SUSC_OK = True
except Exception as _susc_err:
    SUSC_OK = False
    _susc_err_msg = str(_susc_err)

# =============================================================================
# CONFIGURACIÓN DE PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Dashboard SENAMHI — Perú",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# ESTILOS CSS PERSONALIZADOS
# =============================================================================
st.markdown("""
<style>
/* Header principal */
.main-header {
    background: linear-gradient(135deg, #1A5276, #2980B9);
    color: white;
    padding: 16px 24px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.main-header h1 { font-size: 22px; margin: 0; }
.main-header p  { font-size: 13px; margin: 4px 0 0; opacity: 0.85; }

/* Tarjetas de métrica personalizadas */
.metric-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-left: 5px solid #2980B9;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.metric-card h4 { font-size: 11px; color: #777; margin: 0 0 4px; text-transform: uppercase; }
.metric-card .value { font-size: 22px; font-weight: bold; color: #1A5276; }
.metric-card .sub   { font-size: 11px; color: #999; }

/* Tabla de estaciones */
.station-row { padding: 8px; border-bottom: 1px solid #f0f0f0; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #f8f9fa; }

/* Badges */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: bold;
}
.badge-cp  { background: #d4edda; color: #155724; }
.badge-co  { background: #cce5ff; color: #004085; }
.badge-plu { background: #fff3cd; color: #856404; }
.badge-hlg { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATOS DE PRECIPITACIÓN HISTÓRICA POR REGIÓN (referencial SENAMHI)
# =============================================================================
PRECIP_REGIONES = {
    "La Libertad": {
        "estacion": "Otuzco",
        "meses": ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
        "mm":    [85, 120, 135, 95, 45, 15, 8, 10, 25, 55, 70, 75],
        "dias":  [12,  14,  15,  12,  8,  3,  2,  2,  5,  8, 10, 11],
    },
    "Cajamarca": {
        "estacion": "Cajamarca",
        "meses": ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
        "mm":    [100, 130, 150, 110, 60, 20, 10, 12, 30, 65, 85, 90],
        "dias":  [14,  16,  17,  14,  9,  4,  2,  3,  6,  9, 11, 13],
    },
    "Cusco": {
        "estacion": "Cusco",
        "meses": ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
        "mm":    [145, 130, 105, 45, 12, 5, 3, 8, 25, 55, 85, 120],
        "dias":  [18,  16,  14,   8,  3,  1,  1,  2,  5,  8, 11, 15],
    },
    "Lima": {
        "estacion": "Lima CORPAC",
        "meses": ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
        "mm":    [0, 0, 0, 0, 1, 3, 5, 5, 2, 1, 0, 0],
        "dias":  [0,  0,  0,  0,  1,  3,  5,  5,  2,  1,  0,  0],
    },
    "Puno": {
        "estacion": "Puno",
        "meses": ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
        "mm":    [160, 145, 110, 50, 15, 5, 3, 8, 30, 60, 90, 130],
        "dias":  [20,  18,  15,  8,  4,  1,  1,  2,  5,  8, 11, 16],
    },
    "Arequipa": {
        "estacion": "Arequipa",
        "meses": ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
        "mm":    [35, 30, 18, 5, 1, 0, 0, 0, 1, 3, 8, 18],
        "dias":  [5,   4,  3,  1,  0,  0,  0,  0,  0,  1,  2,  4],
    },
    "default": {
        "estacion": "Referencial",
        "meses": ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
        "mm":    [80, 90, 100, 70, 30, 10, 5, 8, 20, 45, 60, 70],
        "dias":  [10,  12,  13,  10,  6,  2,  1,  2,  4,  7,  9, 10],
    }
}

COLORES_RANK = {1:'#E74C3C', 2:'#E67E22', 3:'#27AE60', 4:'#2980B9', 5:'#8E44AD'}
LEAFLET_COLORS = {1:'red', 2:'orange', 3:'green', 4:'blue', 5:'purple'}

# Paleta de colores para capas KMZ (hasta 8 archivos simultáneos)
COLORES_KMZ = [
    '#E74C3C', '#2980B9', '#27AE60', '#F39C12',
    '#8E44AD', '#16A085', '#D35400', '#2C3E50',
]

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def get_precip_data(dpto):
    """Retorna datos de precipitación según el departamento."""
    return PRECIP_REGIONES.get(dpto, PRECIP_REGIONES["default"])


def generar_mapa_folium(lat, lon, nombre, df_cercanas):
    """Genera mapa Folium con el proyecto y las 5 estaciones más cercanas."""
    m = folium.Map(location=[lat, lon], zoom_start=9, tiles='CartoDB positron')

    # Capas de fondo
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='🛰️ Satelital', overlay=False, control=True
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='🗻 Topográfico', overlay=False, control=True
    ).add_to(m)

    # Capa estaciones
    capa_est = folium.FeatureGroup(name="🌦️ Estaciones SENAMHI")
    capa_lin = folium.FeatureGroup(name="📏 Distancias")

    for _, row in df_cercanas.iterrows():
        rank  = int(row['rank'])
        color = COLORES_RANK.get(rank, '#555')
        lcolor = LEAFLET_COLORS.get(rank, 'gray')

        utm_info = ""
        if 'utm_este' in row and pd.notna(row.get('utm_este')):
            utm_info = f"<br>📐 UTM Z{int(row['utm_zona'])}S: {row['utm_este']:,.0f}E, {row['utm_norte']:,.0f}N"

        popup_html = f"""
        <div style='width:260px;font-family:Arial;font-size:12px'>
          <div style='background:{color};color:white;padding:6px 10px;
                      border-radius:4px 4px 0 0;font-weight:bold'>
            #{rank} — {row['nombre']}
          </div>
          <div style='padding:8px'>
            <b>Código:</b> {row['codigo']}<br>
            <b>Tipo:</b> {row['tipo']} — {TIPOS_ESTACION.get(row['tipo'], row['tipo'])}<br>
            <b>Estado:</b> ✅ Activa<br>
            <hr style='margin:5px 0'>
            <b>Dpto:</b> {row['dpto']} | <b>Prov:</b> {row['prov']}<br>
            <b>Elevación:</b> {row['elev']:,} m.s.n.m.<br>
            <hr style='margin:5px 0'>
            🌐 Lat: {row['lat']:.5f}° | Lon: {row['lon']:.5f}°{utm_info}
            <hr style='margin:5px 0'>
            <b style='color:{color}'>📏 {row['distancia_km']:.1f} km del proyecto</b>
          </div>
        </div>"""

        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"#{rank} {row['nombre']} | {row['distancia_km']:.1f} km",
            icon=folium.Icon(color=lcolor, icon='cloud', prefix='glyphicon')
        ).add_to(capa_est)

        # Línea punteada
        folium.PolyLine(
            [[lat, lon], [row['lat'], row['lon']]],
            color=color, weight=2, opacity=0.65, dash_array='5 4'
        ).add_to(capa_lin)

        # Etiqueta en el punto medio
        mid = [(lat + row['lat']) / 2, (lon + row['lon']) / 2]
        folium.Marker(mid, icon=folium.DivIcon(
            html=f"""<div style='background:{color};color:white;padding:1px 5px;
                         border-radius:8px;font-size:10px;font-weight:bold;
                         white-space:nowrap'>{row['distancia_km']:.1f} km</div>""",
            icon_size=(60, 18), icon_anchor=(30, 9)
        )).add_to(capa_lin)

    capa_est.add_to(m)
    capa_lin.add_to(m)

    # Marcador del proyecto
    capa_proy = folium.FeatureGroup(name="🏗️ Proyecto")
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(f"<b>🏗️ {nombre}</b><br>Lat: {lat:.6f}<br>Lon: {lon:.6f}", max_width=200),
        tooltip=f"📍 {nombre}",
        icon=folium.Icon(color='darkblue', icon='home', prefix='glyphicon')
    ).add_to(capa_proy)
    capa_proy.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    # Zoom automático
    bounds = [[lat, lon]] + [[r['lat'], r['lon']] for _, r in df_cercanas.iterrows()]
    m.fit_bounds(bounds, padding=[30, 30])

    return m


def exportar_excel(df_cercanas, lat, lon, nombre):
    """Genera un archivo Excel con los resultados."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: Estaciones
        cols = ['rank', 'nombre', 'codigo', 'tipo', 'distancia_km', 'elev',
                'dpto', 'prov', 'dist', 'lat', 'lon']
        if 'utm_este' in df_cercanas.columns:
            cols += ['utm_zona', 'utm_este', 'utm_norte']
        df_export = df_cercanas[[c for c in cols if c in df_cercanas.columns]].copy()
        df_export.columns = [c.replace('_', ' ').title() for c in df_export.columns]
        df_export.to_excel(writer, sheet_name='Estaciones Cercanas', index=False)

        # Hoja 2: Proyecto
        info = pd.DataFrame([{
            'Proyecto': nombre,
            'Latitud': lat,
            'Longitud': lon,
            'N° estaciones encontradas': len(df_cercanas),
            'Estación más cercana': df_cercanas.iloc[0]['nombre'],
            'Distancia mínima (km)': df_cercanas.iloc[0]['distancia_km'],
        }])
        info.to_excel(writer, sheet_name='Info Proyecto', index=False)

    return output.getvalue()


# =============================================================================
# =============================================================================
# FUNCIONES KMZ / KML — MOTOR GIS ROBUSTO v3
# Soporta: namespaces de cualquier herramienta, KMZ anidados sin limite,
#          multiples Document, Document dentro de Folder, MultiGeometry,
#          XML corrupto, proteccion ZIP bomb y memoria
# =============================================================================

MAX_FILE_MB         = 150
MAX_UNCOMPRESSED_MB = 500
MAX_FEATURES_RENDER = 5000
PERU_BOUNDS = {'lat_min': -19.0, 'lat_max': 1.0,
               'lon_min': -82.0, 'lon_max': -68.0}


def kml_color_to_css(kml_color):
    """Convierte color KML formato AABBGGRR a (#RRGGBB, opacidad 0.0-1.0)."""
    try:
        c = kml_color.strip().lstrip('#')
        if len(c) == 6: c = 'ff' + c
        if len(c) != 8: return '#3388ff', 0.8
        aa = int(c[0:2], 16); bb = int(c[2:4], 16)
        gg = int(c[4:6], 16); rr = int(c[6:8], 16)
        return f'#{rr:02x}{gg:02x}{bb:02x}', round(aa / 255.0, 2)
    except Exception:
        return '#3388ff', 0.8


def _strip_namespaces(kml_text):
    """
    Elimina TODOS los namespaces del XML antes de parsear.
    Convierte <gx:Track> en <Track>, </kml:Document> en </Document>, etc.
    Hace el parser completamente agnóstico a la herramienta de origen.
    """
    result = re.sub(r'\s+xmlns(:\w+)?="[^"]*"', '', kml_text)
    result = re.sub(r'(</?)\w+:(\w)', r'\1\2', result)
    return result


def _decode_kml_bytes(raw_bytes):
    """Detecta encoding y decodifica bytes a texto KML."""
    for enc in ('utf-8-sig', 'utf-8', 'utf-16', 'latin-1'):
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw_bytes.decode('utf-8', errors='replace')


def _parse_coords_kml(coord_text):
    """
    Parsea texto de <coordinates> KML a lista de [lat, lon].
    Formato KML: lon,lat,alt lon,lat,alt ...
    Soporta coma decimal europea y separadores mixtos.
    """
    coords = []
    texto = re.sub(r'[\t\r\n]+', ' ', coord_text.strip())
    for token in texto.split():
        partes = token.split(',')
        if len(partes) >= 2:
            try:
                lon = float(partes[0])
                lat = float(partes[1])
                coords.append([lat, lon])
            except ValueError:
                continue
    return coords


def _coords_regex_fallback(kml_text):
    """Extrae coordenadas por regex cuando el XML esta corrupto (ultimo recurso)."""
    matches = re.findall(r'<coordinates[^>]*>(.*?)</coordinates>', kml_text, re.DOTALL)
    all_coords = []
    for m in matches:
        all_coords.extend(_parse_coords_kml(m))
    return all_coords


def _validar_coords_peru(features):
    """Revisa si las coordenadas estan dentro de los limites de Peru."""
    invalidas = 0
    for f in features:
        for lat, lon in f.get('geom', []):
            if not (PERU_BOUNDS['lat_min'] <= lat <= PERU_BOUNDS['lat_max'] and
                    PERU_BOUNDS['lon_min'] <= lon <= PERU_BOUNDS['lon_max']):
                invalidas += 1
    return invalidas


def parse_estilos_kml(root):
    """
    Extrae estilos KML del arbol XML (ya sin namespaces).
    Retorna dict: '#styleId' -> {line_color, line_width, fill_color, fill_opacity, icon_color}
    """
    default_s = {'line_color': '#3388ff', 'line_width': 2,
                 'fill_color': '#3388ff', 'fill_opacity': 0.35,
                 'icon_color': '#E74C3C'}
    estilos = {}

    for style in root.iter('Style'):
        sid = style.get('id', '').strip()
        if not sid:
            continue
        s = dict(default_s)
        line = style.find('.//LineStyle')
        if line is not None:
            c = (line.findtext('color') or '').strip()
            w = (line.findtext('width') or '').strip()
            if c: s['line_color'], _ = kml_color_to_css(c)
            if w:
                try: s['line_width'] = max(1.0, min(10.0, float(w)))
                except ValueError: pass
        poly = style.find('.//PolyStyle')
        if poly is not None:
            c = (poly.findtext('color') or '').strip()
            f = (poly.findtext('fill') or '').strip()
            if c: s['fill_color'], s['fill_opacity'] = kml_color_to_css(c)
            if f == '0': s['fill_opacity'] = 0.0
        icon = style.find('.//IconStyle')
        if icon is not None:
            c = (icon.findtext('color') or '').strip()
            if c:
                s['icon_color'], _ = kml_color_to_css(c)
                s['line_color'] = s['icon_color']
        estilos[f'#{sid}'] = s

    for smap in root.iter('StyleMap'):
        sid = smap.get('id', '').strip()
        if not sid:
            continue
        for pair in smap.iter('Pair'):
            key = (pair.findtext('key') or '').strip()
            url = (pair.findtext('styleUrl') or '').strip()
            if key == 'normal' and url and url in estilos:
                estilos[f'#{sid}'] = estilos[url]
                break

    return estilos


def _estilo_de_placemark(pm, estilos):
    """Resuelve el estilo de un Placemark (url o inline)."""
    default_s = {'line_color': '#3388ff', 'line_width': 2,
                 'fill_color': '#3388ff', 'fill_opacity': 0.35,
                 'icon_color': '#E74C3C'}
    url = (pm.findtext('styleUrl') or '').strip()
    if url and url in estilos:
        return estilos[url]
    inline = pm.find('Style')
    if inline is not None:
        tmp = parse_estilos_kml(inline)
        if tmp:
            return list(tmp.values())[0]
    return default_s


def _extraer_geometrias(pm):
    """
    Extrae TODAS las geometrias de un Placemark, incluyendo MultiGeometry.
    Retorna lista de (tipo, coords).
    """
    geometrias = []

    def _sacar_coords(elem_geo, tipo):
        cel = elem_geo.find('.//coordinates')
        if cel is not None and cel.text:
            coords = _parse_coords_kml(cel.text)
            if coords:
                geometrias.append((tipo, coords))

    mg = pm.find('.//MultiGeometry')
    if mg is not None:
        for sub in mg:
            tag = sub.tag.lower()
            if 'point' in tag:
                _sacar_coords(sub, 'Punto')
            elif 'linestring' in tag or 'linearring' in tag:
                _sacar_coords(sub, 'Linea')
            elif 'polygon' in tag:
                _sacar_coords(sub, 'Poligono')
        return geometrias

    pt = pm.find('.//Point')
    if pt is not None:
        _sacar_coords(pt, 'Punto')
        return geometrias

    ls = pm.find('.//LineString')
    if ls is not None:
        _sacar_coords(ls, 'Linea')
        return geometrias

    pg = pm.find('.//Polygon')
    if pg is not None:
        outer = pg.find('.//outerBoundaryIs')
        _sacar_coords(outer if outer is not None else pg, 'Poligono')
        return geometrias

    return geometrias


def _placemark_to_features(pm, estilos):
    """Convierte Placemark a lista de features (soporta MultiGeometry)."""
    nombre = (pm.findtext('name') or 'Sin nombre').strip()
    desc_raw = pm.findtext('description') or ''
    desc = re.sub(r'<[^>]+>', ' ', desc_raw).strip()[:200]
    est = _estilo_de_placemark(pm, estilos)
    features = []
    for tipo, coords in _extraer_geometrias(pm):
        if not coords:
            continue
        if tipo == 'Punto':
            centro = coords[0]
        elif tipo == 'Poligono':
            lats = [c[0] for c in coords]; lons = [c[1] for c in coords]
            centro = [sum(lats)/len(lats), sum(lons)/len(lons)]
        else:
            centro = coords[len(coords) // 2]
        features.append({'tipo': tipo, 'nombre': nombre, 'desc': desc,
                         'centro': centro, 'geom': coords, **est})
    return features


def _detectar_networklinks(root):
    """Detecta <NetworkLink> y retorna lista de URLs externas."""
    urls = []
    for nl in root.iter('NetworkLink'):
        href = nl.findtext('.//href') or nl.findtext('href') or ''
        if href.strip():
            urls.append(href.strip())
    return urls


def _parse_scope(scope, estilos, nivel, padre_id):
    """
    Parsea recursivamente un Document o Folder.
    Soporta: Folder, Document anidado, Placemarks sueltos, visibility=0.
    """
    capas = []
    nombre_f = (scope.findtext('name') or f'Capa_{nivel}').strip()
    capa_id = f"{padre_id}/{nombre_f}" if padre_id else nombre_f

    placemarks = []
    for pm in scope.findall('Placemark'):
        placemarks.extend(_placemark_to_features(pm, estilos))

    overlays = []
    for tag in ('GroundOverlay', 'PhotoOverlay', 'ScreenOverlay'):
        for go in scope.findall(tag):
            overlays.append((go.findtext('name') or tag).strip())

    color_dom = placemarks[0].get('line_color', '#888888') if placemarks else '#888888'
    capas.append({
        'id': capa_id, 'nombre': nombre_f, 'nivel': nivel,
        'features': placemarks, 'overlays': overlays, 'color_dom': color_dom,
        'n_puntos':    sum(1 for f in placemarks if f['tipo'] == 'Punto'),
        'n_lineas':    sum(1 for f in placemarks if f['tipo'] == 'Linea'),
        'n_poligonos': sum(1 for f in placemarks if f['tipo'] == 'Poligono'),
        'total': len(placemarks),
    })

    for sub in scope.findall('Folder'):
        capas.extend(_parse_scope(sub, estilos, nivel + 1, capa_id))

    for sub_doc in scope.findall('Document'):
        capas.extend(_parse_scope(sub_doc, estilos, nivel + 1, capa_id))

    return capas


def parse_kml_carpetas(kml_text):
    """
    Parser KML principal. Agnóstico a namespace, soporta XML corrupto,
    múltiples Document, Document dentro de Folder y MultiGeometry.
    """
    kml_clean = _strip_namespaces(kml_text)

    try:
        root = ET.fromstring(kml_clean.encode('utf-8'))
    except ET.ParseError:
        kml_clean2 = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', kml_clean)
        try:
            root = ET.fromstring(kml_clean2.encode('utf-8'))
        except ET.ParseError:
            coords_rescue = _coords_regex_fallback(kml_text)
            if coords_rescue:
                return [{'id': '__rescue__',
                         'nombre': 'Elementos recuperados (XML corrupto)',
                         'nivel': 0, 'overlays': [], 'color_dom': '#E74C3C',
                         'features': [{'tipo': 'Punto', 'nombre': f'Coord {i+1}',
                                       'desc': '', 'centro': c, 'geom': [c],
                                       'line_color': '#E74C3C', 'line_width': 2,
                                       'fill_color': '#E74C3C', 'fill_opacity': 0.5,
                                       'icon_color': '#E74C3C'}
                                      for i, c in enumerate(coords_rescue)],
                         'n_puntos': len(coords_rescue), 'n_lineas': 0,
                         'n_poligonos': 0, 'total': len(coords_rescue)}]
            return []

    estilos = parse_estilos_kml(root)
    networklinks = _detectar_networklinks(root)
    capas = []

    if root.tag == 'Document':
        capas.extend(_parse_scope(root, estilos, nivel=0, padre_id=''))
    else:
        docs = root.findall('Document')
        if not docs:
            docs = root.findall('.//Document')
        if docs:
            for doc in docs:
                capas.extend(_parse_scope(doc, estilos, nivel=0, padre_id=''))
        else:
            capas.extend(_parse_scope(root, estilos, nivel=0, padre_id=''))

    if networklinks:
        if capas:
            capas[0]['_networklinks'] = networklinks
        else:
            capas.append({'id': '__netlinks__', 'nombre': 'NetworkLinks (externos)',
                          'nivel': 0, 'features': [], 'overlays': [],
                          'color_dom': '#F39C12', 'n_puntos': 0,
                          'n_lineas': 0, 'n_poligonos': 0, 'total': 0,
                          '_networklinks': networklinks})
    return capas


def _explorar_zip_recursivo(zip_bytes, nombre_zip, nivel=0):
    """
    Explora un ZIP/KMZ recursivamente sin limite de profundidad.
    Soporta KMZ dentro de KMZ a cualquier nivel de anidamiento.
    """
    capas = []
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            total_bytes = sum(i.file_size for i in zf.infolist())
            if total_bytes > MAX_UNCOMPRESSED_MB * 1024 * 1024:
                return [{'id': f'__zipbomb_{nombre_zip}__',
                         'nombre': f'BLOQUEADO: {nombre_zip} (descomprimido > {MAX_UNCOMPRESSED_MB}MB)',
                         'nivel': nivel, 'features': [], 'overlays': [],
                         'color_dom': '#E74C3C', 'n_puntos': 0,
                         'n_lineas': 0, 'n_poligonos': 0, 'total': 0}]

            nombres = [f for f in zf.namelist()
                       if not any(f.startswith(p) for p in ('__MACOSX', '.'))
                       and '/.' not in f]

            kml_files = sorted([f for f in nombres if f.lower().endswith('.kml')],
                               key=lambda x: (0 if 'doc.kml' in x.lower() else 1, x))
            kmz_files = sorted([f for f in nombres if f.lower().endswith('.kmz')])

            prefijo = os.path.splitext(os.path.basename(nombre_zip))[0]

            for kml_name in kml_files:
                kml_text = _decode_kml_bytes(zf.read(kml_name))
                capas_kml = parse_kml_carpetas(kml_text)
                if len(kml_files) > 1:
                    sub = os.path.splitext(os.path.basename(kml_name))[0]
                    for c in capas_kml:
                        c['nombre'] = f"{sub} / {c['nombre']}"
                elif nivel > 0:
                    for c in capas_kml:
                        c['nombre'] = f"{prefijo} / {c['nombre']}"
                        c['nivel']  = c['nivel'] + nivel
                capas.extend(capas_kml)

            for kmz_name in kmz_files:
                capas.extend(_explorar_zip_recursivo(zf.read(kmz_name), kmz_name, nivel + 1))

    except zipfile.BadZipFile:
        pass

    return capas


def escanear_kmz_v2(uploaded_file):
    """Motor GIS central: entrada principal para KMZ/KML."""
    fname = uploaded_file.name
    raw   = uploaded_file.read()

    size_mb = len(raw) / (1024 * 1024)
    if size_mb > MAX_FILE_MB:
        return [{'id': '__toolarge__',
                 'nombre': f'ARCHIVO DEMASIADO GRANDE ({size_mb:.0f}MB > {MAX_FILE_MB}MB)',
                 'nivel': 0, 'features': [], 'overlays': [],
                 'color_dom': '#E74C3C', 'n_puntos': 0,
                 'n_lineas': 0, 'n_poligonos': 0, 'total': 0}], fname

    if fname.lower().endswith('.kmz'):
        return _explorar_zip_recursivo(raw, fname, nivel=0), fname

    try:
        return parse_kml_carpetas(_decode_kml_bytes(raw)), fname
    except Exception:
        return [], fname


def features_a_geojson(capas_dict):
    """Convierte dict {nombre_capa: [features]} a GeoJSON FeatureCollection."""
    import json
    feats = []
    for nombre_capa, feats_list in capas_dict.items():
        for f in feats_list:
            geom = f.get('geom', [])
            tipo = f.get('tipo', '')
            if tipo == 'Punto' and geom:
                geometry = {"type": "Point", "coordinates": [geom[0][1], geom[0][0]]}
            elif tipo == 'Linea' and len(geom) >= 2:
                geometry = {"type": "LineString",
                            "coordinates": [[c[1], c[0]] for c in geom]}
            elif tipo == 'Poligono' and len(geom) >= 3:
                geometry = {"type": "Polygon",
                            "coordinates": [[[c[1], c[0]] for c in geom]]}
            else:
                continue
            feats.append({"type": "Feature", "geometry": geometry,
                          "properties": {"nombre": f.get('nombre', ''),
                                         "capa": nombre_capa,
                                         "desc": f.get('desc', '')}})
    return json.dumps({"type": "FeatureCollection", "features": feats},
                      ensure_ascii=False, indent=2)



# =============================================================================
# SIDEBAR — INPUTS DEL USUARIO
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1A5276,#2980B9);
                color:white;padding:14px;border-radius:8px;margin-bottom:16px'>
        <div style='font-size:20px'>🌦️</div>
        <div style='font-size:14px;font-weight:bold'>Dashboard SENAMHI</div>
        <div style='font-size:10px;opacity:0.8'>Análisis Geoespacial — Perú</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📍 Coordenadas del proyecto")

    tipo_coord = st.radio(
        "Sistema de coordenadas",
        ["🌐 Geográficas (Lat/Lon)", "📐 UTM (WGS84)", "🧭 Sexagesimal (GMS)"],
        help="Selecciona el sistema de coordenadas de tu proyecto"
    )

    nombre_proyecto = st.text_input(
        "Nombre del proyecto",
        value="Proyecto Sauco",
        help="Nombre descriptivo del proyecto de infraestructura"
    )

    if "Geográficas" in tipo_coord:
        col1, col2 = st.columns(2)
        with col1:
            lat_input = st.number_input(
                "Latitud", value=-8.018, format="%.6f",
                min_value=-18.5, max_value=-0.5,
                help="Negativo = Sur (Perú: -0.5 a -18.5)"
            )
        with col2:
            lon_input = st.number_input(
                "Longitud", value=-78.568, format="%.6f",
                min_value=-82.0, max_value=-68.5,
                help="Negativo = Oeste (Perú: -68.5 a -82)"
            )
        lat_final, lon_final = lat_input, lon_input
        coord_mode = "geo"
    elif "Sexagesimal" in tipo_coord:
        st.caption("Formato Grados, Minutos, Segundos. Para Perú: latitud Sur, longitud Oeste.")

        st.markdown("**Latitud (Sur)**")
        cla1, cla2, cla3 = st.columns(3)
        with cla1:
            lat_g = st.number_input("Grados ° (lat)",  value=8,  min_value=0, max_value=18, step=1, key="lat_g")
        with cla2:
            lat_m = st.number_input("Minutos ′ (lat)", value=1,  min_value=0, max_value=59, step=1, key="lat_m")
        with cla3:
            lat_s = st.number_input("Segundos ″ (lat)", value=4.8, min_value=0.0, max_value=59.99,
                                    step=0.1, format="%.2f", key="lat_s")

        st.markdown("**Longitud (Oeste)**")
        clo1, clo2, clo3 = st.columns(3)
        with clo1:
            lon_g = st.number_input("Grados ° (lon)",  value=78, min_value=68, max_value=82, step=1, key="lon_g")
        with clo2:
            lon_m = st.number_input("Minutos ′ (lon)", value=34, min_value=0, max_value=59, step=1, key="lon_m")
        with clo3:
            lon_s = st.number_input("Segundos ″ (lon)", value=4.8, min_value=0.0, max_value=59.99,
                                    step=0.1, format="%.2f", key="lon_s")

        try:
            lat_final = gms_a_decimal(lat_g, lat_m, lat_s, hemisferio='S')
            lon_final = gms_a_decimal(lon_g, lon_m, lon_s, hemisferio='W')
            st.success(
                f"📍 **Decimal**: lat = {lat_final:.6f}°, lon = {lon_final:.6f}°"
            )
        except Exception as e:
            st.error(f"Error en coordenadas GMS: {e}")
            lat_final, lon_final = -8.018, -78.568
        coord_mode = "gms"
    else:
        zona_utm = st.selectbox(
            "Zona UTM",
            options=[17, 18, 19],
            index=1,
            format_func=lambda z: {
                17: "Zona 17S — Piura, Tumbes, costa norte",
                18: "Zona 18S — Lima, Cusco, Puno (mayoría)",
                19: "Zona 19S — Extremo este Madre de Dios"
            }[z]
        )
        este_input  = st.number_input("Este (m)",  value=768071, step=1,
                                      help="Coordenada Este en metros")
        norte_input = st.number_input("Norte (m)", value=9112918, step=1,
                                      help="Coordenada Norte en metros")
        coord_mode = "utm"

        try:
            lat_final, lon_final, _ = buscar_estaciones_utm(
                zona_utm, este_input, norte_input, n=1
            )
        except Exception:
            lat_final, lon_final = -9.5, -75.5

    n_estaciones = st.slider(
        "N° estaciones a buscar", min_value=3, max_value=10, value=5,
        help="Cuántas estaciones más cercanas mostrar"
    )

    st.markdown("---")
    btn_analizar = st.button("🔍 Analizar", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:10px;color:#999;text-align:center'>
        📡 {len([e for e in ESTACIONES_SENAMHI if e['activa']])} estaciones activas<br>
        Fuente: SENAMHI — senamhi.gob.pe<br>
        Última actualización: Abril 2026
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# ESTADO DE SESIÓN (para mantener resultados entre interacciones)
# =============================================================================
if 'df_result' not in st.session_state:
    st.session_state.df_result   = None
    st.session_state.lat_result  = -8.018
    st.session_state.lon_result  = -78.568
    st.session_state.nombre_result = "Proyecto Sauco"

if btn_analizar or st.session_state.df_result is None:
    with st.spinner("Buscando estaciones más cercanas..."):
        df_found = buscar_estaciones(lat_final, lon_final, n=n_estaciones)
        st.session_state.df_result     = df_found
        st.session_state.lat_result    = lat_final
        st.session_state.lon_result    = lon_final
        st.session_state.nombre_result = nombre_proyecto

df     = st.session_state.df_result
lat    = st.session_state.lat_result
lon    = st.session_state.lon_result
nombre = st.session_state.nombre_result

# =============================================================================
# HEADER PRINCIPAL
# =============================================================================
st.markdown(f"""
<div class='main-header'>
    <h1>🌦️ Dashboard Geoespacial SENAMHI — Perú</h1>
    <p>Análisis de estaciones meteorológicas para infraestructura civil &nbsp;|&nbsp;
       📍 {nombre} &nbsp;|&nbsp; lat: {lat:.5f} | lon: {lon:.5f}</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# MÉTRICAS RÁPIDAS
# =============================================================================
est_cercana = df.iloc[0]
utm_proy = geograficas_a_utm(lat, lon)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📏 Estación más cercana",
              est_cercana['nombre'],
              f"{est_cercana['distancia_km']:.1f} km")
with col2:
    st.metric("🏔️ Elevación (estación #1)",
              f"{est_cercana['elev']:,} m.s.n.m.",
              est_cercana['dpto'])
with col3:
    st.metric("📐 UTM del Proyecto",
              f"Zona {utm_proy['zona']}S",
              f"E:{utm_proy['este_m']:,.0f} N:{utm_proy['norte_m']:,.0f}")
with col4:
    tipos_count = df['tipo'].value_counts().to_dict()
    resumen = " | ".join([f"{t}:{c}" for t, c in tipos_count.items()])
    st.metric("🌦️ Tipos de estación",
              f"{len(df)} encontradas",
              resumen)

st.markdown("---")

# =============================================================================
# TABS PRINCIPALES
# =============================================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🗺️ Mapa Interactivo",
    "📊 Tabla de Estaciones",
    "🌧️ Análisis Climático",
    "📥 Exportar",
    "⛰️ Análisis DEM",
    "🚨 Susceptibilidad",
    "📂 Capas KMZ / KML",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — MAPA INTERACTIVO
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    col_mapa, col_lista = st.columns([3, 1])

    with col_mapa:
        mapa_f = generar_mapa_folium(lat, lon, nombre, df)
        st_folium(mapa_f, width=None, height=520, returned_objects=[])

    with col_lista:
        st.markdown("#### Estaciones encontradas")
        for _, row in df.iterrows():
            rank  = int(row['rank'])
            color = COLORES_RANK.get(rank, '#555')
            st.markdown(f"""
            <div style='border-left:4px solid {color};padding:8px 10px;
                        margin-bottom:8px;background:#fafafa;border-radius:0 6px 6px 0'>
                <div style='font-weight:bold;color:{color}'>#{rank} {row['nombre']}</div>
                <div style='font-size:11px;color:#555'>
                    {TIPOS_ESTACION.get(row['tipo'], row['tipo'])}<br>
                    📏 {row['distancia_km']:.1f} km &nbsp;|&nbsp;
                    ⛰️ {row['elev']:,} m<br>
                    📍 {row['prov']}, {row['dpto']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — TABLA DE ESTACIONES
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### Detalle completo de estaciones más cercanas")

    # Preparar tabla para mostrar
    cols_show = ['rank', 'nombre', 'codigo', 'tipo', 'distancia_km',
                 'elev', 'dpto', 'prov', 'dist', 'lat', 'lon']
    if 'utm_este' in df.columns:
        cols_show += ['utm_zona', 'utm_este', 'utm_norte']

    df_show = df[[c for c in cols_show if c in df.columns]].copy()
    df_show.columns = ['#', 'Nombre', 'Código', 'Tipo', 'Dist. (km)',
                       'Elev. (m)', 'Departamento', 'Provincia', 'Distrito',
                       'Latitud', 'Longitud'] + (
                       ['Zona UTM', 'Este (m)', 'Norte (m)']
                       if 'utm_este' in df.columns else [])
    df_show = df_show.round({'Dist. (km)': 1, 'Latitud': 5, 'Longitud': 5})

    st.dataframe(
        df_show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "#":          st.column_config.NumberColumn(width="small"),
            "Dist. (km)": st.column_config.NumberColumn(format="%.1f km"),
            "Elev. (m)":  st.column_config.NumberColumn(format="%d m"),
        }
    )

    st.markdown("---")
    st.markdown("#### Todas las estaciones activas del catálogo")

    df_todo = pd.DataFrame(ESTACIONES_SENAMHI)
    df_todo = df_todo[df_todo['activa'] == True].drop(columns=['activa'])
    df_todo['dist_al_proyecto_km'] = df_todo.apply(
        lambda r: round(haversine(lat, lon, r['lat'], r['lon']), 1), axis=1
    )
    df_todo = df_todo.sort_values('dist_al_proyecto_km')

    busq = st.text_input("🔎 Buscar estación por nombre o departamento", "")
    if busq:
        df_todo = df_todo[
            df_todo['nombre'].str.contains(busq, case=False) |
            df_todo['dpto'].str.contains(busq, case=False)
        ]

    st.dataframe(
        df_todo.rename(columns={
            'codigo':'Código','nombre':'Nombre','tipo':'Tipo',
            'dpto':'Depto','prov':'Provincia','dist':'Distrito',
            'lat':'Lat','lon':'Lon','elev':'Elev(m)',
            'dist_al_proyecto_km':'Dist. (km)'
        }),
        use_container_width=True,
        hide_index=True,
        height=320
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — ANÁLISIS CLIMÁTICO
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    dpto_ref = est_cercana['dpto']
    precip   = get_precip_data(dpto_ref)

    st.markdown(f"#### Precipitación histórica — Referencia: {precip['estacion']} ({dpto_ref})")
    st.caption("Datos referenciales SENAMHI. Para datos oficiales exactos consultar senamhi.gob.pe")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        # Gráfico de barras de precipitación
        colores_mm = ['#E74C3C' if mm >= 100 else '#E67E22' if mm >= 60
                      else '#3498DB' for mm in precip['mm']]
        fig_precip = go.Figure()
        fig_precip.add_trace(go.Bar(
            x=precip['meses'],
            y=precip['mm'],
            marker_color=colores_mm,
            name='Precipitación (mm)',
            hovertemplate='%{x}: %{y} mm<extra></extra>'
        ))
        fig_precip.add_hline(
            y=80, line_dash="dash", line_color="red",
            annotation_text="Umbral crítico 80mm"
        )
        fig_precip.update_layout(
            title='Precipitación mensual (mm)',
            xaxis_title='Mes',
            yaxis_title='mm',
            height=300,
            margin=dict(t=40, b=30, l=30, r=20),
            showlegend=False
        )
        st.plotly_chart(fig_precip, use_container_width=True)

    with col_g2:
        # Días de lluvia
        fig_dias = go.Figure()
        fig_dias.add_trace(go.Bar(
            x=precip['meses'],
            y=precip['dias'],
            marker_color='#5DADE2',
            name='Días con lluvia',
            hovertemplate='%{x}: %{y} días<extra></extra>'
        ))
        fig_dias.update_layout(
            title='Días con lluvia por mes',
            xaxis_title='Mes',
            yaxis_title='Días',
            height=300,
            margin=dict(t=40, b=30, l=30, r=20),
            showlegend=False
        )
        st.plotly_chart(fig_dias, use_container_width=True)

    # Temporada crítica
    max_mm   = max(precip['mm'])
    mes_pico = precip['meses'][precip['mm'].index(max_mm)]
    meses_criticos = [precip['meses'][i] for i, mm in enumerate(precip['mm']) if mm >= 60]

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("🌧️ Mes más lluvioso", mes_pico, f"{max_mm} mm")
    with col_b:
        st.metric("⚠️ Meses críticos (≥60mm)",
                  f"{len(meses_criticos)} meses",
                  ", ".join(meses_criticos) if meses_criticos else "Ninguno")
    with col_c:
        total_anual = sum(precip['mm'])
        st.metric("📊 Precipitación anual", f"{total_anual} mm",
                  f"Promedio {total_anual/12:.0f} mm/mes")

    st.markdown("---")
    st.markdown("#### Comparativo de precipitación entre las 5 estaciones")
    st.caption("Distancias al proyecto y contexto climático de cada estación")

    fig_comp = go.Figure()
    for _, row in df.iterrows():
        rank  = int(row['rank'])
        color = COLORES_RANK.get(rank, '#555')
        p_data = get_precip_data(row['dpto'])
        fig_comp.add_trace(go.Scatter(
            x=p_data['meses'],
            y=p_data['mm'],
            mode='lines+markers',
            name=f"#{rank} {row['nombre']} ({row['distancia_km']:.0f}km)",
            line=dict(color=color, width=2),
            marker=dict(size=5)
        ))

    fig_comp.update_layout(
        title='Comparativo de precipitación mensual entre estaciones cercanas',
        xaxis_title='Mes',
        yaxis_title='Precipitación (mm)',
        height=350,
        margin=dict(t=40, b=30, l=40, r=20),
        legend=dict(orientation='h', y=-0.2)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — EXPORTAR
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("#### Exportar resultados del análisis")

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.markdown("##### 📊 Excel — Tabla de estaciones")
        st.write("Descarga un archivo Excel con las estaciones encontradas y la información del proyecto.")
        excel_data = exportar_excel(df, lat, lon, nombre)
        st.download_button(
            label="⬇️ Descargar Excel",
            data=excel_data,
            file_name=f"estaciones_{nombre.lower().replace(' ','_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_e2:
        st.markdown("##### 🗺️ Mapa HTML — Archivo interactivo")
        st.write("Descarga el mapa como archivo HTML que puedes abrir en cualquier navegador sin internet.")
        mapa_export = generar_mapa_folium(lat, lon, nombre, df)
        mapa_html   = mapa_export._repr_html_()
        st.download_button(
            label="⬇️ Descargar Mapa HTML",
            data=mapa_html,
            file_name=f"mapa_{nombre.lower().replace(' ','_')}.html",
            mime="text/html",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("##### 📋 Resumen en texto")
    resumen_txt = f"""ANÁLISIS DE ESTACIONES SENAMHI
{'='*50}
Proyecto      : {nombre}
Coordenadas   : lat={lat:.6f}, lon={lon:.6f}
UTM WGS84     : Zona {utm_proy['zona']}S — Este {utm_proy['este_m']:,.0f}m, Norte {utm_proy['norte_m']:,.0f}m
Análisis      : {len(df)} estaciones activas más cercanas

ESTACIONES ENCONTRADAS
{'-'*50}
"""
    for _, row in df.iterrows():
        resumen_txt += (
            f"#{int(row['rank'])}  {row['nombre']:<22} | "
            f"{row['tipo']:<4} | {row['distancia_km']:>6.1f} km | "
            f"{row['elev']:>5,} m.s.n.m. | {row['dpto']}\n"
        )
    resumen_txt += f"\nFuente: SENAMHI — senamhi.gob.pe | Generado: Abril 2026"

    st.code(resumen_txt, language=None)
    st.download_button(
        "⬇️ Descargar resumen .txt",
        data=resumen_txt,
        file_name=f"resumen_{nombre.lower().replace(' ','_')}.txt",
        mime="text/plain"
    )

# =============================================================================
# TAB 5 — ANÁLISIS DEM
# =============================================================================
with tab5:
    st.markdown("#### ⛰️ Análisis de Terreno DEM")
    st.caption(
        "Modelo Digital de Elevación sintético (fractal multicapa) calibrado con la altitud "
        "del punto. Genera mapa de pendiente, delimitación de cuenca hidrográfica D8 y perfil "
        "de elevación transversal."
    )

    if not DEM_OK:
        st.error(f"❌ No se pudo cargar dem_analysis.py: {_dem_err_msg}")
        st.info("Asegúrate de que dem_analysis.py esté en la carpeta notebooks y scipy/matplotlib estén instalados.")
    else:
        # ── Fuente de datos ─────────────────────────────────────────────────
        col_fuente, col_info = st.columns([2, 3])
        with col_fuente:
            fuente_dem = st.radio(
                "Fuente de datos DEM",
                options=["🛰️ SRTM Real (NASA, 90m)", "🔬 Sintético (fractal Andino)"],
                index=0,
                horizontal=True,
                help=(
                    "**SRTM Real**: descarga datos reales del satélite NASA. "
                    "Requiere `pip install srtm.py` e internet.\n\n"
                    "**Sintético**: genera terreno Andino realista sin internet. "
                    "Ideal para pruebas o zonas sin cobertura SRTM."
                )
            )
        with col_info:
            if "SRTM" in fuente_dem:
                st.info(
                    "🛰️ **Datos reales NASA SRTM** — resolución 90m. "
                    "El primer análisis descarga el tile (~2.8 MB); "
                    "los siguientes usan caché local y son instantáneos. "
                    "Requiere: `pip install srtm.py`",
                    icon=None
                )
            else:
                st.info(
                    "🔬 **DEM sintético** — terreno fractal multicapa calibrado "
                    "con la altitud del punto. Funciona sin internet.",
                    icon=None
                )

        usar_srtm_val = "auto" if "SRTM" in fuente_dem else "sintetico"

        # ── Parámetros ──────────────────────────────────────────────────────
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            radio_dem = st.slider("Radio de análisis (km)", 2, 15, 5, 1)
        with col_d2:
            umbral_dem = st.slider("Umbral de flujo (celdas)", 50, 500, 200, 50)
        with col_d3:
            angulo_dem = st.slider("Ángulo del perfil (°)", 0, 175, 45, 5)

        btn_dem = st.button("🔍 Ejecutar Análisis DEM", type="primary", use_container_width=True)

        dem_cache_key = f"{lat:.4f}_{lon:.4f}_{radio_dem}_{umbral_dem}_{angulo_dem}_{usar_srtm_val}"
        if "dem_cache_key" not in st.session_state: st.session_state.dem_cache_key = None
        if "dem_resultado" not in st.session_state: st.session_state.dem_resultado = None

        if btn_dem or st.session_state.dem_cache_key != dem_cache_key:
            spinner_msg = (
                "Descargando tile SRTM NASA y calculando cuenca..."
                if usar_srtm_val == "auto"
                else "Generando DEM sintético y calculando cuenca..."
            )
            with st.spinner(spinner_msg):
                try:
                    res_dem = dem_mod.analisis_dem_completo(
                        lat=lat, lon=lon,
                        nombre_proyecto=nombre,
                        radio_km=radio_dem,
                        elev_base=None,
                        angulo_perfil=angulo_dem,
                        umbral_flujo=umbral_dem,
                        usar_srtm=usar_srtm_val,
                    )
                    st.session_state.dem_resultado = res_dem
                    st.session_state.dem_cache_key = dem_cache_key
                except Exception as e_dem:
                    st.error(f"Error en análisis DEM: {e_dem}")
                    st.session_state.dem_resultado = None

        res = st.session_state.dem_resultado
        if res is None:
            st.info("Ajusta los parámetros y presiona **Ejecutar Análisis DEM** para comenzar.")
        else:
            dem_data   = res["dem_data"]
            cuenca     = res["cuenca_data"]
            perfil     = res["perfil_data"]
            figs       = res["figuras"]
            sp         = figs["stats_pendiente"]
            s          = perfil["stats"]
            fuente_txt = res.get("fuente_dem", "—")

            # Badge de fuente
            badge_color = "#1a6b3c" if "SRTM" in fuente_txt else "#7b5800"
            st.markdown(
                f'<span style="background:{badge_color};color:white;padding:3px 10px;'
                f'border-radius:12px;font-size:12px;font-weight:bold">📡 {fuente_txt}</span>',
                unsafe_allow_html=True
            )
            st.markdown("")

            # ── Métricas rápidas ─────────────────────────────────────────────
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🏔️ Elevación base",  f"{dem_data['elev_base']:,.0f} m.s.n.m.")
            m2.metric("📏 Desnivel total",   f"{s['desnivel_m']:.0f} m")
            m3.metric("🌊 Área de cuenca",   f"{cuenca['area_km2']:.1f} km²")
            m4.metric("📐 Pendiente media",  f"{s['pendiente_media_pct']:.1f}%")

            st.markdown("---")

            # ── Hillshade + Pendiente ────────────────────────────────────────
            col_hs, col_pend = st.columns(2)
            with col_hs:
                st.markdown("##### Relieve Sombreado (Hillshade)")
                fig_hs = figs.get("hillshade") or figs.get("fig_hillshade")
                if fig_hs:
                    st.pyplot(fig_hs, use_container_width=True)

            with col_pend:
                st.markdown("##### Mapa de Pendiente")
                fig_pend = figs.get("pendiente") or figs.get("fig_pendiente")
                if fig_pend:
                    st.pyplot(fig_pend, use_container_width=True)

            # ── Cuenca + Estadísticas ────────────────────────────────────────
            col_cuenca, col_stats = st.columns(2)
            with col_cuenca:
                st.markdown("##### Cuenca Hidrográfica")
                fig_cuenca = figs.get("cuenca") or figs.get("fig_cuenca")
                if fig_cuenca:
                    st.pyplot(fig_cuenca, use_container_width=True)
                st.caption(
                    f"Área: **{cuenca['area_km2']:.2f} km²** · "
                    f"{cuenca['n_celdas']:,} celdas · algoritmo D8"
                )

            with col_stats:
                st.markdown("##### Distribución de Pendiente")
                pend_names  = list(sp.keys())
                pend_pcts   = [sp[k]["porcentaje"] for k in pend_names]
                colores_bar = ["#FFFFCC", "#A1D99B", "#FEC44F", "#F03B20", "#99000D"]

                fig_bar = go.Figure(go.Bar(
                    x=pend_names, y=pend_pcts,
                    marker_color=colores_bar[:len(pend_names)],
                    text=[f"{p:.1f}%" for p in pend_pcts],
                    textposition="outside"
                ))
                fig_bar.update_layout(
                    yaxis_title="% del área",
                    height=300,
                    margin=dict(t=20, b=40),
                    plot_bgcolor="white",
                    yaxis=dict(range=[0, max(pend_pcts)*1.25])
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                rangos = {"Plano": "0°–5°", "Suave": "5°–15°",
                          "Moderada": "15°–30°", "Escarpada": "30°–45°",
                          "Muy Escarpada": "45°–90°"}
                rows = [{"Clase": k,
                         "Rango": rangos.get(k, "—"),
                         "Área (%)": f"{sp[k]['porcentaje']:.1f}%"}
                        for k in pend_names]
                st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

            st.markdown("---")

            # ── Perfil de elevación (Plotly) ─────────────────────────────────
            st.markdown("##### Perfil de Elevación Transversal")
            dist_km    = perfil["distancias_km"]
            elev_m     = perfil["elevaciones"]
            centro_idx = len(dist_km) // 2

            fig_perf = go.Figure()
            fig_perf.add_trace(go.Scatter(
                x=dist_km, y=elev_m,
                mode="lines",
                fill="tozeroy",
                fillcolor="rgba(41,128,185,0.15)",
                line=dict(color="#1A5276", width=2),
                name="Elevación"
            ))
            fig_perf.add_trace(go.Scatter(
                x=[dist_km[centro_idx]], y=[elev_m[centro_idx]],
                mode="markers",
                marker=dict(size=10, color="red", symbol="star"),
                name=nombre
            ))
            fig_perf.update_layout(
                xaxis_title="Distancia (km)",
                yaxis_title="Elevación (m.s.n.m.)",
                height=320,
                margin=dict(t=10, b=40),
                plot_bgcolor="white",
                xaxis=dict(gridcolor="#eee"),
                yaxis=dict(gridcolor="#eee"),
                legend=dict(orientation="h", y=1.05)
            )
            st.plotly_chart(fig_perf, use_container_width=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Elev. mín.",  f"{s['elev_min']:.0f} m")
            c2.metric("Elev. máx.",  f"{s['elev_max']:.0f} m")
            c3.metric("Desnivel",    f"{s['desnivel_m']:.0f} m")
            c4.metric("Pend. media", f"{s['pendiente_media_pct']:.1f}%")

            st.markdown("---")

            # ── Mapa Folium DEM ──────────────────────────────────────────────
            st.markdown("##### Mapa Interactivo con Capas DEM")
            mapa_dem = res.get("mapa")
            if mapa_dem:
                st_folium(mapa_dem, width=None, height=480, returned_objects=[])
                mapa_dem_html = mapa_dem._repr_html_()
                st.download_button(
                    "⬇️ Descargar Mapa DEM (HTML)",
                    data=mapa_dem_html,
                    file_name=f"dem_{nombre.lower().replace(' ','_')}.html",
                    mime="text/html"
                )
            else:
                mapa_simple = folium.Map(location=[lat, lon], zoom_start=12,
                                         tiles="CartoDB positron")
                folium.Marker([lat, lon], tooltip=nombre,
                              icon=folium.Icon(color="red")).add_to(mapa_simple)
                st_folium(mapa_simple, width=None, height=480, returned_objects=[])

# =============================================================================
# TAB 6 — SUSCEPTIBILIDAD A DESLIZAMIENTOS
# =============================================================================
with tab6:
    st.markdown("#### 🚨 Modelo de Susceptibilidad a Deslizamientos")
    st.caption(
        "Análisis multicriterio ponderado (WLC) basado en la metodología CENEPRED Perú. "
        "Combina pendiente, precipitación, elevación y curvatura del terreno para "
        "estimar zonas de riesgo ante movimientos en masa."
    )

    if not SUSC_OK:
        st.error(f"❌ No se pudo cargar susceptibilidad.py: {_susc_err_msg}")
    elif not DEM_OK or st.session_state.get("dem_resultado") is None:
        st.warning(
            "⚠️ Primero ejecuta el **Análisis DEM** en el tab ⛰️ para "
            "generar el modelo de terreno que necesita este módulo."
        )
    else:
        res_dem = st.session_state.dem_resultado
        dem_data_susc = res_dem["dem_data"]

        st.markdown("##### Parámetros del modelo")
        col_p1, col_p2 = st.columns([2, 3])
        with col_p1:
            precip_mm = st.number_input(
                "Precipitación anual estimada (mm/año)",
                min_value=50, max_value=5000, value=700, step=50,
                help=(
                    "Usa el dato de la estación SENAMHI más cercana. "
                    "Referencia: Costa <300 mm | Sierra 500-1000 mm | "
                    "Ceja de selva 1000-3000 mm | Selva >3000 mm"
                )
            )
        with col_p2:
            st.info(
                f"📍 Estación más cercana: **{df.iloc[0]['nombre']}** "
                f"({df.iloc[0]['tipo']}) — {df.iloc[0]['distancia_km']:.1f} km | "
                f"Dpto: {df.iloc[0]['dpto']}",
            )

        with st.expander("⚙️ Ajustar pesos del modelo (avanzado)"):
            st.markdown(
                "Los pesos deben sumar **1.00**. "
                "Valores por defecto según guía técnica CENEPRED."
            )
            cw1, cw2, cw3, cw4 = st.columns(4)
            w_pend = cw1.slider("Pendiente",      0.10, 0.70, 0.40, 0.05)
            w_prec = cw2.slider("Precipitación",  0.10, 0.50, 0.30, 0.05)
            w_elev = cw3.slider("Elevación",      0.05, 0.35, 0.15, 0.05)
            w_curv = cw4.slider("Curvatura",      0.05, 0.35, 0.15, 0.05)
            suma_pesos = w_pend + w_prec + w_elev + w_curv
            if abs(suma_pesos - 1.0) > 0.01:
                st.warning(f"⚠️ Los pesos suman {suma_pesos:.2f} — deben sumar 1.00")
            else:
                st.success(f"✓ Pesos válidos (suma = {suma_pesos:.2f})")

        btn_susc = st.button("🔍 Calcular Susceptibilidad", type="primary",
                              use_container_width=True)

        susc_key = f"{lat:.4f}_{lon:.4f}_{precip_mm}_{w_pend}_{w_prec}_{w_elev}_{w_curv}_{res_dem.get('fuente_dem','')}"
        if "susc_key"       not in st.session_state: st.session_state.susc_key       = None
        if "susc_resultado" not in st.session_state: st.session_state.susc_resultado = None

        if btn_susc or st.session_state.susc_key != susc_key:
            with st.spinner("Calculando índice de susceptibilidad..."):
                try:
                    res_susc = susc_mod.susceptibilidad_completo(
                        dem_data=dem_data_susc,
                        nombre_proyecto=nombre,
                        precip_anual_mm=precip_mm,
                        w_pendiente=w_pend,
                        w_precip=w_prec,
                        w_elevacion=w_elev,
                        w_curvatura=w_curv,
                    )
                    st.session_state.susc_resultado = res_susc
                    st.session_state.susc_key       = susc_key
                except Exception as e_susc:
                    st.error(f"Error: {e_susc}")
                    st.session_state.susc_resultado = None

        res_s = st.session_state.susc_resultado
        if res_s is None:
            st.info("Ajusta los parámetros y presiona **Calcular Susceptibilidad**.")
        else:
            susc_data = res_s["susc_data"]
            stats_s   = susc_data["stats"]
            clase_dom = max(stats_s, key=lambda k: stats_s[k]["porcentaje"])
            color_dom = susc_mod.CLASES_SUSCEPTIBILIDAD[clase_dom]["color"]
            area_alto = sum(stats_s[n]["area_km2"] for n in ["Alta", "Muy Alta"] if n in stats_s)

            st.markdown(
                f'<span style="background:{color_dom};color:white;padding:4px 14px;'
                f'border-radius:12px;font-size:13px;font-weight:bold">'
                f'⚠️ Susceptibilidad Dominante: {clase_dom}</span>',
                unsafe_allow_html=True
            )
            st.markdown("")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📊 Índice promedio",    f"{susc_data['indice_medio']:.2f} / 5.00")
            m2.metric("🔴 Área Alta+Muy Alta",  f"{area_alto:.2f} km²")
            m3.metric("🌧️ Precipitación usada", f"{precip_mm} mm/año")
            m4.metric("📐 Pendiente factor",    f"{susc_data['factores']['pendiente'].mean():.2f} / 5")

            st.markdown("---")
            st.markdown("##### Análisis completo")
            fig_susc = res_s["figura"]
            if fig_susc:
                st.pyplot(fig_susc, use_container_width=True)

            st.markdown("---")
            st.markdown("##### Mapa interactivo de susceptibilidad")
            mapa_susc = res_s["mapa"]
            if mapa_susc:
                from streamlit_folium import st_folium
                st_folium(mapa_susc, width=None, height=500, returned_objects=[])
                mapa_susc_html = mapa_susc._repr_html_()
                st.download_button(
                    "⬇️ Descargar Mapa Susceptibilidad (HTML)",
                    data=mapa_susc_html,
                    file_name=f"susceptibilidad_{nombre.lower().replace(' ','_')}.html",
                    mime="text/html"
                )

            st.markdown("---")
            st.markdown("##### Interpretación técnica")
            st.markdown(f"""
| Factor | Peso | Justificación |
|--------|------|---------------|
| Pendiente | {w_pend*100:.0f}% | Factor geomorfológico dominante en movimientos en masa |
| Precipitación | {w_prec*100:.0f}% | Detonante principal: satura el suelo y reduce cohesión |
| Elevación | {w_elev*100:.0f}% | Contexto altitudinal, permafrost y ciclos hielo-deshielo |
| Curvatura | {w_curv*100:.0f}% | Zonas cóncavas concentran flujo hídrico |

**Clase dominante: {clase_dom}** — Índice promedio {susc_data['indice_medio']:.2f}/5.00

> Ref: CENEPRED — *Manual para la Evaluación de Riesgos originados por Movimientos en Masa*, 2da edición.
            """)

# =============================================================================
# =============================================================================
# TAB 7 — VISOR KMZ / KML (Motor GIS Robusto v3)
# =============================================================================
with tab7:
    st.markdown("#### Visor de Capas KMZ / KML")
    st.caption(
        "Sube un archivo KMZ o KML. Se mostrara el mismo arbol de capas que Google Earth Pro. "
        "Soporta KMZ anidados, multiples capas y estilos originales."
    )

    uploaded_kmz = st.file_uploader(
        "Archivo KMZ / KML",
        type=["kmz", "kml"],
        accept_multiple_files=False,
        help=f"Max {MAX_FILE_MB}MB. Compatible con Google Earth Pro, QGIS, ArcGIS, AutoCAD Civil 3D.",
        key="kmz_uploader_v2"
    )

    if 'kmz_v2_capas'     not in st.session_state: st.session_state.kmz_v2_capas     = []
    if 'kmz_v2_nombre'    not in st.session_state: st.session_state.kmz_v2_nombre    = None
    if 'kmz_v2_seleccion' not in st.session_state: st.session_state.kmz_v2_seleccion = {}

    if uploaded_kmz is not None:
        if st.session_state.kmz_v2_nombre != uploaded_kmz.name:
            with st.spinner(f"Procesando {uploaded_kmz.name}..."):
                capas_v2, fname_v2 = escanear_kmz_v2(uploaded_kmz)
            st.session_state.kmz_v2_capas     = capas_v2
            st.session_state.kmz_v2_nombre    = fname_v2
            st.session_state.kmz_v2_seleccion = {c['id']: True for c in capas_v2}

        capas  = st.session_state.kmz_v2_capas
        nombre = st.session_state.kmz_v2_nombre or uploaded_kmz.name

        if not capas:
            st.warning("No se encontraron capas vectoriales. Verifica que el KMZ contenga marcas de posicion con coordenadas.")
            with st.expander("Diagnostico del archivo", expanded=True):
                import zipfile as _zf, io as _io
                try:
                    uploaded_kmz.seek(0)
                    raw2 = uploaded_kmz.read()
                    if uploaded_kmz.name.lower().endswith('.kmz'):
                        with _zf.ZipFile(_io.BytesIO(raw2)) as _z:
                            st.write("**Archivos dentro del KMZ:**", _z.namelist())
                            kmls2 = [f for f in _z.namelist() if f.lower().endswith('.kml')]
                            if kmls2:
                                txt2 = _z.read(kmls2[0]).decode('utf-8', errors='replace')
                                st.code(txt2[:800], language='xml')
                    else:
                        st.code(raw2.decode('utf-8', errors='replace')[:800], language='xml')
                except Exception as _e:
                    st.error(f"Error al leer: {_e}")
        else:
            # ── Metricas generales ────────────────────────────────────────────
            total_overlays = sum(len(c['overlays']) for c in capas)
            total_feats    = sum(c['total'] for c in capas)
            total_nl       = sum(len(c.get('_networklinks', [])) for c in capas)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Carpetas",          len(capas))
            m2.metric("Elementos vectoriales", total_feats)
            m3.metric("Capas raster",      total_overlays)
            m4.metric("NetworkLinks",       total_nl)

            # ── Advertencias ─────────────────────────────────────────────────
            if total_overlays > 0:
                names_ov = [n for c in capas for n in c['overlays']]
                st.warning(
                    f"Capas raster detectadas (no renderizables en mapa web): "
                    f"{', '.join(names_ov[:5])}{'...' if len(names_ov) > 5 else ''}. "
                    "Exporta el KMZ como KML desde Google Earth Pro para visualizarlas."
                )

            if total_nl > 0:
                all_nl = [url for c in capas for url in c.get('_networklinks', [])]
                st.info(
                    f"NetworkLinks detectados ({total_nl}): referencias a archivos externos "
                    f"que no se descargan automaticamente. URLs: "
                    f"{', '.join(all_nl[:3])}{'...' if len(all_nl) > 3 else ''}"
                )

            # ── Validacion geografica Peru ────────────────────────────────────
            all_features = [f for c in capas for f in c['features']]
            coords_invalidas = _validar_coords_peru(all_features)
            if coords_invalidas > 0:
                st.warning(
                    f"{coords_invalidas} coordenadas fuera del rango geografico de Peru "
                    f"(lat: {PERU_BOUNDS['lat_min']} a {PERU_BOUNDS['lat_max']}, "
                    f"lon: {PERU_BOUNDS['lon_min']} a {PERU_BOUNDS['lon_max']}). "
                    "Verifica el sistema de coordenadas del archivo."
                )

            if total_feats > MAX_FEATURES_RENDER:
                st.warning(
                    f"El archivo contiene {total_feats:,} elementos. "
                    f"Se renderizaran solo los primeros {MAX_FEATURES_RENDER:,} para mantener el rendimiento del mapa."
                )

            # ── Arbol de capas con checkboxes ─────────────────────────────────
            st.markdown("---")
            st.markdown("##### Capas del archivo")

            col_todas, col_ninguna = st.columns([1, 1])
            with col_todas:
                if st.button("Seleccionar todas", key="kmz_todas"):
                    for c in capas:
                        st.session_state.kmz_v2_seleccion[c['id']] = True
                    st.rerun()
            with col_ninguna:
                if st.button("Deseleccionar todas", key="kmz_ninguna"):
                    for c in capas:
                        st.session_state.kmz_v2_seleccion[c['id']] = False
                    st.rerun()

            for c in capas:
                indent  = " " * (c['nivel'] * 6)
                dot_col = c['color_dom'] if c['color_dom'] != '#888888' else '#aaaaaa'
                dot     = f"<span style='color:{dot_col};font-size:14px'>&#9679;</span>"
                stats   = f"<span style='color:#888;font-size:11px'> &nbsp; {c['total']} elem"
                if c['n_puntos']:   stats += f" | {c['n_puntos']} pts"
                if c['n_lineas']:   stats += f" | {c['n_lineas']} lin"
                if c['n_poligonos']: stats += f" | {c['n_poligonos']} pol"
                if c['overlays']:   stats += f" | {len(c['overlays'])} raster"
                if c.get('_networklinks'): stats += f" | {len(c['_networklinks'])} netlink"
                stats += "</span>"
                label_html = f"{indent}{dot} <b>{c['nombre']}</b>{stats}"

                chk_col, lbl_col = st.columns([0.05, 0.95])
                with lbl_col:
                    st.markdown(label_html, unsafe_allow_html=True)
                with chk_col:
                    val = st.session_state.kmz_v2_seleccion.get(c['id'], True)
                    st.session_state.kmz_v2_seleccion[c['id']] = st.checkbox(
                        "", value=val, key=f"chk_{c['id']}", label_visibility="collapsed"
                    )

            # ── Mapa ─────────────────────────────────────────────────────────
            capas_activas = [c for c in capas
                             if st.session_state.kmz_v2_seleccion.get(c['id'], True)
                             and c['features']]

            if capas_activas:
                st.markdown("---")
                mapa_v2 = folium.Map(location=[-9.19, -75.0], zoom_start=6,
                                     tiles='CartoDB positron')
                bounds_pts = []
                feats_rendered = 0

                for c in capas_activas:
                    if feats_rendered >= MAX_FEATURES_RENDER:
                        break
                    fg = folium.FeatureGroup(name=c['nombre'], show=True)
                    for f in c['features']:
                        if feats_rendered >= MAX_FEATURES_RENDER:
                            break
                        geom  = f['geom']
                        tipo  = f['tipo']
                        lc    = f.get('line_color', '#3388ff')
                        lw    = f.get('line_width', 2)
                        fc    = f.get('fill_color', '#3388ff')
                        fo    = f.get('fill_opacity', 0.35)
                        ic    = f.get('icon_color', '#E74C3C')
                        popup = folium.Popup(
                            f"<b>{f['nombre']}</b><br><i>{c['nombre']}</i>"
                            + (f"<br>{f['desc']}" if f['desc'] else ''),
                            max_width=260
                        )
                        if tipo == 'Punto' and geom:
                            folium.CircleMarker(
                                location=geom[0], radius=5, color=ic,
                                fill=True, fill_color=ic, fill_opacity=0.9,
                                popup=popup, tooltip=f['nombre']
                            ).add_to(fg)
                            bounds_pts.append(geom[0])
                        elif tipo == 'Linea' and len(geom) >= 2:
                            folium.PolyLine(
                                geom, color=lc, weight=lw, opacity=0.85,
                                popup=popup, tooltip=f['nombre']
                            ).add_to(fg)
                            bounds_pts.extend(geom[::max(1, len(geom)//10)])
                        elif tipo == 'Poligono' and len(geom) >= 3:
                            folium.Polygon(
                                geom, color=lc, weight=lw,
                                fill=True, fill_color=fc, fill_opacity=fo,
                                popup=popup, tooltip=f['nombre']
                            ).add_to(fg)
                            bounds_pts.extend(geom[::max(1, len(geom)//10)])
                        feats_rendered += 1
                    fg.add_to(mapa_v2)

                if bounds_pts:
                    lats = [p[0] for p in bounds_pts]
                    lons = [p[1] for p in bounds_pts]
                    mapa_v2.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

                folium.LayerControl(collapsed=False).add_to(mapa_v2)
                st_folium(mapa_v2, width=None, height=550, returned_objects=[])

                # ── Inventario ────────────────────────────────────────────────
                st.markdown("---")
                st.markdown("##### Inventario de capas activas")
                inv_data = [{'Capa': c['nombre'],
                             'Nivel': c['nivel'],
                             'Puntos': c['n_puntos'],
                             'Lineas': c['n_lineas'],
                             'Poligonos': c['n_poligonos'],
                             'Total': c['total']}
                            for c in capas_activas]
                st.dataframe(inv_data, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown("##### Exportar capas activas")
                cg, cm = st.columns(2)
                with cg:
                    feats_exp = {c['nombre']: c['features'] for c in capas_activas}
                    st.download_button(
                        "Descargar GeoJSON",
                        data=features_a_geojson(feats_exp),
                        file_name=f"capas_{nombre.lower().replace(' ','_')}.geojson",
                        mime="application/geo+json",
                        use_container_width=True
                    )
                with cm:
                    st.download_button(
                        "Descargar Mapa HTML",
                        data=mapa_v2._repr_html_(),
                        file_name=f"mapa_{nombre.lower().replace(' ','_')}.html",
                        mime="text/html",
                        use_container_width=True
                    )
            else:
                st.info("Selecciona al menos una capa con elementos para visualizar el mapa.")

    else:
        st.markdown(
            "<div style='background:#f0f7ff;border:2px dashed #aac4e8;border-radius:10px;"
            "padding:28px;text-align:center;color:#4a6b8a;margin:12px 0'>"
            "<div style='font-size:38px'>&#128194;</div>"
            "<div style='font-size:15px;font-weight:bold;margin:8px 0'>"
            "Arrastra tu archivo KMZ aqui</div>"
            "<div style='font-size:12px;opacity:0.8'>"
            "Se mostrara el mismo arbol de carpetas que en Google Earth Pro<br>"
            "Compatible con Google Earth - QGIS - ArcGIS - AutoCAD Civil 3D"
            "</div></div>",
            unsafe_allow_html=True
        )
        st.markdown("---")
        st.info(
            "Tip: Google Earth Pro: clic derecho sobre la carpeta del proyecto "
            "> Guardar lugar como > KMZ. Incluira todas las subcapas automaticamente."
        )

