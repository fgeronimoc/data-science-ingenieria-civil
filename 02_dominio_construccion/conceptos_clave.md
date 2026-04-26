# Conceptos Clave de la Industria de la Construcción

Para aplicar data science en construcción hay que hablar el mismo idioma que los ingenieros. Este documento es tu diccionario de la industria.

---

## 1. Estructura de un proyecto de construcción

### Fases principales
1. **Estudios y diseño:** Topografía, estudios de suelos, hidrología, diseño estructural, expediente técnico.
2. **Licitación y contratación:** En obras públicas, proceso regulado por OSCE. En privadas, negociación directa.
3. **Ejecución:** La obra propiamente dicha. Donde se genera la mayor parte de los datos relevantes.
4. **Supervisión:** Control de calidad, avance y seguridad. Generalmente un tercero independiente.
5. **Liquidación:** Cierre técnico y financiero del proyecto.

### Actores clave
- **Propietario / Entidad:** Quien financia y requiere la obra (gobierno, empresa privada).
- **Contratista / Ejecutora:** Empresa que construye. Aquí es donde estás.
- **Supervisor / Inspector:** Controla que se ejecute según el expediente.
- **Proyectista:** Quien diseñó la obra. Puede ser la misma empresa o un tercero.
- **Subcontratistas:** Empresas especializadas (acero, concreto, instalaciones).

---

## 2. Documentos fundamentales

### Expediente Técnico
El documento madre de cualquier obra. Contiene: memoria descriptiva, especificaciones técnicas, planos, metrados, presupuesto y cronograma. Comprender el expediente es comprender el proyecto.

### Metrado
Cuantificación de cada partida de trabajo. Por ejemplo: cuántos m³ de concreto, cuántos kg de acero, cuántos m² de encofrado. Es la base del presupuesto y del análisis de rendimientos.

### Valorización
Informe mensual (o quincenal) que cuantifica el avance de obra ejecutado para efectos de pago. Cruzar valorizaciones con el cronograma es una fuente de datos inmediata para análisis.

### Parte Diario de Obra
Registro diario de: personal en campo, maquinaria operativa, actividades ejecutadas, condiciones climáticas, incidencias. Es el dataset más valioso y más desaprovechado de la industria.

### Cuaderno de Obra
Documento oficial y legal donde se registran las comunicaciones entre el residente, supervisor y entidad. Todo hecho relevante debe asentarse aquí.

---

## 3. KPIs de una obra de construcción

| KPI | Definición | Cómo se calcula | Relevancia para DS |
|-----|------------|-----------------|-------------------|
| Avance físico (%) | Porcentaje de obra ejecutada | Metrado ejecutado / Metrado total | Serie de tiempo del avance |
| Índice de Rendimiento de Cronograma (SPI) | Eficiencia vs. cronograma | Valor Ganado / Valor Planificado | Detectar retrasos anticipadamente |
| Índice de Rendimiento de Costos (CPI) | Eficiencia vs. presupuesto | Valor Ganado / Costo Real | Predicción de sobrecostos |
| Tasa de Frecuencia de Accidentes (TFA) | Accidentes por horas trabajadas | (N° accidentes × 1,000,000) / HH | Objetivo de seguridad |
| Productividad de cuadrilla | Rendimiento por obrero | Metrado ejecutado / (N° obreros × días) | Optimización de recursos |
| HH (Horas-Hombre) | Unidad de trabajo | N° trabajadores × horas | Planificación de personal |

---

## 4. Tipos de obra relevantes para este proyecto

### Carreteras y vías
- **Movimiento de tierras:** Corte, relleno, eliminación de material. Variable crítica: tipo de suelo y condición hídrica.
- **Pavimentación:** Base, sub-base, carpeta asfáltica o concreto. Variable crítica: temperatura ambiente y lluvia.
- **Obras de arte:** Alcantarillas, muros de contención, cunetas. Variable crítica: hidrología de la zona.

### Puentes
- **Subestructura:** Estribos, pilares, cimentaciones. Variable crítica: nivel freático y tipo de suelo.
- **Superestructura:** Vigas, tablero, barandas. Variable crítica: temperatura para control de concreto.
- **Trabajos especiales:** Encofrado deslizante, concreto de alta resistencia, tensado de cables. Alta sensibilidad a condiciones climáticas.

---

## 5. Normativa esencial en Perú

| Norma | Contenido | Por qué importa |
|-------|-----------|----------------|
| Reglamento Nacional de Edificaciones (RNE) | Marco técnico general de construcción | Base de cualquier diseño o análisis técnico |
| Norma G.050 | Seguridad durante la construcción | Define EPPs obligatorios y protocolos de seguridad |
| Norma E.030 | Diseño sismorresistente | Clave para obras en zonas sísmicas de Perú |
| Norma E.050 | Suelos y cimentaciones | Fundamental para análisis geotécnico |
| Ley 29783 | Ley de Seguridad y Salud en el Trabajo | Marco legal de seguridad laboral |
| LEY 30225 | Ley de Contrataciones del Estado | Regula obras públicas — fuente de datos OSCE |

---

## 6. Software que usa la industria

| Software | Uso | Datos exportables |
|----------|-----|-------------------|
| MS Project | Cronogramas (Gantt) | .mpp → CSV/Excel |
| Primavera P6 | Cronogramas complejos | XML, Excel |
| S10 Costos | Presupuestos y metrados | Excel |
| AutoCAD | Diseño 2D | DXF (convertible a geo) |
| Civil 3D | Diseño vial y topografía | DXF, LandXML |
| Revit | BIM (modelado 3D) | IFC |
| QGIS | SIG de escritorio | Múltiples formatos geo |

Conocer qué datos generan estos softwares es el primer paso para saber qué puedes analizar.
