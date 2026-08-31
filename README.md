Sound Detector - Home Assistant

Integración personalizada para Home Assistant desarrollada como parte del Trabajo de Fin de Grado.

Descripción

Este proyecto implementa una integración personalizada para Home Assistant que permite obtener y mostrar el resultado de un sistema de detección de sonidos.
La integración consulta cada segundo un archivo JSON generado por el sistema de detección y utiliza la información obtenida para actualizar un sensor en Home Assistant.
El sensor proporciona:
-Estado de detección: sonido detectado o estado de espera.
-Confianza: valor numérico asociado a la predicción realizada por el detector.

Funcionamiento

De forma simplificada:
Detector de sonido -> Archivo JSON -> Integración Sound Detector -> Home Assistant -> Sensor "Sound Detector"

Instalación

Para instalar la integración personalizada en Home Assistant, seguir los siguientes pasos:

1.Descargar el repositorio

Descargar o clonar este repositorio en el equipo donde se esté trabajando.
La carpeta de la integración es: custom_components/sound_detector/

2.Copiar la integración a Home Assistant

Copiar la carpeta sound_detector dentro del directorio custom_components de la instalación de Home Assistant:
/config/custom_components/sound_detector/

La estructura final debe quedar de forma similar a:
/config/
  custom_components/
    sound_detector/
      __init__.py
      const.py
      detector.py
      manifest.json
      config_flow.py

Si la carpeta custom_components no existe, debe crearse dentro del directorio /config.

3.Configurar la dirección del archivo JSON

La integración está diseñada para funcionar dentro de una red local.
En const.py debe configurarse la dirección correspondiente al recurso JSON generado por el detector:
JSON_URL = "http://<IP_LOCAL>:8000/sound_detector.json"
Sustituir <IP_LOCAL> por la dirección IP del dispositivo que proporciona el archivo JSON.
Es necesario que el dispositivo donde se ejecuta Home Assistant pueda acceder a dicha dirección dentro de la red local.

4.Reiniciar Home Assistant

Después de copiar los archivos y configurar la dirección del recurso JSON, reiniciar Home Assistant para que se cargue la nueva integración.

5.Añadir la integración

Una vez reiniciado Home Assistant:
  1.Acceder a Ajustes.
  2.Entrar en Dispositivos y servicios.
  3.Seleccionar Añadir integración.
  4.Buscar Sound Detector.
  5.Seleccionar la integración para añadirla a Home Assistant.

Una vez configurada, se creará el sensor Sound Detector, que mostrará el estado de detección y el nivel de confianza proporcionado por el sistema.


Nota
Esta integración está diseñada para funcionar en una red local y requiere que el archivo sound_detector.json esté disponible en la dirección configurada en const.py.


Recursos de audio

Los archivos de audio incluidos en este repositorio se han obtenido de Freesound y se utilizan como material de prueba para el sistema. Todos ellos tienen licencia "Creative Commons 0", por lo que no es obligatoria su atribución.

