# Intr. a la Investigación Operativa y Optimización 1C/2C 2025

## ¿Cómo usar el CPLEX interactivo?

Opcionalmente, creamos un entorno virtual:
```
python -m venv venv
```
Y lo activamos:

- En Windows,
```
venv\Scripts\activate
```
- O en linux/MacOS,
```
source venv/bin/activate
```
Instalamos cplex y cualquier libreria extra:
```
pip install -r requirements.txt
```

Finalmente para usar el CPLEX interactivo se abre el archivo **interactive_cplex.py**:
```
python interactive_cplex.py
```
El programa pregunta línea por línea el modelo LP para modelarlo en variables que la API de cplex entiende. 
