#!/usr/bin/env python3
"""
Script para contar todas las líneas en un archivo CSV.
"""

import sys
import os

def contar_lineas_csv(archivo_csv):
    """
    Cuenta todas las líneas en un archivo CSV.
    Intenta diferentes codificaciones para manejar archivos con caracteres especiales.
    
    Args:
        archivo_csv: Ruta al archivo CSV
        
    Returns:
        Número total de líneas en el archivo
    """
    # Lista de codificaciones a intentar (en orden de preferencia)
    codificaciones = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
    
    for encoding in codificaciones:
        try:
            with open(archivo_csv, 'r', encoding=encoding, errors='replace') as f:
                line_count = sum(1 for line in f)
            return line_count
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo '{archivo_csv}'")
            sys.exit(1)
        except Exception as e:
            # Si es otro tipo de error, intentamos con la siguiente codificación
            continue
    
    # Si ninguna codificación funcionó, intentamos en modo binario
    try:
        with open(archivo_csv, 'rb') as f:
            line_count = sum(1 for line in f)
        return line_count
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Nombre del archivo CSV
    archivo = "este_TCIM_195_scored_final.csv"
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo):
        print(f"Error: El archivo '{archivo}' no existe en el directorio actual.")
        sys.exit(1)
    
    # Contar las líneas
    total_lineas = contar_lineas_csv(archivo)
    
    # Mostrar el resultado
    print(f"El archivo '{archivo}' contiene {total_lineas} líneas en total.")
    print(f"(Incluyendo la línea de encabezado: {total_lineas - 1} filas de datos)")

