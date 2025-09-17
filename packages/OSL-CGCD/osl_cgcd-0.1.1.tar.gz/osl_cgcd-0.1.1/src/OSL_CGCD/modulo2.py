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

# Guardar en un solo archivo
np.savetxt("resultados_deconvolucion_completos.txt", all_data_combined, delimiter='\t',
           header=header, comments='', fmt='%.6f')

print("Archivo 'resultados_deconvolucion_completos.txt' creado exitosamente")

# Descargar el archivo (Google Colab)
try:
    from google.colab import files
    files.download("resultados_deconvolucion_completos.txt")
    print("✓ Archivo descargado automáticamente desde Colab")
except:
    print("✓ Archivo guardado localmente: 'resultados_deconvolucion_completos.txt'")

# Mostrar estructura del archivo
print(f"\nESTRUCTURA DEL ARCHIVO:")
print("1 columna: Tiempo[s]")
for i in range(1, 5):
    print(f"5 columnas para Columna {i}: Comp1, Comp2, Comp3, Fit, Muestra")
print(f"TOTAL: {1 + 5*4} = 21 columnas")