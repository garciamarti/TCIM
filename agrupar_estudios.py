#!/usr/bin/env python3
"""
Script para agrupar y contar estudios por categoría y subcategoría. Esto se hizo para el proyecto de la clase de Análisis de Datos de la Universidad de Chile.

"""

import csv
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

try:
    import matplotlib
    # Usar backend Agg que funciona en todos los entornos (guarda archivos)
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False


CSV_FILE = "este_TCIM_195_scored_final.csv"
CATEGORY_FIELD = "Category"
SUBCATEGORY_FIELD = "Subcategory"
ENCODINGS = ["utf-8", "latin-1", "iso-8859-1", "cp1252", "utf-8-sig"]


def leer_csv(archivo_csv: str) -> List[Dict[str, str]]:
    """
    Lee el archivo CSV intentando múltiples codificaciones.

    Returns:
        Lista de filas como diccionarios.
    """
    if not os.path.exists(archivo_csv):
        print(f"Error: El archivo '{archivo_csv}' no existe.")
        sys.exit(1)

    for encoding in ENCODINGS:
        try:
            with open(archivo_csv, "r", encoding=encoding, errors="replace") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except UnicodeDecodeError:
            continue
        except Exception:
            continue

    print("Error: No se pudo leer el archivo con las codificaciones probadas.")
    sys.exit(1)


def normalizar_texto(valor: str, texto_vacio: str = "Sin dato") -> str:
    """Normaliza textos eliminando espacios y valores vacíos."""
    if valor is None:
        return texto_vacio
    limpio = valor.strip()
    return limpio if limpio else texto_vacio


def agrupar_estudios(filas: List[Dict[str, str]]) -> Tuple[Counter, Dict[str, Counter]]:
    """
    Agrupa y cuenta los estudios por categoría y subcategoría.

    Returns:
        Un Counter por categoría y un dict {categoria: Counter(subcategorias)}.
    """
    categorias = Counter()
    subcategorias_por_categoria: Dict[str, Counter] = defaultdict(Counter)

    for fila in filas:
        categoria = normalizar_texto(fila.get(CATEGORY_FIELD), "Sin categoría")
        subcategoria = normalizar_texto(fila.get(SUBCATEGORY_FIELD), "Sin subcategoría")

        categorias[categoria] += 1
        subcategorias_por_categoria[categoria][subcategoria] += 1

    return categorias, subcategorias_por_categoria


def imprimir_resumen(
    categorias: Counter, subcategorias_por_categoria: Dict[str, Counter]
) -> None:
    """Imprime los conteos agrupados."""
    total = sum(categorias.values())
    print(f"\nTotal de estudios analizados: {total}\n")

    print("Conteo por categoría:")
    for categoria, count in categorias.most_common():
        porcentaje = (count / total) * 100 if total else 0
        print(f"- {categoria}: {count} ({porcentaje:.1f}%)")
    print("")

    print("Detalle por categoría y subcategoría:")
    for categoria, counter in categorias.most_common():
        print(f"\n{categoria} ({categorias[categoria]} estudios)")
        for subcategoria, count in subcategorias_por_categoria[categoria].most_common():
            porcentaje = (count / categorias[categoria]) * 100 if categorias[categoria] else 0
            print(f"  • {subcategoria}: {count} ({porcentaje:.1f}%)")
    print("")


def crear_grafico_barras(categorias: Counter) -> None:
    """Crea un gráfico de barras con los conteos por categoría."""
    if not MATPLOTLIB_DISPONIBLE:
        print("\n⚠️  Matplotlib no está instalado. Para ver el gráfico, instálalo con:")
        print("   pip install matplotlib")
        return

    # Preparar datos
    categorias_ordenadas = categorias.most_common()
    nombres = [cat for cat, _ in categorias_ordenadas]
    valores = [count for _, count in categorias_ordenadas]
    
    # Crear el gráfico
    plt.figure(figsize=(12, 6))
    barras = plt.bar(range(len(nombres)), valores, color='steelblue', edgecolor='navy', alpha=0.7)
    
    # Personalizar el gráfico
    plt.xlabel('Categorías', fontsize=12, fontweight='bold')
    plt.ylabel('Número de Estudios', fontsize=12, fontweight='bold')
    plt.title('Distribución de Estudios por Categoría', fontsize=14, fontweight='bold', pad=20)
    plt.xticks(range(len(nombres)), nombres, rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Agregar valores en las barras
    for i, (barra, valor) in enumerate(zip(barras, valores)):
        altura = barra.get_height()
        porcentaje = (valor / sum(valores)) * 100
        plt.text(barra.get_x() + barra.get_width()/2., altura,
                f'{valor}\n({porcentaje:.1f}%)',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Ajustar layout para que no se corten las etiquetas
    plt.tight_layout()
    
    # Guardar el gráfico en un archivo
    nombre_archivo = "grafico_categorias.png"
    plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    print(f"\n📊 Gráfico guardado como '{nombre_archivo}'")
    print(f"   Puedes abrirlo para ver la visualización de las categorías.")
    
    plt.close()  # Cerrar la figura para liberar memoria


def main() -> None:
    filas = leer_csv(CSV_FILE)
    if not filas:
        print("El archivo no contiene datos.")
        return

    categorias, subcategorias_por_categoria = agrupar_estudios(filas)
    imprimir_resumen(categorias, subcategorias_por_categoria)
    crear_grafico_barras(categorias)


if __name__ == "__main__":
    main()

