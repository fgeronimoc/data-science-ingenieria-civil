# Análisis de Riesgo Geoespacial

Herramienta de análisis de riesgo para proyectos de infraestructura civil (puentes, carreteras) en zonas con peligro de huaicos, deslizamientos e inundaciones.

---

## ¿Qué hace?

Genera un mapa interactivo HTML que integra:

- Zonas de peligro por movimientos en masa e inundaciones (fuente: CENEPRED)
- Red hídrica de la zona del proyecto (ríos y quebradas)
- Datos de precipitación histórica mensual (fuente: SENAMHI)
- Perfil de elevación aproximado del área
- Zonificación sísmica según NTE E.030
- Panel de resumen estadístico del riesgo
- Tres vistas intercambiables: mapa base, satelital y topográfico

El resultado es un archivo `.html` que se abre en cualquier navegador, incluyendo desde celular.

---

## Caso de aplicación

**Proyecto:** Centro Poblado Sauco  
**Ubicación:** Distrito de Salpo, Provincia de Otuzco, La Libertad  
**Coordenadas:** -8.018, -78.568  
**Riesgo general:** MUY ALTO  
**Zona sísmica:** 3 (Z = 0.35)  
**Elevación aproximada:** 3,180 m.s.n.m.  
**Temporada crítica:** Noviembre – Abril | Pico: Marzo (135mm)

---

## Archivos

```
riesgo_geoespacial/
├── notebooks/
│   ├── 01_exploracion_riesgo.ipynb          ← Notebook principal con todo el código
│   └── mapa_analisis_proyecto_sauco.html    ← Mapa interactivo generado
└── README.md                                ← Este archivo
```

---

## Cómo reproducir el análisis

**1. Activar el entorno:**
```bash
conda activate data-civil
```

**2. Abrir el notebook:**
```bash
jupyter notebook notebooks/01_exploracion_riesgo.ipynb
```

**3. Ejecutar todas las celdas** en orden de arriba hacia abajo.

**4. Abrir el mapa** generado en `notebooks/mapa_analisis_proyecto_sauco.html`

---

## Cómo usar la herramienta para otro proyecto

Al final del notebook hay una función reutilizable. Solo cambia los parámetros:

```python
generar_analisis_riesgo(
    nombre    = "Nombre del nuevo proyecto",
    lat       = -8.500,   # latitud del proyecto
    lon       = -78.200,  # longitud del proyecto
    region    = "La Libertad",
    provincia = "Otuzco",
    distrito  = "Salpo",
    radio_km  = 2         # radio de análisis en km
)
```

Esto genera automáticamente el mapa completo con todos los análisis.

---

## Librerías requeridas

```
folium==0.20.0
geopandas==1.1.3
pandas==3.0.2
numpy
matplotlib
```

Instalar con:
```bash
pip install folium geopandas pandas numpy matplotlib
```

---

## Fuentes de datos

| Dato | Fuente | Acceso |
|------|--------|--------|
| Zonas de peligro | CENEPRED — SIGRID | sigrid.cenepred.gob.pe |
| Precipitación histórica | SENAMHI — Estación Otuzco | senamhi.gob.pe |
| Cartografía base | IGN | geoportal.igm.gob.pe |
| Imágenes satelitales | Esri World Imagery | Integrado en Folium |
| Zonificación sísmica | NTE E.030 — MVCS | Norma técnica peruana |

---

## Próximas mejoras

- [ ] Integrar shapefile oficial de CENEPRED para La Libertad
- [ ] Conectar API SENAMHI para datos en tiempo real
- [ ] Agregar análisis de pendiente desde DEM (modelo digital de elevación)
- [ ] Exportar reporte en PDF automáticamente

---

*Proyecto desarrollado como parte del repositorio de Data Science aplicado a Ingeniería Civil*  
*Autor: Fernando Geronimo Ccoillor Soto — Abril 2026*
