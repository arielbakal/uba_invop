# Intr. a la Investigación Operativa y Optimización 1C2025

## ¿Cómo usar el CPLEX interactivo?
Primero necesitamos instalar cplex y cualquier libreria extra:
```
pip install -r requirements.txt
```

Para usar el CPLEX interactivo se abre el archivo **interactive_cplex.py**:
```
python interactive_cplex.py
```
El programa pregunta línea por línea el modelo LP para modelarlo en variables que la API de cplex entiende. 

Así se logra una escritura más natural que escribir listas de listas todo el tiempo... y tenemos una herramienta para hallar un optimo sin ponerse a codear.
