# Ingeniería de Datos aplicada a la Construcción

Antes de cualquier modelo o dashboard existe un trabajo invisible pero fundamental: recolectar, limpiar y estructurar los datos. En construcción este proceso es especialmente desafiante porque los datos están dispersos, en papel, en formatos inconsistentes o simplemente no existen aún.

La ingeniería de datos es el 70% del trabajo real en un proyecto de data science.

---

## 1. El pipeline de datos

Un pipeline es la secuencia de pasos que transforma datos crudos en información utilizable.

```
Fuente de datos → Extracción → Limpieza → Transformación → Almacenamiento → Análisis
```

**En el contexto de una constructora:**

```
Parte diario de obra (papel)
        ↓ Extracción (digitización o formulario digital)
Datos crudos en Excel/CSV
        ↓ Limpieza (eliminar duplicados, corregir fechas, imputar vacíos)
Dataset limpio
        ↓ Transformación (calcular avance %, agregar por semana, crear features)
Dataset analítico
        ↓ Almacenamiento (CSV estructurado, SQLite, o base de datos)
        ↓ Análisis y visualización
```

---

## 2. Formatos de datos más comunes

| Formato | Cuándo usarlo | Ventajas | Desventajas |
|---------|--------------|----------|-------------|
| CSV | Datos tabulares simples | Universal, fácil de abrir | No escala bien, sin tipos |
| Excel (.xlsx) | Entrega a ingenieros o gerencia | Familiar para todos | Propenso a errores manuales |
| JSON | APIs y datos anidados | Flexible | Difícil de leer en tablas |
| Parquet | Grandes volúmenes de datos | Comprimido, muy rápido | Requiere Python/Spark |
| GeoJSON | Datos geoespaciales | Estándar web para geo | Solo para datos vectoriales |
| Shapefile | Datos geoespaciales SIG | Compatible con todo SIG | Formato antiguo, múltiples archivos |

---

## 3. Limpieza de datos (Data Cleaning)

El paso más subestimado y más crítico. Datos sucios producen modelos y análisis incorrectos sin importar qué tan sofisticado sea el algoritmo.

### Problemas comunes en datos de construcción

**Valores faltantes (NaN):**
```python
import pandas as pd

df = pd.read_csv('parte_diario.csv')
print(df.isnull().sum())  # Ver cuántos nulos por columna

# Opciones para tratar nulos:
df['avance_pct'].fillna(method='ffill')  # Rellenar con valor anterior
df['lluvia_mm'].fillna(0)               # Asumir 0 si no se registró
df.dropna(subset=['fecha'])              # Eliminar filas sin fecha (crítico)
```

**Tipos de datos incorrectos:**
```python
# La columna 'fecha' llegó como texto
df['fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y')

# El avance llegó como texto ('45%' en vez de 0.45)
df['avance'] = df['avance'].str.replace('%','').astype(float) / 100
```

**Duplicados:**
```python
df.duplicated().sum()          # Contar duplicados
df.drop_duplicates(inplace=True)  # Eliminar
```

**Outliers:**
```python
# Detectar con IQR
Q1 = df['avance_diario'].quantile(0.25)
Q3 = df['avance_diario'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['avance_diario'] < Q1 - 1.5*IQR) | (df['avance_diario'] > Q3 + 1.5*IQR)]
```

**Inconsistencias en texto:**
```python
# 'Lima', 'LIMA', 'lima' son la misma ciudad
df['ciudad'] = df['ciudad'].str.strip().str.title()
```

---

## 4. Transformación de datos

Convertir datos limpios en variables útiles para el análisis.

**Agregación temporal:**
```python
# Convertir registros diarios a resumen semanal
df['semana'] = df['fecha'].dt.isocalendar().week
resumen_semanal = df.groupby('semana').agg({
    'avance_diario': 'sum',
    'trabajadores': 'mean',
    'lluvia_mm': 'sum'
}).reset_index()
```

**Creación de features:**
```python
# Variable: ¿el día anterior llovió más de 15mm?
df['lluvia_ayer'] = df['lluvia_mm'].shift(1)
df['dia_critico'] = (df['lluvia_ayer'] > 15).astype(int)

# Variable: semana del año
df['semana_año'] = df['fecha'].dt.isocalendar().week

# Variable: mes
df['mes'] = df['fecha'].dt.month
```

---

## 5. Almacenamiento estructurado

### Para proyectos individuales: CSV con nomenclatura clara
```
06_datos/
├── raw/
│   └── parte_diario_obra_norte_2024.csv     ← NUNCA se modifica
└── processed/
    └── parte_diario_obra_norte_2024_clean.csv  ← Resultado de limpieza
```

### Para múltiples proyectos: SQLite (base de datos liviana)
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('06_datos/construccion.db')
df.to_sql('avance_obra', conn, if_exists='append', index=False)
conn.close()
```

---

## 6. Estrategia para recolectar datos en una constructora

El mayor reto en Perú es que los datos simplemente no existen en formato digital. Estrategia sugerida:

**Corto plazo — digitalizar lo que ya existe:**
- Solicitar los últimos 12 meses de partes diarios de obra
- Digitalizar en un formato estructurado (Google Sheets o Excel con campos fijos)
- Establecer un formulario Google Forms o Kobo Toolbox para que el personal de campo registre diariamente

**Mediano plazo — captura sistemática:**
- Diseñar plantillas estándar de registro de campo
- Entrenar al personal en 15 minutos sobre el formulario digital
- Automatizar la descarga y limpieza de datos semanalmente

**Largo plazo — integración de sistemas:**
- Conectar con el software de gestión de proyectos (MS Project, Primavera)
- Integrar APIs de datos climáticos automáticamente
- Considerar sensores IoT para variables críticas (temperatura del concreto, humedad)

---

## Conexión con proyectos de este repositorio

- `06_datos/` — aquí viven todos los datos del proyecto
- `07_proyectos/` — cada proyecto tiene su propio pipeline de datos documentado
- `05_herramientas/snippets/` — funciones reutilizables de limpieza de datos
