# OSL_CGCD

Programa para la deconvolución de curvas OSL utilizando el método CGCD.

## Autor
**EDWIN JOEL PILCO QUISPE**  
Email: edwinpilco10@gmail.com

## Descripción
Este paquete permite analizar y deconvolucionar curvas OSL (Optically Stimulated Luminescence) usando el método CGCD. Incluye herramientas para procesar archivos Excel, ajustar curvas y guardar resultados.

## Instalación
Puedes instalar el paquete desde PyPI:

```bash
python -m pip install OSL_CGCD
```

O instalarlo localmente desde el archivo `.whl` generado:

```bash
cd dist
python -m pip install osl_cgcd-0.1.1-py3-none-any.whl
```

## Uso básico
Crea un script y utiliza los módulos incluidos:

```python
from OSL_CGCD import modulo1, modulo2
# Ejemplo de uso: ejecutar funciones de análisis
```

## Estructura del paquete

- `modulo1.py`: Deconvolución de curvas OSL a partir de archivos Excel. Permite seleccionar el archivo a procesar y guarda los resultados en la carpeta `deconvolution_results`.
- `modulo2.py`: Combina los resultados de varias columnas en un solo archivo continuo para análisis posterior.
- `run_all.py`: Automatiza la ejecución de los módulos 1 y 2 en orden.

## Ejemplo de ejecución
1. Ejecuta `modulo1.py` para procesar tu archivo Excel:
	```bash
	python src/OSL_CGCD/modulo1.py
	```
2. Ejecuta `modulo2.py` para combinar los resultados:
	```bash
	python src/OSL_CGCD/modulo2.py
	```
3. O ejecuta todo automáticamente:
	```bash
	python src/OSL_CGCD/run_all.py
	```

## Publicación en PyPI
Para publicar una nueva versión:
1. Actualiza la versión en `setup.py`.
2. Construye el paquete:
	```bash
	python -m build
	```
3. Sube el paquete:
	```bash
	python -m twine upload dist/*
	```

## Requisitos
- Python >= 3.6
- Paquetes recomendados: numpy, scipy, matplotlib, pandas, prettytable

## Licencia
Este proyecto es de uso libre para fines académicos y personales.
