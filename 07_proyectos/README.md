# Proyectos Aplicados

Cada proyecto en esta carpeta sigue la misma estructura interna para garantizar replicabilidad.

---

## Estructura interna de cada proyecto

```
nombre_proyecto/
├── README.md          ← Descripción, objetivo, resultados y cómo reproducir
├── data/              ← Datos específicos de este proyecto (o enlaces a 06_datos/)
├── notebooks/         ← Exploración y análisis en Jupyter
│   ├── 01_exploracion.ipynb
│   ├── 02_limpieza.ipynb
│   └── 03_modelo.ipynb
├── src/               ← Scripts Python listos para producción
│   └── pipeline.py
├── outputs/           ← Gráficos, mapas y resultados generados
└── requirements.txt   ← Dependencias específicas del proyecto
```

---

## Proyectos activos

| Proyecto | Estado | Descripción | Técnica |
|----------|--------|-------------|---------|
| `clima_obra/` | 🔄 En desarrollo | Pronóstico climático integrado a cronograma | Prophet + SENAMHI |
| `seguridad_vision/` | 🔄 En desarrollo | Detección de EPPs en tiempo real | YOLOv8 |
| `riesgo_geoespacial/` | 🔄 En desarrollo | Mapa de riesgo para zonas de proyecto | GeoPandas + CENEPRED |

---

## Cómo agregar un nuevo proyecto

1. Crear carpeta con nombre descriptivo en snake_case
2. Copiar la estructura interna de arriba
3. Escribir el README.md antes de cualquier código
4. Documentar el entorno en requirements.txt
5. Agregar el proyecto a la tabla de arriba
