# Cómo Presentar Data Science a Gerencia de Construcción

La mejor solución técnica del mundo falla si no se comunica bien. Este documento te ayuda a traducir tu trabajo en lenguaje de negocio.

---

## Principio fundamental

> Gerencia no compra tecnología. Compra tiempo ahorrado, dinero no perdido y riesgos evitados. Habla siempre en esos términos.

---

## Los 3 argumentos que siempre funcionan

**1. Cuantificar el costo del problema actual**
Antes de proponer la solución, cuantifica el problema. "¿Cuántos días al año se pierden por lluvia en obra? Si son 20 días y la obra cuesta S/. 50,000 por día en gastos generales, eso son S/. 1,000,000 al año de costo por condiciones climáticas. Un sistema de pronóstico que reduzca eso en 30% ahorra S/. 300,000."

**2. Mostrar el resultado, no el método**
Muestra el mapa de riesgo, el dashboard, la alerta de lluvia. No expliques cómo funciona Prophet ni qué es un modelo de series de tiempo. "Este sistema te avisa con 5 días de anticipación si habrá lluvia crítica en la zona del proyecto y qué actividades deben reprogramarse."

**3. Empezar pequeño y escalar**
No proponer el sistema completo desde el inicio. "Empezamos con un piloto en la obra X durante 2 meses. Si reduce retrasos por clima en al menos 10%, expandimos a todas las obras."

---

## Estructura de una presentación a gerencia (10 minutos)

### Diapositiva 1 — El problema (2 minutos)
- Cuánto pierde la empresa por [clima / accidentes / retrasos]
- Evidencia concreta (días de obra perdidos, incidentes documentados)
- La pregunta: ¿y si pudiéramos anticiparlo?

### Diapositiva 2 — Lo que ya se hace en el mundo (2 minutos)
- 2-3 casos concretos (UK, Singapur, USA) en una oración cada uno
- Mostrar que esto no es experimental — ya funciona en la industria
- Énfasis: estas soluciones cuestan millones allá; nosotros lo hacemos con herramientas gratuitas

### Diapositiva 3 — Nuestra propuesta (3 minutos)
- El dashboard o resultado concreto (que puedan VER)
- Qué datos usa (datos que ya tenemos o son públicos y gratuitos)
- Costo de implementación (principalmente tiempo, no dinero)

### Diapositiva 4 — Piloto y siguientes pasos (2 minutos)
- Proyecto piloto específico, con obra y plazo concreto
- Métricas de éxito claras y medibles
- Qué necesitas de ellos (acceso a datos de obra, tiempo de personal)

### Cierre — Una sola pregunta
"¿Podemos empezar el piloto en la obra X el próximo mes?"

---

## Vocabulario que conecta con ingenieros civiles

| No digas | Di esto |
|----------|---------|
| Machine learning | Sistema que aprende de datos históricos |
| Modelo predictivo | Herramienta que anticipa problemas |
| Feature engineering | Preparación de la información |
| Dashboard interactivo | Panel de control en tiempo real |
| Series de tiempo | Registro histórico y proyección |
| Computer vision | Cámara inteligente que detecta riesgos |
| Data pipeline | Flujo automático de información |
| API | Conexión entre sistemas |

---

## Cómo manejar las objeciones más comunes

**"No tenemos datos"**
"Empezamos con los datos que sí existen: partes diarios, valorizaciones y datos públicos del SENAMHI y CENEPRED. En 2 semanas tenemos un primer análisis."

**"Es muy caro"**
"Las herramientas son gratuitas (Python, Google Earth Engine). El costo es mi tiempo. El piloto no requiere inversión en software."

**"No es nuestro negocio"**
"Las constructoras que ya hacen esto en UK y Singapur tienen ventaja competitiva en licitaciones porque pueden demostrar menor riesgo de retraso. En Perú, nadie lo está haciendo todavía."

**"¿Y si no funciona?"**
"Por eso propongo un piloto de 2 meses con métricas claras. Si no hay mejora medible, paramos. El costo del experimento es mínimo."

---

## Métricas de éxito para el piloto (ejemplos)

| Métrica | Línea base | Meta del piloto |
|---------|-----------|-----------------|
| Días de obra perdidos por lluvia | X días/mes (histórico) | Reducir 20% |
| Tiempo de respuesta ante lluvia imprevista | 0 (reacción) | 3-5 días de anticipación |
| Incidentes de EPP sin cumplir | Y por semana | Reducir 30% |
| Tiempo de generación de informe de avance | Manual, 4 horas | Automático, 15 minutos |
