"""
PolarisX — Monitor de Riesgo Climático
Dashboard Streamlit para análisis de riesgo en proyectos de infraestructura civil

Autor: Fernando Geronimo Ccoillor
Proyecto: Data Science aplicado a Ingeniería Civil
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
import json

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PolarisX | Monitor de Riesgo",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
st.markdown("""
<style>
    /* Fondo general */
    .stApp { background-color: #F5F7FA; }

    /* Tarjetas de métricas */
    .kpi-card {
        background: #1B3A5C;
        border-radius: 12px;
        padding: 18px 14px;
        text-align: center;
        color: white;
        height: 120px;
    }
    .kpi-value   { font-size: 2rem; font-weight: 800; color: #F18F01; }
    .kpi-label   { font-size: 0.78rem; color: #CBD5E1; margin-top: 4px; }
    .kpi-sub     { font-size: 0.72rem; color: #94A3B8; margin-top: 2px; }

    /* Badge de riesgo */
    .badge-muy-alto { background:#C0392B; color:white; padding:4px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }
    .badge-alto     { background:#E67E22; color:white; padding:4px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }
    .badge-medio    { background:#F1C40F; color:#333;  padding:4px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }
    .badge-bajo     { background:#27AE60; color:white; padding:4px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }

    /* Cabecera */
    .header-box {
        background: linear-gradient(135deg, #0D1B2A 0%, #1B3A5C 100%);
        border-radius: 12px;
        padding: 20px 28px;
        color: white;
        margin-bottom: 20px;
    }
    .header-title { font-size: 1.4rem; font-weight: 800; color: #F18F01; margin: 0; }
    .header-sub   { font-size: 0.9rem;  color: #CBD5E1; margin: 4px 0 0 0; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #0D1B2A; }
    [data-testid="stSidebar"] .stSelectbox label { color: #CBD5E1 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATOS ESTÁTICOS DEL PROYECTO SAUCO
# ─────────────────────────────────────────────────────────────────────────────
PROYECTO = {
    "nombre":       "Centro Poblado Sauco",
    "region":       "La Libertad",
    "provincia":    "Otuzco",
    "distrito":     "Salpo",
    "lat":          -8.018,
    "lon":          -78.568,
    "elevacion":    3180,
    "zona_sismica": 3,
    "factor_z":     0.35,
    "riesgo":       "MUY ALTO",
    "radio_km":     2,
}

# Precipitación mensual — Estación Otuzco (SENAMHI)
PRECIP = pd.DataFrame({
    "mes":       ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"],
    "mes_num":   list(range(1, 13)),
    "pp_mm":     [85, 120, 135, 95, 45, 15, 8, 10, 25, 55, 70, 75],
    "temporada": ["crítica","crítica","crítica","crítica","moderada",
                  "seca","seca","seca","seca","moderada","crítica","crítica"],
})
COLOR_MAP = {"crítica": "#C0392B", "moderada": "#E67E22", "seca": "#2E86AB"}
PRECIP["color"] = PRECIP["temporada"].map(COLOR_MAP)
UMBRAL_CRITICO = 80  # mm — umbral a partir del cual se suspenden trabajos de riesgo

ZONAS = pd.DataFrame([
    {"zona": "Zona A",  "tipo": "Deslizamiento activo", "nivel": "MUY ALTO", "dist_km": 0.8,  "lat": -8.012, "lon": -78.562},
    {"zona": "Zona B",  "tipo": "Huaico / Quebrada",    "nivel": "MUY ALTO", "dist_km": 1.2,  "lat": -8.025, "lon": -78.558},
    {"zona": "Zona C",  "tipo": "Deslizamiento ladera", "nivel": "ALTO",     "dist_km": 1.7,  "lat": -8.010, "lon": -78.575},
    {"zona": "Zona D",  "tipo": "Inundación cauce sec.", "nivel": "ALTO",     "dist_km": 1.9,  "lat": -8.030, "lon": -78.570},
])

# ─────────────────────────────────────────────────────────────────────────────
# GENERADOR DE PARTES DIARIOS SINTÉTICOS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def generar_partes(inicio_str="2025-10-01", dias=120):
    np.random.seed(42)
    lluvia_por_mes = dict(zip(PRECIP["mes_num"], PRECIP["pp_mm"]))
    inicio = datetime.strptime(inicio_str, "%Y-%m-%d")
    fechas = [inicio + timedelta(days=i) for i in range(dias)]

    registros = []
    acum_plan = 0.0
    acum_real = 0.0

    for i, fecha in enumerate(fechas):
        mes = fecha.month
        pp_mes = lluvia_por_mes.get(mes, 30)
        prob_lluvia_fuerte = min(pp_mes / 350, 0.45)

        if np.random.random() < prob_lluvia_fuerte:
            clima = "Lluvia fuerte"
            horas = round(np.random.uniform(0, 2), 1)
            tipo_dia = "Perdido"
        elif np.random.random() < 0.12:
            clima = "Nublado / Llovizna"
            horas = round(np.random.uniform(5, 7), 1)
            tipo_dia = "Parcial"
        else:
            clima = "Soleado"
            horas = round(np.random.uniform(7.5, 9), 1)
            tipo_dia = "Normal"

        avance_plan_dia = 100.0 / dias
        avance_real_dia = (horas / 8.0) * avance_plan_dia

        acum_plan = min(100.0, acum_plan + avance_plan_dia)
        acum_real = min(100.0, acum_real + avance_real_dia)

        registros.append({
            "fecha":            fecha,
            "semana":           f"Sem {(i // 7) + 1:02d}",
            "mes":              fecha.strftime("%b %Y"),
            "mes_num":          mes,
            "clima":            clima,
            "tipo_dia":         tipo_dia,
            "horas_plan":       8.0,
            "horas_real":       horas,
            "avance_plan_pct":  round(avance_plan_dia, 3),
            "avance_real_pct":  round(avance_real_dia, 3),
            "acum_plan":        round(acum_plan, 1),
            "acum_real":        round(acum_real, 1),
        })

    return pd.DataFrame(registros)

# ─────────────────────────────────────────────────────────────────────────────
# GENERADOR DE MAPA FOLIUM
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def generar_mapa_html():
    lat, lon = PROYECTO["lat"], PROYECTO["lon"]
    m = folium.Map(location=[lat, lon], zoom_start=13,
                   tiles="CartoDB positron")

    # Capas base alternativas
    folium.TileLayer("CartoDB positron",      name="Mapa base").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Satélite"
    ).add_to(m)
    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="OpenTopoMap", name="Topográfico"
    ).add_to(m)

    # Radio de análisis
    folium.Circle(
        location=[lat, lon], radius=PROYECTO["radio_km"] * 1000,
        color="#2E86AB", fill=True, fill_opacity=0.08,
        popup="Radio de análisis: 2 km"
    ).add_to(m)

    # Marcador del proyecto
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(
            f"<b>{PROYECTO['nombre']}</b><br>"
            f"Riesgo: <b style='color:#C0392B'>MUY ALTO</b><br>"
            f"Elevación: {PROYECTO['elevacion']} m.s.n.m.<br>"
            f"Zona sísmica: {PROYECTO['zona_sismica']} (Z={PROYECTO['factor_z']})",
            max_width=250
        ),
        tooltip="Proyecto Sauco",
        icon=folium.Icon(color="darkblue", icon="home", prefix="fa")
    ).add_to(m)

    # Zonas de peligro
    color_nivel = {"MUY ALTO": "#C0392B", "ALTO": "#E67E22", "MEDIO": "#F1C40F"}
    for _, z in ZONAS.iterrows():
        color = color_nivel.get(z["nivel"], "#888")
        folium.CircleMarker(
            location=[z["lat"], z["lon"]],
            radius=14,
            color=color, fill=True, fill_opacity=0.6, fill_color=color,
            popup=folium.Popup(
                f"<b>{z['zona']}</b><br>Tipo: {z['tipo']}<br>"
                f"Nivel: <b style='color:{color}'>{z['nivel']}</b><br>"
                f"Distancia: {z['dist_km']} km",
                max_width=220
            ),
            tooltip=f"{z['zona']} — {z['nivel']}",
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m._repr_html_()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — NAVEGACIÓN
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='padding:16px 0 8px 0;'>
            <span style='color:#F18F01;font-size:1.3rem;font-weight:800;'>PolarisX</span>
            <br>
            <span style='color:#CBD5E1;font-size:0.8rem;'>Monitor de Riesgo Climático</span>
        </div>
        <hr style='border-color:#1B3A5C;margin:8px 0 16px 0;'>
    """, unsafe_allow_html=True)

    pagina = st.selectbox(
        "Sección",
        ["🏠  Resumen del Proyecto",
         "🌧  Análisis Climático",
         "📅  Cronograma de Riesgo"],
        label_visibility="collapsed"
    )

    st.markdown("""
        <hr style='border-color:#1B3A5C;margin:16px 0 12px 0;'>
        <div style='color:#64748B;font-size:0.72rem;padding:0 4px;'>
            Fuentes de datos<br>
            <span style='color:#94A3B8;'>SENAMHI · CENEPRED · IGN · NTE E.030</span>
        </div>
        <div style='color:#64748B;font-size:0.72rem;padding:8px 4px 0 4px;'>
            Costo en software: <b style='color:#F18F01;'>S/. 0</b>
        </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA 1 — RESUMEN DEL PROYECTO
# ─────────────────────────────────────────────────────────────────────────────
if "Resumen" in pagina:

    st.markdown(f"""
    <div class="header-box">
        <p class="header-title">Análisis de Riesgo — {PROYECTO['nombre']}</p>
        <p class="header-sub">
            {PROYECTO['distrito']} · {PROYECTO['provincia']} · {PROYECTO['region']} &nbsp;|&nbsp;
            {PROYECTO['lat']}, {PROYECTO['lon']} &nbsp;|&nbsp;
            ~{PROYECTO['elevacion']:,} m.s.n.m.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-value" style="color:#C0392B;">MUY ALTO</div>
            <div class="kpi-label">Riesgo General</div>
            <div class="kpi-sub">4 zonas en 2 km</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-value">3</div>
            <div class="kpi-label">Zona Sísmica</div>
            <div class="kpi-sub">Z = 0.35 (NTE E.030)</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-value">135mm</div>
            <div class="kpi-label">Lluvia pico (Marzo)</div>
            <div class="kpi-sub">Umbral crítico: 80mm</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-value" style="color:#E67E22;">5</div>
            <div class="kpi-label">Meses de riesgo</div>
            <div class="kpi-sub">Nov – Mar (temporada)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_mapa, col_tabla = st.columns([2, 1])

    with col_mapa:
        st.subheader("Mapa del área del proyecto")
        mapa_html = generar_mapa_html()
        st.components.v1.html(mapa_html, height=420, scrolling=False)

    with col_tabla:
        st.subheader("Zonas de peligro identificadas")
        st.markdown("<br>", unsafe_allow_html=True)
        for _, z in ZONAS.iterrows():
            badge_cls = "badge-muy-alto" if z["nivel"] == "MUY ALTO" else "badge-alto"
            st.markdown(f"""
            <div style='background:white;border-radius:8px;padding:12px 14px;
                        margin-bottom:10px;border-left:4px solid
                        {"#C0392B" if z["nivel"]=="MUY ALTO" else "#E67E22"};
                        box-shadow:0 1px 4px rgba(0,0,0,0.08);'>
                <b style='color:#1B3A5C;'>{z['zona']}</b>
                &nbsp;<span class='{badge_cls}'>{z['nivel']}</span><br>
                <span style='color:#64748B;font-size:0.82rem;'>
                    {z['tipo']} &nbsp;·&nbsp; {z['dist_km']} km del proyecto
                </span>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style='background:#FEF3C7;border-radius:8px;padding:12px;
                    border-left:4px solid #F18F01;margin-top:6px;'>
            <b style='color:#92400E;'>⚠ Recomendación</b><br>
            <span style='color:#78350F;font-size:0.83rem;'>
                Plan de contingencia y protocolos de evacuación
                deben incluirse en el expediente técnico.
            </span>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA 2 — ANÁLISIS CLIMÁTICO
# ─────────────────────────────────────────────────────────────────────────────
elif "Climático" in pagina:

    st.markdown("""
    <div class="header-box">
        <p class="header-title">Análisis Climático — Estación Otuzco (SENAMHI)</p>
        <p class="header-sub">Precipitación mensual histórica · Alertas por umbral crítico · Temporadas de riesgo</p>
    </div>
    """, unsafe_allow_html=True)

    # Gráfico de precipitación
    st.subheader("Precipitación mensual promedio (mm)")

    fig = go.Figure()

    fig.add_bar(
        x=PRECIP["mes"],
        y=PRECIP["pp_mm"],
        marker_color=PRECIP["color"],
        text=PRECIP["pp_mm"],
        textposition="outside",
        textfont=dict(size=11, color="#1E293B"),
        name="Precipitación",
        hovertemplate="<b>%{x}</b><br>Precipitación: %{y} mm<extra></extra>",
    )

    # Línea de umbral
    fig.add_hline(
        y=UMBRAL_CRITICO,
        line_dash="dash", line_color="#C0392B", line_width=2,
        annotation_text=f"  Umbral crítico: {UMBRAL_CRITICO} mm",
        annotation_position="top left",
        annotation_font_color="#C0392B",
    )

    fig.update_layout(
        height=360,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Calibri, Arial", color="#1E293B"),
        xaxis=dict(title="", gridcolor="#F1F5F9"),
        yaxis=dict(title="Precipitación (mm)", gridcolor="#F1F5F9"),
        margin=dict(l=40, r=20, t=20, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabla de meses con semáforo
    col_tabla, col_alerta = st.columns([2, 1])

    with col_tabla:
        st.subheader("Clasificación mensual por riesgo climático")
        for _, row in PRECIP.iterrows():
            if row["temporada"] == "crítica":
                bg, txt, badge = "#FEF2F2", "#7F1D1D", "🔴 CRÍTICO"
                recom = "Evitar vaciados y movimiento de tierras"
            elif row["temporada"] == "moderada":
                bg, txt, badge = "#FFFBEB", "#78350F", "🟡 MODERADO"
                recom = "Monitorear lluvia — posible suspensión"
            else:
                bg, txt, badge = "#F0FDF4", "#14532D", "🟢 SEGURO"
                recom = "Condiciones óptimas para trabajos en campo"

            st.markdown(f"""
            <div style='background:{bg};border-radius:8px;padding:10px 16px;
                        margin-bottom:6px;display:flex;align-items:center;gap:12px;'>
                <span style='font-weight:800;color:#1B3A5C;min-width:38px;'>{row['mes']}</span>
                <span style='color:{txt};min-width:100px;'>{badge}</span>
                <span style='color:#475569;font-size:0.82rem;'>{row['pp_mm']} mm &nbsp;·&nbsp; {recom}</span>
            </div>""", unsafe_allow_html=True)

    with col_alerta:
        st.subheader("Resumen de temporadas")
        meses_criticos  = PRECIP[PRECIP["temporada"] == "crítica"].shape[0]
        meses_moderados = PRECIP[PRECIP["temporada"] == "moderada"].shape[0]
        meses_secos     = PRECIP[PRECIP["temporada"] == "seca"].shape[0]
        pp_total = PRECIP["pp_mm"].sum()
        pp_critica = PRECIP[PRECIP["temporada"] == "crítica"]["pp_mm"].sum()

        st.markdown(f"""
        <div style='background:white;border-radius:10px;padding:20px;
                    box-shadow:0 1px 6px rgba(0,0,0,0.08);margin-top:8px;'>
            <div style='margin-bottom:12px;'>
                <div style='font-size:1.8rem;font-weight:800;color:#C0392B;'>{meses_criticos}</div>
                <div style='font-size:0.82rem;color:#64748B;'>meses críticos (Nov–Mar)</div>
            </div>
            <div style='margin-bottom:12px;'>
                <div style='font-size:1.8rem;font-weight:800;color:#E67E22;'>{meses_moderados}</div>
                <div style='font-size:0.82rem;color:#64748B;'>meses moderados</div>
            </div>
            <div style='margin-bottom:16px;'>
                <div style='font-size:1.8rem;font-weight:800;color:#27AE60;'>{meses_secos}</div>
                <div style='font-size:0.82rem;color:#64748B;'>meses seguros (Jun–Sep)</div>
            </div>
            <hr style='border-color:#E2E8F0;'>
            <div style='margin-top:12px;'>
                <span style='font-size:0.82rem;color:#64748B;'>Lluvia anual total</span><br>
                <b style='color:#1B3A5C;'>{pp_total} mm</b>
            </div>
            <div style='margin-top:8px;'>
                <span style='font-size:0.82rem;color:#64748B;'>Concentrada en temporada crítica</span><br>
                <b style='color:#C0392B;'>{round(pp_critica/pp_total*100)}% del total anual</b>
            </div>
        </div>
        <div style='background:#FEF3C7;border-radius:10px;padding:16px;
                    margin-top:12px;border-left:4px solid #F18F01;'>
            <b style='color:#92400E;font-size:0.85rem;'>Implicancia para diseño</b><br>
            <span style='color:#78350F;font-size:0.8rem;'>
                Sistema de drenaje debe soportar pico de <b>135mm/mes</b>.
                Diseñar cunetas, alcantarillas y canales con caudal
                correspondiente a temporada crítica.
            </span>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA 3 — CRONOGRAMA DE RIESGO
# ─────────────────────────────────────────────────────────────────────────────
elif "Cronograma" in pagina:

    st.markdown("""
    <div class="header-box">
        <p class="header-title">Cronograma de Riesgo — Proyecto Sauco</p>
        <p class="header-sub">
            Simulación con datos de ejemplo · 120 días · Inicio: Oct 2025
            &nbsp;|&nbsp; <i>Conectar con partes diarios reales para activar</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = generar_partes(inicio_str="2025-10-01", dias=120)

    # KPIs superiores
    dias_perdidos  = df[df["tipo_dia"] == "Perdido"].shape[0]
    dias_parciales = df[df["tipo_dia"] == "Parcial"].shape[0]
    dias_normales  = df[df["tipo_dia"] == "Normal"].shape[0]
    avance_final   = df["acum_real"].iloc[-1]
    retraso        = round(df["acum_plan"].iloc[-1] - avance_final, 1)
    horas_perdidas = round(df[df["tipo_dia"] == "Perdido"]["horas_plan"].sum(), 0)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Días perdidos por lluvia",  f"{dias_perdidos} días",
                  delta=f"-{round(dias_perdidos/120*100, 1)}% del total", delta_color="inverse")
    with col2:
        st.metric("Horas de trabajo perdidas", f"{int(horas_perdidas)} h",
                  delta="vs. plan de 960 h", delta_color="inverse")
    with col3:
        st.metric("Avance real acumulado",     f"{avance_final:.1f}%",
                  delta=f"-{retraso}% vs plan", delta_color="inverse")
    with col4:
        st.metric("Días en condiciones óptimas", f"{dias_normales} días",
                  delta=f"{round(dias_normales/120*100, 1)}% del proyecto")

    st.markdown("---")

    # Gráfico 1: Avance acumulado real vs planificado
    st.subheader("Avance acumulado: real vs. planificado")
    fig_avance = go.Figure()
    fig_avance.add_scatter(
        x=df["fecha"], y=df["acum_plan"],
        name="Plan", line=dict(color="#2E86AB", dash="dash", width=2),
        hovertemplate="%{x|%d %b}<br>Plan: %{y:.1f}%<extra></extra>",
    )
    fig_avance.add_scatter(
        x=df["fecha"], y=df["acum_real"],
        name="Real", line=dict(color="#C0392B", width=2.5),
        fill="tonexty", fillcolor="rgba(192,57,43,0.08)",
        hovertemplate="%{x|%d %b}<br>Real: %{y:.1f}%<extra></extra>",
    )
    # Sombrear temporada crítica (nov-mar)
    for anio in [2025, 2026]:
        fig_avance.add_vrect(
            x0=f"{anio}-11-01", x1=f"{anio}-04-01" if anio < 2026 else f"2026-04-01",
            fillcolor="#C0392B", opacity=0.06, layer="below", line_width=0,
            annotation_text="Temporada crítica" if anio == 2025 else "",
            annotation_position="top left",
            annotation_font_color="#C0392B",
            annotation_font_size=11,
        )

    fig_avance.update_layout(
        height=300,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Calibri, Arial"),
        xaxis=dict(title="", gridcolor="#F1F5F9"),
        yaxis=dict(title="Avance (%)", range=[0, 105], gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=20, t=20, b=20),
        hovermode="x unified",
    )
    st.plotly_chart(fig_avance, use_container_width=True)

    # Gráfico 2: Días perdidos por mes
    st.subheader("Días perdidos por lluvia — por mes")
    perdidos_mes = df[df["tipo_dia"] == "Perdido"].groupby("mes").size().reset_index(name="dias_perdidos")
    # Conservar orden cronológico
    orden_meses = df["mes"].unique().tolist()
    perdidos_mes["mes"] = pd.Categorical(perdidos_mes["mes"], categories=orden_meses, ordered=True)
    perdidos_mes = perdidos_mes.sort_values("mes")

    fig_barras = px.bar(
        perdidos_mes, x="mes", y="dias_perdidos",
        color="dias_perdidos",
        color_continuous_scale=["#2E86AB", "#E67E22", "#C0392B"],
        text="dias_perdidos",
        labels={"mes": "", "dias_perdidos": "Días perdidos"},
    )
    fig_barras.update_traces(textposition="outside", textfont_size=11)
    fig_barras.update_layout(
        height=260,
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False,
        margin=dict(l=40, r=20, t=10, b=20),
    )
    st.plotly_chart(fig_barras, use_container_width=True)

    # Tabla de partes diarios — últimos 20 días visibles
    st.subheader("Partes diarios (muestra)")
    color_tipo = {"Normal": "🟢", "Parcial": "🟡", "Perdido": "🔴"}
    df_show = df[["fecha","clima","tipo_dia","horas_real","acum_real"]].copy()
    df_show["fecha"]    = df_show["fecha"].dt.strftime("%d %b %Y")
    df_show["tipo_dia"] = df_show["tipo_dia"].map(lambda x: f"{color_tipo[x]} {x}")
    df_show.columns     = ["Fecha","Condición climática","Estado del día","Horas trabajadas","Avance acum. (%)"]

    n_filas = st.slider("Registros a mostrar", min_value=10, max_value=120, value=30, step=10)
    st.dataframe(
        df_show.tail(n_filas).sort_index(ascending=False),
        use_container_width=True, hide_index=True,
    )

    # Nota explicativa
    st.info(
        "📋  **Datos de ejemplo** — Esta simulación replica el comportamiento "
        "estadístico de la temporada lluviosa en Otuzco (SENAMHI). "
        "Para conectar partes diarios reales de PolarisX, reemplaza la función "
        "`generar_partes()` por la lectura de tu Excel o CSV."
    )
