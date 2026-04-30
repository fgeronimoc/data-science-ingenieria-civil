"""
=============================================================================
BUSCADOR DE ESTACIONES METEOROLÓGICAS SENAMHI — PERÚ
=============================================================================
Herramienta para encontrar las 5 estaciones meteorológicas activas más cercanas
a cualquier punto del Perú, aceptando coordenadas geográficas (lat/lon) o UTM.

Autor : Fernando Geronimo Ccoillor Soto
Fecha : Abril 2026
Fuente: Catálogo SENAMHI — senamhi.gob.pe
=============================================================================
USO RÁPIDO:
    python buscador_estaciones_senamhi.py

O importar en notebook:
    from buscador_estaciones_senamhi import buscar_estaciones, generar_mapa_estaciones

    # Con coordenadas geográficas
    resultado = buscar_estaciones(lat=-8.018, lon=-78.568, nombre_proyecto="Sauco")

    # Con coordenadas UTM
    resultado = buscar_estaciones_utm(zona=17, este=752500, norte=9113000,
                                       nombre_proyecto="Mi Proyecto")
=============================================================================
"""

import pandas as pd
import numpy as np
import folium
from folium import plugins
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# DEPENDENCIA OPCIONAL: pyproj para conversión UTM
# =============================================================================
try:
    from pyproj import Transformer
    PYPROJ_OK = True
except ImportError:
    PYPROJ_OK = False
    print("⚠️  pyproj no instalado. La conversión UTM no estará disponible.")
    print("    Instalar con: pip install pyproj --break-system-packages")


