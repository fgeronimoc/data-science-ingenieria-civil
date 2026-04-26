# Data Science en Construcción — Casos por País

Lo que en Perú todavía no existe como área formal, en otros países ya lleva años operando. Este documento mapea los casos más relevantes y extrae lo que es replicable aquí.

---

## Reino Unido 🇬🇧

### Mandato BIM y digitalización forzada
En 2016 el gobierno británico exigió BIM Level 2 en todos los proyectos públicos. Esto no fue solo un cambio tecnológico — fue una política que obligó a toda la industria a generar datos estructurados. El resultado: un ecosistema de startups de construcción digital que no existía antes.

### nPlan
**Qué hace:** Usa machine learning sobre millones de cronogramas de proyectos históricos para predecir la probabilidad de retraso en cada actividad de un proyecto nuevo. Los modelos aprenden de patrones que ningún planificador humano puede ver manualmente.
**Resultado reportado:** Reducción de hasta 30% en desviaciones de cronograma en proyectos piloto.
**Replicable en Perú:** Sí, con datos del OSCE (contratos de obras públicas, ampliaciones de plazo, penalidades). El dataset existe — nadie lo ha analizado sistemáticamente.

### Construction Innovation Hub
Centro financiado por el gobierno con universidades y empresas privadas. Desarrolla herramientas digitales para constructoras medianas y pequeñas. Su enfoque en empresas sin grandes presupuestos de I+D es especialmente relevante para el contexto peruano.

---

## Estados Unidos 🇺🇸

### Smartvid.io (adquirida por Procore)
**Qué hace:** Computer vision para análisis automático de fotos y videos de obra. Detecta EPPs, condiciones inseguras, y genera reportes de seguridad automáticamente.
**Replicable en Perú:** Exactamente esto es lo que el proyecto de seguridad con YOLO busca construir, a escala local y con costo mínimo.

### Buildots
**Qué hace:** Cámaras 360° montadas en cascos de supervisores capturan imágenes de toda la obra. El sistema compara automáticamente el avance real con el modelo BIM y genera reportes de desvíos.
**Replicable en Perú:** Parcialmente. Sin BIM, se puede implementar una versión simplificada comparando fotos geolocalizadas con el cronograma planificado.

### Kiewit y Turner Construction
Las constructoras más grandes de EE.UU. tienen equipos internos de data science que analizan datos de productividad, seguridad y costos. Sus modelos internos no son públicos pero sus casos de estudio sí.

### Autodesk Construction Cloud
Plataforma integrada que centraliza todos los datos de un proyecto (documentos, RFIs, cronograma, seguridad). Genera analytics automáticamente. Muchas constructoras peruanas grandes ya la usan — pero sin aprovechar su capa de datos.

---

## Japón 🇯🇵

### Komatsu Smart Construction
**Qué hace:** Integra drones para topografía, maquinaria autónoma y una plataforma de gestión de datos para movimiento de tierras. El sistema calcula automáticamente el volumen movido y optimiza la ruta de los equipos.
**Replicable en Perú:** Los drones y fotogrametría sí. OpenDroneMap (gratuito) permite generar modelos 3D de terreno comparables a soluciones comerciales costosas.

### Obayashi Corporation
Una de las mayores constructoras japonesas. Ha implementado robots para colocación de acero, sistemas de IA para control de calidad de concreto y análisis de datos de productividad en tiempo real.

---

## Singapur 🇸🇬

### Building and Construction Authority (BCA) — Smart Construction
El gobierno de Singapur tiene una agenda nacional de digitalización de la construcción con tres pilares: prefabricación (reducir trabajo in situ), integración digital (BIM + datos) y mano de obra calificada en tecnología.

**Por qué es relevante para Perú:** Singapur tiene un contexto de recursos limitados y necesidad de eficiencia — similar a muchos proyectos peruanos de infraestructura. Sus soluciones tienden a ser pragmáticas y de bajo costo relativo.

### Drones en fiscalización
La autoridad de construcción usa drones regularmente para fiscalizar el avance de obras públicas y detectar incumplimientos sin necesidad de visitas físicas frecuentes. Directamente aplicable a obras en zonas remotas del Perú.

---

## Australia 🇦🇺

### CSIRO y análisis de datos en construcción
El organismo de investigación científica australiano tiene proyectos activos de ML aplicados a predicción de costos en infraestructura y análisis de fallos en activos de construcción.

### Laing O'Rourke
Constructora que ha apostado fuertemente por la prefabricación digital y el análisis de datos de productividad. Su modelo de "digital engineering" busca integrar datos de diseño, fabricación y construcción en un flujo continuo.

---

## Países Bajos 🇳🇱

### Gestión de agua e infraestructura
Dado su contexto geográfico (país bajo el nivel del mar), los Países Bajos tienen las capacidades geoespaciales más avanzadas del mundo para gestión de riesgos hídricos. Sus modelos de inundación y sistemas de alerta temprana son referencia global.

**Replicable en Perú:** Los datos existen (SENAMHI, IGN, ANA). Las técnicas son las mismas: modelado hidrológico + análisis geoespacial + alertas automatizadas. Perú tiene cuencas con alta actividad de huaicos y crecidas que justifican exactamente este tipo de sistema.

---

## Colombia y Chile 🇨🇴🇨🇱

### Avance en América Latina
Chile tiene la adopción de BIM más madura de la región, con mandato gubernamental desde 2020. Colombia ha desarrollado plataformas de datos para infraestructura vial (INVIAS).

**Por qué importa para Perú:** Estas experiencias muestran que el contexto latinoamericano es viable. Los retos de datos escasos, informalidad y resistencia al cambio existen allá también, y hay soluciones desarrolladas para ese contexto que son directamente adaptables.
