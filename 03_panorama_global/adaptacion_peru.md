# Adaptación al Contexto Peruano

Cada caso global tiene una versión peruana posible. Este documento mapea directamente qué se puede replicar, con qué datos disponibles y qué nivel de complejidad técnica requiere.

---

## Tabla de adaptación

| Caso global | País | Lo que hace | Versión peruana posible | Datos disponibles | Complejidad |
|-------------|------|-------------|------------------------|-------------------|-------------|
| nPlan | UK/USA | ML para predecir retrasos en cronogramas | Análisis de ampliaciones de plazo y penalidades en obras públicas peruanas | OSCE (público y gratuito) | Media |
| Smartvid.io | USA | Computer vision para seguridad en obra | Detección de EPPs con YOLOv8 en cámara de bajo costo | Imágenes propias de obra | Media (ya hay base) |
| Buildots | USA | Monitoreo de avance vs. BIM con fotos 360° | Comparación de fotos geolocalizadas vs. cronograma planificado | Fotos de obra + cronograma | Media |
| Komatsu Smart Construction | Japón | Drones + fotogrametría para movimiento de tierras | OpenDroneMap para generar modelos 3D de volumen excavado | Drones DJI accesibles | Media-Alta |
| BCA Singapur — drones en fiscalización | Singapur | Fiscalización remota de avance con drones | Monitoreo de avance en obras remotas (sierra, selva) | Drones + GPS | Media |
| Países Bajos — gestión hídrica | NL | Modelos de inundación y alerta temprana | Mapa de riesgo de huaicos e inundaciones para zonas de proyecto | SENAMHI + CENEPRED + IGN | Media |
| Prophet para pronóstico climático | USA (Meta) | Pronóstico de series de tiempo | Pronóstico de lluvia en Lima con datos SENAMHI | SENAMHI (público) | Baja-Media |
| Valor Ganado automatizado | Global | Control de SPI/CPI automático | Dashboard de valor ganado conectado a valorizaciones | Datos internos de obra | Media |

---

## Proyectos prioritarios para Perú (orden de impacto vs. esfuerzo)

### 1. Análisis de riesgo geoespacial para zonas de proyecto
**Impacto:** Alto — directamente útil para expedientes técnicos y decisiones de diseño.
**Esfuerzo:** Medio — datos públicos disponibles, herramientas gratuitas.
**Descripción:** Mapa interactivo que cruza la ubicación de proyectos activos con zonas de riesgo del CENEPRED, datos de lluvia del SENAMHI y modelos de elevación del IGN. Exportable a HTML para compartir sin necesidad de software SIG.
**Ver:** `07_proyectos/riesgo_geoespacial/`

### 2. Monitor de seguridad con Computer Vision
**Impacto:** Alto — visible, comprensible para gerencia, cumple normativa G.050.
**Esfuerzo:** Medio — Fernando ya tiene base en YOLO.
**Descripción:** Sistema que procesa video de cámaras de obra y detecta en tiempo real incumplimientos de EPP. Genera reporte diario automático de infracciones por zona y hora.
**Ver:** `07_proyectos/seguridad_vision/`

### 3. Pronóstico climático integrado a cronograma
**Impacto:** Alto — traduce lluvia directamente en días de retraso y dinero.
**Esfuerzo:** Medio — datos SENAMHI + Prophet.
**Descripción:** Modelo que descarga automáticamente el pronóstico del SENAMHI, identifica días con probabilidad de lluvia crítica (>15mm) y los cruza con las actividades del cronograma para alertar al residente de obra con 3-5 días de anticipación.
**Ver:** `07_proyectos/clima_obra/`

### 4. Análisis de datos OSCE para predicción de retrasos
**Impacto:** Medio-Alto — aplicable a licitaciones y planificación de nuevos proyectos.
**Esfuerzo:** Medio — requiere web scraping o descarga masiva del portal OSCE.
**Descripción:** Modelo entrenado con datos históricos de obras públicas peruanas (tipo de obra, zona geográfica, monto, plazo contractual) que predice la probabilidad de ampliación de plazo o penalidad.

### 5. Dashboard de productividad de cuadrilla
**Impacto:** Medio — optimización operativa, requiere datos internos.
**Esfuerzo:** Bajo-Medio — depende de la disponibilidad de datos de partes diarios.
**Descripción:** Visualización del rendimiento de cuadrillas por actividad, comparando rendimientos reales vs. rendimientos de análisis de precios unitarios (APU). Identifica automáticamente actividades con rendimiento por debajo del 80%.

---

## Ventajas competitivas del contexto peruano

**El dato público existe pero nadie lo usa:** El OSCE tiene décadas de datos de obras públicas. El SENAMHI tiene series climáticas largas. El IGN tiene cartografía detallada. Ninguna constructora peruana ha construido un sistema que integre todo esto.

**El costo de entrada es bajo:** Las herramientas son gratuitas (Python, QGIS, Google Earth Engine con cuenta académica). Los datos son públicos. La inversión es tiempo y conocimiento — exactamente lo que este repositorio está construyendo.

**La competencia es casi nula:** En UK o USA ya hay docenas de startups haciendo esto. En Perú el campo está prácticamente vacío. El costo de diferenciación es mucho menor.

**El sector es enorme:** La inversión en infraestructura pública en Perú supera los S/. 30,000 millones anuales. Incluso mejorar la eficiencia en un 1% representa cientos de millones de soles.

---

## Lo que Perú tiene que no tienen otros países

La **data de desastres naturales** es única. Perú concentra tres zonas de riesgo distintas (costa desértica, sierra andina, selva amazónica) con dinámicas completamente diferentes. Los modelos de riesgo climático y geológico entrenados con datos peruanos tienen aplicación directa en proyectos de infraestructura que ningún modelo global puede replicar con la misma precisión.
