# Machine Learning aplicado a la Construcción

Machine Learning es enseñarle a una computadora a encontrar patrones en datos para hacer predicciones. No reemplaza al ingeniero — le da al ingeniero información que antes era imposible de calcular manualmente.

---

## 1. ¿Qué es Machine Learning?

Un modelo de ML aprende de ejemplos históricos para predecir o clasificar casos nuevos. En vez de programar reglas manualmente ("si llueve más de 20mm, detener obra"), el modelo aprende esas reglas solo desde los datos.

**Analogía en construcción:** Un maestro de obra experimentado sabe, con solo ver el cielo y sentir el aire, si va a llover esa tarde. Aprendió eso de miles de días en campo. Un modelo de ML hace lo mismo, pero con datos numéricos de presión atmosférica, humedad y temperatura.

---

## 2. Tipos de aprendizaje

### Supervisado
El modelo aprende de ejemplos etiquetados: datos de entrada + respuesta correcta conocida.

**Tipos:**
- **Regresión:** Predice un número continuo.
  - Ejemplo: predecir el costo final de una obra dado su presupuesto inicial, tipo de terreno y ubicación.
- **Clasificación:** Predice una categoría.
  - Ejemplo: ¿Este tramo de carretera tiene riesgo ALTO, MEDIO o BAJO de deslizamiento?

### No supervisado
El modelo encuentra estructura en datos sin etiquetas. Agrupa, comprime o descubre patrones ocultos.
- **Clustering:** Agrupar proyectos similares por tipo de retraso sin saber de antemano cuántos grupos hay.

### Aprendizaje por refuerzo
El modelo aprende por prueba y error con recompensas. Menos común en construcción por ahora, pero relevante para optimización de rutas de maquinaria.

---

## 3. El flujo estándar de un proyecto de ML

```
Definir el problema
       ↓
Recolectar y limpiar datos
       ↓
Análisis exploratorio (EDA)
       ↓
Ingeniería de features (variables)
       ↓
Seleccionar y entrenar modelo
       ↓
Evaluar y validar
       ↓
Desplegar y monitorear
```

Cada etapa en construcción tiene su particularidad. La más difícil suele ser la recolección y limpieza — los datos de obra son escasos, inconsistentes y a veces en papel.

---

## 4. Conceptos críticos que todo profesional debe dominar

### Train/Test Split
Los datos se dividen en dos grupos: uno para entrenar el modelo y otro para evaluar si realmente aprendió o solo memorizó.
- Típico: 80% entrenamiento, 20% prueba.

### Overfitting (sobreajuste)
El modelo memoriza los datos de entrenamiento pero falla con datos nuevos. Como un estudiante que memoriza los ejercicios del libro pero no puede resolver uno diferente en el examen.

**Cómo detectarlo:** Alta precisión en entrenamiento, baja precisión en prueba.
**Cómo corregirlo:** Más datos, regularización, modelos más simples.

### Validación cruzada (Cross-validation)
Técnica para evaluar el modelo de forma más robusta. En vez de un solo split train/test, se hacen múltiples particiones y se promedia el resultado. Especialmente útil cuando los datos son escasos (situación común en construcción).

### Métricas de evaluación

**Para regresión:**
- MAE (Error Absoluto Medio): cuánto se equivoca el modelo en promedio, en las mismas unidades del problema.
- RMSE: similar al MAE pero penaliza más los errores grandes.
- R²: qué porcentaje de la variabilidad explica el modelo (1 = perfecto, 0 = no sirve).

**Para clasificación:**
- Precisión: de todos los que predijo como "riesgo alto", ¿cuántos realmente lo eran?
- Recall: de todos los casos realmente de "riesgo alto", ¿cuántos detectó el modelo?
- F1-Score: balance entre precisión y recall.
- Matriz de confusión: tabla que muestra aciertos y errores por categoría.

---

## 5. Algoritmos más usados en construcción

| Algoritmo | Tipo | Aplicación en construcción |
|-----------|------|---------------------------|
| Regresión lineal | Regresión | Predicción de costos y plazos |
| Árbol de decisión | Regresión / Clasificación | Clasificación de riesgo de zona |
| Random Forest | Regresión / Clasificación | Predicción de retrasos, robusto con pocos datos |
| XGBoost | Regresión / Clasificación | El más usado en competencias, muy preciso |
| K-Means | Clustering | Agrupar zonas de obra por características similares |
| YOLO | Computer Vision | Detección de EPPs y objetos en obra |
| Prophet | Series de tiempo | Pronóstico de avance de obra y variables climáticas |

---

## 6. Ingeniería de features (variables)

El arte de transformar datos crudos en variables útiles para el modelo. En construcción es especialmente importante porque los datos raramente vienen listos.

**Ejemplos:**
- De una fecha de inicio y fin de actividad → calcular duración y si hubo retraso (sí/no)
- De coordenadas geográficas → extraer altitud, distancia a río, pendiente del terreno
- De registros de lluvia diaria → crear "lluvia acumulada últimos 7 días" como variable predictora

---

## Conexión con proyectos de este repositorio

- `07_proyectos/clima_obra/` — Random Forest y regresión para predecir impacto de lluvia en cronograma
- `07_proyectos/seguridad_vision/` — YOLO (deep learning) para clasificación visual de EPPs
- `07_proyectos/riesgo_geoespacial/` — Clasificación de riesgo por zona con árbol de decisión
