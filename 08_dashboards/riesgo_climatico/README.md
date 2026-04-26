# Dashboard — Monitor de Riesgo Climático

Dashboard Streamlit interactivo para análisis de riesgo en proyectos de infraestructura civil.
Accesible desde navegador y celular. Costo en software: **S/. 0**.

---

## Secciones

| Sección | Contenido |
|---------|-----------|
| 🏠 Resumen del Proyecto | KPIs de riesgo + mapa interactivo con zonas de peligro |
| 🌧 Análisis Climático | Precipitación mensual histórica, umbral crítico y semáforo por mes |
| 📅 Cronograma de Riesgo | Partes diarios simulados, avance real vs. planificado, días perdidos por lluvia |

---

## Cómo ejecutar

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Lanzar el dashboard
streamlit run app.py
```

El navegador se abre automáticamente en `http://localhost:8501`

---

## Conectar datos reales

En la sección **Cronograma de Riesgo**, la función `generar_partes()` genera datos sintéticos.
Para conectar partes diarios reales de PolarisX:

```python
# Reemplazar generar_partes() por:
df = pd.read_excel("ruta/a/partes_diarios_sauco.xlsx")
# Asegurarse de que tenga columnas: fecha, clima, horas_real, etc.
```

---

## Fuentes de datos

| Dato | Fuente |
|------|--------|
| Precipitación histórica | SENAMHI — Estación Otuzco |
| Zonas de peligro | CENEPRED — SIGRID |
| Zonificación sísmica | NTE E.030 — MVCS |
| Cartografía | Esri, OpenTopoMap |

---

*Dashboard desarrollado por Fernando Geronimo Ccoillor — Abril 2026*
