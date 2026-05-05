# Lista de revisión — Catálogo de estaciones SENAMHI

Estaciones donde el nombre del catálogo original (`.py`) **se renombró** al nombre oficial del PDF Atlas Climático.
Revisar a ojo si el match es correcto.

| Código nuevo | Nombre nuevo (oficial PDF) | Nombre antiguo (.py) | Distancia |
|---|---|---|---|
| 112038 | **Alexander Von Humboldt** | La Molina (era 000902) | 5.8 km |
| 103057 | **Amazonas** | Iquitos (era 002101) | 3.7 km |
| 107028 | **Augusto Weberbauer** | Weberbauer (era 000511) | 3.7 km |
| 115015 | **Coracora** | Cora Cora (era 001104) | 4.1 km |
| 113019 | **Huamanga** | Ayacucho (era 001101) | 4.1 km |
| 118004 | **Jorge Basadre** | Tacna (era 001601) | 6.4 km |
| 114032 | **Yauri** | Espinar (era 001204) | 1.9 km |

## Notas adicionales

- **Tipos:** la regla aplicada es: si el PDF dice que la estación mide solo PP → `PLU`; si mide PP+TMAX+TMIN → `CO`. Se respeta `CP` original.
  Esto puede haber cambiado el tipo de algunas estaciones que estaban como PLU en tu `.py` pero que el PDF clasifica como CO.
- **Coordenadas:** para las estaciones que ya estaban en tu `.py`, se conservaron las coordenadas más precisas del archivo original (3 decimales).
- **Estaciones sin match:** las 65+ estaciones del `.py` que no aparecen en el PDF se conservaron tal cual.
- **Nombres rotos por saltos de línea en el PDF (ya corregidos):** Jamalca, Las Salinas, Caycay, Challabamba, Virrey, San Miguel, Chilaco, Mañazo, Chazuta, Jayanca (La Viña), Chalhuanca II, Alexander Von Humboldt, Andahuaylas, UNJF Sanchez Carrion - Huacho.
- **Provincias/Distritos rotos (ya corregidos):** Aymaraes/Chalhuanca, Condesuyos/Chichas, Chiclayo/Eten, Candarave/Cairani, Contralmirante Villar/Casitas, Jorge Basadre/Ite, Jorge Basadre/Locumba.