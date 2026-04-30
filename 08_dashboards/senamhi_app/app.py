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
    generar_mapa_estaciones, haversine, geograficas_a_utm
)

# ── Módulo de análisis DEM ────────────────────────────────────────────────────
try:
    import dem_analysis as dem_mod
    DEM_OK = True
except Exception as _dem_err:
    DEM_OK = False
    _dem_err_msg = str(_dem_err)

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
        ["🌐 Geográficas (Lat/Lon)", "📐 UTM (WGS84)"],
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Mapa Interactivo",
    "📊 Tabla de Estaciones",
    "🌧️ Análisis Climático",
    "📥 Exportar",
    "⛰️ Análisis DEM"
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
