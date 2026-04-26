# Dashboards

Aplicaciones web construidas con Streamlit para visualización en campo y en oficina.

## Por qué Streamlit
- Desarrollado 100% en Python — sin necesidad de aprender HTML/CSS/JavaScript
- Listo para usar en celular desde cualquier navegador
- Deploy gratuito en Streamlit Community Cloud
- Ideal para compartir con ingenieros de campo que no tienen acceso a Python

## Dashboards planeados

| Dashboard | Estado | Descripción |
|-----------|--------|-------------|
| `clima_cronograma/` | Pendiente | Pronóstico climático vs. actividades críticas del cronograma |
| `seguridad_epp/` | Pendiente | Reportes de cumplimiento de EPP por zona y turno |
| `riesgo_proyecto/` | Pendiente | Mapa interactivo de riesgo geoespacial por proyecto |
| `avance_obra/` | Pendiente | SPI/CPI en tiempo real con predicción de fecha de término |

## Estructura de cada dashboard

```
nombre_dashboard/
├── app.py             ← Aplicación Streamlit principal
├── utils.py           ← Funciones auxiliares
├── requirements.txt   ← Dependencias
└── README.md          ← Cómo correr y desplegar
```

## Cómo correr un dashboard localmente

```bash
pip install streamlit
streamlit run app.py
```

## Cómo desplegarlo gratis

1. Subir el código a GitHub
2. Ir a share.streamlit.io
3. Conectar el repositorio
4. El dashboard queda disponible en una URL pública
