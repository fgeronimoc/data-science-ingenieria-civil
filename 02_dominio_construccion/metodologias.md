# Metodologías de Gestión en Construcción

Entender cómo se planifica y controla una obra te permite identificar dónde los datos pueden mejorar el proceso.

---

## 1. Gestión de Proyectos Tradicional (CPM)

El método más usado en Perú. Se basa en el cronograma de Gantt y la ruta crítica.

### Ruta Crítica (CPM — Critical Path Method)
Identifica la secuencia de actividades que determina la duración mínima del proyecto. Cualquier retraso en la ruta crítica retrasa toda la obra.

**Relevancia para DS:** Cruzar el pronóstico climático con las actividades en la ruta crítica permite priorizar cuáles son las que realmente no pueden interrumpirse.

### Valor Ganado (EVM — Earned Value Management)
Sistema de control que integra alcance, tiempo y costo en una sola métrica.

| Indicador | Fórmula | Interpretación |
|-----------|---------|----------------|
| SPI (Schedule Performance Index) | EV / PV | >1: adelantado, <1: retrasado |
| CPI (Cost Performance Index) | EV / AC | >1: bajo presupuesto, <1: sobrecosto |
| EAC (Estimate at Completion) | BAC / CPI | Costo estimado final del proyecto |

**Relevancia para DS:** Los índices de valor ganado son series de tiempo naturales — perfectos para modelos predictivos de sobrecosto o retraso.

---

## 2. Last Planner System (LPS)

Metodología desarrollada por el Lean Construction Institute. Muy difundida en proyectos complejos y en crecimiento en Perú.

### Principios
- Planificación colaborativa con los ejecutores directos (el "último planificador" es el capataz o jefe de cuadrilla)
- Compromisos semanales verificables
- Análisis de causas de incumplimiento

### PPC (Porcentaje de Plan Completado)
Métrica central del LPS: qué porcentaje de las actividades comprometidas para la semana se completaron efectivamente.

**Relevancia para DS:** El registro semanal de PPC y sus causas de incumplimiento es un dataset perfecto para análisis de patrones. Si el 40% de los incumplimientos se deben a lluvia, eso justifica un sistema de pronóstico climático integrado al LPS.

---

## 3. Lean Construction

Filosofía que busca eliminar desperdicios en el proceso constructivo, tomada del Lean Manufacturing de Toyota.

### Los 7 desperdicios aplicados a construcción

1. **Sobreproducción:** Fabricar más concreto del necesario (se fragua y se pierde)
2. **Espera:** Cuadrilla parada esperando materiales o maquinaria
3. **Transporte innecesario:** Movimientos innecesarios de materiales en obra
4. **Sobreprocesamiento:** Hacer más trabajo del que especifica el plano
5. **Inventario excesivo:** Acumular materiales que se dañan o roban
6. **Movimiento innecesario:** Trabajadores buscando herramientas o materiales
7. **Defectos:** Trabajos que hay que rehacer por mala calidad

**Relevancia para DS:** Cada uno de estos desperdicios es cuantificable con datos. Un sistema que registra tiempos de espera por cuadrilla y los categoriza puede identificar automáticamente qué tipo de desperdicio domina en una obra.

---

## 4. BIM (Building Information Modeling)

No es solo un software de diseño 3D — es una metodología de trabajo colaborativo basada en un modelo digital que contiene toda la información del proyecto.

### Dimensiones del BIM
- **3D:** Modelo geométrico del proyecto
- **4D:** 3D + tiempo (cronograma vinculado al modelo)
- **5D:** 4D + costos (presupuesto vinculado)
- **6D:** 5D + sostenibilidad
- **7D:** 6D + mantenimiento (facility management)

### Plan BIM Perú
El Ministerio de Vivienda (MVCS) tiene una hoja de ruta para implementar BIM en obras públicas peruanas. Desde 2023 es obligatorio en proyectos sobre cierto monto. Esto significa que en los próximos años, los proyectos públicos generarán datos estructurados en formato IFC.

**Relevancia para DS:** El modelo BIM contiene datos geométricos, de materiales, de costos y de cronograma en un solo archivo. Extraer esos datos para análisis de rendimiento o predicción de costos es una de las fronteras más interesantes del campo.

---

## 5. Gestión de Riesgos en Proyectos

Todo proyecto tiene riesgos. La gestión formal de riesgos los identifica, cuantifica y planifica respuestas.

### Matriz de riesgo
Herramienta básica: probabilidad de ocurrencia × impacto = nivel de riesgo.

| Riesgo | Probabilidad | Impacto | Nivel | Respuesta |
|--------|-------------|---------|-------|-----------|
| Lluvias intensas en vaciado | Alta | Alto | Crítico | Pronóstico climático + plan de contingencia |
| Deslizamiento en talud | Media | Alto | Alto | Análisis geoespacial de estabilidad |
| Accidente con maquinaria | Baja | Muy alto | Alto | Sistema de detección con CV |

**Relevancia para DS:** La cuantificación del riesgo es exactamente el tipo de problema que data science resuelve mejor. Pasar de una matriz cualitativa ("probabilidad alta") a una predicción cuantitativa ("72% de probabilidad de lluvia crítica en los próximos 3 días") es el salto de valor que aporta este proyecto.
