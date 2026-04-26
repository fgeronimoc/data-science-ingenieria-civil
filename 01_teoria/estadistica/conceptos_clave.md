# Estadística Aplicada a la Construcción

La estadística es el lenguaje con el que describes la realidad de una obra antes de modelarla. Sin estadística sólida, los modelos de ML son cajas negras que no puedes defender ante un ingeniero.

---

## 1. Probabilidad y distribuciones

**¿Qué es?** La probabilidad cuantifica la incertidumbre. Una distribución describe cómo se comportan los datos — dónde se concentran, qué tan dispersos están, qué valores son raros.

**Distribuciones más comunes en construcción:**

- **Normal (Gaussiana):** Errores de medición en topografía, variabilidad en resistencia de materiales. Si mides la resistencia a la compresión de 100 probetas de concreto f'c=210, los valores se distribuirán aproximadamente de forma normal alrededor de 210 kg/cm².
- **Poisson:** Frecuencia de accidentes en obra por mes. ¿Cuántos incidentes esperar si el promedio histórico es 2 por mes?
- **Weibull:** Vida útil de equipos y maquinaria. Muy usada en mantenimiento predictivo.
- **Log-normal:** Costos de proyectos de construcción (los sobrecostos no son simétricos — nunca hay un proyecto que cueste la mitad de lo estimado, pero sí uno que cueste el doble).

**Aplicación directa:** Al modelar el tiempo de duración de una actividad de obra (ej: vaciado de concreto), no basta decir "dura 3 días". La distribución correcta te dice: hay 80% de probabilidad de que dure entre 2.5 y 4 días, y 5% de que se extienda más de 5 días por lluvias.

---

## 2. Estadística descriptiva

**¿Qué es?** Resumir un conjunto de datos en números que lo caracterizan.

| Medida | Fórmula conceptual | Uso en construcción |
|--------|-------------------|---------------------|
| Media (μ) | Suma / n | Rendimiento promedio de cuadrilla |
| Mediana | Valor central | Costo típico de proyecto (robusta ante outliers) |
| Desviación estándar (σ) | Dispersión respecto a la media | Variabilidad en avance de obra |
| Rango intercuartil | Q3 - Q1 | Detectar días atípicos en producción |
| Coeficiente de variación | σ / μ | Comparar variabilidad entre distintas actividades |

**Concepto crítico — Outlier:** Un dato que se aleja significativamente del resto. En construcción, un día con producción cero (por lluvia o huelga) es un outlier. Saber identificarlos y decidir si se excluyen del análisis es fundamental.

---

## 3. Intervalos de confianza

**¿Qué es?** En vez de decir "el costo promedio de esta partida es S/. 45,000", un intervalo de confianza dice: "con 95% de confianza, el costo real estará entre S/. 42,000 y S/. 48,000". Es la diferencia entre una estimación puntual y una estimación honesta.

**Por qué importa en construcción:** Los expedientes técnicos incluyen estimaciones de costo y plazo. Un profesional que puede cuantificar la incertidumbre de esas estimaciones aporta un valor que la mayoría no puede dar.

---

## 4. Pruebas de hipótesis

**¿Qué es?** Un procedimiento formal para decidir si una observación es evidencia real o solo ruido aleatorio.

**Ejemplo en obra:** ¿El nuevo proveedor de concreto realmente entrega mayor resistencia, o la diferencia que vemos en las probetas es por azar? Una prueba t de Student responde eso con rigor.

**Conceptos clave:**
- **H0 (hipótesis nula):** No hay diferencia / el efecto no existe.
- **H1 (hipótesis alternativa):** Sí hay diferencia.
- **p-valor:** Probabilidad de observar ese resultado si H0 fuera cierta. Si p < 0.05, rechazamos H0.
- **Error Tipo I:** Decir que hay diferencia cuando no la hay (falsa alarma).
- **Error Tipo II:** No detectar una diferencia real (perder una señal importante).

---

## 5. Correlación y regresión

**Correlación:** Mide la relación lineal entre dos variables. Va de -1 a +1.
- +1: cuando una sube, la otra también (temperatura y evaporación del agua en concreto fresco)
- -1: relación inversa (precipitación y días productivos de obra)
- 0: no hay relación lineal

**Importante:** Correlación no es causalidad. Que dos cosas estén correlacionadas no significa que una cause la otra.

**Regresión lineal:** Predice el valor de una variable en función de otra(s). Ejemplo: predecir el número de días de retraso de una obra en función de las lluvias acumuladas del mes.

```
Días_retraso = β0 + β1 × Precipitación_mm + ε
```

**Regresión múltiple:** Múltiples variables predictoras. Más realista para la construcción donde el retraso depende de lluvia, temperatura, disponibilidad de materiales, etc.

---

## Conexión con proyectos de este repositorio

- `07_proyectos/clima_obra/` — usa correlación y regresión para relacionar lluvia con avance de obra
- `07_proyectos/seguridad_vision/` — usa distribución de Poisson para modelar frecuencia de incidentes
- `07_proyectos/riesgo_geoespacial/` — usa estadística descriptiva para caracterizar zonas de riesgo
