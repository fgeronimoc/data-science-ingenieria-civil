# Estrategias para Aprender el Dominio de la Construcción

El mayor diferencial de un data scientist especializado en construcción no es conocer más algoritmos — es entender profundamente la industria a la que aplica esos algoritmos. Esta guía te ayuda a acelerar ese aprendizaje de forma sistemática.

---

## Principio fundamental

> No necesitas saber diseñar un puente. Necesitas entender qué decisiones toman los ingenieros que diseñan puentes, qué información necesitan para tomarlas mejor, y qué les cuesta equivocarse.

---

## Estrategia 1 — Aprende desde los documentos que ya existen en la empresa

Los proyectos de construcción generan documentación abundante. Esos documentos son tu primer aula.

**Qué solicitar y qué aprender de cada uno:**

| Documento | Qué aprender |
|-----------|--------------|
| Expediente técnico de una obra activa | Cómo se estructura un proyecto, qué partidas tiene, cómo se mide el avance |
| Cronograma de obra (Gantt en MS Project) | Cómo se planifica el tiempo, qué actividades son críticas, qué depende de qué |
| Partes diarios del último mes | Qué se registra día a día, qué variables existen, cómo se captura la información |
| Valorizaciones de los últimos 3 meses | Cómo se mide el avance real vs. planificado, qué genera retrasos |
| Informe de seguridad | Qué incidentes ocurren, cómo se clasifican, qué causas se identifican |

**Cómo pedirlos:** De manera informal, como parte de querer entender mejor el negocio. "¿Me puedes compartir un ejemplo de parte diario para entender qué datos se generan en obra?"

---

## Estrategia 2 — Entrevistas informales con el personal de campo

Los residentes de obra, jefes de campo y maestros de obras tienen conocimiento que no está en ningún libro. Son los expertos reales del dominio.

**Preguntas clave para hacer:**

- ¿Qué es lo que más retrasa una obra como esta?
- ¿En qué momento del proyecto es más difícil tomar decisiones?
- ¿Qué información querrías tener en tiempo real que ahora no tienes?
- ¿Cuándo llueve, qué actividades se paralizan exactamente y por cuánto tiempo?
- ¿Cuál fue el problema más costoso en la última obra que ejecutaron?
- ¿Qué datos registran actualmente que nunca nadie usa?

**Formato:** 20-30 minutos de conversación informal, sin grabadora. Toma notas después. El objetivo es entender los dolores reales, no recolectar datos.

---

## Estrategia 3 — Visitas a obra

No hay substituto para ver una obra en operación. Observa con ojos de data scientist:

- ¿Qué se mide y cómo se mide? (¿con cinta métrica, con nivel, a ojo?)
- ¿Qué se registra en papel que podría digitalizarse?
- ¿Qué decisiones toma el residente cada mañana? ¿Con qué información?
- ¿Qué cámaras existen? ¿Dónde están posicionadas? ¿Alguien las revisa?
- ¿Cómo se comunican el equipo en campo con la oficina?

---

## Estrategia 4 — Normativa como base de conocimiento

Leer normativa es árido pero te da el lenguaje técnico y los estándares que definen la industria. No hay que leerla de corrido — úsala como referencia.

**Orden sugerido:**
1. **G.050** (Seguridad durante la construcción) — 50 páginas. Define exactamente qué EPPs son obligatorios, en qué condiciones y cómo se fiscaliza. Directamente relevante para el proyecto de computer vision.
2. **E.050** (Suelos y cimentaciones) — Te explica qué es un estudio de suelos y por qué importa la geología de la zona.
3. **Reglamento Nacional de Edificaciones** — Marco general. Lee solo el índice y los capítulos relevantes a los proyectos de la empresa.

---

## Estrategia 5 — Comunidades y eventos del sector

**Online:**
- LinkedIn: seguir a profesionales de construcción en Perú, grupos de ingeniería civil peruana, BIM Forum Perú.
- YouTube: buscar "obra de puente Perú", "vaciado de concreto", "movimiento de tierras". Ver los videos con ojos de "¿qué datos genera este proceso?"

**Presencial:**
- Eventos del Colegio de Ingenieros del Perú (CIP)
- BIM Forum Perú (anual)
- PMI Capítulo Perú — eventos gratuitos
- Ferias de construcción: Excon (bienal, Lima)

---

## Estrategia 6 — Aprender el idioma financiero de la obra

Los que toman decisiones en una constructora piensan en dinero. Para comunicarte con gerencia necesitas saber cómo se mide el éxito financiero de un proyecto.

**Conceptos financieros clave:**
- **Utilidad bruta:** Diferencia entre el precio de contrato y el costo real de ejecución.
- **Adicionales de obra:** Trabajos no contemplados en el contrato original. Fuente de conflictos frecuente.
- **Penalidades:** Multas por retrasos en la entrega. Cuantificar días de retraso en dinero es el argumento más poderoso.
- **Gastos generales:** Costos fijos de la empresa (oficina, personal técnico, equipos) que no están en las partidas de obra.
- **Flujo de caja:** Cuándo entra el dinero (valorizaciones aprobadas) vs. cuándo sale (pago a proveedores y obreros).

---

## Plan de 90 días para dominar el dominio

| Período | Actividad |
|---------|-----------|
| Días 1-15 | Leer expediente técnico de una obra activa + entrevista con residente |
| Días 16-30 | Leer G.050 + visita a obra con checklist de observación |
| Días 31-45 | Digitalizar y analizar 3 meses de partes diarios de una obra |
| Días 46-60 | Entender el cronograma de MS Project de un proyecto activo |
| Días 61-75 | Leer 3 valorizaciones y trazar el avance real vs. planificado |
| Días 76-90 | Presentar un análisis preliminar al equipo técnico y recoger feedback |