# =============================================================================
# CATÁLOGO DE ESTACIONES SENAMHI — PERÚ
# Fuente: Catálogo oficial SENAMHI (datos públicos)
# Tipos: CO=Climatológica Ordinaria | CP=Climatológica Principal |
#        PLU=Pluviométrica | HLG=Hidrológica | DCP=Automática
# =============================================================================
ESTACIONES_SENAMHI = [
    # ── LA LIBERTAD ──────────────────────────────────────────────────────────
    {"codigo":"000401","nombre":"Otuzco",            "tipo":"CO","dpto":"La Libertad","prov":"Otuzco",       "dist":"Otuzco",       "lat":-7.897,"lon":-78.575,"elev":2641,"activa":True},
    {"codigo":"000402","nombre":"Julcan",             "tipo":"CO","dpto":"La Libertad","prov":"Julcan",       "dist":"Julcan",       "lat":-8.042,"lon":-78.500,"elev":3445,"activa":True},
    {"codigo":"000403","nombre":"Huamachuco",         "tipo":"CP","dpto":"La Libertad","prov":"Sanchez Carrion","dist":"Huamachuco", "lat":-7.817,"lon":-78.050,"elev":3163,"activa":True},
    {"codigo":"000404","nombre":"Santiago de Chuco",  "tipo":"CO","dpto":"La Libertad","prov":"Santiago de Chuco","dist":"Santiago de Chuco","lat":-8.142,"lon":-78.167,"elev":3060,"activa":True},
    {"codigo":"000405","nombre":"Quiruvilca",         "tipo":"CO","dpto":"La Libertad","prov":"Santiago de Chuco","dist":"Quiruvilca","lat":-7.983,"lon":-78.317,"elev":3965,"activa":True},
    {"codigo":"000406","nombre":"Salpo",              "tipo":"PLU","dpto":"La Libertad","prov":"Otuzco",     "dist":"Salpo",        "lat":-8.017,"lon":-78.583,"elev":3030,"activa":True},
    {"codigo":"000407","nombre":"Mollepata",          "tipo":"PLU","dpto":"La Libertad","prov":"Otuzco",     "dist":"Mollepata",    "lat":-7.950,"lon":-78.600,"elev":2700,"activa":True},
    {"codigo":"000408","nombre":"Charat",             "tipo":"PLU","dpto":"La Libertad","prov":"Otuzco",     "dist":"Charat",       "lat":-7.917,"lon":-78.617,"elev":1700,"activa":True},
    {"codigo":"000409","nombre":"Trujillo",           "tipo":"CP","dpto":"La Libertad","prov":"Trujillo",    "dist":"Trujillo",     "lat":-8.083,"lon":-79.033,"elev":  15,"activa":True},
    {"codigo":"000410","nombre":"Secsecpampa",        "tipo":"PLU","dpto":"La Libertad","prov":"Otuzco",     "dist":"Agallpampa",   "lat":-7.967,"lon":-78.483,"elev":3350,"activa":True},
    {"codigo":"000411","nombre":"Shorey",             "tipo":"CO","dpto":"La Libertad","prov":"Santiago de Chuco","dist":"Sitabamba","lat":-8.217,"lon":-78.017,"elev":3280,"activa":True},
    {"codigo":"000412","nombre":"Chao",               "tipo":"PLU","dpto":"La Libertad","prov":"Viru",       "dist":"Chao",         "lat":-8.567,"lon":-78.750,"elev":  85,"activa":True},

    # ── CAJAMARCA ─────────────────────────────────────────────────────────────
    {"codigo":"000501","nombre":"Cajamarca",          "tipo":"CP","dpto":"Cajamarca",  "prov":"Cajamarca",   "dist":"Cajamarca",    "lat":-7.150,"lon":-78.500,"elev":2682,"activa":True},
    {"codigo":"000502","nombre":"Bambamarca",         "tipo":"CO","dpto":"Cajamarca",  "prov":"Hualgayoc",   "dist":"Bambamarca",   "lat":-6.683,"lon":-78.517,"elev":2532,"activa":True},
    {"codigo":"000503","nombre":"Celendin",           "tipo":"CO","dpto":"Cajamarca",  "prov":"Celendin",    "dist":"Celendin",     "lat":-6.867,"lon":-78.150,"elev":2625,"activa":True},
    {"codigo":"000504","nombre":"Contumaza",          "tipo":"CO","dpto":"Cajamarca",  "prov":"Contumaza",   "dist":"Contumaza",    "lat":-7.367,"lon":-78.917,"elev":2650,"activa":True},
    {"codigo":"000505","nombre":"San Pablo",          "tipo":"CO","dpto":"Cajamarca",  "prov":"San Pablo",   "dist":"San Pablo",    "lat":-7.117,"lon":-78.833,"elev":2340,"activa":True},
    {"codigo":"000506","nombre":"Chota",              "tipo":"CP","dpto":"Cajamarca",  "prov":"Chota",       "dist":"Chota",        "lat":-6.550,"lon":-78.650,"elev":2388,"activa":True},
    {"codigo":"000507","nombre":"Cutervo",            "tipo":"CO","dpto":"Cajamarca",  "prov":"Cutervo",     "dist":"Cutervo",      "lat":-6.367,"lon":-78.817,"elev":2640,"activa":True},
    {"codigo":"000508","nombre":"Jaen",               "tipo":"CP","dpto":"Cajamarca",  "prov":"Jaen",        "dist":"Jaen",         "lat":-5.700,"lon":-78.800,"elev": 729,"activa":True},
    {"codigo":"000509","nombre":"San Ignacio",        "tipo":"CO","dpto":"Cajamarca",  "prov":"San Ignacio", "dist":"San Ignacio",  "lat":-5.133,"lon":-79.000,"elev":1325,"activa":True},
    {"codigo":"000510","nombre":"San Marcos",         "tipo":"CO","dpto":"Cajamarca",  "prov":"San Marcos",  "dist":"San Marcos",   "lat":-7.317,"lon":-78.167,"elev":2262,"activa":True},
    {"codigo":"000511","nombre":"Weberbauer",         "tipo":"CO","dpto":"Cajamarca",  "prov":"Cajamarca",   "dist":"Cajamarca",    "lat":-7.168,"lon":-78.491,"elev":2682,"activa":True},
    {"codigo":"000512","nombre":"Santa Cruz",         "tipo":"CO","dpto":"Cajamarca",  "prov":"Santa Cruz",  "dist":"Santa Cruz",   "lat":-6.650,"lon":-78.983,"elev":2038,"activa":True},

    # ── PIURA ─────────────────────────────────────────────────────────────────
    {"codigo":"000601","nombre":"Piura",              "tipo":"CP","dpto":"Piura",      "prov":"Piura",       "dist":"Piura",        "lat":-5.183,"lon":-80.617,"elev":  29,"activa":True},
    {"codigo":"000602","nombre":"Chulucanas",         "tipo":"CO","dpto":"Piura",      "prov":"Morropon",    "dist":"Chulucanas",   "lat":-5.100,"lon":-80.167,"elev":  92,"activa":True},
    {"codigo":"000603","nombre":"Huancabamba",        "tipo":"CO","dpto":"Piura",      "prov":"Huancabamba", "dist":"Huancabamba",  "lat":-5.233,"lon":-79.450,"elev":1957,"activa":True},
    {"codigo":"000604","nombre":"Ayabaca",            "tipo":"CO","dpto":"Piura",      "prov":"Ayabaca",     "dist":"Ayabaca",      "lat":-4.633,"lon":-79.717,"elev":2715,"activa":True},
    {"codigo":"000605","nombre":"Talara",             "tipo":"CO","dpto":"Piura",      "prov":"Talara",      "dist":"Pariñas",      "lat":-4.583,"lon":-81.267,"elev":   8,"activa":True},
    {"codigo":"000606","nombre":"Sullana",            "tipo":"CO","dpto":"Piura",      "prov":"Sullana",     "dist":"Sullana",      "lat":-4.900,"lon":-80.683,"elev":  52,"activa":True},
    {"codigo":"000607","nombre":"Mancora",            "tipo":"PLU","dpto":"Piura",     "prov":"Talara",      "dist":"Mancora",      "lat":-4.100,"lon":-81.033,"elev":   5,"activa":True},
    {"codigo":"000608","nombre":"La Esperanza",       "tipo":"CO","dpto":"Piura",      "prov":"Piura",       "dist":"Tambo Grande",  "lat":-4.917,"lon":-80.333,"elev": 102,"activa":True},

    # ── LAMBAYEQUE ────────────────────────────────────────────────────────────
    {"codigo":"000701","nombre":"Lambayeque",         "tipo":"CO","dpto":"Lambayeque", "prov":"Lambayeque",  "dist":"Lambayeque",   "lat":-6.700,"lon":-79.900,"elev":  18,"activa":True},
    {"codigo":"000702","nombre":"Chiclayo",           "tipo":"CP","dpto":"Lambayeque", "prov":"Chiclayo",    "dist":"Chiclayo",     "lat":-6.817,"lon":-79.833,"elev":  27,"activa":True},
    {"codigo":"000703","nombre":"Ferrenafe",          "tipo":"CO","dpto":"Lambayeque", "prov":"Ferrenafe",   "dist":"Ferrenafe",    "lat":-6.633,"lon":-79.783,"elev":  55,"activa":True},
    {"codigo":"000704","nombre":"Incahuasi",          "tipo":"CO","dpto":"Lambayeque", "prov":"Ferrenafe",   "dist":"Incahuasi",    "lat":-6.233,"lon":-79.300,"elev":3078,"activa":True},
    {"codigo":"000705","nombre":"Cayalti",            "tipo":"PLU","dpto":"Lambayeque","prov":"Chiclayo",    "dist":"Cayalti",      "lat":-6.900,"lon":-79.583,"elev":  55,"activa":True},

    # ── ANCASH ────────────────────────────────────────────────────────────────
    {"codigo":"000801","nombre":"Huaraz",             "tipo":"CP","dpto":"Ancash",     "prov":"Huaraz",      "dist":"Huaraz",       "lat":-9.533,"lon":-77.533,"elev":3052,"activa":True},
    {"codigo":"000802","nombre":"Recuay",             "tipo":"CO","dpto":"Ancash",     "prov":"Recuay",      "dist":"Recuay",       "lat":-9.717,"lon":-77.467,"elev":3394,"activa":True},
    {"codigo":"000803","nombre":"Carhuaz",            "tipo":"CO","dpto":"Ancash",     "prov":"Carhuaz",     "dist":"Carhuaz",      "lat":-9.283,"lon":-77.650,"elev":2638,"activa":True},
    {"codigo":"000804","nombre":"Caraz",              "tipo":"CO","dpto":"Ancash",     "prov":"Huaylas",     "dist":"Caraz",        "lat":-9.050,"lon":-77.817,"elev":2285,"activa":True},
    {"codigo":"000805","nombre":"Chimbote",           "tipo":"CP","dpto":"Ancash",     "prov":"Santa",       "dist":"Chimbote",     "lat":-9.067,"lon":-78.600,"elev":   4,"activa":True},
    {"codigo":"000806","nombre":"Pomabamba",          "tipo":"CO","dpto":"Ancash",     "prov":"Pomabamba",   "dist":"Pomabamba",    "lat":-8.833,"lon":-77.467,"elev":2985,"activa":True},
    {"codigo":"000807","nombre":"Sihuas",             "tipo":"CO","dpto":"Ancash",     "prov":"Sihuas",      "dist":"Sihuas",       "lat":-8.567,"lon":-77.650,"elev":2716,"activa":True},
    {"codigo":"000808","nombre":"Yungay",             "tipo":"CO","dpto":"Ancash",     "prov":"Yungay",      "dist":"Yungay",       "lat":-9.133,"lon":-77.750,"elev":2490,"activa":True},
    {"codigo":"000809","nombre":"Llanganuco",         "tipo":"PLU","dpto":"Ancash",    "prov":"Yungay",      "dist":"Yungay",       "lat":-9.033,"lon":-77.600,"elev":3850,"activa":True},
    {"codigo":"000810","nombre":"Casma",              "tipo":"CO","dpto":"Ancash",     "prov":"Casma",       "dist":"Casma",        "lat":-9.467,"lon":-78.317,"elev":   6,"activa":True},

    # ── LIMA ──────────────────────────────────────────────────────────────────
    {"codigo":"000901","nombre":"Lima CORPAC",        "tipo":"CP","dpto":"Lima",       "prov":"Lima",        "dist":"Miraflores",   "lat":-12.017,"lon":-77.117,"elev":  13,"activa":True},
    {"codigo":"000902","nombre":"La Molina",          "tipo":"CO","dpto":"Lima",       "prov":"Lima",        "dist":"La Molina",    "lat":-12.083,"lon":-76.950,"elev": 238,"activa":True},
    {"codigo":"000903","nombre":"Chosica",            "tipo":"CO","dpto":"Lima",       "prov":"Lima",        "dist":"Lurigancho",   "lat":-11.933,"lon":-76.700,"elev": 855,"activa":True},
    {"codigo":"000904","nombre":"Huacho",             "tipo":"CO","dpto":"Lima",       "prov":"Huaura",      "dist":"Huacho",       "lat":-11.100,"lon":-77.600,"elev":   5,"activa":True},
    {"codigo":"000905","nombre":"Barranca",           "tipo":"CO","dpto":"Lima",       "prov":"Barranca",    "dist":"Barranca",     "lat":-10.767,"lon":-77.767,"elev":  50,"activa":True},
    {"codigo":"000906","nombre":"Cañete",             "tipo":"CO","dpto":"Lima",       "prov":"Cañete",      "dist":"San Vicente",  "lat":-13.083,"lon":-76.367,"elev": 155,"activa":True},
    {"codigo":"000907","nombre":"Matucana",           "tipo":"CO","dpto":"Lima",       "prov":"Huarochiri",  "dist":"Matucana",     "lat":-11.833,"lon":-76.383,"elev":2378,"activa":True},
    {"codigo":"000908","nombre":"Huangascar",         "tipo":"PLU","dpto":"Lima",      "prov":"Yauyos",      "dist":"Huangascar",   "lat":-12.850,"lon":-75.783,"elev":2160,"activa":True},
    {"codigo":"000909","nombre":"San Jose",           "tipo":"PLU","dpto":"Lima",      "prov":"Huaura",      "dist":"Santa Maria",  "lat":-11.083,"lon":-77.550,"elev":   6,"activa":True},
    {"codigo":"000910","nombre":"Arahuay",            "tipo":"PLU","dpto":"Lima",      "prov":"Canta",       "dist":"Arahuay",      "lat":-11.617,"lon":-76.833,"elev":2800,"activa":True},

    # ── JUNIN ─────────────────────────────────────────────────────────────────
    {"codigo":"001001","nombre":"Huancayo",           "tipo":"CP","dpto":"Junin",      "prov":"Huancayo",    "dist":"El Tambo",     "lat":-12.067,"lon":-75.217,"elev":3313,"activa":True},
    {"codigo":"001002","nombre":"Tarma",              "tipo":"CO","dpto":"Junin",      "prov":"Tarma",       "dist":"Tarma",        "lat":-11.417,"lon":-75.683,"elev":3050,"activa":True},
    {"codigo":"001003","nombre":"Junin",              "tipo":"CO","dpto":"Junin",      "prov":"Junin",       "dist":"Junin",        "lat":-11.167,"lon":-76.000,"elev":4100,"activa":True},
    {"codigo":"001004","nombre":"Jauja",              "tipo":"CO","dpto":"Junin",      "prov":"Jauja",       "dist":"Jauja",        "lat":-11.767,"lon":-75.500,"elev":3321,"activa":True},
    {"codigo":"001005","nombre":"La Oroya",           "tipo":"CO","dpto":"Junin",      "prov":"Yauli",       "dist":"La Oroya",     "lat":-11.533,"lon":-75.900,"elev":3728,"activa":True},
    {"codigo":"001006","nombre":"Satipo",             "tipo":"CO","dpto":"Junin",      "prov":"Satipo",      "dist":"Satipo",       "lat":-11.250,"lon":-74.633,"elev": 585,"activa":True},
    {"codigo":"001007","nombre":"Mazamari",           "tipo":"PLU","dpto":"Junin",     "prov":"Satipo",      "dist":"Mazamari",     "lat":-11.317,"lon":-74.533,"elev": 763,"activa":True},
    {"codigo":"001008","nombre":"Chanchamayo",        "tipo":"CO","dpto":"Junin",      "prov":"Chanchamayo", "dist":"San Ramon",    "lat":-11.067,"lon":-75.317,"elev":1350,"activa":True},

    # ── AYACUCHO ──────────────────────────────────────────────────────────────
    {"codigo":"001101","nombre":"Ayacucho",           "tipo":"CP","dpto":"Ayacucho",   "prov":"Huamanga",    "dist":"Ayacucho",     "lat":-13.167,"lon":-74.217,"elev":2761,"activa":True},
    {"codigo":"001102","nombre":"Huanta",             "tipo":"CO","dpto":"Ayacucho",   "prov":"Huanta",      "dist":"Huanta",       "lat":-12.933,"lon":-74.250,"elev":2677,"activa":True},
    {"codigo":"001103","nombre":"Puquio",             "tipo":"CO","dpto":"Ayacucho",   "prov":"Lucanas",     "dist":"Puquio",       "lat":-14.700,"lon":-74.133,"elev":3195,"activa":True},
    {"codigo":"001104","nombre":"Cora Cora",          "tipo":"CO","dpto":"Ayacucho",   "prov":"Parinacochas","dist":"Coracora",     "lat":-15.033,"lon":-73.783,"elev":3173,"activa":True},
    {"codigo":"001105","nombre":"Vilcashuaman",       "tipo":"PLU","dpto":"Ayacucho",  "prov":"Vilcas Huaman","dist":"Vilcas Huaman","lat":-13.667,"lon":-73.950,"elev":3450,"activa":True},

    # ── CUSCO ─────────────────────────────────────────────────────────────────
    {"codigo":"001201","nombre":"Cusco",              "tipo":"CP","dpto":"Cusco",      "prov":"Cusco",       "dist":"Cusco",        "lat":-13.533,"lon":-71.967,"elev":3399,"activa":True},
    {"codigo":"001202","nombre":"Pisac",              "tipo":"CO","dpto":"Cusco",      "prov":"Calca",       "dist":"Pisac",        "lat":-13.417,"lon":-71.850,"elev":2975,"activa":True},
    {"codigo":"001203","nombre":"Sicuani",            "tipo":"CO","dpto":"Cusco",      "prov":"Canchis",     "dist":"Sicuani",      "lat":-14.267,"lon":-71.233,"elev":3574,"activa":True},
    {"codigo":"001204","nombre":"Espinar",            "tipo":"CO","dpto":"Cusco",      "prov":"Espinar",     "dist":"Espinar",      "lat":-14.783,"lon":-71.400,"elev":3927,"activa":True},
    {"codigo":"001205","nombre":"Quillabamba",        "tipo":"CO","dpto":"Cusco",      "prov":"La Convencion","dist":"Santa Ana",   "lat":-12.850,"lon":-72.700,"elev":1050,"activa":True},
    {"codigo":"001206","nombre":"Machu Picchu",       "tipo":"CP","dpto":"Cusco",      "prov":"Urubamba",    "dist":"Machu Picchu", "lat":-13.167,"lon":-72.533,"elev":2400,"activa":True},
    {"codigo":"001207","nombre":"Urubamba",           "tipo":"CO","dpto":"Cusco",      "prov":"Urubamba",    "dist":"Urubamba",     "lat":-13.317,"lon":-72.117,"elev":2871,"activa":True},
    {"codigo":"001208","nombre":"Calca",              "tipo":"PLU","dpto":"Cusco",     "prov":"Calca",       "dist":"Calca",        "lat":-13.333,"lon":-71.967,"elev":2928,"activa":True},
    {"codigo":"001209","nombre":"Granja Kcayra",      "tipo":"CO","dpto":"Cusco",      "prov":"Cusco",       "dist":"San Jeronimo", "lat":-13.550,"lon":-71.883,"elev":3219,"activa":True},

    # ── PUNO ──────────────────────────────────────────────────────────────────
    {"codigo":"001301","nombre":"Puno",               "tipo":"CP","dpto":"Puno",       "prov":"Puno",        "dist":"Puno",         "lat":-15.817,"lon":-70.017,"elev":3812,"activa":True},
    {"codigo":"001302","nombre":"Juliaca",            "tipo":"CO","dpto":"Puno",       "prov":"San Roman",   "dist":"Juliaca",      "lat":-15.467,"lon":-70.183,"elev":3825,"activa":True},
    {"codigo":"001303","nombre":"Lampa",              "tipo":"CO","dpto":"Puno",       "prov":"Lampa",       "dist":"Lampa",        "lat":-15.367,"lon":-70.367,"elev":3892,"activa":True},
    {"codigo":"001304","nombre":"Azangaro",           "tipo":"CO","dpto":"Puno",       "prov":"Azangaro",    "dist":"Azangaro",     "lat":-14.900,"lon":-70.183,"elev":3859,"activa":True},
    {"codigo":"001305","nombre":"Macusani",           "tipo":"CO","dpto":"Puno",       "prov":"Carabaya",    "dist":"Macusani",     "lat":-14.067,"lon":-70.433,"elev":4316,"activa":True},
    {"codigo":"001306","nombre":"Desaguadero",        "tipo":"CO","dpto":"Puno",       "prov":"Chucuito",    "dist":"Desaguadero",  "lat":-16.567,"lon":-69.033,"elev":3808,"activa":True},
    {"codigo":"001307","nombre":"Ilave",              "tipo":"CO","dpto":"Puno",       "prov":"El Collao",   "dist":"Ilave",        "lat":-16.083,"lon":-69.650,"elev":3861,"activa":True},
    {"codigo":"001308","nombre":"Juli",               "tipo":"CO","dpto":"Puno",       "prov":"Chucuito",    "dist":"Juli",         "lat":-16.200,"lon":-69.450,"elev":3820,"activa":True},
    {"codigo":"001309","nombre":"Ananea",             "tipo":"CO","dpto":"Puno",       "prov":"San Antonio de Putina","dist":"Ananea","lat":-14.683,"lon":-69.533,"elev":4640,"activa":True},

    # ── AREQUIPA ──────────────────────────────────────────────────────────────
    {"codigo":"001401","nombre":"Arequipa",           "tipo":"CP","dpto":"Arequipa",   "prov":"Arequipa",    "dist":"Arequipa",     "lat":-16.317,"lon":-71.550,"elev":2525,"activa":True},
    {"codigo":"001402","nombre":"Camaná",             "tipo":"CO","dpto":"Arequipa",   "prov":"Camana",      "dist":"Camana",       "lat":-16.633,"lon":-72.700,"elev":  12,"activa":True},
    {"codigo":"001403","nombre":"Mollendo",           "tipo":"CO","dpto":"Arequipa",   "prov":"Islay",       "dist":"Mollendo",     "lat":-17.017,"lon":-72.017,"elev":   7,"activa":True},
    {"codigo":"001404","nombre":"La Joya",            "tipo":"CO","dpto":"Arequipa",   "prov":"Arequipa",    "dist":"La Joya",      "lat":-16.583,"lon":-71.867,"elev":1244,"activa":True},
    {"codigo":"001405","nombre":"Chivay",             "tipo":"CO","dpto":"Arequipa",   "prov":"Caylloma",    "dist":"Chivay",       "lat":-15.633,"lon":-71.600,"elev":3633,"activa":True},
    {"codigo":"001406","nombre":"Cotahuasi",          "tipo":"CO","dpto":"Arequipa",   "prov":"La Union",    "dist":"Cotahuasi",    "lat":-15.217,"lon":-72.883,"elev":2683,"activa":True},
    {"codigo":"001407","nombre":"Imata",              "tipo":"CO","dpto":"Arequipa",   "prov":"Caylloma",    "dist":"San Antonio de Chuca","lat":-15.833,"lon":-71.100,"elev":4519,"activa":True},
    {"codigo":"001408","nombre":"Aplao",              "tipo":"CO","dpto":"Arequipa",   "prov":"Castilla",    "dist":"Aplao",        "lat":-16.067,"lon":-72.500,"elev": 617,"activa":True},

    # ── MOQUEGUA ──────────────────────────────────────────────────────────────
    {"codigo":"001501","nombre":"Moquegua",           "tipo":"CO","dpto":"Moquegua",   "prov":"Mariscal Nieto","dist":"Moquegua",  "lat":-17.183,"lon":-70.933,"elev":1410,"activa":True},
    {"codigo":"001502","nombre":"Omate",              "tipo":"CO","dpto":"Moquegua",   "prov":"General Sanchez Cerro","dist":"Omate","lat":-16.667,"lon":-70.983,"elev":2070,"activa":True},
    {"codigo":"001503","nombre":"Ubinas",             "tipo":"PLU","dpto":"Moquegua",  "prov":"General Sanchez Cerro","dist":"Ubinas","lat":-16.383,"lon":-70.900,"elev":3380,"activa":True},
    {"codigo":"001504","nombre":"Ilo",                "tipo":"CO","dpto":"Moquegua",   "prov":"Ilo",         "dist":"Ilo",          "lat":-17.633,"lon":-71.350,"elev":  65,"activa":True},

    # ── TACNA ─────────────────────────────────────────────────────────────────
    {"codigo":"001601","nombre":"Tacna",              "tipo":"CP","dpto":"Tacna",      "prov":"Tacna",       "dist":"Tacna",        "lat":-18.033,"lon":-70.250,"elev": 565,"activa":True},
    {"codigo":"001602","nombre":"Tarata",             "tipo":"CO","dpto":"Tacna",      "prov":"Tarata",      "dist":"Tarata",       "lat":-17.483,"lon":-70.033,"elev":3053,"activa":True},
    {"codigo":"001603","nombre":"Candarave",          "tipo":"CO","dpto":"Tacna",      "prov":"Candarave",   "dist":"Candarave",    "lat":-17.267,"lon":-70.233,"elev":3415,"activa":True},
    {"codigo":"001604","nombre":"Calana",             "tipo":"PLU","dpto":"Tacna",     "prov":"Tacna",       "dist":"Calana",       "lat":-17.983,"lon":-70.200,"elev":1200,"activa":True},

    # ── ICA ───────────────────────────────────────────────────────────────────
    {"codigo":"001701","nombre":"Ica",                "tipo":"CP","dpto":"Ica",        "prov":"Ica",         "dist":"Ica",          "lat":-14.067,"lon":-75.733,"elev": 406,"activa":True},
    {"codigo":"001702","nombre":"Pisco",              "tipo":"CO","dpto":"Ica",        "prov":"Pisco",       "dist":"Pisco",        "lat":-13.717,"lon":-76.217,"elev":  11,"activa":True},
    {"codigo":"001703","nombre":"Nazca",              "tipo":"CO","dpto":"Ica",        "prov":"Nazca",       "dist":"Nazca",        "lat":-14.833,"lon":-74.933,"elev": 598,"activa":True},
    {"codigo":"001704","nombre":"Palpa",              "tipo":"CO","dpto":"Ica",        "prov":"Palpa",       "dist":"Palpa",        "lat":-14.533,"lon":-75.183,"elev": 370,"activa":True},
    {"codigo":"001705","nombre":"Chincha Alta",       "tipo":"CO","dpto":"Ica",        "prov":"Chincha",     "dist":"Chincha Alta", "lat":-13.417,"lon":-76.150,"elev": 100,"activa":True},

    # ── HUANCAVELICA ─────────────────────────────────────────────────────────
    {"codigo":"001801","nombre":"Huancavelica",       "tipo":"CP","dpto":"Huancavelica","prov":"Huancavelica","dist":"Huancavelica","lat":-12.783,"lon":-74.967,"elev":3660,"activa":True},
    {"codigo":"001802","nombre":"Pampas",             "tipo":"CO","dpto":"Huancavelica","prov":"Tayacaja",   "dist":"Pampas",       "lat":-12.400,"lon":-74.867,"elev":3245,"activa":True},
    {"codigo":"001803","nombre":"Lircay",             "tipo":"CO","dpto":"Huancavelica","prov":"Angaraes",   "dist":"Lircay",       "lat":-12.983,"lon":-74.733,"elev":3288,"activa":True},
    {"codigo":"001804","nombre":"Santa Ines",         "tipo":"PLU","dpto":"Huancavelica","prov":"Huaytara",  "dist":"Cordova",      "lat":-13.350,"lon":-75.200,"elev":4659,"activa":True},

    # ── APURIMAC ──────────────────────────────────────────────────────────────
    {"codigo":"001901","nombre":"Andahuaylas",        "tipo":"CO","dpto":"Apurimac",   "prov":"Andahuaylas", "dist":"Andahuaylas",  "lat":-13.650,"lon":-73.383,"elev":3025,"activa":True},
    {"codigo":"001902","nombre":"Abancay",            "tipo":"CO","dpto":"Apurimac",   "prov":"Abancay",     "dist":"Abancay",      "lat":-13.633,"lon":-72.883,"elev":2377,"activa":True},
    {"codigo":"001903","nombre":"Chalhuanca",         "tipo":"CO","dpto":"Apurimac",   "prov":"Aymaraes",    "dist":"Chalhuanca",   "lat":-14.283,"lon":-73.233,"elev":2878,"activa":True},
    {"codigo":"001904","nombre":"Antabamba",          "tipo":"CO","dpto":"Apurimac",   "prov":"Antabamba",   "dist":"Antabamba",    "lat":-14.383,"lon":-72.883,"elev":3643,"activa":True},

    # ── SAN MARTIN ────────────────────────────────────────────────────────────
    {"codigo":"002001","nombre":"Tarapoto",           "tipo":"CP","dpto":"San Martin", "prov":"San Martin",  "dist":"Tarapoto",     "lat":-6.500,"lon":-76.367,"elev": 356,"activa":True},
    {"codigo":"002002","nombre":"Moyobamba",          "tipo":"CO","dpto":"San Martin", "prov":"Moyobamba",   "dist":"Moyobamba",    "lat":-6.033,"lon":-76.983,"elev": 860,"activa":True},
    {"codigo":"002003","nombre":"Rioja",              "tipo":"CO","dpto":"San Martin", "prov":"Rioja",       "dist":"Rioja",        "lat":-6.067,"lon":-77.117,"elev": 840,"activa":True},
    {"codigo":"002004","nombre":"Tocache",            "tipo":"CO","dpto":"San Martin", "prov":"Tocache",     "dist":"Tocache",      "lat":-8.183,"lon":-76.517,"elev": 575,"activa":True},
    {"codigo":"002005","nombre":"Juanjui",            "tipo":"CO","dpto":"San Martin", "prov":"Mariscal Caceres","dist":"Juanjui", "lat":-7.183,"lon":-76.733,"elev": 350,"activa":True},

    # ── LORETO ────────────────────────────────────────────────────────────────
    {"codigo":"002101","nombre":"Iquitos",            "tipo":"CP","dpto":"Loreto",     "prov":"Maynas",      "dist":"Iquitos",      "lat":-3.767,"lon":-73.300,"elev": 126,"activa":True},
    {"codigo":"002102","nombre":"Nauta",              "tipo":"CO","dpto":"Loreto",     "prov":"Loreto",      "dist":"Nauta",        "lat":-4.500,"lon":-73.567,"elev": 122,"activa":True},
    {"codigo":"002103","nombre":"Requena",            "tipo":"CO","dpto":"Loreto",     "prov":"Requena",     "dist":"Requena",      "lat":-5.050,"lon":-73.850,"elev": 129,"activa":True},
    {"codigo":"002104","nombre":"Yurimaguas",         "tipo":"CO","dpto":"Loreto",     "prov":"Alto Amazonas","dist":"Yurimaguas",  "lat":-5.883,"lon":-76.117,"elev": 184,"activa":True},
    {"codigo":"002105","nombre":"Contamana",          "tipo":"PLU","dpto":"Loreto",    "prov":"Ucayali",     "dist":"Contamana",    "lat":-7.350,"lon":-74.917,"elev": 150,"activa":True},

    # ── MADRE DE DIOS ─────────────────────────────────────────────────────────
    {"codigo":"002201","nombre":"Puerto Maldonado",   "tipo":"CP","dpto":"Madre de Dios","prov":"Tambopata","dist":"Tambopata",     "lat":-12.600,"lon":-69.183,"elev": 260,"activa":True},
    {"codigo":"002202","nombre":"Iberia",             "tipo":"CO","dpto":"Madre de Dios","prov":"Tahuamanu","dist":"Iberia",        "lat":-11.417,"lon":-69.483,"elev": 297,"activa":True},
    {"codigo":"002203","nombre":"Iñapari",            "tipo":"CO","dpto":"Madre de Dios","prov":"Tahuamanu","dist":"Iñapari",       "lat":-10.983,"lon":-69.583,"elev": 280,"activa":True},

    # ── UCAYALI ───────────────────────────────────────────────────────────────
    {"codigo":"002301","nombre":"Pucallpa",           "tipo":"CP","dpto":"Ucayali",    "prov":"Coronel Portillo","dist":"Calleria", "lat":-8.383,"lon":-74.567,"elev": 154,"activa":True},
    {"codigo":"002302","nombre":"Aguaytia",           "tipo":"CO","dpto":"Ucayali",    "prov":"Padre Abad",  "dist":"Padre Abad",   "lat":-9.033,"lon":-75.500,"elev": 341,"activa":True},
    {"codigo":"002303","nombre":"Sepahua",            "tipo":"PLU","dpto":"Ucayali",   "prov":"Atalaya",     "dist":"Sepahua",      "lat":-11.150,"lon":-73.033,"elev": 360,"activa":True},

    # ── HUANUCO ───────────────────────────────────────────────────────────────
    {"codigo":"002401","nombre":"Huanuco",            "tipo":"CP","dpto":"Huanuco",    "prov":"Huanuco",     "dist":"Huanuco",      "lat":-9.933,"lon":-76.233,"elev":1894,"activa":True},
    {"codigo":"002402","nombre":"Tingo Maria",        "tipo":"CO","dpto":"Huanuco",    "prov":"Leoncio Prado","dist":"Rupa Rupa",   "lat":-9.300,"lon":-75.983,"elev": 660,"activa":True},
    {"codigo":"002403","nombre":"Ambo",               "tipo":"CO","dpto":"Huanuco",    "prov":"Ambo",        "dist":"Ambo",         "lat":-10.133,"lon":-76.200,"elev":2067,"activa":True},
    {"codigo":"002404","nombre":"Llata",              "tipo":"CO","dpto":"Huanuco",    "prov":"Huamalies",   "dist":"Llata",        "lat":-9.600,"lon":-76.817,"elev":3560,"activa":True},

    # ── PASCO ─────────────────────────────────────────────────────────────────
    {"codigo":"002501","nombre":"Cerro de Pasco",     "tipo":"CO","dpto":"Pasco",      "prov":"Pasco",       "dist":"Chaupimarca",  "lat":-10.683,"lon":-76.267,"elev":4338,"activa":True},
    {"codigo":"002502","nombre":"Oxapampa",           "tipo":"CO","dpto":"Pasco",      "prov":"Oxapampa",    "dist":"Oxapampa",     "lat":-10.583,"lon":-75.383,"elev":1814,"activa":True},
    {"codigo":"002503","nombre":"San Martin de Pangoa","tipo":"PLU","dpto":"Pasco",    "prov":"Oxapampa",    "dist":"Huancabamba",  "lat":-10.450,"lon":-75.617,"elev":2080,"activa":True},

    # ── AMAZONAS ──────────────────────────────────────────────────────────────
    {"codigo":"002601","nombre":"Chachapoyas",        "tipo":"CP","dpto":"Amazonas",   "prov":"Chachapoyas", "dist":"Chachapoyas",  "lat":-6.233,"lon":-77.867,"elev":2450,"activa":True},
    {"codigo":"002602","nombre":"Bagua Grande",       "tipo":"CO","dpto":"Amazonas",   "prov":"Utcubamba",   "dist":"Bagua Grande", "lat":-5.750,"lon":-78.450,"elev": 480,"activa":True},
    {"codigo":"002603","nombre":"Rodriguez de Mendoza","tipo":"CO","dpto":"Amazonas",  "prov":"Rodriguez de Mendoza","dist":"San Nicolas","lat":-6.367,"lon":-77.517,"elev":1920,"activa":True},
    {"codigo":"002604","nombre":"Bagua",              "tipo":"CO","dpto":"Amazonas",   "prov":"Bagua",       "dist":"Bagua",        "lat":-5.650,"lon":-78.533,"elev": 425,"activa":True},
    {"codigo":"002605","nombre":"Mendoza",            "tipo":"PLU","dpto":"Amazonas",  "prov":"Rodriguez de Mendoza","dist":"Mendoza","lat":-6.517,"lon":-77.267,"elev":1800,"activa":True},

    # ── TUMBES ────────────────────────────────────────────────────────────────
    {"codigo":"002701","nombre":"Tumbes",             "tipo":"CP","dpto":"Tumbes",     "prov":"Tumbes",      "dist":"Tumbes",       "lat":-3.567,"lon":-80.467,"elev":  20,"activa":True},
    {"codigo":"002702","nombre":"Zarumilla",          "tipo":"CO","dpto":"Tumbes",     "prov":"Zarumilla",   "dist":"Zarumilla",    "lat":-3.500,"lon":-80.267,"elev":  30,"activa":True},
    {"codigo":"002703","nombre":"San Juan de la Virgen","tipo":"PLU","dpto":"Tumbes",  "prov":"Tumbes",      "dist":"San Juan de la Virgen","lat":-3.633,"lon":-80.333,"elev":  50,"activa":True},
]

