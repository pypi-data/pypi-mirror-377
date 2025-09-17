# Deconvolution with FOK-CW for multiple columns
from scipy import optimize
import numpy as np
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import warnings
import pandas as pd
import os

# Suppress warnings
warnings.filterwarnings("ignore")

# Solicitar el nombre del archivo al usuario
filename = input("Ingrese el nombre del archivo .xlsx a procesar: ")
df = pd.read_excel(filename, decimal=',')  # Usar coma como decimal

# Convert to numpy array ensuring numeric values
data = df.apply(pd.to_numeric, errors='coerce').values

# Remove any rows with NaN values
data = data[~np.isnan(data).any(axis=1)]

# Ensure x_data is correct
x_data = np.array(data[0:1000, 0], dtype=float)

def FOKCW(t, A, tau):
    CW = A * np.exp(-t/tau)
    return CW

def total_CW(t, *inis):
    u = np.zeros(len(t))
    nPks = (len(inis) - 1) // 2
    As, taus = inis[0:nPks], inis[nPks:2*nPks]
    bgd = inis[-1]
    for i in range(nPks):
        u = u + FOKCW(t, As[i], taus[i])
    u = u + bgd
    return u

# Main analysis parameters
nPks = 3
inis = [0.5, 0.3, 0.2, 5, 20, 100, 0.01]  # 3 amplitudes + 3 tiempos + fondo


# Process each column from 1 to 4
for colum in range(1, 5):
    print(f"\n{'='*50}")
    print(f"PROCESANDO COLUMNA {colum}")
    print(f"{'='*50}")

    try:
        # Get y_data for current column
        y_data = np.array(data[0:1000, colum], dtype=float)
        y_data = y_data / max(y_data)

        # Perform curve fitting
        params, cov = optimize.curve_fit(total_CW, x_data, y_data, p0=inis, maxfev=10000)

        # Create figure
        plt.figure(figsize=(12, 8))
        plt.scatter(x_data, y_data, c='r', label=f'Columna {colum}', alpha=0.7)
        plt.plot(x_data, total_CW(x_data, *params), c='black', label='FOK-CW equation', linewidth=2)

        # Plot individual components
        colors = ['blue', 'green', 'orange']
        for i in range(nPks):
            CWi = FOKCW(x_data, params[i], params[nPks+i])
            plt.plot(x_data, CWi, '--', color=colors[i], label=f'Component {i+1}')

        # Plot background
        plt.axhline(y=params[-1], color='purple', linestyle=':', label='Background')

        plt.legend()
        plt.ylabel('CW-OSL [a.u.]')
        plt.xlabel('Stimulation time [s]')
        plt.title(f'FOK-CW Deconvolution - Columna {colum}')
        plt.grid(True, alpha=0.3)

        # Calculate FOM
        res = total_CW(x_data, *params) - y_data
        FOM = 100 * np.sum(abs(res)) / np.sum(y_data)

        # Create results table
        As = [round(x, 4) for x in params[0:nPks]]
        taus = [round(x, 3) for x in params[nPks:2*nPks]]

        # Calculate errors from covariance matrix
        dAs = [round(np.sqrt(cov[x][x]), 4) for x in range(nPks)]
        dtaus = [round(np.sqrt(cov[x+nPks][x+nPks]), 3) for x in range(nPks)]
        dbgd = round(np.sqrt(cov[-1][-1]), 4)

        myTable = PrettyTable()
        myTable.field_names = ["Parámetro", "Valor", "Error", "Unidad"]
        myTable.add_row(["FOM", f"{FOM:.1f}%", "", ""])

        for i in range(nPks):
            myTable.add_row([f"A{i+1}", As[i], f"±{dAs[i]}", "a.u."])
            myTable.add_row([f"τ{i+1}", taus[i], f"±{dtaus[i]}", "s"])

        myTable.add_row(["Background", round(params[-1], 4), f"±{dbgd}", "a.u."])

        print(myTable)

    except Exception as e:
        print(f"✗ Error processing column {colum}: {e}")
        continue

# Crear un solo archivo con todos los datos en formato continuo
header = "Tiempo[s]"
all_columns_data = [x_data]  # Empezar con la columna de tiempo

# Preparar encabezado y datos en el orden específico
for colum in range(1, 5):
    try:
        # Get y_data for current column
        y_data = np.array(data[0:1000, colum], dtype=float)
        y_data_normalized = y_data / max(y_data)

        # Perform curve fitting
        params, cov = optimize.curve_fit(total_CW, x_data, y_data_normalized, p0=inis, maxfev=10000)

        # Calcular componentes individuales y fit
        comp1 = FOKCW(x_data, params[0], params[3])
        comp2 = FOKCW(x_data, params[1], params[4])
        comp3 = FOKCW(x_data, params[2], params[5])
        fok_cw_eq = total_CW(x_data, *params)

        # Agregar al encabezado en el orden específico
        header += f"\tCol{colum}_Comp1\tCol{colum}_Comp2\tCol{colum}_Comp3\tCol{colum}_Fit\tCol{colum}_Muestra"

        # Agregar datos en el orden específico: Comp1, Comp2, Comp3, Fit, Muestra
        all_columns_data.extend([comp1, comp2, comp3, fok_cw_eq, y_data_normalized])

    except Exception as e:
        print(f"✗ Error procesando columna {colum}: {e}")
        continue


# Combinar todos los datos en un solo array
all_data_combined = np.column_stack(all_columns_data)


# Crear carpeta si no existe
output_dir = 'resultados_deconvolucion_completos'
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'resultados_deconvolucion_completos.txt')
np.savetxt(output_file, all_data_combined, delimiter='\t', header=header, comments='', fmt='%.6f')

print(f"Archivo '{output_file}' creado exitosamente")


# Mostrar estructura del archivo
print(f"\nESTRUCTURA DEL ARCHIVO:")
print("1 columna: Tiempo[s]")
for i in range(1, 5):
    print(f"5 columnas para Columna {i}: Comp1, Comp2, Comp3, Fit, Muestra")
print(f"TOTAL: {1 + 5*4} = 21 columnas")
    