# Datos Públicos de Perú para Construcción

El Estado peruano publica una cantidad considerable de datos que nadie en la industria de la construcción está analizando sistemáticamente. Esta es tu ventaja.

---

## OSCE — Organismo Supervisor de las Contrataciones del Estado

**URL:** osce.gob.pe | prodapp2.seace.gob.pe
**Datos disponibles:**
- Todos los contratos de obras públicas (monto, plazo, ubicación, empresa)
- Ampliaciones de plazo aprobadas
- Adicionales de obra
- Penalidades aplicadas
- Proceso de licitación completo

**Por qué es invaluable:** Es el dataset más completo de rendimiento histórico de proyectos de construcción en Perú. Nadie lo ha usado para ML.

**Cómo acceder:**
```python
# Opción 1: Descarga manual desde el portal SEACE
# URL: prodapp2.seace.gob.pe/seace/jsp/busCon/bcSeguimiento.jsf

# Opción 2: OSCE tiene un portal de datos abiertos
# datosabiertos.osce.gob.pe
import pandas as pd
url = 'https://datosabiertos.osce.gob.pe/dataset/contrataciones-publicas'
# Descargar el CSV disponible en el portal
df_osce = pd.read_csv('contrataciones_osce.csv', encoding='latin1')
```

**Análisis posibles:**
- ¿Qué tipo de obras tiene mayor porcentaje de ampliaciones de plazo?
- ¿En qué regiones los proyectos tienen más sobrecostos?
- ¿Hay un monto umbral a partir del cual la probabilidad de penalidad sube?
- ¿Las empresas con mayor experiencia tienen mejor desempeño?

---

## INEI — Instituto Nacional de Estadística e Informática

**URL:** inei.gob.pe | gis.inei.gob.pe
**Datos disponibles:**
- Censos poblacionales (2007, 2017)
- Proyecciones de población por distrito
- Datos de pobreza y desarrollo humano
- Límites distritales georreferenciados
- Índices de precios de construcción (IPAM — Índice de Precios de Materiales de Construcción)

**Relevancia directa:**
- El IPAM mensual es una serie de tiempo del costo de materiales — útil para modelos de predicción de costos.
- Los datos de pobreza por zona ayudan a priorizar donde el impacto de infraestructura es mayor.

```python
import pandas as pd
# IPAM mensual - disponible como serie histórica en INEI
ipam = pd.read_excel('ipam_historico.xlsx')
ipam['fecha'] = pd.to_datetime(ipam['fecha'])
ipam.set_index('fecha', inplace=True)
```

---

## Ministerio de Economía y Finanzas — MEF

**URL:** mef.gob.pe | ofi5.mef.gob.pe/maps/Ymaps.aspx (Mapa de Inversiones)

**Datos disponibles:**
- SIAF: Sistema Integrado de Administración Financiera — ejecución presupuestal de obras
- Mapa de Inversiones: visualización georreferenciada de proyectos de inversión pública
- Banco de Inversiones: proyectos de inversión pública registrados

**Relevancia:** El Mapa de Inversiones del MEF muestra georreferenciados todos los proyectos de inversión pública activos y en formulación. Es una fuente directa para identificar dónde se construirá infraestructura en Perú.

---

## Provías Nacional — MTC

**URL:** proviasnac.gob.pe
**Datos disponibles:**
- Estado de conservación de la red vial nacional
- Proyectos de rehabilitación y mejoramiento en ejecución
- Datos de tráfico (IMD — Índice Medio Diario) por tramo vial

**Relevancia:** Para proyectos viales, los datos de tráfico (IMD) son fundamentales para el diseño y también para modelos predictivos de desgaste de pavimento.

---

## COFOPRI y SUNARP — Datos de propiedad

**Relevancia para construcción:** Para proyectos que requieren expropiación o saneamiento de terrenos, los datos del registro predial son críticos. Directamente relevante para obras viales que cruzan propiedades privadas.

---

## Portal de Datos Abiertos del Estado Peruano

**URL:** datosabiertos.gob.pe
**Qué contiene:** Datasets de múltiples entidades del estado, incluyendo salud, educación, economía y algunos de infraestructura.

**Cómo explorarlo:**
```python
# Buscar datasets relacionados a construcción
import requests
response = requests.get('https://www.datosabiertos.gob.pe/api/3/action/package_search?q=construccion&rows=20')
resultados = response.json()
for ds in resultados['result']['results']:
    print(ds['title'], '—', ds['organization']['title'])
```

---

## Tabla resumen — Datos públicos de Perú

| Fuente | Datos clave | Aplicación en DS | Acceso |
|--------|-------------|-----------------|--------|
| OSCE | Contratos obras públicas, ampliaciones, penalidades | Predicción de retrasos y sobrecostos | Gratuito |
| INEI | IPAM, población, límites geográficos | Series de tiempo de costos, análisis demográfico | Gratuito |
| MEF Mapa Inversiones | Proyectos de inversión pública georreferenciados | Identificar zonas de actividad constructiva | Gratuito |
| Provías | IMD, estado de vías, proyectos en ejecución | Análisis de demanda vial y mantenimiento | Gratuito |
| SENAMHI | Clima histórico y pronóstico | Pronóstico de impacto climático en obra | Gratuito |
| CENEPRED | Mapas de riesgo de desastres | Análisis de riesgo geoespacial | Gratuito |