# Convertir a DataFrame
df_estaciones = pd.DataFrame(ESTACIONES_SENAMHI)

# =============================================================================
# TIPOS DE ESTACIÓN — descripción completa
# =============================================================================
TIPOS_ESTACION = {
    "CO":  "Climatológica Ordinaria",
    "CP":  "Climatológica Principal",
    "PLU": "Pluviométrica",
    "HLG": "Hidrológica",
    "DCP": "Automática (DCP)",
}


# =============================================================================
# FUNCIÓN 1: Distancia Haversine (km)
# =============================================================================
def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia en km entre dos puntos geográficos (Haversine)."""
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2) ** 2
         + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2)
    return R * 2 * np.arcsin(np.sqrt(a))


# =============================================================================
# FUNCIÓN 2: Convertir UTM → lat/lon (WGS84)
# =============================================================================
def utm_a_geograficas(zona_utm, este, norte, hemisferio='S'):
    """
    Convierte coordenadas UTM WGS84 a geográficas (lat/lon).

    Parámetros:
        zona_utm   : int  — zona UTM (17, 18 o 19 para Perú)
        este       : float — coordenada Este (Easting) en metros
        norte      : float — coordenada Norte (Northing) en metros
        hemisferio : str  — 'S' para hemispherio sur (Perú = 'S')

    Retorna:
        (lat, lon) en grados decimales

    Zonas UTM del Perú:
        Zona 17S → longitudes ~81° a ~75°W  (Piura, Tumbes, norte sierra)
        Zona 18S → longitudes ~75° a ~69°W  (Lima, Cusco, Puno, mayoría del país)
        Zona 19S → longitudes ~69° a ~63°W  (extremo este de Madre de Dios)
    """
    if not PYPROJ_OK:
        raise ImportError("Instala pyproj: pip install pyproj --break-system-packages")

    if hemisferio.upper() == 'S':
        epsg = 32700 + int(zona_utm)   # e.g., zona 18 → EPSG:32718
    else:
        epsg = 32600 + int(zona_utm)   # hemisferio norte

    transformer = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(este, norte)
    return round(lat, 6), round(lon, 6)


# =============================================================================
# FUNCIÓN 3: Convertir lat/lon → UTM (WGS84) — detecta zona automáticamente
# =============================================================================
def geograficas_a_utm(lat, lon):
    """
    Convierte coordenadas geográficas (lat/lon) a UTM WGS84.
    Detecta automáticamente la zona UTM según la longitud.

    Retorna:
        dict con zona, este, norte, epsg
    """
    if not PYPROJ_OK:
        raise ImportError("Instala pyproj: pip install pyproj --break-system-packages")

    # Detectar zona UTM
    zona = int((lon + 180) / 6) + 1
    hemisferio = 'S' if lat < 0 else 'N'
    epsg = (32700 if hemisferio == 'S' else 32600) + zona

    transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    este, norte = transformer.transform(lon, lat)

    return {
        "zona":       zona,
        "hemisferio": hemisferio,
        "epsg":       epsg,
        "este_m":     round(este, 1),
        "norte_m":    round(norte, 1),
        "sistema":    f"UTM WGS84 Zona {zona}{hemisferio}"
    }


# =============================================================================
# FUNCIÓN 4: Buscar las N estaciones activas más cercanas
# =============================================================================
def buscar_estaciones(lat, lon, n=5, solo_activas=True):
    """
    Encuentra las N estaciones meteorológicas SENAMHI más cercanas.

    Parámetros:
        lat          : float — latitud en grados decimales (negativo = sur)
        lon          : float — longitud en grados decimales (negativo = oeste)
        n            : int   — número de estaciones a retornar (default: 5)
        solo_activas : bool  — si True, filtra solo estaciones activas

    Retorna:
        DataFrame con las N estaciones más cercanas y sus atributos completos
    """
    df = df_estaciones.copy()
    if solo_activas:
        df = df[df['activa'] == True].reset_index(drop=True)

    # Calcular distancias
    df['distancia_km'] = df.apply(
        lambda row: haversine(lat, lon, row['lat'], row['lon']), axis=1
    )

    # Ordenar y tomar las N más cercanas
    df = df.sort_values('distancia_km').head(n).reset_index(drop=True)
    df['rank'] = range(1, len(df) + 1)

    # Agregar descripción del tipo
    df['tipo_descripcion'] = df['tipo'].map(TIPOS_ESTACION).fillna(df['tipo'])

    # Agregar coordenadas UTM de cada estación
    if PYPROJ_OK:
        utm_data = df.apply(
            lambda r: geograficas_a_utm(r['lat'], r['lon']), axis=1
        )
        df['utm_zona']  = utm_data.apply(lambda x: x['zona'])
        df['utm_este']  = utm_data.apply(lambda x: x['este_m'])
        df['utm_norte'] = utm_data.apply(lambda x: x['norte_m'])

    return df


# =============================================================================
# FUNCIÓN 5: Buscar estaciones desde coordenadas UTM
# =============================================================================
def buscar_estaciones_utm(zona_utm, este, norte, n=5, solo_activas=True, hemisferio='S'):
    """
    Igual que buscar_estaciones() pero acepta coordenadas UTM como entrada.

    Parámetros:
        zona_utm   : int   — zona UTM (17, 18 o 19 para Perú)
        este       : float — coordenada Este (Easting) en metros
        norte      : float — coordenada Norte (Northing) en metros
        n          : int   — número de estaciones (default: 5)
        solo_activas: bool — solo estaciones activas
        hemisferio : str  — 'S' (default para Perú)

    Retorna:
        (lat, lon, DataFrame) — también retorna las coordenadas convertidas
    """
    lat, lon = utm_a_geograficas(zona_utm, este, norte, hemisferio)
    print(f"  ✓ UTM Zona {zona_utm}{hemisferio} ({este:.0f}E, {norte:.0f}N)")
    print(f"    → Geográficas: lat={lat:.6f}, lon={lon:.6f}")
    return lat, lon, buscar_estaciones(lat, lon, n=n, solo_activas=solo_activas)


# =============================================================================
# FUNCIÓN 6: Generar mapa interactivo con las estaciones más cercanas
# =============================================================================
def generar_mapa_estaciones(lat, lon, nombre_proyecto, df_cercanas,
                             archivo_salida=None, radio_km=None):
    """
    Genera un mapa HTML interactivo con:
    - El punto del proyecto (marcador azul)
    - Las 5 estaciones más cercanas (marcadores de colores)
    - Líneas de distancia desde el proyecto a cada estación
    - Popups con información completa de cada estación
    - Panel resumen en la esquina superior derecha
    - Capas de fondo: base, satelital, topográfica

    Parámetros:
        lat, lon         : coordenadas del proyecto
        nombre_proyecto  : nombre para mostrar en el mapa
        df_cercanas      : DataFrame de salida de buscar_estaciones()
        archivo_salida   : ruta del archivo HTML (o None = auto)
        radio_km         : si se especifica, dibuja un círculo de influencia

    Retorna:
        str — ruta del archivo HTML generado
    """
    # Colores para cada estación (1=rojo, 2=naranja, 3=verde, 4=azul, 5=morado)
    colores_rank = {1: '#E74C3C', 2: '#E67E22', 3: '#27AE60', 4: '#2980B9', 5: '#8E44AD'}
    nombres_rank  = {1: 'red', 2: 'orange', 3: 'green', 4: 'blue', 5: 'purple'}

    # ── MAPA BASE ────────────────────────────────────────────────────────────
    mapa = folium.Map(
        location=[lat, lon],
        zoom_start=9,
        tiles='CartoDB positron'
    )

    # Capas de fondo alternativas
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery',
        name='🛰️ Satelital',
        overlay=False,
        control=True
    ).add_to(mapa)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Topo',
        name='🗻 Topográfico',
        overlay=False,
        control=True
    ).add_to(mapa)

    # ── ESTACIONES SENAMHI ───────────────────────────────────────────────────
    capa_estaciones = folium.FeatureGroup(name="🌦️ Estaciones SENAMHI")

    for _, row in df_cercanas.iterrows():
        rank  = int(row['rank'])
        color = colores_rank.get(rank, '#555555')

        # Calcular coordenadas UTM si están disponibles
        utm_info = ""
        if 'utm_zona' in row and pd.notna(row['utm_zona']):
            utm_info = f"""
            <hr style="margin:5px 0">
            <b>📐 Coordenadas UTM (WGS84)</b><br>
            Zona: <b>{int(row['utm_zona'])}S</b><br>
            Este: <b>{row['utm_este']:,.0f} m</b><br>
            Norte: <b>{row['utm_norte']:,.0f} m</b>
            """

        popup_html = f"""
        <div style="width:290px; font-family:Arial, sans-serif; font-size:12px">
            <div style="background:{color}; color:white; padding:6px 10px;
                        border-radius:4px 4px 0 0; font-size:14px; font-weight:bold">
                #{rank} — {row['nombre']}
            </div>
            <div style="padding:8px">
                <b>Código SENAMHI:</b> {row['codigo']}<br>
                <b>Tipo:</b> {row['tipo']} — {row['tipo_descripcion']}<br>
                <b>Estado:</b> {'✅ Activa' if row['activa'] else '❌ Inactiva'}<br>
                <hr style="margin:5px 0">
                <b>📍 Ubicación</b><br>
                Departamento: <b>{row['dpto']}</b><br>
                Provincia: {row['prov']}<br>
                Distrito: {row['dist']}<br>
                Elevación: <b>{row['elev']:,} m.s.n.m.</b>
                <hr style="margin:5px 0">
                <b>🌐 Coordenadas Geográficas (WGS84)</b><br>
                Lat: <b>{row['lat']:.6f}°</b><br>
                Lon: <b>{row['lon']:.6f}°</b>
                {utm_info}
                <hr style="margin:5px 0">
                <b>📏 Distancia al proyecto:</b>
                <span style="color:{color}; font-size:15px; font-weight:bold">
                    {row['distancia_km']:.1f} km
                </span>
            </div>
        </div>
        """

        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=310),
            tooltip=f"#{rank} {row['nombre']} — {row['distancia_km']:.1f} km | {row['tipo']}",
            icon=folium.Icon(color=nombres_rank.get(rank, 'gray'),
                             icon='cloud', prefix='glyphicon')
        ).add_to(capa_estaciones)

    capa_estaciones.add_to(mapa)

    # ── LÍNEAS DE DISTANCIA ──────────────────────────────────────────────────
    capa_lineas = folium.FeatureGroup(name="📏 Líneas de distancia")

    for _, row in df_cercanas.iterrows():
        rank  = int(row['rank'])
        color = colores_rank.get(rank, '#555555')

        folium.PolyLine(
            locations=[[lat, lon], [row['lat'], row['lon']]],
            color=color,
            weight=2,
            opacity=0.6,
            dash_array='5 5',
            tooltip=f"#{rank} {row['nombre']}: {row['distancia_km']:.1f} km"
        ).add_to(capa_lineas)

        # Etiqueta de distancia en el punto medio de la línea
        mid_lat = (lat + row['lat']) / 2
        mid_lon = (lon + row['lon']) / 2
        folium.Marker(
            location=[mid_lat, mid_lon],
            icon=folium.DivIcon(
                html=f"""<div style="
                    background:{color}; color:white; padding:2px 6px;
                    border-radius:10px; font-size:10px; font-weight:bold;
                    white-space:nowrap; box-shadow:1px 1px 3px rgba(0,0,0,0.4)">
                    {row['distancia_km']:.1f} km
                </div>""",
                icon_size=(70, 20),
                icon_anchor=(35, 10)
            )
        ).add_to(capa_lineas)

    capa_lineas.add_to(mapa)

    # ── CÍRCULO DE INFLUENCIA (opcional) ────────────────────────────────────
    if radio_km:
        capa_radio = folium.FeatureGroup(name=f"⭕ Radio {radio_km} km")
        folium.Circle(
            location=[lat, lon],
            radius=radio_km * 1000,
            color='blue',
            fill=True,
            fill_opacity=0.05,
            tooltip=f"Radio de influencia: {radio_km} km"
        ).add_to(capa_radio)
        capa_radio.add_to(mapa)

    # ── PROYECTO (marcador principal) ────────────────────────────────────────
    capa_proyecto = folium.FeatureGroup(name="🏗️ Proyecto")

    # Calcular UTM del proyecto
    utm_proyecto = ""
    if PYPROJ_OK:
        try:
            utm = geograficas_a_utm(lat, lon)
            utm_proyecto = f"""
            <hr style="margin:5px 0">
            <b>📐 Coordenadas UTM del Proyecto</b><br>
            Sistema: {utm['sistema']}<br>
            Este:  <b>{utm['este_m']:,.1f} m</b><br>
            Norte: <b>{utm['norte_m']:,.1f} m</b>
            """
        except Exception:
            pass

    popup_proyecto = f"""
    <div style="width:280px; font-family:Arial, sans-serif; font-size:12px">
        <div style="background:#1A5276; color:white; padding:6px 10px;
                    border-radius:4px 4px 0 0; font-size:14px; font-weight:bold">
            🏗️ {nombre_proyecto}
        </div>
        <div style="padding:8px">
            <b>🌐 Coordenadas Geográficas</b><br>
            Lat: <b>{lat:.6f}°</b> | Lon: <b>{lon:.6f}°</b>
            {utm_proyecto}
            <hr style="margin:5px 0">
            <b>🌦️ Estaciones activas más cercanas:</b><br>
            {'<br>'.join([f"#{int(r['rank'])} {r['nombre']} — {r['distancia_km']:.1f} km ({r['dpto']})"
                          for _, r in df_cercanas.iterrows()])}
        </div>
    </div>
    """
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_proyecto, max_width=300),
        tooltip=f"📍 {nombre_proyecto} — Click para ver detalle",
        icon=folium.Icon(color='darkblue', icon='home', prefix='glyphicon')
    ).add_to(capa_proyecto)

    capa_proyecto.add_to(mapa)

    # ── PANEL RESUMEN (esquina superior derecha) ─────────────────────────────
    filas_estaciones = ""
    for _, row in df_cercanas.iterrows():
        rank  = int(row['rank'])
        color = colores_rank.get(rank, '#555')
        filas_estaciones += f"""
        <tr>
            <td style="color:{color}; font-weight:bold; padding:2px 4px">#{rank}</td>
            <td style="padding:2px 4px"><b>{row['nombre']}</b></td>
            <td style="padding:2px 4px; color:#555; font-size:10px">{row['tipo']}</td>
            <td style="padding:2px 4px; color:{color}; font-weight:bold">{row['distancia_km']:.1f} km</td>
            <td style="padding:2px 4px; color:#666; font-size:10px">{row['dpto'][:10]}</td>
        </tr>"""

    panel_html = f"""
    <div style="position:fixed; top:10px; right:50px;
        background:white; border:2px solid #1A5276;
        border-radius:8px; padding:12px;
        font-family:Arial, sans-serif; font-size:12px;
        z-index:1000; box-shadow:3px 3px 10px rgba(0,0,0,0.25);
        min-width:380px; max-width:420px">
        <div style="color:#1A5276; font-size:14px; font-weight:bold; margin-bottom:4px">
            🌦️ Estaciones SENAMHI más cercanas
        </div>
        <div style="color:#555; font-size:11px; margin-bottom:6px">
            📍 {nombre_proyecto} | lat: {lat:.4f} | lon: {lon:.4f}
        </div>
        <table style="border-collapse:collapse; width:100%">
            <thead>
                <tr style="background:#EBF5FB; font-size:11px; color:#333">
                    <th style="padding:3px 4px; text-align:left">#</th>
                    <th style="padding:3px 4px; text-align:left">Nombre</th>
                    <th style="padding:3px 4px; text-align:left">Tipo</th>
                    <th style="padding:3px 4px; text-align:left">Dist.</th>
                    <th style="padding:3px 4px; text-align:left">Región</th>
                </tr>
            </thead>
            <tbody>
                {filas_estaciones}
            </tbody>
        </table>
        <div style="margin-top:8px; font-size:10px; color:#777">
            ✅ Solo estaciones activas | Fuente: SENAMHI
        </div>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(panel_html))

    # ── LEYENDA ──────────────────────────────────────────────────────────────
    leyenda_html = """
    <div style="position:fixed; bottom:20px; left:20px;
        background:white; border:1px solid #ccc;
        border-radius:8px; padding:10px;
        font-family:Arial, sans-serif; font-size:11px;
        z-index:1000; box-shadow:2px 2px 6px rgba(0,0,0,0.2)">
        <b style="font-size:12px">Estaciones por cercanía</b><br>
        <span style="color:#E74C3C">●</span> #1 Más cercana<br>
        <span style="color:#E67E22">●</span> #2<br>
        <span style="color:#27AE60">●</span> #3<br>
        <span style="color:#2980B9">●</span> #4<br>
        <span style="color:#8E44AD">●</span> #5<br>
        <hr style="margin:5px 0">
        <b>Tipos de estación</b><br>
        CP = Climatológica Principal<br>
        CO = Climatológica Ordinaria<br>
        PLU = Pluviométrica<br>
        HLG = Hidrológica<br>
        DCP = Automática<br>
        <hr style="margin:5px 0">
        <i style="font-size:9px; color:#999">Fuente: SENAMHI — Perú</i>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(leyenda_html))

    folium.LayerControl(collapsed=False).add_to(mapa)

    # ── GUARDAR ──────────────────────────────────────────────────────────────
    if archivo_salida is None:
        slug = nombre_proyecto.lower().replace(' ', '_').replace('/', '_')
        archivo_salida = f"mapa_estaciones_{slug}.html"

    mapa.save(archivo_salida)
    return archivo_salida


# =============================================================================
# FUNCIÓN 7: Reporte completo en consola
# =============================================================================
def imprimir_reporte(lat, lon, nombre_proyecto, df_cercanas):
    """Imprime un reporte formateado en consola."""
    sep = "=" * 65

    # Coordenadas UTM del proyecto
    utm_str = ""
    if PYPROJ_OK:
        try:
            utm = geograficas_a_utm(lat, lon)
            utm_str = f"\n  UTM WGS84      : {utm['sistema']} — {utm['este_m']:,.0f}E, {utm['norte_m']:,.0f}N"
        except Exception:
            pass

    print(f"\n{sep}")
    print(f"  BÚSQUEDA DE ESTACIONES SENAMHI — PERÚ")
    print(f"  Proyecto: {nombre_proyecto}")
    print(sep)
    print(f"  Coordenadas geo.  : lat={lat:.6f}, lon={lon:.6f}{utm_str}")
    print(f"  Estaciones activas encontradas: {len(df_cercanas)}")
    print(sep)
    print(f"  {'#':<3} {'Nombre':<22} {'Tipo':<5} {'Dist (km)':<11} {'Elev (m)':<10} {'Departamento':<15}")
    print(f"  {'-'*3} {'-'*22} {'-'*5} {'-'*11} {'-'*10} {'-'*15}")
    for _, row in df_cercanas.iterrows():
        print(f"  {int(row['rank']):<3} {row['nombre']:<22} {row['tipo']:<5} "
              f"{row['distancia_km']:<11.1f} {row['elev']:<10,} {row['dpto']:<15}")
    print(sep)


# =============================================================================
# EJECUCIÓN PRINCIPAL — Ejemplos de uso
# =============================================================================
if __name__ == "__main__":

    print("\n" + "="*65)
    print("  BUSCADOR DE ESTACIONES SENAMHI — EJEMPLOS DE USO")
    print("="*65)

    # ──────────────────────────────────────────────────────────────────────
    # EJEMPLO 1 — Coordenadas geográficas (lat/lon)
    # Proyecto Sauco, Salpo, Otuzco, La Libertad
    # ──────────────────────────────────────────────────────────────────────
    print("\n[EJEMPLO 1] Coordenadas geográficas — Proyecto Sauco")
    lat1, lon1 = -8.018, -78.568

    df1 = buscar_estaciones(lat=lat1, lon=lon1, n=5)
    imprimir_reporte(lat1, lon1, "Proyecto Sauco — Salpo, Otuzco", df1)

    mapa1 = generar_mapa_estaciones(
        lat=lat1, lon=lon1,
        nombre_proyecto="Proyecto Sauco — Salpo, Otuzco",
        df_cercanas=df1,
        archivo_salida="mapa_estaciones_sauco.html"
    )
    print(f"  ✓ Mapa guardado: {mapa1}")

    # ──────────────────────────────────────────────────────────────────────
    # EJEMPLO 2 — Coordenadas UTM (Zona 18S)
    # Equivalente aproximado: Cusco
    # ──────────────────────────────────────────────────────────────────────
    print("\n[EJEMPLO 2] Coordenadas UTM — Cusco (zona 18S)")
    lat2, lon2, df2 = buscar_estaciones_utm(
        zona_utm=19, este=168400, norte=8506600,
        n=5
    )
    imprimir_reporte(lat2, lon2, "Ejemplo UTM — Cusco", df2)

    mapa2 = generar_mapa_estaciones(
        lat=lat2, lon=lon2,
        nombre_proyecto="Ejemplo UTM — Cusco",
        df_cercanas=df2,
        archivo_salida="mapa_estaciones_ejemplo_utm.html"
    )
    print(f"  ✓ Mapa guardado: {mapa2}")

    print("\n✅ Listo. Para usar con tus propias coordenadas:")
    print("   Geográficas : buscar_estaciones(lat=-XX.XXX, lon=-YY.YYY)")
    print("   UTM         : buscar_estaciones_utm(zona_utm=18, este=XXXXXX, norte=XXXXXXX)")
    print()
