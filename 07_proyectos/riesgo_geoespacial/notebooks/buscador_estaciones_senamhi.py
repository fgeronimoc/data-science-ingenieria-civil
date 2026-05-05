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

    # ── AMAZONAS ──────────────────────────────────────────────────────────────
    {"codigo":"105075","nombre":"Aramango","tipo":"CO","dpto":"Amazonas","prov":"Bagua","dist":"Aramango","lat":-5.4,"lon":-78.4,"elev":508,"activa":True},
    {"codigo":"002604","nombre":"Bagua","tipo":"CO","dpto":"Amazonas","prov":"Bagua","dist":"Bagua","lat":-5.65,"lon":-78.533,"elev":425,"activa":True},
    {"codigo":"105068","nombre":"Bagua Chica","tipo":"CO","dpto":"Amazonas","prov":"Utcubamba","dist":"Bagua Grande","lat":-5.7,"lon":-78.5,"elev":397,"activa":True},
    {"codigo":"002602","nombre":"Bagua Grande","tipo":"CO","dpto":"Amazonas","prov":"Utcubamba","dist":"Bagua Grande","lat":-5.75,"lon":-78.45,"elev":480,"activa":True},
    {"codigo":"002601","nombre":"Chachapoyas","tipo":"CP","dpto":"Amazonas","prov":"Chachapoyas","dist":"Chachapoyas","lat":-6.233,"lon":-77.867,"elev":2450,"activa":True},
    {"codigo":"106121","nombre":"El Palto","tipo":"CO","dpto":"Amazonas","prov":"Utcubamba","dist":"Lonya Grande","lat":-6.0,"lon":-78.5,"elev":1467,"activa":True},
    {"codigo":"105040","nombre":"El Pintor","tipo":"PLU","dpto":"Amazonas","prov":"Utcubamba","dist":"Bagua Grande","lat":-5.8,"lon":-78.5,"elev":533,"activa":True},
    {"codigo":"105042","nombre":"Jamalca","tipo":"CO","dpto":"Amazonas","prov":"Utcubamba","dist":"Jamalca","lat":-5.9,"lon":-78.2,"elev":1173,"activa":True},
    {"codigo":"105079","nombre":"Jazan","tipo":"CO","dpto":"Amazonas","prov":"Bongara","dist":"Jazan","lat":-5.9,"lon":-78.0,"elev":1354,"activa":True},
    {"codigo":"105046","nombre":"Magunchal","tipo":"PLU","dpto":"Amazonas","prov":"Utcubamba","dist":"Jamalca","lat":-5.9,"lon":-78.2,"elev":632,"activa":True},
    {"codigo":"002605","nombre":"Mendoza","tipo":"PLU","dpto":"Amazonas","prov":"Rodriguez de Mendoza","dist":"Mendoza","lat":-6.517,"lon":-77.267,"elev":1800,"activa":True},
    {"codigo":"002603","nombre":"Rodriguez de Mendoza","tipo":"CO","dpto":"Amazonas","prov":"Rodriguez de Mendoza","dist":"San Nicolas","lat":-6.367,"lon":-77.517,"elev":1920,"activa":True},

    # ── ANCASH ────────────────────────────────────────────────────────────────
    {"codigo":"109014","nombre":"Buena Vista","tipo":"CO","dpto":"Ancash","prov":"Casma","dist":"Buena Vista Alta","lat":-9.4,"lon":-78.2,"elev":213,"activa":True},
    {"codigo":"109046","nombre":"Cajamarquilla","tipo":"CO","dpto":"Ancash","prov":"Huaraz","dist":"La Libertad","lat":-9.6,"lon":-77.7,"elev":3286,"activa":True},
    {"codigo":"000804","nombre":"Caraz","tipo":"CO","dpto":"Ancash","prov":"Huaylas","dist":"Caraz","lat":-9.05,"lon":-77.817,"elev":2285,"activa":True},
    {"codigo":"000803","nombre":"Carhuaz","tipo":"CO","dpto":"Ancash","prov":"Carhuaz","dist":"Carhuaz","lat":-9.283,"lon":-77.65,"elev":2638,"activa":True},
    {"codigo":"000810","nombre":"Casma","tipo":"CO","dpto":"Ancash","prov":"Casma","dist":"Casma","lat":-9.467,"lon":-78.317,"elev":6,"activa":True},
    {"codigo":"109045","nombre":"Chacchan","tipo":"PLU","dpto":"Ancash","prov":"Huaraz","dist":"Pariacoto","lat":-9.5,"lon":-77.8,"elev":2266,"activa":True},
    {"codigo":"110039","nombre":"Chamana","tipo":"CO","dpto":"Ancash","prov":"Recuay","dist":"Llacllin","lat":-10.2,"lon":-77.6,"elev":1260,"activa":True},
    {"codigo":"109019","nombre":"Chavin","tipo":"CO","dpto":"Ancash","prov":"Huari","dist":"Chavin de Huantar","lat":-9.6,"lon":-77.2,"elev":3140,"activa":True},
    {"codigo":"000805","nombre":"Chimbote","tipo":"CP","dpto":"Ancash","prov":"Santa","dist":"Chimbote","lat":-9.067,"lon":-78.6,"elev":4,"activa":True},
    {"codigo":"110018","nombre":"Chiquian","tipo":"CO","dpto":"Ancash","prov":"Bolognesi","dist":"Chiquian","lat":-10.1,"lon":-77.2,"elev":3386,"activa":True},
    {"codigo":"109023","nombre":"Huallanca","tipo":"PLU","dpto":"Ancash","prov":"Bolognesi","dist":"Huallanca","lat":-9.9,"lon":-77.0,"elev":3796,"activa":True},
    {"codigo":"109001","nombre":"Huaraz","tipo":"CP","dpto":"Ancash","prov":"Huaraz","dist":"Independencia","lat":-9.533,"lon":-77.533,"elev":3052,"activa":True},
    {"codigo":"000809","nombre":"Llanganuco","tipo":"PLU","dpto":"Ancash","prov":"Yungay","dist":"Yungay","lat":-9.033,"lon":-77.6,"elev":3850,"activa":True},
    {"codigo":"109038","nombre":"Malvas","tipo":"CO","dpto":"Ancash","prov":"Huarmey","dist":"Malvas","lat":-9.9,"lon":-77.7,"elev":2979,"activa":True},
    {"codigo":"110040","nombre":"Mayorarca","tipo":"PLU","dpto":"Ancash","prov":"Bolognesi","dist":"Cajacay","lat":-10.2,"lon":-77.3,"elev":3335,"activa":True},
    {"codigo":"109039","nombre":"Milpo","tipo":"PLU","dpto":"Ancash","prov":"Recuay","dist":"Catac","lat":-9.9,"lon":-77.2,"elev":4400,"activa":True},
    {"codigo":"110051","nombre":"Ocros","tipo":"PLU","dpto":"Ancash","prov":"Ocros","dist":"Ocros","lat":-10.4,"lon":-77.4,"elev":3249,"activa":True},
    {"codigo":"109040","nombre":"Pariacoto","tipo":"CO","dpto":"Ancash","prov":"Huaraz","dist":"Pariacoto","lat":-9.6,"lon":-77.9,"elev":1312,"activa":True},
    {"codigo":"109048","nombre":"Pira","tipo":"PLU","dpto":"Ancash","prov":"Huaraz","dist":"Pira","lat":-9.6,"lon":-77.7,"elev":3625,"activa":True},
    {"codigo":"108017","nombre":"Pomabamba","tipo":"CO","dpto":"Ancash","prov":"Pomabamba","dist":"Pomabamba","lat":-8.833,"lon":-77.467,"elev":2985,"activa":True},
    {"codigo":"109017","nombre":"Recuay","tipo":"CO","dpto":"Ancash","prov":"Recuay","dist":"Recuay","lat":-9.717,"lon":-77.467,"elev":3394,"activa":True},
    {"codigo":"109013","nombre":"San Lorenzo # 5","tipo":"PLU","dpto":"Ancash","prov":"Recuay","dist":"Ticapampa","lat":-9.8,"lon":-77.4,"elev":3850,"activa":True},
    {"codigo":"109009","nombre":"Santiago Antunez de Mayolo","tipo":"CO","dpto":"Ancash","prov":"Huaraz","dist":"Independencia","lat":-9.5,"lon":-77.5,"elev":3079,"activa":True},
    {"codigo":"108047","nombre":"Sihuas","tipo":"CO","dpto":"Ancash","prov":"Sihuas","dist":"Sihuas","lat":-8.567,"lon":-77.65,"elev":2716,"activa":True},
    {"codigo":"000808","nombre":"Yungay","tipo":"CO","dpto":"Ancash","prov":"Yungay","dist":"Yungay","lat":-9.133,"lon":-77.75,"elev":2490,"activa":True},

    # ── APURIMAC ──────────────────────────────────────────────────────────────
    {"codigo":"001902","nombre":"Abancay","tipo":"CO","dpto":"Apurimac","prov":"Abancay","dist":"Abancay","lat":-13.633,"lon":-72.883,"elev":2377,"activa":True},
    {"codigo":"113025","nombre":"Andahuaylas","tipo":"CO","dpto":"Apurimac","prov":"Andahuaylas","dist":"Andahuaylas","lat":-13.65,"lon":-73.383,"elev":3025,"activa":True},
    {"codigo":"114029","nombre":"Antabamba","tipo":"PLU","dpto":"Apurimac","prov":"Antabamba","dist":"Antabamba","lat":-14.383,"lon":-72.883,"elev":3643,"activa":True},
    {"codigo":"114028","nombre":"Chalhuanca","tipo":"CO","dpto":"Apurimac","prov":"Aymaraes","dist":"Cotaruse","lat":-14.283,"lon":-73.233,"elev":2878,"activa":True},
    {"codigo":"114104","nombre":"Chalhuanca II","tipo":"CO","dpto":"Apurimac","prov":"Aymaraes","dist":"Chalhuanca","lat":-14.3,"lon":-73.2,"elev":3548,"activa":True},
    {"codigo":"113029","nombre":"Curahuasi","tipo":"CO","dpto":"Apurimac","prov":"Abancay","dist":"Curahuasi","lat":-13.6,"lon":-72.7,"elev":2763,"activa":True},
    {"codigo":"113059","nombre":"Tambobamba","tipo":"CO","dpto":"Apurimac","prov":"Cotabambas","dist":"Tambobamba","lat":-13.9,"lon":-72.2,"elev":3317,"activa":True},

    # ── AREQUIPA ──────────────────────────────────────────────────────────────
    {"codigo":"100009","nombre":"Acari","tipo":"PLU","dpto":"Arequipa","prov":"Caraveli","dist":"Bella Union","lat":-15.4,"lon":-74.6,"elev":228,"activa":True},
    {"codigo":"115085","nombre":"Andahua","tipo":"CO","dpto":"Arequipa","prov":"Castilla","dist":"Andagua","lat":-15.5,"lon":-72.4,"elev":3562,"activa":True},
    {"codigo":"116014","nombre":"Aplao","tipo":"CO","dpto":"Arequipa","prov":"Castilla","dist":"Aplao","lat":-16.067,"lon":-72.5,"elev":617,"activa":True},
    {"codigo":"001401","nombre":"Arequipa","tipo":"CP","dpto":"Arequipa","prov":"Arequipa","dist":"Arequipa","lat":-16.317,"lon":-71.55,"elev":2525,"activa":True},
    {"codigo":"100012","nombre":"Atiquipa","tipo":"PLU","dpto":"Arequipa","prov":"Caraveli","dist":"Atiquipa","lat":-15.8,"lon":-74.4,"elev":518,"activa":True},
    {"codigo":"115088","nombre":"Ayo","tipo":"CO","dpto":"Arequipa","prov":"Castilla","dist":"Ayo","lat":-15.7,"lon":-72.3,"elev":1956,"activa":True},
    {"codigo":"115041","nombre":"Cabanaconde","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"Cabanaconde","lat":-15.6,"lon":-72.0,"elev":3333,"activa":True},
    {"codigo":"116013","nombre":"Camana","tipo":"CO","dpto":"Arequipa","prov":"Camana","dist":"Samuel Pastor","lat":-16.633,"lon":-72.7,"elev":12,"activa":True},
    {"codigo":"115018","nombre":"Caraveli","tipo":"CO","dpto":"Arequipa","prov":"Caraveli","dist":"Caraveli","lat":-15.8,"lon":-73.4,"elev":1755,"activa":True},
    {"codigo":"115022","nombre":"Caylloma","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"Caylloma","lat":-15.2,"lon":-71.8,"elev":4318,"activa":True},
    {"codigo":"115087","nombre":"Chachas","tipo":"CO","dpto":"Arequipa","prov":"Castilla","dist":"Chachas","lat":-15.5,"lon":-72.3,"elev":3071,"activa":True},
    {"codigo":"100022","nombre":"Chala","tipo":"CO","dpto":"Arequipa","prov":"Caraveli","dist":"Chala","lat":-15.9,"lon":-74.2,"elev":43,"activa":True},
    {"codigo":"100026","nombre":"Chaparra","tipo":"CO","dpto":"Arequipa","prov":"Caraveli","dist":"Chaparra","lat":-15.7,"lon":-73.9,"elev":1033,"activa":True},
    {"codigo":"115078","nombre":"Chichas","tipo":"CO","dpto":"Arequipa","prov":"Condesuyos","dist":"Chichas","lat":-15.5,"lon":-72.9,"elev":2170,"activa":True},
    {"codigo":"116020","nombre":"Chiguata","tipo":"CO","dpto":"Arequipa","prov":"Arequipa","dist":"Chiguata","lat":-16.4,"lon":-71.4,"elev":2902,"activa":True},
    {"codigo":"115025","nombre":"Chivay","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"Chivay","lat":-15.633,"lon":-71.6,"elev":3633,"activa":True},
    {"codigo":"115089","nombre":"Choco","tipo":"CO","dpto":"Arequipa","prov":"Castilla","dist":"Choco","lat":-15.6,"lon":-72.1,"elev":2428,"activa":True},
    {"codigo":"115020","nombre":"Chuquibamba","tipo":"CO","dpto":"Arequipa","prov":"Condesuyos","dist":"Chuquibamba","lat":-15.8,"lon":-72.7,"elev":2850,"activa":True},
    {"codigo":"115019","nombre":"Cotahuasi","tipo":"CO","dpto":"Arequipa","prov":"La Union","dist":"Cotahuasi","lat":-15.217,"lon":-72.883,"elev":2683,"activa":True},
    {"codigo":"116022","nombre":"El Frayle","tipo":"CO","dpto":"Arequipa","prov":"Arequipa","dist":"San Juan de Tarucani","lat":-16.2,"lon":-71.2,"elev":4131,"activa":True},
    {"codigo":"115090","nombre":"Huambo","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"Huambo","lat":-15.7,"lon":-72.1,"elev":3312,"activa":True},
    {"codigo":"116003","nombre":"Huasacache","tipo":"CO","dpto":"Arequipa","prov":"Arequipa","dist":"Jacobo Hunter","lat":-16.5,"lon":-71.6,"elev":2200,"activa":True},
    {"codigo":"115029","nombre":"Imata","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"San Antonio de Chuca","lat":-15.833,"lon":-71.1,"elev":4519,"activa":True},
    {"codigo":"115023","nombre":"La Angostura","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"Caylloma","lat":-15.2,"lon":-71.7,"elev":4258,"activa":True},
    {"codigo":"117006","nombre":"La Haciendita","tipo":"CO","dpto":"Arequipa","prov":"Islay","dist":"Cocachacra","lat":-17.0,"lon":-71.6,"elev":282,"activa":True},
    {"codigo":"116005","nombre":"La Joya","tipo":"CO","dpto":"Arequipa","prov":"Arequipa","dist":"Vitor","lat":-16.583,"lon":-71.867,"elev":1244,"activa":True},
    {"codigo":"116017","nombre":"La Pampilla","tipo":"CO","dpto":"Arequipa","prov":"Arequipa","dist":"Arequipa","lat":-16.4,"lon":-71.5,"elev":2326,"activa":True},
    {"codigo":"116046","nombre":"Las Salinas","tipo":"CO","dpto":"Arequipa","prov":"Arequipa","dist":"Chiguata","lat":-16.3,"lon":-71.1,"elev":4378,"activa":True},
    {"codigo":"115136","nombre":"Lomas","tipo":"CO","dpto":"Arequipa","prov":"Caraveli","dist":"Lomas","lat":-15.6,"lon":-74.8,"elev":20,"activa":True},
    {"codigo":"115129","nombre":"Machahuay","tipo":"CO","dpto":"Arequipa","prov":"Castilla","dist":"Machaguay","lat":-15.6,"lon":-72.5,"elev":3150,"activa":True},
    {"codigo":"115092","nombre":"Madrigal","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"Madrigal","lat":-15.6,"lon":-71.8,"elev":3276,"activa":True},
    {"codigo":"001403","nombre":"Mollendo","tipo":"CO","dpto":"Arequipa","prov":"Islay","dist":"Mollendo","lat":-17.017,"lon":-72.017,"elev":7,"activa":True},
    {"codigo":"116012","nombre":"Ocoña","tipo":"PLU","dpto":"Arequipa","prov":"Camana","dist":"Ocoña","lat":-16.4,"lon":-73.1,"elev":270,"activa":True},
    {"codigo":"115086","nombre":"Orcopampa","tipo":"CO","dpto":"Arequipa","prov":"Cast","dist":"Illa Orcopampa","lat":-15.3,"lon":-72.3,"elev":3779,"activa":True},
    {"codigo":"117005","nombre":"Pampa Blanca","tipo":"CO","dpto":"Arequipa","prov":"Islay","dist":"Cocachacra","lat":-17.1,"lon":-71.7,"elev":106,"activa":True},
    {"codigo":"116043","nombre":"Pampa de Arrieros","tipo":"CO","dpto":"Arequipa","prov":"Arequipa","dist":"Yura","lat":-16.1,"lon":-71.6,"elev":3715,"activa":True},
    {"codigo":"116006","nombre":"Pampa de Majes","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"Majes","lat":-16.3,"lon":-72.2,"elev":1498,"activa":True},
    {"codigo":"115021","nombre":"Pampacolca","tipo":"CO","dpto":"Arequipa","prov":"Castilla","dist":"Pampacolca","lat":-15.7,"lon":-72.6,"elev":2950,"activa":True},
    {"codigo":"115126","nombre":"Pillones","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"San Antonio de Chuca","lat":-16.0,"lon":-71.2,"elev":4455,"activa":True},
    {"codigo":"115101","nombre":"Porpera","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"Tisco","lat":-15.4,"lon":-71.3,"elev":4195,"activa":True},
    {"codigo":"115084","nombre":"Pullhuay (ayahuasi)","tipo":"CO","dpto":"Arequipa","prov":"La Union","dist":"Alca","lat":-15.1,"lon":-72.8,"elev":3455,"activa":True},
    {"codigo":"116011","nombre":"Punta Atico","tipo":"CO","dpto":"Arequipa","prov":"Caraveli","dist":"Atico","lat":-16.2,"lon":-73.7,"elev":20,"activa":True},
    {"codigo":"100111","nombre":"Punta Islay","tipo":"PLU","dpto":"Arequipa","prov":"Islay","dist":"Islay","lat":-17.0,"lon":-72.1,"elev":15,"activa":True},
    {"codigo":"115043","nombre":"Salamanca","tipo":"CO","dpto":"Arequipa","prov":"Condesuyos","dist":"Salamanca","lat":-15.5,"lon":-72.8,"elev":3203,"activa":True},
    {"codigo":"116010","nombre":"Santa Rita","tipo":"CO","dpto":"Arequipa","prov":"Arequipa","dist":"Santa Rita de Siguas","lat":-16.5,"lon":-72.1,"elev":1297,"activa":True},
    {"codigo":"115024","nombre":"Sibayo","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"Sibayo","lat":-15.5,"lon":-71.5,"elev":3806,"activa":True},
    {"codigo":"115098","nombre":"Tisco","tipo":"CO","dpto":"Arequipa","prov":"Caylloma","dist":"Tisco","lat":-15.4,"lon":-71.5,"elev":4175,"activa":True},
    {"codigo":"115128","nombre":"Yanaquihua","tipo":"CO","dpto":"Arequipa","prov":"Condesuyos","dist":"Yanaquihua","lat":-15.8,"lon":-72.9,"elev":3130,"activa":True},

    # ── AYACUCHO ──────────────────────────────────────────────────────────────
    {"codigo":"113101","nombre":"Chilcayoc","tipo":"CO","dpto":"Ayacucho","prov":"Sucre","dist":"Chilcayoc","lat":-13.9,"lon":-73.7,"elev":3400,"activa":True},
    {"codigo":"115015","nombre":"Coracora","tipo":"CO","dpto":"Ayacucho","prov":"Parinacochas","dist":"Coracora","lat":-15.033,"lon":-73.783,"elev":3173,"activa":True},
    {"codigo":"114055","nombre":"Huac -huas","tipo":"CO","dpto":"Ayacucho","prov":"Lucanas","dist":"Huac -huas","lat":-14.1,"lon":-74.9,"elev":3180,"activa":True},
    {"codigo":"113019","nombre":"Huamanga","tipo":"CP","dpto":"Ayacucho","prov":"Huamanga","dist":"Jesus Nazareno","lat":-13.167,"lon":-74.217,"elev":2761,"activa":True},
    {"codigo":"113022","nombre":"Huancapi","tipo":"CO","dpto":"Ayacucho","prov":"Victor","dist":"Fajardo Huancapi","lat":-13.8,"lon":-74.1,"elev":3120,"activa":True},
    {"codigo":"001102","nombre":"Huanta","tipo":"CO","dpto":"Ayacucho","prov":"Huanta","dist":"Huanta","lat":-12.933,"lon":-74.25,"elev":2677,"activa":True},
    {"codigo":"113021","nombre":"La Quinua","tipo":"CO","dpto":"Ayacucho","prov":"Huamanga","dist":"Quinua","lat":-13.1,"lon":-74.1,"elev":3240,"activa":True},
    {"codigo":"115076","nombre":"Lampa","tipo":"PLU","dpto":"Ayacucho","prov":"Paucar","dist":"Del Sara Sara Lampa","lat":-15.2,"lon":-73.3,"elev":2790,"activa":True},
    {"codigo":"114067","nombre":"Llauta","tipo":"PLU","dpto":"Ayacucho","prov":"Lucanas","dist":"Llauta","lat":-14.2,"lon":-74.9,"elev":2445,"activa":True},
    {"codigo":"114072","nombre":"Lucanas","tipo":"PLU","dpto":"Ayacucho","prov":"Lucanas","dist":"Lucanas","lat":-14.6,"lon":-74.2,"elev":3354,"activa":True},
    {"codigo":"115017","nombre":"Pauza","tipo":"CO","dpto":"Ayacucho","prov":"Paucar","dist":"Del Sara Sara Pausa","lat":-15.3,"lon":-73.3,"elev":2477,"activa":True},
    {"codigo":"114023","nombre":"Puquio","tipo":"CO","dpto":"Ayacucho","prov":"Lucanas","dist":"Puquio","lat":-14.7,"lon":-74.133,"elev":3195,"activa":True},
    {"codigo":"100127","nombre":"San Pedro de Cachi","tipo":"CO","dpto":"Ayacucho","prov":"Huamanga","dist":"Santiago de Pischa","lat":-13.1,"lon":-74.4,"elev":2990,"activa":True},
    {"codigo":"113100","nombre":"Vilcashuaman","tipo":"CO","dpto":"Ayacucho","prov":"Vilcas Huaman","dist":"Vilcas Huaman","lat":-13.667,"lon":-73.95,"elev":3450,"activa":True},

    # ── CAJAMARCA ─────────────────────────────────────────────────────────────
    {"codigo":"107018","nombre":"Asuncion","tipo":"CO","dpto":"Cajamarca","prov":"Cajamarca","dist":"Asuncion","lat":-7.3,"lon":-78.5,"elev":2270,"activa":True},
    {"codigo":"107028","nombre":"Augusto Weberbauer","tipo":"CO","dpto":"Cajamarca","prov":"Cajamarca","dist":"Cajamarca","lat":-7.168,"lon":-78.491,"elev":2682,"activa":True},
    {"codigo":"100015","nombre":"Bambamarca","tipo":"CO","dpto":"Cajamarca","prov":"Hualgayoc","dist":"Bambamarca","lat":-6.683,"lon":-78.517,"elev":2532,"activa":True},
    {"codigo":"107068","nombre":"Cachachi","tipo":"PLU","dpto":"Cajamarca","prov":"Cajabamba","dist":"Cachachi","lat":-7.5,"lon":-78.3,"elev":3203,"activa":True},
    {"codigo":"107008","nombre":"Cajabamba","tipo":"CO","dpto":"Cajamarca","prov":"Cajabamba","dist":"Cajabamba","lat":-7.6,"lon":-78.1,"elev":2625,"activa":True},
    {"codigo":"000501","nombre":"Cajamarca","tipo":"CP","dpto":"Cajamarca","prov":"Cajamarca","dist":"Cajamarca","lat":-7.15,"lon":-78.5,"elev":2682,"activa":True},
    {"codigo":"106010","nombre":"Celendin","tipo":"CO","dpto":"Cajamarca","prov":"Celendin","dist":"Celendin","lat":-6.867,"lon":-78.15,"elev":2625,"activa":True},
    {"codigo":"106022","nombre":"Chancay Baños","tipo":"CO","dpto":"Cajamarca","prov":"Santa Cruz","dist":"Chancaybaños","lat":-6.6,"lon":-78.9,"elev":1677,"activa":True},
    {"codigo":"107058","nombre":"Chilete","tipo":"PLU","dpto":"Cajamarca","prov":"Contumaza","dist":"Chilete","lat":-7.2,"lon":-78.8,"elev":848,"activa":True},
    {"codigo":"105065","nombre":"Chontali","tipo":"CO","dpto":"Cajamarca","prov":"Jaen","dist":"Chontali","lat":-5.6,"lon":-79.1,"elev":1627,"activa":True},
    {"codigo":"106034","nombre":"Chota","tipo":"CP","dpto":"Cajamarca","prov":"Chota","dist":"Chota","lat":-6.55,"lon":-78.65,"elev":2388,"activa":True},
    {"codigo":"106084","nombre":"Chotano Lajas","tipo":"PLU","dpto":"Cajamarca","prov":"Chota","dist":"Lajas","lat":-6.6,"lon":-78.7,"elev":2163,"activa":True},
    {"codigo":"106077","nombre":"Chugur","tipo":"PLU","dpto":"Cajamarca","prov":"Hualgayoc","dist":"Chugur","lat":-6.7,"lon":-78.7,"elev":2757,"activa":True},
    {"codigo":"106058","nombre":"Cochabamba","tipo":"CO","dpto":"Cajamarca","prov":"Chota","dist":"Cochabamba","lat":-6.5,"lon":-78.9,"elev":1653,"activa":True},
    {"codigo":"107052","nombre":"Contumaza","tipo":"CO","dpto":"Cajamarca","prov":"Contumaza","dist":"Contumaza","lat":-7.367,"lon":-78.917,"elev":2650,"activa":True},
    {"codigo":"100037","nombre":"Cospan","tipo":"CO","dpto":"Cajamarca","prov":"Cajamarca","dist":"Cospan","lat":-7.4,"lon":-78.5,"elev":2423,"activa":True},
    {"codigo":"106057","nombre":"Cutervo","tipo":"CO","dpto":"Cajamarca","prov":"Cutervo","dist":"Cutervo","lat":-6.367,"lon":-78.817,"elev":2640,"activa":True},
    {"codigo":"105057","nombre":"El Limon","tipo":"CO","dpto":"Cajamarca","prov":"Jaen","dist":"Pomahuaca","lat":-5.9,"lon":-79.3,"elev":1110,"activa":True},
    {"codigo":"107002","nombre":"Granja Porcon","tipo":"CO","dpto":"Cajamarca","prov":"Cajamarca","dist":"Cajamarca","lat":-7.0,"lon":-78.6,"elev":3149,"activa":True},
    {"codigo":"106065","nombre":"Hacienda Pucara","tipo":"PLU","dpto":"Cajamarca","prov":"Jaen","dist":"Pucara","lat":-6.0,"lon":-79.1,"elev":1062,"activa":True},
    {"codigo":"106054","nombre":"Huambos","tipo":"CO","dpto":"Cajamarca","prov":"Chota","dist":"Huambos","lat":-6.5,"lon":-79.0,"elev":2263,"activa":True},
    {"codigo":"105067","nombre":"Jaen","tipo":"CP","dpto":"Cajamarca","prov":"Jaen","dist":"Jaen","lat":-5.7,"lon":-78.8,"elev":729,"activa":True},
    {"codigo":"105062","nombre":"La Cascarilla","tipo":"CO","dpto":"Cajamarca","prov":"Jaen","dist":"Jaen","lat":-5.7,"lon":-78.9,"elev":1991,"activa":True},
    {"codigo":"107093","nombre":"La Encañada","tipo":"CO","dpto":"Cajamarca","prov":"Cajamarca","dist":"Encañada","lat":-7.1,"lon":-78.3,"elev":2980,"activa":True},
    {"codigo":"107055","nombre":"Lives","tipo":"PLU","dpto":"Cajamarca","prov":"San Miguel","dist":"Union Agua Blanca","lat":-7.1,"lon":-79.0,"elev":1931,"activa":True},
    {"codigo":"106053","nombre":"Llama","tipo":"CO","dpto":"Cajamarca","prov":"Chota","dist":"Llama","lat":-6.5,"lon":-79.1,"elev":2096,"activa":True},
    {"codigo":"106019","nombre":"Llapa","tipo":"CO","dpto":"Cajamarca","prov":"San Miguel","dist":"Llapa","lat":-7.0,"lon":-78.8,"elev":2932,"activa":True},
    {"codigo":"107017","nombre":"Magdalena","tipo":"CO","dpto":"Cajamarca","prov":"Cajamarca","dist":"Magdalena","lat":-7.3,"lon":-78.7,"elev":1307,"activa":True},
    {"codigo":"107037","nombre":"Namora","tipo":"CO","dpto":"Cajamarca","prov":"Cajamarca","dist":"Namora","lat":-7.2,"lon":-78.3,"elev":2744,"activa":True},
    {"codigo":"100092","nombre":"Niepos","tipo":"CO","dpto":"Cajamarca","prov":"San Miguel","dist":"Niepos","lat":-6.9,"lon":-79.1,"elev":2424,"activa":True},
    {"codigo":"100113","nombre":"Quebrada Shugar","tipo":"PLU","dpto":"Cajamarca","prov":"Hualgayoc","dist":"Bambamarca","lat":-6.7,"lon":-78.5,"elev":3293,"activa":True},
    {"codigo":"106067","nombre":"Querocotillo","tipo":"PLU","dpto":"Cajamarca","prov":"Cutervo","dist":"Querocotillo","lat":-6.3,"lon":-79.0,"elev":1970,"activa":True},
    {"codigo":"106039","nombre":"Quilcate","tipo":"CO","dpto":"Cajamarca","prov":"San Miguel","dist":"Catilluc","lat":-6.8,"lon":-78.7,"elev":3082,"activa":True},
    {"codigo":"105025","nombre":"Sallique","tipo":"CO","dpto":"Cajamarca","prov":"Jaen","dist":"Sallique","lat":-5.7,"lon":-79.3,"elev":1750,"activa":True},
    {"codigo":"107057","nombre":"San Benito","tipo":"CO","dpto":"Cajamarca","prov":"Contumaza","dist":"San Benito","lat":-7.4,"lon":-78.9,"elev":1317,"activa":True},
    {"codigo":"000509","nombre":"San Ignacio","tipo":"CO","dpto":"Cajamarca","prov":"San Ignacio","dist":"San Ignacio","lat":-5.133,"lon":-79.0,"elev":1325,"activa":True},
    {"codigo":"107005","nombre":"San Juan","tipo":"CO","dpto":"Cajamarca","prov":"Cajamarca","dist":"San Juan","lat":-7.3,"lon":-78.5,"elev":2228,"activa":True},
    {"codigo":"107006","nombre":"San Marcos","tipo":"CO","dpto":"Cajamarca","prov":"San Marcos","dist":"Pedro Galvez","lat":-7.317,"lon":-78.167,"elev":2262,"activa":True},
    {"codigo":"106038","nombre":"San Miguel","tipo":"CO","dpto":"Cajamarca","prov":"San Miguel","dist":"San Miguel","lat":-7.0,"lon":-78.9,"elev":2658,"activa":True},
    {"codigo":"107036","nombre":"San Pablo","tipo":"CO","dpto":"Cajamarca","prov":"San Pablo","dist":"San Pablo","lat":-7.117,"lon":-78.833,"elev":2340,"activa":True},
    {"codigo":"106056","nombre":"Santa Cruz","tipo":"CO","dpto":"Cajamarca","prov":"Santa Cruz","dist":"Santa Cruz","lat":-6.65,"lon":-78.983,"elev":2038,"activa":True},
    {"codigo":"105056","nombre":"Tabaconas","tipo":"CO","dpto":"Cajamarca","prov":"San Ignacio","dist":"Tabaconas","lat":-5.3,"lon":-79.3,"elev":1605,"activa":True},
    {"codigo":"106061","nombre":"Tocmoche","tipo":"CO","dpto":"Cajamarca","prov":"Chota","dist":"Tocmoche","lat":-6.4,"lon":-79.4,"elev":1435,"activa":True},
    {"codigo":"106068","nombre":"Udima","tipo":"CO","dpto":"Cajamarca","prov":"Santa Cruz","dist":"Catache","lat":-6.8,"lon":-79.1,"elev":2466,"activa":True},

    # ── CALLAO ────────────────────────────────────────────────────────────────
    {"codigo":"112043","nombre":"Hipolito Unanue","tipo":"CO","dpto":"Callao","prov":"Callao","dist":"La Perla","lat":-12.1,"lon":-77.1,"elev":23,"activa":True},
    {"codigo":"100064","nombre":"Isla Palomino","tipo":"PLU","dpto":"Callao","prov":"Callao","dist":"La Punta","lat":-12.1,"lon":-77.2,"elev":60,"activa":True},

    # ── CUSCO ─────────────────────────────────────────────────────────────────
    {"codigo":"113038","nombre":"Acomayo","tipo":"CO","dpto":"Cusco","prov":"Acomayo","dist":"Acomayo","lat":-13.9,"lon":-71.7,"elev":3160,"activa":True},
    {"codigo":"113035","nombre":"Anta Ancachuro","tipo":"CO","dpto":"Cusco","prov":"Anta","dist":"Zurite","lat":-13.5,"lon":-72.2,"elev":3340,"activa":True},
    {"codigo":"001208","nombre":"Calca","tipo":"PLU","dpto":"Cusco","prov":"Calca","dist":"Calca","lat":-13.333,"lon":-71.967,"elev":2928,"activa":True},
    {"codigo":"113122","nombre":"Caycay","tipo":"CO","dpto":"Cusco","prov":"Paucartambo","dist":"Caicay","lat":-13.6,"lon":-71.7,"elev":3150,"activa":True},
    {"codigo":"113041","nombre":"Ccatcca","tipo":"CO","dpto":"Cusco","prov":"Quispicanchi","dist":"Ccatca","lat":-13.6,"lon":-71.6,"elev":3729,"activa":True},
    {"codigo":"100030","nombre":"Chontachaca","tipo":"CO","dpto":"Cusco","prov":"Paucartambo","dist":"Kosñipata","lat":-13.0,"lon":-71.5,"elev":982,"activa":True},
    {"codigo":"113116","nombre":"Colquepata","tipo":"CO","dpto":"Cusco","prov":"Pauc","dist":"Artambo Colquepata","lat":-13.4,"lon":-71.7,"elev":3729,"activa":True},
    {"codigo":"001201","nombre":"Cusco","tipo":"CP","dpto":"Cusco","prov":"Cusco","dist":"Cusco","lat":-13.533,"lon":-71.967,"elev":3399,"activa":True},
    {"codigo":"100044","nombre":"Granja Kcayra","tipo":"CO","dpto":"Cusco","prov":"Cusco","dist":"San Jeronimo","lat":-13.55,"lon":-71.883,"elev":3219,"activa":True},
    {"codigo":"113030","nombre":"Huyro","tipo":"PLU","dpto":"Cusco","prov":"La Convencion","dist":"Huayopata","lat":-13.1,"lon":-72.5,"elev":2326,"activa":True},
    {"codigo":"001206","nombre":"Machu Picchu","tipo":"CP","dpto":"Cusco","prov":"Urubamba","dist":"Machu Picchu","lat":-13.167,"lon":-72.533,"elev":2400,"activa":True},
    {"codigo":"113037","nombre":"Paruro","tipo":"CO","dpto":"Cusco","prov":"Paruro","dist":"Paruro","lat":-13.8,"lon":-71.8,"elev":3084,"activa":True},
    {"codigo":"100101","nombre":"Pisac","tipo":"CO","dpto":"Cusco","prov":"Calca","dist":"Pisac","lat":-13.417,"lon":-71.85,"elev":2975,"activa":True},
    {"codigo":"114046","nombre":"Pomacanchi","tipo":"CO","dpto":"Cusco","prov":"Acomayo","dist":"Pomacanchi","lat":-14.0,"lon":-71.6,"elev":3200,"activa":True},
    {"codigo":"112154","nombre":"Quebrada Yanatile","tipo":"CO","dpto":"Cusco","prov":"Calca","dist":"Yanatile","lat":-12.7,"lon":-72.3,"elev":1050,"activa":True},
    {"codigo":"112036","nombre":"Quillabamba","tipo":"CO","dpto":"Cusco","prov":"La Convencion","dist":"Santa Ana","lat":-12.85,"lon":-72.7,"elev":1050,"activa":True},
    {"codigo":"100114","nombre":"Quincemil","tipo":"CO","dpto":"Cusco","prov":"Quispicanchi","dist":"Camanti","lat":-13.2,"lon":-70.8,"elev":651,"activa":True},
    {"codigo":"114030","nombre":"Santo Tomas","tipo":"CO","dpto":"Cusco","prov":"Chumbivilcas","dist":"Llusco","lat":-14.4,"lon":-72.1,"elev":3253,"activa":True},
    {"codigo":"114033","nombre":"Sicuani","tipo":"CO","dpto":"Cusco","prov":"Canchis","dist":"Sicuani","lat":-14.267,"lon":-71.233,"elev":3574,"activa":True},
    {"codigo":"113039","nombre":"Urcos","tipo":"PLU","dpto":"Cusco","prov":"Quispicanchi","dist":"Urcos","lat":-13.7,"lon":-71.6,"elev":3666,"activa":True},
    {"codigo":"001207","nombre":"Urubamba","tipo":"CO","dpto":"Cusco","prov":"Urubamba","dist":"Urubamba","lat":-13.317,"lon":-72.117,"elev":2871,"activa":True},
    {"codigo":"114032","nombre":"Yauri","tipo":"CO","dpto":"Cusco","prov":"Espinar","dist":"Espinar","lat":-14.783,"lon":-71.4,"elev":3927,"activa":True},

    # ── HUANCAVELICA ──────────────────────────────────────────────────────────
    {"codigo":"112067","nombre":"Acobamba","tipo":"CO","dpto":"Huancavelica","prov":"Acobamba","dist":"Acobamba","lat":-12.9,"lon":-74.6,"elev":3236,"activa":True},
    {"codigo":"112051","nombre":"Acostambo","tipo":"CO","dpto":"Huancavelica","prov":"Tayacaja","dist":"Acostambo","lat":-12.4,"lon":-75.1,"elev":3675,"activa":True},
    {"codigo":"113128","nombre":"Challabamba","tipo":"CO","dpto":"Huancavelica","prov":"Huaytara","dist":"Sant Iago de Chocorvos","lat":-13.8,"lon":-75.4,"elev":1800,"activa":True},
    {"codigo":"113091","nombre":"Choclococha","tipo":"PLU","dpto":"Huancavelica","prov":"Castrovi","dist":"Rreyna Santa Ana","lat":-13.2,"lon":-75.1,"elev":4547,"activa":True},
    {"codigo":"112163","nombre":"Colcabamba","tipo":"CO","dpto":"Huancavelica","prov":"Tayacaja","dist":"Colcabamba","lat":-12.4,"lon":-74.7,"elev":3055,"activa":True},
    {"codigo":"114065","nombre":"Cordova","tipo":"PLU","dpto":"Huancavelica","prov":"Huaytara","dist":"Cordova","lat":-14.0,"lon":-75.2,"elev":3225,"activa":True},
    {"codigo":"113086","nombre":"Cusicancha","tipo":"CO","dpto":"Huancavelica","prov":"Huaytara","dist":"San Antonio de Cusicancha","lat":-13.5,"lon":-75.3,"elev":3253,"activa":True},
    {"codigo":"113067","nombre":"Huachos","tipo":"CO","dpto":"Huancavelica","prov":"Castrovirreyna","dist":"Huachos","lat":-13.2,"lon":-75.5,"elev":2744,"activa":True},
    {"codigo":"112142","nombre":"Huancalpi","tipo":"CO","dpto":"Huancavelica","prov":"Huancavelica","dist":"Vilca","lat":-12.5,"lon":-75.2,"elev":3450,"activa":True},
    {"codigo":"112061","nombre":"Huancavelica","tipo":"CP","dpto":"Huancavelica","prov":"Huancavelica","dist":"Ascension","lat":-12.783,"lon":-74.967,"elev":3660,"activa":True},
    {"codigo":"112065","nombre":"Lircay","tipo":"CO","dpto":"Huancavelica","prov":"Angaraes","dist":"Lircay","lat":-12.983,"lon":-74.733,"elev":3288,"activa":True},
    {"codigo":"112012","nombre":"Pampas","tipo":"CO","dpto":"Huancavelica","prov":"Tayacaja","dist":"Pampas","lat":-12.4,"lon":-74.867,"elev":3245,"activa":True},
    {"codigo":"112060","nombre":"Pilchaca","tipo":"CO","dpto":"Huancavelica","prov":"Huancavelica","dist":"Pilchaca","lat":-12.4,"lon":-75.1,"elev":3880,"activa":True},
    {"codigo":"100120","nombre":"Salcabamba","tipo":"CO","dpto":"Huancavelica","prov":"Tayacaja","dist":"Salcabamba","lat":-12.2,"lon":-74.8,"elev":3280,"activa":True},
    {"codigo":"113082","nombre":"San Juan de Castrovirreyna","tipo":"CO","dpto":"Huancavelica","prov":"Castrovirreyna","dist":"San Juan","lat":-13.2,"lon":-75.6,"elev":1856,"activa":True},
    {"codigo":"001804","nombre":"Santa Ines","tipo":"PLU","dpto":"Huancavelica","prov":"Huaytara","dist":"Cordova","lat":-13.35,"lon":-75.2,"elev":4659,"activa":True},
    {"codigo":"113088","nombre":"Santiago de Chocorvos","tipo":"CO","dpto":"Huancavelica","prov":"Huaytara","dist":"Santiago de Chocorvos","lat":-13.8,"lon":-75.3,"elev":2700,"activa":True},
    {"codigo":"113087","nombre":"Tambo","tipo":"CO","dpto":"Huancavelica","prov":"Huaytara","dist":"Tambo","lat":-13.7,"lon":-75.3,"elev":3138,"activa":True},
    {"codigo":"113016","nombre":"Tunel Cero","tipo":"CO","dpto":"Huancavelica","prov":"Huaytara","dist":"Pilpichaca","lat":-13.3,"lon":-75.1,"elev":4498,"activa":True},

    # ── HUANUCO ───────────────────────────────────────────────────────────────
    {"codigo":"002403","nombre":"Ambo","tipo":"CO","dpto":"Huanuco","prov":"Ambo","dist":"Ambo","lat":-10.133,"lon":-76.2,"elev":2067,"activa":True},
    {"codigo":"108033","nombre":"Aucayacu","tipo":"CO","dpto":"Huanuco","prov":"Leoncio","dist":"Prado Jose Crespo y Castillo","lat":-8.9,"lon":-76.1,"elev":586,"activa":True},
    {"codigo":"100020","nombre":"Canchan","tipo":"CO","dpto":"Huanuco","prov":"Huanuco","dist":"Huanuco","lat":-9.9,"lon":-76.3,"elev":1986,"activa":True},
    {"codigo":"109020","nombre":"Carpish","tipo":"CO","dpto":"Huanuco","prov":"Huanuco","dist":"Chinc Hao","lat":-9.7,"lon":-76.1,"elev":1950,"activa":True},
    {"codigo":"109077","nombre":"Dos de Mayo","tipo":"CO","dpto":"Huanuco","prov":"Dos","dist":"De Mayo Pachas","lat":-9.7,"lon":-76.8,"elev":3442,"activa":True},
    {"codigo":"109003","nombre":"Huanuco","tipo":"CP","dpto":"Huanuco","prov":"Huanuco","dist":"Amarilis","lat":-9.933,"lon":-76.233,"elev":1894,"activa":True},
    {"codigo":"109022","nombre":"Jacas Chico","tipo":"CO","dpto":"Huanuco","prov":"Yarowilca","dist":"Jacas Chico","lat":-9.9,"lon":-76.5,"elev":3673,"activa":True},
    {"codigo":"108025","nombre":"La Divisoria","tipo":"CO","dpto":"Huanuco","prov":"Leoncio","dist":"Prado Hermilio Valdizan","lat":-9.2,"lon":-75.8,"elev":1961,"activa":True},
    {"codigo":"002404","nombre":"Llata","tipo":"CO","dpto":"Huanuco","prov":"Huamalies","dist":"Llata","lat":-9.6,"lon":-76.817,"elev":3560,"activa":True},
    {"codigo":"109032","nombre":"Puerto Inca","tipo":"CO","dpto":"Huanuco","prov":"Puerto Inca","dist":"Puerto Inca","lat":-9.4,"lon":-75.0,"elev":249,"activa":True},
    {"codigo":"110025","nombre":"San Rafael","tipo":"CO","dpto":"Huanuco","prov":"Ambo","dist":"San Rafael","lat":-10.3,"lon":-76.2,"elev":2722,"activa":True},
    {"codigo":"109027","nombre":"Tingo Maria","tipo":"CO","dpto":"Huanuco","prov":"Leoncio","dist":"Prado Rupa -rupa","lat":-9.3,"lon":-75.983,"elev":660,"activa":True},
    {"codigo":"109028","nombre":"Tulumayo","tipo":"CO","dpto":"Huanuco","prov":"Leoncio","dist":"Prado Jose Crespo y Castillo","lat":-9.1,"lon":-76.0,"elev":640,"activa":True},

    # ── ICA ───────────────────────────────────────────────────────────────────
    {"codigo":"001705","nombre":"Chincha Alta","tipo":"CO","dpto":"Ica","prov":"Chincha","dist":"Chincha Alta","lat":-13.417,"lon":-76.15,"elev":100,"activa":True},
    {"codigo":"114011","nombre":"Cipa","tipo":"CO","dpto":"Ica","prov":"Ica","dist":"San Juan Bautista","lat":-14.0,"lon":-75.8,"elev":398,"activa":True},
    {"codigo":"114018","nombre":"Copara","tipo":"CO","dpto":"Ica","prov":"Nazca","dist":"Vista Alegre","lat":-15.0,"lon":-74.9,"elev":587,"activa":True},
    {"codigo":"114007","nombre":"El Carmen","tipo":"CO","dpto":"Ica","prov":"Palpa","dist":"Santa Cruz","lat":-14.5,"lon":-75.2,"elev":570,"activa":True},
    {"codigo":"100043","nombre":"Fonagro (chincha)","tipo":"CO","dpto":"Ica","prov":"Chincha","dist":"Chincha Baja","lat":-13.5,"lon":-76.1,"elev":71,"activa":True},
    {"codigo":"114051","nombre":"Fundo Don Carlos","tipo":"CO","dpto":"Ica","prov":"Ica","dist":"La Tinguiña","lat":-14.0,"lon":-75.7,"elev":425,"activa":True},
    {"codigo":"100046","nombre":"Hacienda Bernales","tipo":"CO","dpto":"Ica","prov":"Pisco","dist":"Humay","lat":-13.7,"lon":-76.0,"elev":293,"activa":True},
    {"codigo":"113010","nombre":"Huamani","tipo":"CO","dpto":"Ica","prov":"Ica","dist":"San Jose de los Molinos","lat":-13.8,"lon":-75.6,"elev":790,"activa":True},
    {"codigo":"001701","nombre":"Ica","tipo":"CP","dpto":"Ica","prov":"Ica","dist":"Ica","lat":-14.067,"lon":-75.733,"elev":406,"activa":True},
    {"codigo":"001703","nombre":"Nazca","tipo":"CO","dpto":"Ica","prov":"Nazca","dist":"Nazca","lat":-14.833,"lon":-74.933,"elev":598,"activa":True},
    {"codigo":"114020","nombre":"Ocucaje","tipo":"CO","dpto":"Ica","prov":"Ica","dist":"Ocucaje","lat":-14.4,"lon":-75.7,"elev":311,"activa":True},
    {"codigo":"001704","nombre":"Palpa","tipo":"CO","dpto":"Ica","prov":"Palpa","dist":"Palpa","lat":-14.533,"lon":-75.183,"elev":370,"activa":True},
    {"codigo":"114066","nombre":"Pampa Blanca","tipo":"CO","dpto":"Ica","prov":"Palpa","dist":"Rio Grande","lat":-14.2,"lon":-75.1,"elev":1020,"activa":True},
    {"codigo":"001702","nombre":"Pisco","tipo":"CO","dpto":"Ica","prov":"Pisco","dist":"Pisco","lat":-13.717,"lon":-76.217,"elev":11,"activa":True},
    {"codigo":"114006","nombre":"Rio Grande","tipo":"CO","dpto":"Ica","prov":"Palpa","dist":"Rio Grande","lat":-14.5,"lon":-75.2,"elev":325,"activa":True},
    {"codigo":"114009","nombre":"San Borja","tipo":"CO","dpto":"Ica","prov":"Palpa","dist":"Palpa","lat":-14.5,"lon":-75.2,"elev":415,"activa":True},
    {"codigo":"114008","nombre":"San Camilo","tipo":"CO","dpto":"Ica","prov":"Ica","dist":"Parcona","lat":-14.1,"lon":-75.7,"elev":407,"activa":True},
    {"codigo":"113081","nombre":"San Juan de Yanac","tipo":"CO","dpto":"Ica","prov":"Chincha","dist":"San Juan de Yanac","lat":-13.2,"lon":-75.8,"elev":2513,"activa":True},
    {"codigo":"113058","nombre":"Tacama","tipo":"CO","dpto":"Ica","prov":"Ica","dist":"La Tinguiña","lat":-14.0,"lon":-75.7,"elev":429,"activa":True},

    # ── JUNIN ─────────────────────────────────────────────────────────────────
    {"codigo":"111070","nombre":"Carhuacayan","tipo":"PLU","dpto":"Junin","prov":"Yauli","dist":"Santa Barbara de Carhuacayan","lat":-11.2,"lon":-76.3,"elev":4127,"activa":True},
    {"codigo":"001008","nombre":"Chanchamayo","tipo":"CO","dpto":"Junin","prov":"Chanchamayo","dist":"San Ramon","lat":-11.067,"lon":-75.317,"elev":1350,"activa":True},
    {"codigo":"001001","nombre":"Huancayo","tipo":"CP","dpto":"Junin","prov":"Huancayo","dist":"El Tambo","lat":-12.067,"lon":-75.217,"elev":3313,"activa":True},
    {"codigo":"112056","nombre":"Huayao","tipo":"CO","dpto":"Junin","prov":"Chupaca","dist":"Huachac","lat":-12.0,"lon":-75.3,"elev":3360,"activa":True},
    {"codigo":"111097","nombre":"Ingenio","tipo":"CO","dpto":"Junin","prov":"Concepcion","dist":"Santa Rosa de Ocopa","lat":-11.9,"lon":-75.3,"elev":3390,"activa":True},
    {"codigo":"111005","nombre":"Jauja","tipo":"CO","dpto":"Junin","prov":"Jauja","dist":"Jauja","lat":-11.767,"lon":-75.5,"elev":3321,"activa":True},
    {"codigo":"111583","nombre":"Junin","tipo":"CO","dpto":"Junin","prov":"Junin","dist":"Junin","lat":-11.167,"lon":-76.0,"elev":4100,"activa":True},
    {"codigo":"111046","nombre":"La Oroya","tipo":"CO","dpto":"Junin","prov":"Yauli","dist":"Santa Rosa de Sacco","lat":-11.533,"lon":-75.9,"elev":3728,"activa":True},
    {"codigo":"112059","nombre":"Laive","tipo":"CO","dpto":"Junin","prov":"Chupaca","dist":"Yanacancha","lat":-12.3,"lon":-75.4,"elev":3860,"activa":True},
    {"codigo":"111028","nombre":"Marcapomacocha","tipo":"CO","dpto":"Junin","prov":"Yauli","dist":"Marcapomacocha","lat":-11.4,"lon":-76.3,"elev":4447,"activa":True},
    {"codigo":"001007","nombre":"Mazamari","tipo":"PLU","dpto":"Junin","prov":"Satipo","dist":"Mazamari","lat":-11.317,"lon":-74.533,"elev":763,"activa":True},
    {"codigo":"110008","nombre":"Pichanaky","tipo":"CO","dpto":"Junin","prov":"Chanchamayo","dist":"Pichanaqui","lat":-11.0,"lon":-74.8,"elev":546,"activa":True},
    {"codigo":"111039","nombre":"Puerto Ocopa","tipo":"CO","dpto":"Junin","prov":"Satipo","dist":"Rio Tambo","lat":-11.1,"lon":-74.3,"elev":690,"activa":True},
    {"codigo":"111095","nombre":"Ricran","tipo":"CO","dpto":"Junin","prov":"Jauja","dist":"Ricran","lat":-11.5,"lon":-75.5,"elev":3820,"activa":True},
    {"codigo":"100119","nombre":"Runatullo","tipo":"CO","dpto":"Junin","prov":"Concepcion","dist":"Comas","lat":-11.6,"lon":-75.1,"elev":3690,"activa":True},
    {"codigo":"112028","nombre":"San Juan de Jarpa","tipo":"CO","dpto":"Junin","prov":"Chupaca","dist":"San Juan de Jarpa","lat":-12.1,"lon":-75.4,"elev":3600,"activa":True},
    {"codigo":"112083","nombre":"Santa Ana","tipo":"CO","dpto":"Junin","prov":"Huancayo","dist":"El Tambo","lat":-12.0,"lon":-75.2,"elev":3295,"activa":True},
    {"codigo":"111038","nombre":"Satipo","tipo":"CO","dpto":"Junin","prov":"Satipo","dist":"Satipo","lat":-11.25,"lon":-74.633,"elev":585,"activa":True},
    {"codigo":"112184","nombre":"Shullcas","tipo":"PLU","dpto":"Junin","prov":"Huancayo","dist":"El Tambo","lat":-12.0,"lon":-75.2,"elev":3750,"activa":True},
    {"codigo":"111029","nombre":"Tarma","tipo":"CO","dpto":"Junin","prov":"Tarma","dist":"Tarma","lat":-11.417,"lon":-75.683,"elev":3050,"activa":True},
    {"codigo":"112037","nombre":"Viques","tipo":"CO","dpto":"Junin","prov":"Huancayo","dist":"Viques","lat":-12.2,"lon":-75.2,"elev":3186,"activa":True},
    {"codigo":"111076","nombre":"Yantac","tipo":"PLU","dpto":"Junin","prov":"Yauli","dist":"Marcapomacocha","lat":-11.3,"lon":-76.4,"elev":4617,"activa":True},

    # ── LA LIBERTAD ───────────────────────────────────────────────────────────
    {"codigo":"108045","nombre":"Cachicadan","tipo":"CO","dpto":"La Libertad","prov":"Santiago de Chuco","dist":"Cachicadan","lat":-8.1,"lon":-78.1,"elev":2900,"activa":True},
    {"codigo":"107054","nombre":"Callancas","tipo":"CO","dpto":"La Libertad","prov":"Otuzco","dist":"Charat","lat":-7.8,"lon":-78.5,"elev":1501,"activa":True},
    {"codigo":"107049","nombre":"Cartavio","tipo":"CO","dpto":"La Libertad","prov":"Ascope","dist":"Santiago de Cao","lat":-7.9,"lon":-79.2,"elev":58,"activa":True},
    {"codigo":"000412","nombre":"Chao","tipo":"PLU","dpto":"La Libertad","prov":"Viru","dist":"Chao","lat":-8.567,"lon":-78.75,"elev":85,"activa":True},
    {"codigo":"000408","nombre":"Charat","tipo":"PLU","dpto":"La Libertad","prov":"Otuzco","dist":"Charat","lat":-7.917,"lon":-78.617,"elev":1700,"activa":True},
    {"codigo":"107045","nombre":"Chepen","tipo":"PLU","dpto":"La Libertad","prov":"Chepen","dist":"Chepen","lat":-7.2,"lon":-79.4,"elev":114,"activa":True},
    {"codigo":"100028","nombre":"Cherrepe","tipo":"CO","dpto":"La Libertad","prov":"Chepen","dist":"Pacanga","lat":-7.1,"lon":-79.6,"elev":51,"activa":True},
    {"codigo":"108048","nombre":"Huacamarcanga","tipo":"PLU","dpto":"La Libertad","prov":"Santiago de Chuco","dist":"Quiruvilca","lat":-8.1,"lon":-78.3,"elev":3883,"activa":True},
    {"codigo":"107009","nombre":"Huamachuco","tipo":"CP","dpto":"La Libertad","prov":"Sanchez Carrion","dist":"Huamachuco","lat":-7.817,"lon":-78.05,"elev":3163,"activa":True},
    {"codigo":"108043","nombre":"Julcan","tipo":"PLU","dpto":"La Libertad","prov":"Julcan","dist":"Julcan","lat":-8.042,"lon":-78.5,"elev":3445,"activa":True},
    {"codigo":"000407","nombre":"Mollepata","tipo":"PLU","dpto":"La Libertad","prov":"Otuzco","dist":"Mollepata","lat":-7.95,"lon":-78.6,"elev":2700,"activa":True},
    {"codigo":"108046","nombre":"Mollepata","tipo":"PLU","dpto":"La Libertad","prov":"Santiago de Chuco","dist":"Mollepata","lat":-8.2,"lon":-78.0,"elev":2708,"activa":True},
    {"codigo":"000401","nombre":"Otuzco","tipo":"CO","dpto":"La Libertad","prov":"Otuzco","dist":"Otuzco","lat":-7.897,"lon":-78.575,"elev":2641,"activa":True},
    {"codigo":"108044","nombre":"Quiruvilca","tipo":"PLU","dpto":"La Libertad","prov":"Santiago de Chuco","dist":"Quiruvilca","lat":-7.983,"lon":-78.317,"elev":3965,"activa":True},
    {"codigo":"108001","nombre":"Salpo","tipo":"CO","dpto":"La Libertad","prov":"Otuzco","dist":"Salpo","lat":-8.017,"lon":-78.583,"elev":3030,"activa":True},
    {"codigo":"100153","nombre":"San Jose","tipo":"PLU","dpto":"La Libertad","prov":"Pacasmayo","dist":"San Jose","lat":-7.4,"lon":-79.5,"elev":100,"activa":True},
    {"codigo":"000404","nombre":"Santiago de Chuco","tipo":"CO","dpto":"La Libertad","prov":"Santiago de Chuco","dist":"Santiago de Chuco","lat":-8.142,"lon":-78.167,"elev":3060,"activa":True},
    {"codigo":"000410","nombre":"Secsecpampa","tipo":"PLU","dpto":"La Libertad","prov":"Otuzco","dist":"Agallpampa","lat":-7.967,"lon":-78.483,"elev":3350,"activa":True},
    {"codigo":"000411","nombre":"Shorey","tipo":"CO","dpto":"La Libertad","prov":"Santiago de Chuco","dist":"Sitabamba","lat":-8.217,"lon":-78.017,"elev":3280,"activa":True},
    {"codigo":"107059","nombre":"Sinsicap","tipo":"PLU","dpto":"La Libertad","prov":"Otuzco","dist":"Sinsicap","lat":-7.9,"lon":-78.8,"elev":2315,"activa":True},
    {"codigo":"100136","nombre":"Talla (guadalupe)","tipo":"CO","dpto":"La Libertad","prov":"Pacasmayo","dist":"Guadalupe","lat":-7.3,"lon":-79.4,"elev":117,"activa":True},
    {"codigo":"108068","nombre":"Trujillo","tipo":"CP","dpto":"La Libertad","prov":"Trujillo","dist":"Laredo","lat":-8.083,"lon":-79.033,"elev":15,"activa":True},

    # ── LAMBAYEQUE ────────────────────────────────────────────────────────────
    {"codigo":"106042","nombre":"Cayalti","tipo":"CO","dpto":"Lambayeque","prov":"Chiclayo","dist":"Cayalti","lat":-6.9,"lon":-79.583,"elev":55,"activa":True},
    {"codigo":"105122","nombre":"Cerro de Arena","tipo":"PLU","dpto":"Lambayeque","prov":"Lambayeque","dist":"Olmos","lat":-5.9,"lon":-80.2,"elev":59,"activa":True},
    {"codigo":"000702","nombre":"Chiclayo","tipo":"CP","dpto":"Lambayeque","prov":"Chiclayo","dist":"Chiclayo","lat":-6.817,"lon":-79.833,"elev":27,"activa":True},
    {"codigo":"106060","nombre":"Cueva Blanca","tipo":"PLU","dpto":"Lambayeque","prov":"Ferreñafe","dist":"Incahuasi","lat":-6.1,"lon":-79.4,"elev":3300,"activa":True},
    {"codigo":"106052","nombre":"El Espinal","tipo":"CO","dpto":"Lambayeque","prov":"Chiclayo","dist":"Oyotun","lat":-6.8,"lon":-79.2,"elev":371,"activa":True},
    {"codigo":"106045","nombre":"Ferreñafe","tipo":"CO","dpto":"Lambayeque","prov":"Chiclayo","dist":"Picsi","lat":-6.633,"lon":-79.783,"elev":55,"activa":True},
    {"codigo":"106037","nombre":"Incahuasi","tipo":"CO","dpto":"Lambayeque","prov":"Ferreñafe","dist":"Incahuasi","lat":-6.233,"lon":-79.3,"elev":3078,"activa":True},
    {"codigo":"106047","nombre":"Jayanca (La Viña)","tipo":"CO","dpto":"Lambayeque","prov":"Lambayeque","dist":"Jayanca","lat":-6.3,"lon":-79.8,"elev":78,"activa":True},
    {"codigo":"106108","nombre":"Lambayeque","tipo":"CO","dpto":"Lambayeque","prov":"Lambayeque","dist":"Lambayeque","lat":-6.7,"lon":-79.9,"elev":18,"activa":True},
    {"codigo":"106021","nombre":"Morrope","tipo":"CO","dpto":"Lambayeque","prov":"Lambayeque","dist":"Morrope","lat":-6.5,"lon":-80.0,"elev":18,"activa":True},
    {"codigo":"105054","nombre":"Olmos","tipo":"CO","dpto":"Lambayeque","prov":"Lambayeque","dist":"Olmos","lat":-5.8,"lon":-79.9,"elev":115,"activa":True},
    {"codigo":"106109","nombre":"Oyotun","tipo":"CO","dpto":"Lambayeque","prov":"Chiclayo","dist":"Oyotun","lat":-6.9,"lon":-79.3,"elev":187,"activa":True},
    {"codigo":"105076","nombre":"Pasabar","tipo":"CO","dpto":"Lambayeque","prov":"Lambayeque","dist":"Olmos","lat":-5.8,"lon":-79.8,"elev":124,"activa":True},
    {"codigo":"106106","nombre":"Pucala","tipo":"CO","dpto":"Lambayeque","prov":"Chiclayo","dist":"Patapo","lat":-6.8,"lon":-79.6,"elev":85,"activa":True},
    {"codigo":"106071","nombre":"Puchaca","tipo":"CO","dpto":"Lambayeque","prov":"Ferreñafe","dist":"Incahuasi","lat":-6.4,"lon":-79.5,"elev":800,"activa":True},
    {"codigo":"106046","nombre":"Reque","tipo":"CO","dpto":"Lambayeque","prov":"Chiclayo","dist":"Eten","lat":-6.9,"lon":-79.8,"elev":13,"activa":True},
    {"codigo":"106036","nombre":"Sipan","tipo":"CO","dpto":"Lambayeque","prov":"Chiclayo","dist":"Saña","lat":-6.8,"lon":-79.6,"elev":87,"activa":True},

    # ── LIMA ──────────────────────────────────────────────────────────────────
    {"codigo":"111004","nombre":"Alcantarilla","tipo":"CO","dpto":"Lima","prov":"Huaura","dist":"Huaura","lat":-11.1,"lon":-77.6,"elev":131,"activa":True},
    {"codigo":"112038","nombre":"Alexander Von Humboldt","tipo":"CO","dpto":"Lima","prov":"Lima","dist":"La Molina","lat":-12.083,"lon":-76.95,"elev":238,"activa":True},
    {"codigo":"110057","nombre":"Andajes","tipo":"PLU","dpto":"Lima","prov":"Oyon","dist":"Andajes","lat":-10.8,"lon":-76.9,"elev":3950,"activa":True},
    {"codigo":"112124","nombre":"Antioquia","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Antioquia","lat":-12.1,"lon":-76.5,"elev":1839,"activa":True},
    {"codigo":"111057","nombre":"Arahuay","tipo":"PLU","dpto":"Lima","prov":"Canta","dist":"Arahuay","lat":-11.617,"lon":-76.833,"elev":2800,"activa":True},
    {"codigo":"111077","nombre":"Autisha","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"San Antonio","lat":-11.7,"lon":-76.6,"elev":2181,"activa":True},
    {"codigo":"112128","nombre":"Ayaviri","tipo":"PLU","dpto":"Lima","prov":"Yauyos","dist":"Ayaviri","lat":-12.4,"lon":-76.1,"elev":3224,"activa":True},
    {"codigo":"000905","nombre":"Barranca","tipo":"CO","dpto":"Lima","prov":"Barranca","dist":"Barranca","lat":-10.767,"lon":-77.767,"elev":50,"activa":True},
    {"codigo":"110019","nombre":"Cajatambo","tipo":"CO","dpto":"Lima","prov":"Cajatambo","dist":"Cajatambo","lat":-10.5,"lon":-77.0,"elev":3432,"activa":True},
    {"codigo":"110017","nombre":"Camay","tipo":"CO","dpto":"Lima","prov":"Hua","dist":"Ura Vegueta","lat":-10.9,"lon":-77.6,"elev":59,"activa":True},
    {"codigo":"112171","nombre":"Campo de Marte","tipo":"CO","dpto":"Lima","prov":"Lima","dist":"Jesus Maria","lat":-12.1,"lon":-77.0,"elev":123,"activa":True},
    {"codigo":"111058","nombre":"Canchacalla","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"San Mateo de Otao","lat":-11.8,"lon":-76.5,"elev":2400,"activa":True},
    {"codigo":"111026","nombre":"Canta","tipo":"CO","dpto":"Lima","prov":"Canta","dist":"Canta","lat":-11.5,"lon":-76.6,"elev":2818,"activa":True},
    {"codigo":"111091","nombre":"Carampoma","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Carampoma","lat":-11.7,"lon":-76.5,"elev":3424,"activa":True},
    {"codigo":"112133","nombre":"Carania","tipo":"CO","dpto":"Lima","prov":"Yauyos","dist":"Carania","lat":-12.3,"lon":-75.9,"elev":3820,"activa":True},
    {"codigo":"111114","nombre":"Casapalca","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Chicla","lat":-11.6,"lon":-76.2,"elev":4233,"activa":True},
    {"codigo":"113006","nombre":"Cañete","tipo":"CO","dpto":"Lima","prov":"Cañete","dist":"Imperial","lat":-13.083,"lon":-76.367,"elev":155,"activa":True},
    {"codigo":"111060","nombre":"Chosica","tipo":"PLU","dpto":"Lima","prov":"Lima","dist":"Lurigancho","lat":-11.933,"lon":-76.7,"elev":855,"activa":True},
    {"codigo":"100031","nombre":"Cochaquillo","tipo":"PLU","dpto":"Lima","prov":"Oyon","dist":"Oyon","lat":-10.8,"lon":-76.7,"elev":4575,"activa":True},
    {"codigo":"111025","nombre":"Donoso","tipo":"CO","dpto":"Lima","prov":"Huaral","dist":"Huaral","lat":-11.5,"lon":-77.2,"elev":127,"activa":True},
    {"codigo":"110041","nombre":"Gorgor","tipo":"PLU","dpto":"Lima","prov":"Cajatambo","dist":"Gorgor","lat":-10.6,"lon":-77.0,"elev":3025,"activa":True},
    {"codigo":"000904","nombre":"Huacho","tipo":"CO","dpto":"Lima","prov":"Huaura","dist":"Huacho","lat":-11.1,"lon":-77.6,"elev":5,"activa":True},
    {"codigo":"111085","nombre":"Huamantanga","tipo":"PLU","dpto":"Lima","prov":"Canta","dist":"Huamantanga","lat":-11.5,"lon":-76.8,"elev":3392,"activa":True},
    {"codigo":"112080","nombre":"Huancata","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Sangallaya","lat":-12.2,"lon":-76.2,"elev":2684,"activa":True},
    {"codigo":"112134","nombre":"Huangascar","tipo":"CO","dpto":"Lima","prov":"Yauyos","dist":"Huangascar","lat":-12.85,"lon":-75.783,"elev":2160,"activa":True},
    {"codigo":"111021","nombre":"Huaral","tipo":"PLU","dpto":"Lima","prov":"Huaral","dist":"Huaral","lat":-11.5,"lon":-77.2,"elev":182,"activa":True},
    {"codigo":"111047","nombre":"Huarangal","tipo":"CO","dpto":"Lima","prov":"Lima","dist":"Carabayllo","lat":-11.8,"lon":-77.0,"elev":404,"activa":True},
    {"codigo":"112055","nombre":"Huarochiri","tipo":"CO","dpto":"Lima","prov":"Huarochiri","dist":"Huarochiri","lat":-12.1,"lon":-76.2,"elev":3120,"activa":True},
    {"codigo":"111089","nombre":"Huaros","tipo":"PLU","dpto":"Lima","prov":"Canta","dist":"Huaros","lat":-11.4,"lon":-76.6,"elev":3569,"activa":True},
    {"codigo":"111022","nombre":"Huayan","tipo":"CO","dpto":"Lima","prov":"Huaral","dist":"Huaral","lat":-11.5,"lon":-77.1,"elev":346,"activa":True},
    {"codigo":"112127","nombre":"Huañec","tipo":"PLU","dpto":"Lima","prov":"Yauyos","dist":"Huañec","lat":-12.3,"lon":-76.1,"elev":3200,"activa":True},
    {"codigo":"111017","nombre":"Humaya","tipo":"PLU","dpto":"Lima","prov":"Huaura","dist":"Huaura","lat":-11.1,"lon":-77.4,"elev":310,"activa":True},
    {"codigo":"100061","nombre":"Isla Don Martin","tipo":"CO","dpto":"Lima","prov":"Huaura","dist":"Vegueta","lat":-11.0,"lon":-77.7,"elev":8,"activa":True},
    {"codigo":"112054","nombre":"La Capilla 2","tipo":"CO","dpto":"Lima","prov":"Cañete","dist":"Calango","lat":-12.5,"lon":-76.5,"elev":442,"activa":True},
    {"codigo":"111088","nombre":"Lachaqui","tipo":"PLU","dpto":"Lima","prov":"Canta","dist":"Lachaqui","lat":-11.6,"lon":-76.6,"elev":3670,"activa":True},
    {"codigo":"112082","nombre":"Langa","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Langa","lat":-12.1,"lon":-76.4,"elev":2863,"activa":True},
    {"codigo":"000901","nombre":"Lima CORPAC","tipo":"CP","dpto":"Lima","prov":"Lima","dist":"Miraflores","lat":-12.017,"lon":-77.117,"elev":13,"activa":True},
    {"codigo":"111018","nombre":"Lomas de Lachay","tipo":"CO","dpto":"Lima","prov":"Huaura","dist":"Huacho","lat":-11.4,"lon":-77.4,"elev":384,"activa":True},
    {"codigo":"112053","nombre":"Manchay Bajo","tipo":"PLU","dpto":"Lima","prov":"Lima","dist":"Pachacamac","lat":-12.2,"lon":-76.9,"elev":164,"activa":True},
    {"codigo":"111027","nombre":"Matucana","tipo":"CO","dpto":"Lima","prov":"Huarochiri","dist":"Matucana","lat":-11.833,"lon":-76.383,"elev":2378,"activa":True},
    {"codigo":"111144","nombre":"Milloc","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Carampoma","lat":-11.6,"lon":-76.3,"elev":4384,"activa":True},
    {"codigo":"112044","nombre":"Modelo","tipo":"CO","dpto":"Lima","prov":"Lima","dist":"Jesus Maria","lat":-12.1,"lon":-77.0,"elev":123,"activa":True},
    {"codigo":"110020","nombre":"Oyon","tipo":"CO","dpto":"Lima","prov":"Oyon","dist":"Oyon","lat":-10.7,"lon":-76.8,"elev":3667,"activa":True},
    {"codigo":"112058","nombre":"Pacaran","tipo":"CO","dpto":"Lima","prov":"Cañete","dist":"Pacaran","lat":-12.9,"lon":-76.1,"elev":684,"activa":True},
    {"codigo":"110056","nombre":"Paccho","tipo":"PLU","dpto":"Lima","prov":"Huaura","dist":"Paccho","lat":-11.0,"lon":-76.9,"elev":3250,"activa":True},
    {"codigo":"111084","nombre":"Pachamachay","tipo":"PLU","dpto":"Lima","prov":"Huaura","dist":"Leoncio Prado","lat":-11.1,"lon":-76.9,"elev":3175,"activa":True},
    {"codigo":"111083","nombre":"Pallac","tipo":"PLU","dpto":"Lima","prov":"Huaral","dist":"Atavillos Bajo","lat":-11.3,"lon":-76.8,"elev":2367,"activa":True},
    {"codigo":"110053","nombre":"Pampa Libre","tipo":"CO","dpto":"Lima","prov":"Huaura","dist":"Checras","lat":-10.9,"lon":-77.0,"elev":1756,"activa":True},
    {"codigo":"112159","nombre":"Pantanos de Villa","tipo":"CO","dpto":"Lima","prov":"Lima","dist":"Chorrillos","lat":-12.2,"lon":-77.0,"elev":4,"activa":True},
    {"codigo":"111067","nombre":"Pariacancha","tipo":"PLU","dpto":"Lima","prov":"Canta","dist":"Huaros","lat":-11.4,"lon":-76.5,"elev":3842,"activa":True},
    {"codigo":"110063","nombre":"Parquin","tipo":"PLU","dpto":"Lima","prov":"Huaura","dist":"Santa Leonor","lat":-11.0,"lon":-76.7,"elev":3571,"activa":True},
    {"codigo":"110021","nombre":"Picoy","tipo":"CO","dpto":"Lima","prov":"Huaura","dist":"Santa Leonor","lat":-10.9,"lon":-76.7,"elev":2920,"activa":True},
    {"codigo":"111087","nombre":"Pirca","tipo":"PLU","dpto":"Lima","prov":"Huaral","dist":"Atavillos Alto","lat":-11.2,"lon":-76.7,"elev":3342,"activa":True},
    {"codigo":"111061","nombre":"Rio Blanco","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Chicla","lat":-11.7,"lon":-76.3,"elev":3503,"activa":True},
    {"codigo":"000909","nombre":"San Jose","tipo":"PLU","dpto":"Lima","prov":"Huaura","dist":"Santa Maria","lat":-11.083,"lon":-77.55,"elev":6,"activa":True},
    {"codigo":"112126","nombre":"San Lazaro de Escomarca","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Langa","lat":-12.2,"lon":-76.4,"elev":3758,"activa":True},
    {"codigo":"112081","nombre":"San Pedro de Pilas","tipo":"PLU","dpto":"Lima","prov":"Yauyos","dist":"San Pedro de Pilas","lat":-12.5,"lon":-76.2,"elev":2707,"activa":True},
    {"codigo":"111081","nombre":"Santa Cruz","tipo":"PLU","dpto":"Lima","prov":"Huaral","dist":"Santa Cruz de Andamarca","lat":-11.2,"lon":-76.6,"elev":3583,"activa":True},
    {"codigo":"111086","nombre":"Santa Eulalia","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Santa Eulalia","lat":-11.9,"lon":-76.7,"elev":970,"activa":True},
    {"codigo":"111020","nombre":"Santa Rosa","tipo":"CO","dpto":"Lima","prov":"Huaura","dist":"Sayan","lat":-11.2,"lon":-77.4,"elev":380,"activa":True},
    {"codigo":"111092","nombre":"Santiago de Tuna","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Santiago de Tuna","lat":-12.0,"lon":-76.5,"elev":2924,"activa":True},
    {"codigo":"111062","nombre":"Sheque","tipo":"PLU","dpto":"Lima","prov":"Huarochiri","dist":"Carampoma","lat":-11.7,"lon":-76.5,"elev":3188,"activa":True},
    {"codigo":"110012","nombre":"Surasaca","tipo":"CO","dpto":"Lima","prov":"Oyon","dist":"Oyon","lat":-10.5,"lon":-76.8,"elev":4546,"activa":True},
    {"codigo":"112130","nombre":"Tanta","tipo":"PLU","dpto":"Lima","prov":"Yauyos","dist":"Tanta","lat":-12.1,"lon":-76.0,"elev":4323,"activa":True},
    {"codigo":"111163","nombre":"UNJF Sanchez Carrion - Huacho","tipo":"PLU","dpto":"Lima","prov":"Huaura","dist":"Huacho","lat":-11.1,"lon":-77.6,"elev":45,"activa":True},
    {"codigo":"112135","nombre":"Vilca","tipo":"CO","dpto":"Lima","prov":"Yauyos","dist":"Huancaya","lat":-12.1,"lon":-75.8,"elev":3832,"activa":True},
    {"codigo":"112096","nombre":"Yauricocha","tipo":"PLU","dpto":"Lima","prov":"Yauyos","dist":"Alis","lat":-12.3,"lon":-75.7,"elev":4560,"activa":True},

    # ── LORETO ────────────────────────────────────────────────────────────────
    {"codigo":"103057","nombre":"Amazonas","tipo":"CP","dpto":"Loreto","prov":"Maynas","dist":"Iquitos","lat":-3.767,"lon":-73.3,"elev":126,"activa":True},
    {"codigo":"104067","nombre":"Bagazan","tipo":"PLU","dpto":"Loreto","prov":"Loreto","dist":"Nauta","lat":-4.8,"lon":-73.6,"elev":250,"activa":True},
    {"codigo":"103012","nombre":"Bellavista","tipo":"PLU","dpto":"Loreto","prov":"Maynas","dist":"Mazan","lat":-3.5,"lon":-73.6,"elev":105,"activa":True},
    {"codigo":"105090","nombre":"Bretaña","tipo":"PLU","dpto":"Loreto","prov":"Requena","dist":"Puinahua","lat":-5.3,"lon":-74.4,"elev":200,"activa":True},
    {"codigo":"103031","nombre":"Caballococha","tipo":"CO","dpto":"Loreto","prov":"Maris","dist":"Cal Ramon Castilla Ramon Castilla","lat":-3.9,"lon":-70.5,"elev":107,"activa":True},
    {"codigo":"100034","nombre":"Contamana","tipo":"CO","dpto":"Loreto","prov":"Ucayali","dist":"Contamana","lat":-7.35,"lon":-74.917,"elev":150,"activa":True},
    {"codigo":"105092","nombre":"Flor de Punga","tipo":"PLU","dpto":"Loreto","prov":"Requena","dist":"Puinahua","lat":-5.4,"lon":-74.2,"elev":135,"activa":True},
    {"codigo":"103024","nombre":"Francisco Orellana","tipo":"PLU","dpto":"Loreto","prov":"Maynas","dist":"Las Amazonas","lat":-3.4,"lon":-72.8,"elev":137,"activa":True},
    {"codigo":"104071","nombre":"Genaro Herrera","tipo":"CO","dpto":"Loreto","prov":"Requena","dist":"Jenaro Herrera","lat":-4.9,"lon":-73.6,"elev":126,"activa":True},
    {"codigo":"100070","nombre":"Juancito","tipo":"CO","dpto":"Loreto","prov":"Ucayali","dist":"Sarayacu","lat":-6.0,"lon":-74.9,"elev":124,"activa":True},
    {"codigo":"103014","nombre":"La Libertad","tipo":"PLU","dpto":"Loreto","prov":"Maynas","dist":"Mazan","lat":-3.5,"lon":-73.2,"elev":100,"activa":True},
    {"codigo":"103009","nombre":"Maniti","tipo":"PLU","dpto":"Loreto","prov":"Maynas","dist":"Indiana","lat":-3.5,"lon":-72.8,"elev":125,"activa":True},
    {"codigo":"103044","nombre":"Mazan","tipo":"CO","dpto":"Loreto","prov":"Maynas","dist":"Mazan","lat":-3.5,"lon":-73.1,"elev":103,"activa":True},
    {"codigo":"104056","nombre":"Nauta","tipo":"CO","dpto":"Loreto","prov":"Loreto","dist":"Nauta","lat":-4.5,"lon":-73.567,"elev":122,"activa":True},
    {"codigo":"103054","nombre":"Pebas","tipo":"CO","dpto":"Loreto","prov":"Mariscal","dist":"Ramon Castilla Pebas","lat":-3.3,"lon":-71.9,"elev":106,"activa":True},
    {"codigo":"103046","nombre":"Puerto Almendra","tipo":"CO","dpto":"Loreto","prov":"Maynas","dist":"San Juan Bautista","lat":-3.8,"lon":-73.3,"elev":146,"activa":True},
    {"codigo":"103015","nombre":"Punchana","tipo":"PLU","dpto":"Loreto","prov":"Maynas","dist":"Iquitos","lat":-3.7,"lon":-73.3,"elev":116,"activa":True},
    {"codigo":"105095","nombre":"Requena","tipo":"CO","dpto":"Loreto","prov":"Requena","dist":"Requena","lat":-5.05,"lon":-73.85,"elev":129,"activa":True},
    {"codigo":"100128","nombre":"San Ramon","tipo":"CO","dpto":"Loreto","prov":"Alto","dist":"Ama Zonas Yurimaguas","lat":-5.9,"lon":-76.1,"elev":120,"activa":True},
    {"codigo":"103052","nombre":"San Roque","tipo":"CO","dpto":"Loreto","prov":"Maynas","dist":"Iquitos","lat":-3.8,"lon":-73.3,"elev":98,"activa":True},
    {"codigo":"102009","nombre":"Santa Clotilde","tipo":"CO","dpto":"Loreto","prov":"Maynas","dist":"Napo","lat":-2.5,"lon":-73.7,"elev":150,"activa":True},
    {"codigo":"103013","nombre":"Santa Cruz","tipo":"PLU","dpto":"Loreto","prov":"Maynas","dist":"Mazan","lat":-3.5,"lon":-73.1,"elev":122,"activa":True},
    {"codigo":"103030","nombre":"Santa Maria de Nanay","tipo":"PLU","dpto":"Loreto","prov":"Maynas","dist":"Mazan","lat":-3.9,"lon":-73.7,"elev":120,"activa":True},
    {"codigo":"104065","nombre":"Santa Rita de Castilla","tipo":"PLU","dpto":"Loreto","prov":"Loreto","dist":"Parinari","lat":-4.6,"lon":-74.4,"elev":100,"activa":True},
    {"codigo":"100132","nombre":"Shanusi","tipo":"PLU","dpto":"Loreto","prov":"Alto Amazonas","dist":"Yurimaguas","lat":-6.1,"lon":-76.3,"elev":160,"activa":True},
    {"codigo":"103049","nombre":"Tamshiyacu","tipo":"CO","dpto":"Loreto","prov":"Maynas","dist":"Fernando Lores","lat":-4.0,"lon":-73.2,"elev":98,"activa":True},
    {"codigo":"103011","nombre":"Timicurillo","tipo":"PLU","dpto":"Loreto","prov":"Maynas","dist":"Indiana","lat":-3.5,"lon":-73.1,"elev":106,"activa":True},
    {"codigo":"002104","nombre":"Yurimaguas","tipo":"CO","dpto":"Loreto","prov":"Alto Amazonas","dist":"Yurimaguas","lat":-5.883,"lon":-76.117,"elev":184,"activa":True},
    {"codigo":"103048","nombre":"Zungarococha","tipo":"CO","dpto":"Loreto","prov":"Maynas","dist":"Iquitos","lat":-3.8,"lon":-73.3,"elev":91,"activa":True},

    # ── MADRE DE DIOS ─────────────────────────────────────────────────────────
    {"codigo":"111044","nombre":"Iberia","tipo":"PLU","dpto":"Madre de Dios","prov":"Tahuamanu","dist":"Iberia","lat":-11.417,"lon":-69.483,"elev":297,"activa":True},
    {"codigo":"002203","nombre":"Iñapari","tipo":"CO","dpto":"Madre de Dios","prov":"Tahuamanu","dist":"Iñapari","lat":-10.983,"lon":-69.583,"elev":280,"activa":True},
    {"codigo":"113042","nombre":"Pilcopata","tipo":"CO","dpto":"Madre de Dios","prov":"Manu","dist":"Madre de Dios","lat":-13.1,"lon":-71.0,"elev":900,"activa":True},
    {"codigo":"100109","nombre":"Puerto Maldonado","tipo":"CP","dpto":"Madre de Dios","prov":"Tambopata","dist":"Tambopata","lat":-12.6,"lon":-69.183,"elev":260,"activa":True},

    # ── MOQUEGUA ──────────────────────────────────────────────────────────────
    {"codigo":"116051","nombre":"Calacoa","tipo":"PLU","dpto":"Moquegua","prov":"Mariscal Nieto","dist":"San Cristobal","lat":-16.7,"lon":-70.7,"elev":3260,"activa":True},
    {"codigo":"116025","nombre":"Carumas","tipo":"CO","dpto":"Moquegua","prov":"Mariscal Nieto","dist":"Carumas","lat":-16.8,"lon":-70.7,"elev":2976,"activa":True},
    {"codigo":"100059","nombre":"Ichuña","tipo":"CO","dpto":"Moquegua","prov":"General Sanchez Cerro","dist":"Ichuña","lat":-16.1,"lon":-70.6,"elev":3800,"activa":True},
    {"codigo":"117007","nombre":"Ilo","tipo":"CO","dpto":"Moquegua","prov":"Ilo","dist":"El Algarrobal","lat":-17.633,"lon":-71.35,"elev":65,"activa":True},
    {"codigo":"117002","nombre":"Moquegua","tipo":"CO","dpto":"Moquegua","prov":"Mariscal Nieto","dist":"Moquegua","lat":-17.183,"lon":-70.933,"elev":1410,"activa":True},
    {"codigo":"116023","nombre":"Omate","tipo":"CO","dpto":"Moquegua","prov":"General Sanchez Cerro","dist":"Omate","lat":-16.667,"lon":-70.983,"elev":2070,"activa":True},
    {"codigo":"117008","nombre":"Punta Coles","tipo":"PLU","dpto":"Moquegua","prov":"Ilo","dist":"Ilo","lat":-17.7,"lon":-71.4,"elev":25,"activa":True},
    {"codigo":"116021","nombre":"Puquina","tipo":"CO","dpto":"Moquegua","prov":"General Sanchez Cerro","dist":"Puquina","lat":-16.6,"lon":-71.2,"elev":3284,"activa":True},
    {"codigo":"116049","nombre":"Quinistaquillas","tipo":"CO","dpto":"Moquegua","prov":"Mariscal Nieto","dist":"Carumas","lat":-16.8,"lon":-70.9,"elev":1590,"activa":True},
    {"codigo":"100142","nombre":"Ubinas","tipo":"CO","dpto":"Moquegua","prov":"General Sanchez Cerro","dist":"Ubinas","lat":-16.383,"lon":-70.9,"elev":3380,"activa":True},
    {"codigo":"100150","nombre":"Yacango","tipo":"CO","dpto":"Moquegua","prov":"Mariscal Nieto","dist":"Torata","lat":-17.1,"lon":-70.9,"elev":2091,"activa":True},

    # ── PASCO ─────────────────────────────────────────────────────────────────
    {"codigo":"110037","nombre":"Cerro de Pasco","tipo":"CO","dpto":"Pasco","prov":"Pasco","dist":"Chaupimarca","lat":-10.683,"lon":-76.267,"elev":4338,"activa":True},
    {"codigo":"110028","nombre":"Oxapampa","tipo":"CO","dpto":"Pasco","prov":"Oxapampa","dist":"Oxapampa","lat":-10.583,"lon":-75.383,"elev":1814,"activa":True},
    {"codigo":"110027","nombre":"Pozuzo","tipo":"CO","dpto":"Pasco","prov":"Oxapampa","dist":"Pozuzo","lat":-10.1,"lon":-75.6,"elev":1000,"activa":True},
    {"codigo":"002503","nombre":"San Martin de Pangoa","tipo":"PLU","dpto":"Pasco","prov":"Oxapampa","dist":"Huancabamba","lat":-10.45,"lon":-75.617,"elev":2080,"activa":True},
    {"codigo":"110007","nombre":"Yanahuanca","tipo":"CO","dpto":"Pasco","prov":"Daniel Alcides Carrion","dist":"Yanahuanca","lat":-10.5,"lon":-76.5,"elev":3150,"activa":True},

    # ── PIURA ─────────────────────────────────────────────────────────────────
    {"codigo":"104058","nombre":"Ayabaca","tipo":"CO","dpto":"Piura","prov":"Ayabaca","dist":"Ayabaca","lat":-4.633,"lon":-79.717,"elev":2715,"activa":True},
    {"codigo":"104088","nombre":"Bayobar","tipo":"PLU","dpto":"Piura","prov":"Paita","dist":"Amotape","lat":-4.8,"lon":-81.0,"elev":35,"activa":True},
    {"codigo":"105012","nombre":"Bernal","tipo":"CO","dpto":"Piura","prov":"Sechura","dist":"Bernal","lat":-5.5,"lon":-80.7,"elev":14,"activa":True},
    {"codigo":"105016","nombre":"Chalaco","tipo":"CO","dpto":"Piura","prov":"Morropon","dist":"Chalaco","lat":-5.0,"lon":-79.8,"elev":2296,"activa":True},
    {"codigo":"104091","nombre":"Chilaco","tipo":"CO","dpto":"Piura","prov":"Sullana","dist":"Sullana","lat":-4.7,"lon":-80.5,"elev":100,"activa":True},
    {"codigo":"105070","nombre":"Chulucanas","tipo":"CO","dpto":"Piura","prov":"Morropon","dist":"Chulucanas","lat":-5.1,"lon":-80.167,"elev":92,"activa":True},
    {"codigo":"105105","nombre":"Chusis","tipo":"CO","dpto":"Piura","prov":"Sechura","dist":"Sechura","lat":-5.5,"lon":-80.8,"elev":8,"activa":True},
    {"codigo":"104092","nombre":"Curvan","tipo":"PLU","dpto":"Piura","prov":"Piura","dist":"Tambo Grande","lat":-5.0,"lon":-80.3,"elev":61,"activa":True},
    {"codigo":"104077","nombre":"El Tablazo","tipo":"PLU","dpto":"Piura","prov":"Piura","dist":"Tambo Grande","lat":-4.9,"lon":-80.5,"elev":106,"activa":True},
    {"codigo":"105015","nombre":"Hacienda Bigote","tipo":"PLU","dpto":"Piura","prov":"Morropon","dist":"San Juan de Bigote","lat":-5.3,"lon":-79.8,"elev":198,"activa":True},
    {"codigo":"105024","nombre":"Hacienda Shumaya","tipo":"PLU","dpto":"Piura","prov":"Huancabamba","dist":"Sondor","lat":-5.4,"lon":-79.4,"elev":1991,"activa":True},
    {"codigo":"105055","nombre":"Huancabamba","tipo":"CO","dpto":"Piura","prov":"Huancabamba","dist":"Huancabamba","lat":-5.233,"lon":-79.45,"elev":1957,"activa":True},
    {"codigo":"105064","nombre":"Huarmaca","tipo":"CO","dpto":"Piura","prov":"Huancabamba","dist":"Huarmaca","lat":-5.6,"lon":-79.5,"elev":2178,"activa":True},
    {"codigo":"000608","nombre":"La Esperanza","tipo":"CO","dpto":"Piura","prov":"Piura","dist":"Tambo Grande","lat":-4.917,"lon":-80.333,"elev":102,"activa":True},
    {"codigo":"104090","nombre":"La Esperanza","tipo":"CO","dpto":"Piura","prov":"Paita","dist":"Colan","lat":-4.9,"lon":-81.1,"elev":7,"activa":True},
    {"codigo":"104016","nombre":"Lancones","tipo":"CO","dpto":"Piura","prov":"Sullana","dist":"Lancones","lat":-4.6,"lon":-80.5,"elev":133,"activa":True},
    {"codigo":"104079","nombre":"Mallares","tipo":"CO","dpto":"Piura","prov":"Sullana","dist":"Marcavelica","lat":-4.9,"lon":-80.7,"elev":44,"activa":True},
    {"codigo":"000607","nombre":"Mancora","tipo":"PLU","dpto":"Piura","prov":"Talara","dist":"Mancora","lat":-4.1,"lon":-81.033,"elev":5,"activa":True},
    {"codigo":"105100","nombre":"Miraflores","tipo":"CO","dpto":"Piura","prov":"Piura","dist":"Castilla","lat":-5.2,"lon":-80.6,"elev":34,"activa":True},
    {"codigo":"107027","nombre":"Montegrande","tipo":"CO","dpto":"Piura","prov":"Piura","dist":"La Arena","lat":-5.4,"lon":-80.7,"elev":13,"activa":True},
    {"codigo":"105106","nombre":"Morropon","tipo":"CO","dpto":"Piura","prov":"Morropon","dist":"Morropon","lat":-5.2,"lon":-80.0,"elev":128,"activa":True},
    {"codigo":"104023","nombre":"Pacaypampa","tipo":"CO","dpto":"Piura","prov":"Ayabaca","dist":"Pacaipampa","lat":-5.0,"lon":-79.7,"elev":2028,"activa":True},
    {"codigo":"104014","nombre":"Pananga","tipo":"PLU","dpto":"Piura","prov":"Sullana","dist":"Marcavelica","lat":-4.5,"lon":-80.7,"elev":360,"activa":True},
    {"codigo":"105001","nombre":"Piura","tipo":"CP","dpto":"Piura","prov":"Piura","dist":"Castilla","lat":-5.183,"lon":-80.617,"elev":29,"activa":True},
    {"codigo":"100105","nombre":"Porculla","tipo":"PLU","dpto":"Piura","prov":"Huancabamba","dist":"Huarmaca","lat":-5.8,"lon":-79.5,"elev":2142,"activa":True},
    {"codigo":"105063","nombre":"San Miguel","tipo":"CO","dpto":"Piura","prov":"Piura","dist":"Catacaos","lat":-5.2,"lon":-80.7,"elev":24,"activa":True},
    {"codigo":"100126","nombre":"San Pedro","tipo":"PLU","dpto":"Piura","prov":"Morropon","dist":"Morropon","lat":-5.1,"lon":-80.0,"elev":240,"activa":True},
    {"codigo":"105014","nombre":"Santo Domingo","tipo":"CO","dpto":"Piura","prov":"Morropon","dist":"Santo Domingo","lat":-5.0,"lon":-79.9,"elev":1475,"activa":True},
    {"codigo":"104019","nombre":"Sapillica","tipo":"PLU","dpto":"Piura","prov":"Ayabaca","dist":"Sapillica","lat":-4.8,"lon":-80.0,"elev":1466,"activa":True},
    {"codigo":"104059","nombre":"Sausal de Culucan","tipo":"CO","dpto":"Piura","prov":"Ayabaca","dist":"Ayabaca","lat":-4.8,"lon":-79.8,"elev":997,"activa":True},
    {"codigo":"105022","nombre":"Sondorillo","tipo":"CO","dpto":"Piura","prov":"Huancabamba","dist":"Sondorillo","lat":-5.3,"lon":-79.4,"elev":1917,"activa":True},
    {"codigo":"000606","nombre":"Sullana","tipo":"CO","dpto":"Piura","prov":"Sullana","dist":"Sullana","lat":-4.9,"lon":-80.683,"elev":52,"activa":True},
    {"codigo":"000605","nombre":"Talara","tipo":"CO","dpto":"Piura","prov":"Talara","dist":"Pariñas","lat":-4.583,"lon":-81.267,"elev":8,"activa":True},
    {"codigo":"104078","nombre":"Tejedores","tipo":"PLU","dpto":"Piura","prov":"Piura","dist":"Tambo Grande","lat":-4.8,"lon":-80.2,"elev":211,"activa":True},
    {"codigo":"105023","nombre":"Tuluce","tipo":"PLU","dpto":"Piura","prov":"Huancabamba","dist":"Sondor","lat":-5.5,"lon":-79.3,"elev":2233,"activa":True},
    {"codigo":"105013","nombre":"Virrey","tipo":"PLU","dpto":"Piura","prov":"Morropon","dist":"La Matanza","lat":-5.5,"lon":-80.0,"elev":206,"activa":True},

    # ── PUNO ──────────────────────────────────────────────────────────────────
    {"codigo":"114050","nombre":"Ananea","tipo":"CO","dpto":"Puno","prov":"San Antonio de Putina","dist":"Ananea","lat":-14.683,"lon":-69.533,"elev":4640,"activa":True},
    {"codigo":"115035","nombre":"Arapa","tipo":"CO","dpto":"Puno","prov":"Azangaro","dist":"Arapa","lat":-15.1,"lon":-70.1,"elev":3830,"activa":True},
    {"codigo":"114038","nombre":"Ayaviri","tipo":"CO","dpto":"Puno","prov":"Melgar","dist":"Ayaviri","lat":-14.9,"lon":-70.6,"elev":3928,"activa":True},
    {"codigo":"114041","nombre":"Azangaro","tipo":"CO","dpto":"Puno","prov":"Azangaro","dist":"Azangaro","lat":-14.9,"lon":-70.183,"elev":3859,"activa":True},
    {"codigo":"115033","nombre":"Cabanillas","tipo":"CO","dpto":"Puno","prov":"San Roman","dist":"Cabanillas","lat":-15.2,"lon":-70.0,"elev":3920,"activa":True},
    {"codigo":"100021","nombre":"Capachica","tipo":"CO","dpto":"Puno","prov":"Puno","dist":"Capachica","lat":-15.6,"lon":-69.8,"elev":3828,"activa":True},
    {"codigo":"117041","nombre":"Capazo","tipo":"CO","dpto":"Puno","prov":"El Collao","dist":"Capaso","lat":-17.2,"lon":-69.7,"elev":4530,"activa":True},
    {"codigo":"114035","nombre":"Chuquibambilla","tipo":"CO","dpto":"Puno","prov":"Melgar","dist":"Umachiri","lat":-14.8,"lon":-70.7,"elev":3971,"activa":True},
    {"codigo":"115053","nombre":"Cojata","tipo":"CO","dpto":"Puno","prov":"Huancane","dist":"Cojata","lat":-15.0,"lon":-69.4,"elev":4344,"activa":True},
    {"codigo":"114058","nombre":"Crucero","tipo":"CO","dpto":"Puno","prov":"Carabaya","dist":"Crucero","lat":-14.4,"lon":-70.0,"elev":4183,"activa":True},
    {"codigo":"115044","nombre":"Crucero Alto","tipo":"CO","dpto":"Puno","prov":"Lampa","dist":"Santa Lucia","lat":-15.8,"lon":-70.9,"elev":4521,"activa":True},
    {"codigo":"114096","nombre":"Cuyo Cuyo","tipo":"CO","dpto":"Puno","prov":"Sandia","dist":"Cuyocuyo","lat":-14.5,"lon":-69.5,"elev":3414,"activa":True},
    {"codigo":"116060","nombre":"Desaguadero","tipo":"CO","dpto":"Puno","prov":"Chucuito","dist":"Desaguadero","lat":-16.567,"lon":-69.033,"elev":3808,"activa":True},
    {"codigo":"115037","nombre":"Huancane","tipo":"CO","dpto":"Puno","prov":"Huancane","dist":"Huan Cane","lat":-15.2,"lon":-69.8,"elev":3890,"activa":True},
    {"codigo":"115038","nombre":"Huaraya Moho","tipo":"CO","dpto":"Puno","prov":"Moho","dist":"Moho","lat":-15.4,"lon":-69.5,"elev":3890,"activa":True},
    {"codigo":"116027","nombre":"Ilave","tipo":"CO","dpto":"Puno","prov":"El Collao","dist":"Ilave","lat":-16.083,"lon":-69.65,"elev":3861,"activa":True},
    {"codigo":"100065","nombre":"Isla Soto","tipo":"CO","dpto":"Puno","prov":"Moho","dist":"Conima","lat":-15.6,"lon":-69.5,"elev":3815,"activa":True},
    {"codigo":"116009","nombre":"Isla Suana","tipo":"CO","dpto":"Puno","prov":"Yunguyo","dist":"Ollaraya","lat":-16.3,"lon":-68.9,"elev":3830,"activa":True},
    {"codigo":"115049","nombre":"Isla Taquile","tipo":"CO","dpto":"Puno","prov":"Puno","dist":"Capachica","lat":-15.7,"lon":-69.7,"elev":3850,"activa":True},
    {"codigo":"116061","nombre":"Juli","tipo":"CO","dpto":"Puno","prov":"Chucuito","dist":"Juli","lat":-16.2,"lon":-69.45,"elev":3820,"activa":True},
    {"codigo":"115138","nombre":"Juliaca","tipo":"CO","dpto":"Puno","prov":"San Roman","dist":"Juliaca","lat":-15.467,"lon":-70.183,"elev":3825,"activa":True},
    {"codigo":"100081","nombre":"Lampa","tipo":"CO","dpto":"Puno","prov":"Lampa","dist":"Lampa","lat":-15.367,"lon":-70.367,"elev":3892,"activa":True},
    {"codigo":"116033","nombre":"Laraqueri","tipo":"CO","dpto":"Puno","prov":"Puno","dist":"Pichacani","lat":-16.2,"lon":-70.1,"elev":3900,"activa":True},
    {"codigo":"114049","nombre":"Limbani","tipo":"CO","dpto":"Puno","prov":"Sandia","dist":"Limbani","lat":-14.2,"lon":-69.7,"elev":3320,"activa":True},
    {"codigo":"114034","nombre":"Llally","tipo":"CO","dpto":"Puno","prov":"Melgar","dist":"Llalli","lat":-14.9,"lon":-70.9,"elev":3980,"activa":True},
    {"codigo":"114039","nombre":"Macusani","tipo":"CO","dpto":"Puno","prov":"Carabaya","dist":"Macusani","lat":-14.067,"lon":-70.433,"elev":4316,"activa":True},
    {"codigo":"116026","nombre":"Mazo Cruz","tipo":"CO","dpto":"Puno","prov":"El Collao","dist":"Santa Rosa","lat":-16.7,"lon":-69.7,"elev":4003,"activa":True},
    {"codigo":"115051","nombre":"Mañazo","tipo":"CO","dpto":"Puno","prov":"Puno","dist":"Mañazo","lat":-14.8,"lon":-70.1,"elev":3920,"activa":True},
    {"codigo":"114042","nombre":"Muñani","tipo":"CO","dpto":"Puno","prov":"Azangaro","dist":"Muñani","lat":-14.8,"lon":-70.0,"elev":3948,"activa":True},
    {"codigo":"113044","nombre":"Ollachea","tipo":"CO","dpto":"Puno","prov":"Carabaya","dist":"Ollachea","lat":-13.8,"lon":-70.5,"elev":2850,"activa":True},
    {"codigo":"115027","nombre":"Pampahuta","tipo":"CO","dpto":"Puno","prov":"Lampa","dist":"Paratia","lat":-15.5,"lon":-70.7,"elev":4400,"activa":True},
    {"codigo":"116029","nombre":"Pizacoma","tipo":"CO","dpto":"Puno","prov":"Chucuito","dist":"Pisacoma","lat":-16.9,"lon":-69.4,"elev":3930,"activa":True},
    {"codigo":"114040","nombre":"Progreso","tipo":"CO","dpto":"Puno","prov":"Azangaro","dist":"Asillo","lat":-14.7,"lon":-70.0,"elev":3980,"activa":True},
    {"codigo":"115046","nombre":"Pucara","tipo":"CO","dpto":"Puno","prov":"Lampa","dist":"Pucara","lat":-15.0,"lon":-70.4,"elev":3900,"activa":True},
    {"codigo":"100110","nombre":"Puno","tipo":"CP","dpto":"Puno","prov":"Puno","dist":"Puno","lat":-15.817,"lon":-70.017,"elev":3812,"activa":True},
    {"codigo":"114093","nombre":"Putina","tipo":"CO","dpto":"Puno","prov":"San Antonio de Putina","dist":"Putina","lat":-14.9,"lon":-69.9,"elev":3878,"activa":True},
    {"codigo":"115052","nombre":"Rincon de la Cruz","tipo":"CO","dpto":"Puno","prov":"Puno","dist":"Acora","lat":-16.0,"lon":-69.8,"elev":3935,"activa":True},
    {"codigo":"113119","nombre":"San Gaban","tipo":"CO","dpto":"Puno","prov":"Carabaya","dist":"San Gaban","lat":-13.4,"lon":-70.4,"elev":635,"activa":True},
    {"codigo":"115140","nombre":"Santa Lucia","tipo":"CO","dpto":"Puno","prov":"Lampa","dist":"Santa Lucia","lat":-15.7,"lon":-70.6,"elev":4034,"activa":True},
    {"codigo":"114047","nombre":"Santa Rosa","tipo":"CO","dpto":"Puno","prov":"Melgar","dist":"Santa Rosa","lat":-14.6,"lon":-70.8,"elev":3986,"activa":True},
    {"codigo":"116030","nombre":"Tahuaco - Yunguyo","tipo":"CO","dpto":"Puno","prov":"Yunguyo","dist":"Yunguyo","lat":-16.3,"lon":-69.1,"elev":3891,"activa":True},
    {"codigo":"114043","nombre":"Tambopata","tipo":"CO","dpto":"Puno","prov":"Sandia","dist":"San Juan del Oro","lat":-15.2,"lon":-69.2,"elev":1385,"activa":True},
    {"codigo":"115047","nombre":"Taraco","tipo":"CO","dpto":"Puno","prov":"Huancane","dist":"Taraco","lat":-15.3,"lon":-70.0,"elev":3849,"activa":True},

    # ── SAN MARTIN ────────────────────────────────────────────────────────────
    {"codigo":"106092","nombre":"Alao","tipo":"CO","dpto":"San Martin","prov":"El Dorado","dist":"San Martin","lat":-6.5,"lon":-76.7,"elev":420,"activa":True},
    {"codigo":"107012","nombre":"Bellavista","tipo":"CO","dpto":"San Martin","prov":"Bellavista","dist":"Bellavista","lat":-7.1,"lon":-76.6,"elev":247,"activa":True},
    {"codigo":"100019","nombre":"Campanilla","tipo":"CO","dpto":"San Martin","prov":"Mariscal Caceres","dist":"Campanilla","lat":-7.4,"lon":-76.7,"elev":290,"activa":True},
    {"codigo":"106101","nombre":"Chazuta","tipo":"PLU","dpto":"San Martin","prov":"San Martin","dist":"Chazuta","lat":-6.6,"lon":-76.1,"elev":160,"activa":True},
    {"codigo":"106094","nombre":"Cuñumbuque","tipo":"PLU","dpto":"San Martin","prov":"Lamas","dist":"Zapatero","lat":-6.5,"lon":-76.5,"elev":280,"activa":True},
    {"codigo":"107069","nombre":"Dos de Mayo (j. Olaya)","tipo":"CO","dpto":"San Martin","prov":"Bellavista","dist":"Alto Biavo","lat":-7.4,"lon":-76.4,"elev":290,"activa":True},
    {"codigo":"106040","nombre":"El Porvenir","tipo":"CO","dpto":"San Martin","prov":"San Martin","dist":"Juan Guerra","lat":-6.6,"lon":-76.3,"elev":230,"activa":True},
    {"codigo":"106088","nombre":"Jepelacio","tipo":"PLU","dpto":"San Martin","prov":"Moyobamba","dist":"Jepelacio","lat":-6.1,"lon":-76.9,"elev":1000,"activa":True},
    {"codigo":"002005","nombre":"Juanjui","tipo":"CO","dpto":"San Martin","prov":"Mariscal Caceres","dist":"Juanjui","lat":-7.183,"lon":-76.733,"elev":350,"activa":True},
    {"codigo":"107013","nombre":"La Union","tipo":"CO","dpto":"San Martin","prov":"Bellavista","dist":"Bajo Biavo","lat":-7.2,"lon":-76.5,"elev":240,"activa":True},
    {"codigo":"106016","nombre":"Lamas","tipo":"CO","dpto":"San Martin","prov":"Lamas","dist":"Lamas","lat":-6.4,"lon":-76.5,"elev":790,"activa":True},
    {"codigo":"106014","nombre":"Moyobamba","tipo":"CO","dpto":"San Martin","prov":"Moyobamba","dist":"Moyobamba","lat":-6.033,"lon":-76.983,"elev":860,"activa":True},
    {"codigo":"105103","nombre":"Naranjillo","tipo":"CO","dpto":"San Martin","prov":"Rioja","dist":"Nueva Cajamarca","lat":-5.8,"lon":-77.4,"elev":890,"activa":True},
    {"codigo":"106018","nombre":"Navarro","tipo":"CO","dpto":"San Martin","prov":"San Martin","dist":"Chipurana","lat":-6.4,"lon":-75.8,"elev":130,"activa":True},
    {"codigo":"107089","nombre":"Nuevo Lima","tipo":"PLU","dpto":"San Martin","prov":"Bellavista","dist":"Bajo Biavo","lat":-7.1,"lon":-76.5,"elev":260,"activa":True},
    {"codigo":"107010","nombre":"Pachiza","tipo":"CO","dpto":"San Martin","prov":"Mariscal Caceres","dist":"Pachiza","lat":-7.3,"lon":-76.8,"elev":380,"activa":True},
    {"codigo":"106112","nombre":"Pelejo","tipo":"PLU","dpto":"San Martin","prov":"San Martin","dist":"El Porvenir","lat":-6.2,"lon":-75.8,"elev":100,"activa":True},
    {"codigo":"106095","nombre":"Picota","tipo":"PLU","dpto":"San Martin","prov":"Picota","dist":"Picota","lat":-6.9,"lon":-76.3,"elev":200,"activa":True},
    {"codigo":"106098","nombre":"Pilluana","tipo":"PLU","dpto":"San Martin","prov":"Picota","dist":"Pilluana","lat":-6.8,"lon":-76.3,"elev":195,"activa":True},
    {"codigo":"100104","nombre":"Pongo de Caynarachi","tipo":"CO","dpto":"San Martin","prov":"Lamas","dist":"Caynarachi","lat":-6.3,"lon":-76.3,"elev":230,"activa":True},
    {"codigo":"106110","nombre":"Pucallpa - Huimbayoc","tipo":"PLU","dpto":"San Martin","prov":"San Martin","dist":"Huimbayoc","lat":-6.5,"lon":-75.8,"elev":120,"activa":True},
    {"codigo":"106013","nombre":"Rioja","tipo":"CO","dpto":"San Martin","prov":"Rioja","dist":"Rioja","lat":-6.067,"lon":-77.117,"elev":840,"activa":True},
    {"codigo":"106096","nombre":"San Antonio","tipo":"CO","dpto":"San Martin","prov":"San Martin","dist":"San Antonio","lat":-6.4,"lon":-76.4,"elev":430,"activa":True},
    {"codigo":"106091","nombre":"San Pablo","tipo":"CO","dpto":"San Martin","prov":"Bellavista","dist":"San Pablo","lat":-6.8,"lon":-76.6,"elev":270,"activa":True},
    {"codigo":"106032","nombre":"Saposoa","tipo":"CO","dpto":"San Martin","prov":"Huallaga","dist":"Saposoa","lat":-6.9,"lon":-76.8,"elev":320,"activa":True},
    {"codigo":"106017","nombre":"Sauce","tipo":"CO","dpto":"San Martin","prov":"San Martin","dist":"Sauce","lat":-6.7,"lon":-76.2,"elev":580,"activa":True},
    {"codigo":"106083","nombre":"Soritor","tipo":"CO","dpto":"San Martin","prov":"Moyobamba","dist":"Soritor","lat":-6.1,"lon":-77.1,"elev":890,"activa":True},
    {"codigo":"106043","nombre":"Tabalosos","tipo":"CO","dpto":"San Martin","prov":"Lamas","dist":"Tabalosos","lat":-6.4,"lon":-76.6,"elev":480,"activa":True},
    {"codigo":"100137","nombre":"Tananta","tipo":"CO","dpto":"San Martin","prov":"Tocache","dist":"Polvora","lat":-8.1,"lon":-76.6,"elev":480,"activa":True},
    {"codigo":"002001","nombre":"Tarapoto","tipo":"CP","dpto":"San Martin","prov":"San Martin","dist":"Tarapoto","lat":-6.5,"lon":-76.367,"elev":356,"activa":True},
    {"codigo":"100139","nombre":"Tocache","tipo":"CO","dpto":"San Martin","prov":"Tocache","dist":"Tocache","lat":-8.183,"lon":-76.517,"elev":575,"activa":True},

    # ── TACNA ─────────────────────────────────────────────────────────────────
    {"codigo":"117054","nombre":"Aricota","tipo":"CO","dpto":"Tacna","prov":"Candarave","dist":"Quilahuani","lat":-17.3,"lon":-70.2,"elev":2825,"activa":True},
    {"codigo":"100007","nombre":"Bocatoma","tipo":"CO","dpto":"Tacna","prov":"Tacna","dist":"Palca","lat":-17.6,"lon":-69.6,"elev":4260,"activa":True},
    {"codigo":"117030","nombre":"Cairani","tipo":"CO","dpto":"Tacna","prov":"Candarave","dist":"Cairani","lat":-17.3,"lon":-70.3,"elev":3920,"activa":True},
    {"codigo":"117003","nombre":"Calana","tipo":"CO","dpto":"Tacna","prov":"Tacna","dist":"Calana","lat":-17.983,"lon":-70.2,"elev":1200,"activa":True},
    {"codigo":"117019","nombre":"Candarave","tipo":"CO","dpto":"Tacna","prov":"Candarave","dist":"Candarave","lat":-17.267,"lon":-70.233,"elev":3415,"activa":True},
    {"codigo":"117048","nombre":"Challapalca","tipo":"PLU","dpto":"Tacna","prov":"Tarata","dist":"Ticaco","lat":-17.2,"lon":-69.8,"elev":4280,"activa":True},
    {"codigo":"117013","nombre":"Chuapalca","tipo":"CO","dpto":"Tacna","prov":"Tarata","dist":"Tarata","lat":-17.3,"lon":-69.6,"elev":4177,"activa":True},
    {"codigo":"117012","nombre":"Ite","tipo":"CO","dpto":"Tacna","prov":"Jorge Basadre","dist":"Ite","lat":-17.9,"lon":-71.0,"elev":154,"activa":True},
    {"codigo":"118004","nombre":"Jorge Basadre","tipo":"CP","dpto":"Tacna","prov":"Tacna","dist":"Tacna","lat":-18.033,"lon":-70.25,"elev":565,"activa":True},
    {"codigo":"118002","nombre":"La Yarada","tipo":"CO","dpto":"Tacna","prov":"Tacna","dist":"Tacna","lat":-18.2,"lon":-70.5,"elev":21,"activa":True},
    {"codigo":"117010","nombre":"Locumba","tipo":"CO","dpto":"Tacna","prov":"Jorge Basadre","dist":"Locumba","lat":-17.6,"lon":-70.8,"elev":550,"activa":True},
    {"codigo":"118001","nombre":"Magollo","tipo":"CO","dpto":"Tacna","prov":"Tacna","dist":"Tacna","lat":-18.1,"lon":-70.3,"elev":260,"activa":True},
    {"codigo":"117037","nombre":"Palca","tipo":"CO","dpto":"Tacna","prov":"Tacna","dist":"Palca","lat":-17.8,"lon":-70.0,"elev":2953,"activa":True},
    {"codigo":"116052","nombre":"Pampa Umalzo (titijones)","tipo":"CO","dpto":"Tacna","prov":"Candarave","dist":"Candarave","lat":-16.9,"lon":-70.4,"elev":4609,"activa":True},
    {"codigo":"117043","nombre":"Paucarani","tipo":"CO","dpto":"Tacna","prov":"Tacna","dist":"Palca","lat":-17.5,"lon":-69.8,"elev":4609,"activa":True},
    {"codigo":"117018","nombre":"Sama Grande","tipo":"CO","dpto":"Tacna","prov":"Tacna","dist":"Inclan","lat":-17.8,"lon":-70.5,"elev":534,"activa":True},
    {"codigo":"117034","nombre":"Sitajara","tipo":"PLU","dpto":"Tacna","prov":"Tarata","dist":"Sitajara","lat":-17.4,"lon":-70.1,"elev":3132,"activa":True},
    {"codigo":"117033","nombre":"Susapaya","tipo":"CO","dpto":"Tacna","prov":"Tarata","dist":"Susapaya","lat":-17.4,"lon":-70.1,"elev":3433,"activa":True},
    {"codigo":"117039","nombre":"Talabaya","tipo":"CO","dpto":"Tacna","prov":"Tarata","dist":"Estique","lat":-17.6,"lon":-70.0,"elev":3420,"activa":True},
    {"codigo":"117020","nombre":"Tarata","tipo":"CO","dpto":"Tacna","prov":"Tarata","dist":"Tarata","lat":-17.483,"lon":-70.033,"elev":3053,"activa":True},
    {"codigo":"117040","nombre":"Toquela","tipo":"PLU","dpto":"Tacna","prov":"Tacna","dist":"Pachia","lat":-17.7,"lon":-69.9,"elev":3566,"activa":True},
    {"codigo":"117014","nombre":"Vilacota","tipo":"CO","dpto":"Tacna","prov":"Tarata","dist":"Susapaya","lat":-17.1,"lon":-70.1,"elev":4440,"activa":True},

    # ── TUMBES ────────────────────────────────────────────────────────────────
    {"codigo":"103043","nombre":"Cabo Inga","tipo":"CO","dpto":"Tumbes","prov":"Tumbes","dist":"San Jacinto","lat":-4.0,"lon":-80.4,"elev":228,"activa":True},
    {"codigo":"103042","nombre":"Cañaveral","tipo":"CO","dpto":"Tumbes","prov":"Contralmirante Villar","dist":"Casitas","lat":-3.9,"lon":-80.7,"elev":131,"activa":True},
    {"codigo":"103047","nombre":"Cia. Tumpis","tipo":"CO","dpto":"Tumbes","prov":"Zarumilla","dist":"Papayal","lat":-3.5,"lon":-80.3,"elev":15,"activa":True},
    {"codigo":"103041","nombre":"El Salto","tipo":"CO","dpto":"Tumbes","prov":"Zarumilla","dist":"Zarumilla","lat":-3.5,"lon":-80.3,"elev":4,"activa":True},
    {"codigo":"103016","nombre":"El Tigre","tipo":"PLU","dpto":"Tumbes","prov":"Tumbes","dist":"Pam Pas de Hospital","lat":-3.8,"lon":-80.5,"elev":45,"activa":True},
    {"codigo":"100072","nombre":"La Cruz","tipo":"CO","dpto":"Tumbes","prov":"Tumbes","dist":"La Cruz","lat":-3.6,"lon":-80.6,"elev":7,"activa":True},
    {"codigo":"117009","nombre":"Los Cedros","tipo":"CO","dpto":"Tumbes","prov":"Tumbes","dist":"Corrales","lat":-3.6,"lon":-80.5,"elev":74,"activa":True},
    {"codigo":"103008","nombre":"Matapalo","tipo":"PLU","dpto":"Tumbes","prov":"Zarumilla","dist":"Matapalo","lat":-3.7,"lon":-80.2,"elev":56,"activa":True},
    {"codigo":"103040","nombre":"Papayal","tipo":"CO","dpto":"Tumbes","prov":"Zarumilla","dist":"Papayal","lat":-3.6,"lon":-80.2,"elev":50,"activa":True},
    {"codigo":"103038","nombre":"Puerto Pizarro","tipo":"CO","dpto":"Tumbes","prov":"Tumbes","dist":"Tumbes","lat":-3.5,"lon":-80.4,"elev":2,"activa":True},
    {"codigo":"103036","nombre":"Rica Playa","tipo":"CO","dpto":"Tumbes","prov":"Tumbes","dist":"San Jacinto","lat":-3.8,"lon":-80.5,"elev":68,"activa":True},
    {"codigo":"002703","nombre":"San Juan de la Virgen","tipo":"PLU","dpto":"Tumbes","prov":"Tumbes","dist":"San Juan de la Virgen","lat":-3.633,"lon":-80.333,"elev":50,"activa":True},
    {"codigo":"002701","nombre":"Tumbes","tipo":"CP","dpto":"Tumbes","prov":"Tumbes","dist":"Tumbes","lat":-3.567,"lon":-80.467,"elev":20,"activa":True},
    {"codigo":"103039","nombre":"Zarumilla","tipo":"PLU","dpto":"Tumbes","prov":"Zarumilla","dist":"Zarumilla","lat":-3.5,"lon":-80.267,"elev":30,"activa":True},

    # ── UCAYALI ───────────────────────────────────────────────────────────────
    {"codigo":"108028","nombre":"Aguaytia","tipo":"CO","dpto":"Ucayali","prov":"Padre Abad","dist":"Padre Abad","lat":-9.033,"lon":-75.5,"elev":341,"activa":True},
    {"codigo":"108027","nombre":"El Maronal","tipo":"CO","dpto":"Ucayali","prov":"Padre Abad","dist":"Curimana","lat":-8.4,"lon":-75.1,"elev":185,"activa":True},
    {"codigo":"108026","nombre":"Las Palmeras de Ucayali","tipo":"CO","dpto":"Ucayali","prov":"Padre Abad","dist":"Curimana","lat":-8.6,"lon":-74.9,"elev":170,"activa":True},
    {"codigo":"002301","nombre":"Pucallpa","tipo":"CP","dpto":"Ucayali","prov":"Coronel Portillo","dist":"Calleria","lat":-8.383,"lon":-74.567,"elev":154,"activa":True},
    {"codigo":"100121","nombre":"San Alejandro","tipo":"CO","dpto":"Ucayali","prov":"Padre Abad","dist":"Irazola","lat":-8.8,"lon":-75.2,"elev":210,"activa":True},
    {"codigo":"108003","nombre":"San Jorge","tipo":"PLU","dpto":"Ucayali","prov":"Coronel Portillo","dist":"Campoverde","lat":-8.5,"lon":-74.9,"elev":180,"activa":True},
    {"codigo":"002303","nombre":"Sepahua","tipo":"PLU","dpto":"Ucayali","prov":"Atalaya","dist":"Sepahua","lat":-11.15,"lon":-73.033,"elev":360,"activa":True},
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
# FUNCIONES DE CONVERSIÓN GMS (Grados, Minutos, Segundos / Sexagesimal)
# =============================================================================
def gms_a_decimal(grados, minutos=0, segundos=0.0, hemisferio=None):
    """
    Convierte coordenadas en formato Grados, Minutos, Segundos (GMS / Sexagesimal)
    a grados decimales.

    Parámetros:
        grados     : int — grados (puede ser negativo)
        minutos    : int — minutos (0–59)
        segundos   : float — segundos (0.0–59.999...)
        hemisferio : str — 'N','S','E','W' (opcional). Si se especifica, se aplica
                     el signo correspondiente. 'S' y 'W' fuerzan negativo.

    Retorna:
        float — grados decimales con signo

    Ejemplos:
        gms_a_decimal(-8, 1, 4.8)              → -8.018
        gms_a_decimal(8, 1, 4.8, 'S')          → -8.018
        gms_a_decimal(78, 34, 4.8, 'W')        → -78.5680
    """
    if minutos < 0 or minutos >= 60:
        raise ValueError(f"Minutos fuera de rango (0–59): {minutos}")
    if segundos < 0 or segundos >= 60:
        raise ValueError(f"Segundos fuera de rango (0.0–59.99): {segundos}")

    signo = -1 if grados < 0 else 1
    decimal = abs(grados) + minutos / 60.0 + segundos / 3600.0
    decimal *= signo

    if hemisferio is not None:
        h = hemisferio.upper().strip()
        if h in ('S', 'W'):
            decimal = -abs(decimal)
        elif h in ('N', 'E'):
            decimal = abs(decimal)
    return round(decimal, 6)


def decimal_a_gms(decimal, tipo='lat'):
    """
    Convierte grados decimales a formato GMS (sexagesimal).

    Parámetros:
        decimal : float — coordenada en grados decimales
        tipo    : str — 'lat' o 'lon' (determina N/S o E/W)

    Retorna:
        dict con grados, minutos, segundos, hemisferio y string formateado

    Ejemplo:
        decimal_a_gms(-8.018, 'lat') →
        {'grados':8,'minutos':1,'segundos':4.8,'hemisferio':'S',
         'texto':"8°1'4.8\"S"}
    """
    abs_d = abs(decimal)
    grados = int(abs_d)
    resto_min = (abs_d - grados) * 60
    minutos = int(resto_min)
    segundos = round((resto_min - minutos) * 60, 2)

    # Carry si segundos quedó en 60.0 por redondeo
    if segundos >= 60:
        segundos = 0.0
        minutos += 1
    if minutos >= 60:
        minutos = 0
        grados += 1

    if tipo == 'lat':
        hemisferio = 'S' if decimal < 0 else 'N'
    else:
        hemisferio = 'W' if decimal < 0 else 'E'

    texto = f"{grados}°{minutos}'{segundos}\"{hemisferio}"
    return {
        'grados': grados,
        'minutos': minutos,
        'segundos': segundos,
        'hemisferio': hemisferio,
        'texto': texto,
    }


def parse_gms(texto):
    """
    Parsea un string en formato GMS (varios formatos aceptados) y devuelve
    grados decimales.

    Formatos aceptados (ejemplos):
        "8°1'4.8\"S"
        "-8 1 4.8"
        "8 1 4.8 S"
        "8d1m4.8sS"
        "8 grados 1 minutos 4.8 segundos S"

    Retorna:
        float — grados decimales con signo
    """
    import re as _re
    s = texto.strip().upper()
    # Detectar hemisferio
    hemi = None
    m = _re.search(r'([NSEW])\s*$', s)
    if m:
        hemi = m.group(1)
        s = s[:m.start()].strip()
    # Extraer números (incluyendo signo)
    nums = _re.findall(r'-?\d+(?:\.\d+)?', s)
    if not nums:
        raise ValueError(f"No se pudieron extraer números de: {texto!r}")
    g = float(nums[0])
    mi = float(nums[1]) if len(nums) > 1 else 0.0
    se = float(nums[2]) if len(nums) > 2 else 0.0
    return gms_a_decimal(int(g) if g.is_integer() else g, int(mi), se, hemi)


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
