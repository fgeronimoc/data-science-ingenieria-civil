# Computer Vision aplicada a la Construcción

Computer vision permite que una computadora "vea" e interprete imágenes y video. En construcción, esto abre la puerta a monitoreo automatizado de seguridad, control de avance de obra y análisis de condiciones de campo sin necesidad de inspección humana constante.

---

## 1. ¿Cómo "ve" una computadora?

Una imagen digital es una matriz de números. Cada píxel tiene un valor entre 0 y 255 para cada canal de color (R, G, B). Una imagen de 1920x1080 píxeles es una matriz de 1920 × 1080 × 3 = ~6 millones de números.

El reto de computer vision es encontrar patrones en esos números que correspondan a objetos del mundo real (un casco, una persona, una grieta en un puente).

---

## 2. Redes Neuronales Convolucionales (CNN)

Las CNN son la arquitectura base de la mayoría de modelos modernos de visión computacional. A diferencia de una red neuronal común, las CNN aprenden filtros que detectan bordes, texturas y formas de forma jerárquica.

**Cómo funciona (intuitivamente):**
- Las primeras capas detectan bordes y gradientes simples
- Las capas intermedias combinan bordes en formas (círculo, rectángulo)
- Las capas finales combinan formas en objetos (casco, chaleco, persona)

**En construcción:** Una CNN entrenada con miles de imágenes de trabajadores con y sin EPP aprende a distinguir automáticamente si alguien lleva puesto el casco o no.

---

## 3. Detección de objetos

Más complejo que clasificar una imagen entera — la detección localiza y clasifica múltiples objetos dentro de una imagen simultáneamente.

**Output de un detector:** Para cada objeto detectado, devuelve:
- Bounding box (coordenadas del rectángulo que lo encierra)
- Clase (casco, chaleco, persona, maquinaria...)
- Confianza (probabilidad de que la predicción sea correcta)

**Métricas clave:**
- **IoU (Intersection over Union):** Qué tanto se superpone el bounding box predicho con el real. > 0.5 se considera buena detección.
- **mAP (mean Average Precision):** Métrica principal para evaluar detectores. Combina precisión y recall para todas las clases.

---

## 4. YOLO — You Only Look Once

YOLO es la familia de modelos de detección de objetos más popular por su velocidad y precisión. Puede procesar video en tiempo real, lo que lo hace ideal para monitoreo en obra.

### Versiones relevantes
- **YOLOv8** (actual recomendado): Desarrollado por Ultralytics. Excelente balance entre velocidad y precisión. Documentación muy completa.
- **YOLOv10**: Más reciente, aún más eficiente.

### Flujo de trabajo con YOLOv8

**1. Usar modelo preentrenado (sin entrenamiento propio):**
```python
from ultralytics import YOLO
modelo = YOLO('yolov8n.pt')  # n = nano (más rápido), x = extra large (más preciso)
resultados = modelo('imagen_obra.jpg')
resultados[0].show()
```

**2. Entrenar modelo personalizado (para EPPs específicos):**
- Recolectar imágenes de obra (mínimo 200-300 por clase)
- Etiquetar con herramientas como Roboflow o Label Studio
- Entrenar con transfer learning sobre pesos preentrenados
- Evaluar con mAP en conjunto de validación

```python
modelo = YOLO('yolov8n.pt')
modelo.train(data='dataset_epp.yaml', epochs=100, imgsz=640)
```

**3. Inferencia en video:**
```python
modelo = YOLO('modelo_epp_entrenado.pt')
modelo.predict(source='video_obra.mp4', save=True, conf=0.5)
```

---

## 5. Aplicaciones en construcción

| Aplicación | Descripción | Complejidad |
|------------|-------------|-------------|
| Detección de EPPs | Casco, chaleco, arnés, botas en tiempo real | Media (ya existe base) |
| Conteo de trabajadores | Cuántas personas hay en zona de riesgo | Baja |
| Monitoreo de avance | Comparar estado de obra vs. modelo BIM | Alta |
| Detección de grietas | En estructuras de concreto o asfalto | Media |
| Control de maquinaria | Detectar maquinaria en zonas restringidas | Media |
| Fotogrametría con drones | Reconstrucción 3D de terreno | Alta |

---

## 6. Consideraciones prácticas en obra

**Cámaras:** No se necesitan cámaras costosas. Una cámara IP de $30-50 USD conectada a una Raspberry Pi o a un servidor local puede correr YOLOv8 en tiempo casi real.

**Iluminación:** El mayor enemigo de computer vision en obra. Planificar posicionamiento de cámaras considerando sombras y reflejos.

**Privacidad:** En Perú no hay normativa específica aún, pero se recomienda informar a los trabajadores del sistema de monitoreo y no almacenar imágenes innecesariamente.

**Falsos positivos:** Un sistema que alerta cuando no hay infracción (o viceversa) pierde credibilidad. Calibrar el umbral de confianza es esencial.

---

## Conexión con proyectos de este repositorio

- `07_proyectos/seguridad_vision/` — implementación completa del sistema de detección de EPPs
- `05_herramientas/snippets/` — snippets reutilizables para inferencia con YOLO
