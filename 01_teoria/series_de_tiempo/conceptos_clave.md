# Series de Tiempo aplicadas a la Construcción

Una serie de tiempo es cualquier variable medida de forma secuencial a lo largo del tiempo. En construcción, casi todo lo que importa es una serie de tiempo: el avance diario de obra, la lluvia acumulada, el consumo de materiales, el número de trabajadores activos.

---

## 1. ¿Qué es una serie de tiempo?

Es una secuencia de observaciones ordenadas cronológicamente. A diferencia de datos transversales (donde el orden no importa), en series de tiempo el orden es fundamental — lo que pasó ayer afecta lo que pasa hoy.

**Ejemplos directos en construcción:**
- Precipitación diaria en Lima (mm) — últimos 10 años
- Avance físico semanal de una obra (% completado)
- Consumo de concreto mensual en m³
- Número de trabajadores por día en campo
- Precio del acero de construcción por mes

---

## 2. Componentes de una serie de tiempo

Toda serie de tiempo puede descomponerse en cuatro elementos:

### Tendencia (Trend)
Dirección general de largo plazo. El precio del acero de construcción en Perú ha tenido tendencia al alza en los últimos 10 años, con oscilaciones de corto plazo.

### Estacionalidad (Seasonality)
Patrones que se repiten con frecuencia fija. La lluvia en Lima tiene estacionalidad anual clara: muy seca en verano (enero-marzo), algo más húmeda en invierno (junio-agosto). El avance de obras tiene estacionalidad dentro del año fiscal peruano.

### Ciclo (Cycle)
Fluctuaciones de largo plazo sin frecuencia fija. El ciclo de inversión en infraestructura pública en Perú sigue en parte los ciclos políticos de 5 años.

### Ruido (Residual)
Lo que no explican los tres anteriores. Variaciones aleatorias, eventos inesperados (huelgas, lluvias atípicas, accidentes).

**Descomposición práctica:**
```python
from statsmodels.tsa.seasonal import seasonal_decompose
resultado = seasonal_decompose(serie, model='additive', period=12)
resultado.plot()
```

---

## 3. Estacionariedad

**Concepto crítico:** Una serie es estacionaria cuando su media y varianza no cambian con el tiempo. La mayoría de modelos clásicos requieren estacionariedad.

**¿Cómo detectarla?**
- Visualmente: si la serie tiene tendencia o varianza creciente, no es estacionaria
- Formalmente: Prueba de Dickey-Fuller (ADF) — si p < 0.05, es estacionaria

**¿Cómo corregirla?**
- Diferenciación: restar cada valor del anterior elimina tendencias
- Transformación logarítmica: estabiliza varianza creciente

---

## 4. Autocorrelación (ACF y PACF)

**Autocorrelación (ACF):** Mide qué tan correlacionado está un valor con sus versiones pasadas. Si la lluvia de hoy está correlacionada con la de ayer, ACF lo detecta.

**Autocorrelación parcial (PACF):** Similar pero eliminando la influencia de los rezagos intermedios.

**Uso práctico:** Los gráficos ACF y PACF se usan para elegir los parámetros del modelo ARIMA.

---

## 5. Modelos de pronóstico

### ARIMA (AutoRegressive Integrated Moving Average)
El modelo clásico. Funciona bien para series univariadas sin estacionalidad marcada.
- **AR (p):** Cuántos valores pasados usa para predecir el presente
- **I (d):** Cuántas veces se diferencia para lograr estacionariedad
- **MA (q):** Cuántos errores pasados se incorporan al modelo

**SARIMA:** Extensión de ARIMA que maneja estacionalidad explícita. Ideal para lluvia mensual.

### Prophet (Facebook/Meta)
Diseñado para series con estacionalidad múltiple y datos faltantes. Muy robusto y fácil de usar. Excelente para pronóstico de variables climáticas y avance de obra.

```python
from prophet import Prophet
modelo = Prophet()
modelo.fit(df)  # df con columnas 'ds' (fecha) y 'y' (valor)
futuro = modelo.make_future_dataframe(periods=30)
pronostico = modelo.predict(futuro)
```

### Modelos de ML para series de tiempo
Random Forest, XGBoost y LSTMs (redes recurrentes) pueden usarse cuando hay múltiples variables predictoras (lluvia + temperatura + mes del año + tipo de actividad).

---

## 6. Métricas de evaluación para pronóstico

| Métrica | Qué mide | Cuándo usarla |
|---------|----------|---------------|
| MAE | Error absoluto promedio | Cuando todos los errores pesan igual |
| RMSE | Error cuadrático medio | Cuando los errores grandes son más costosos |
| MAPE | Error porcentual promedio | Para comparar modelos en distintas escalas |

---

## 7. Aplicación concreta: lluvia vs. avance de obra

**Escenario:** Tienes registro diario de precipitación en Lima (SENAMHI) y el avance semanal de una obra de puente. Quieres predecir cuándo habrá interrupciones.

**Proceso:**
1. Descomponer la serie de lluvia para identificar estacionalidad
2. Definir umbral crítico (ej: >15mm/día paraliza vaciado de concreto)
3. Entrenar modelo Prophet con datos históricos de SENAMHI
4. Generar pronóstico de lluvia para las próximas 4 semanas
5. Cruzar con cronograma de obra para identificar actividades en riesgo

---

## Conexión con proyectos de este repositorio

- `07_proyectos/clima_obra/` — implementación completa de pronóstico climático con Prophet
- `04_fuentes_de_datos/datos_climaticos.md` — dónde obtener datos de SENAMHI
