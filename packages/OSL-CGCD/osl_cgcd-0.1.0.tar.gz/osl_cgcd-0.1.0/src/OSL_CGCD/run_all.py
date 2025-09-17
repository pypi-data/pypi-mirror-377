import subprocess
import sys
import os

# Ruta de los módulos
modulo1 = os.path.join(os.path.dirname(__file__), 'modulo1.py')
modulo2 = os.path.join(os.path.dirname(__file__), 'modulo2.py')

# Ejecutar módulo 1
print('Ejecutando modulo1.py...')
subprocess.run([sys.executable, modulo1], check=True)

# Ejecutar módulo 2
print('Ejecutando modulo2.py...')
subprocess.run([sys.executable, modulo2], check=True)

print('Automatización completada.')
