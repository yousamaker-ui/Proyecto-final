# Evaluación de la fatiga neuromuscular durante el ejercicio (EMG + ECG)


## Integrantes
- [Helena Valenzuela P.]
- [Daniela Alvarez P.]
- [Yahir Daniel Romero D.]

Este proyecto consiste en procesar las señales obtenidas de un EMG y un ECG para encontrar el punto donde la MDF del EMG baje lo suficiente en niveles de frecuencia y donde la frecuencia cardíaca siga subiendo o este bastante activa, lo que indicaría fatiga muscular.

Las señales fueron tomadas de un circuito y convertidas a dos archivos csv, el ecg fue obtenido del módulo AD8232 con un Arduino UNO (respectivos electrodos también) y el EMG de un amplificador de instrumentación con filtros pasa altas y bajas aplicados en hardware.


## Estructura del Repositorio
- **/Hardware**: Fotos y diagrama del circuito.
- **/Software**: Código de la interfaz en python.
- **/Reporte**: Artículo con formato IEEE y editable (.docx).

  ## Tecnologías de software que se deben tener instaladas
* **Librerías principales:**
    * `tkinter`: Para la nterfaz gráfica de usuario (GUI).
    * `pandas` & `numpy`: Se encarga de la manipulación y el cálculo numérico de señales.
    * `scipy`: Procesamientos como filtrado Butterworth, detección de picos y STFT.
    * `matplotlib`: Visualización de señales en tiempo real.
    * `winsound`: Emisión de alertas auditivas cuando hay fatiga.
 
