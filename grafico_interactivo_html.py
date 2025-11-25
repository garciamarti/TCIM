#!/usr/bin/env python3
"""
Script para generar un gráfico de barras interactivo en HTML.
Permite hacer clic en las barras para ver detalles de las subcategorías.
"""

import csv
import os
import sys
import json
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

try:
    import plotly.graph_objects as go
    import plotly.offline as pyo
    PLOTLY_DISPONIBLE = True
except ImportError:
    PLOTLY_DISPONIBLE = False


CSV_FILE = "data/este_TCIM_195_scored_final.csv"
CATEGORY_FIELD = "Category"
SUBCATEGORY_FIELD = "Subcategory"
SUITABILITY_FIELD = "TCIM_suitability_level"
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


def agrupar_estudios(filas: List[Dict[str, str]]) -> Tuple[Counter, Dict[str, Counter], Dict[str, List[Dict]], Dict[str, Counter]]:
    """
    Agrupa y cuenta los estudios por categoría, subcategoría y nivel de aplicabilidad TCIM.

    Returns:
        Un Counter por categoría, un dict {categoria: Counter(subcategorias)},
        un dict con los estudios completos por categoría,
        y un dict {categoria: Counter(suitability_levels)}.
    """
    categorias = Counter()
    subcategorias_por_categoria: Dict[str, Counter] = defaultdict(Counter)
    estudios_por_categoria: Dict[str, List[Dict]] = defaultdict(list)
    suitability_por_categoria: Dict[str, Counter] = defaultdict(Counter)

    for fila in filas:
        categoria = normalizar_texto(fila.get(CATEGORY_FIELD), "Sin categoría")
        subcategoria = normalizar_texto(fila.get(SUBCATEGORY_FIELD), "Sin subcategoría")
        suitability = normalizar_texto(fila.get(SUITABILITY_FIELD), "Not applicable")

        categorias[categoria] += 1
        subcategorias_por_categoria[categoria][subcategoria] += 1
        estudios_por_categoria[categoria].append(fila)
        suitability_por_categoria[categoria][suitability] += 1

    return categorias, subcategorias_por_categoria, estudios_por_categoria, suitability_por_categoria


def crear_grafico_html_interactivo(
    categorias: Counter,
    subcategorias_por_categoria: Dict[str, Counter],
    estudios_por_categoria: Dict[str, List[Dict]],
    suitability_por_categoria: Dict[str, Counter]
) -> None:
    """Crea un gráfico de barras interactivo en HTML con Plotly."""
    if not PLOTLY_DISPONIBLE:
        print("\n⚠️  Plotly is not installed. To generate the chart, install it with:")
        print("   pip install plotly")
        return

    # Preparar datos para barras apiladas
    categorias_ordenadas = categorias.most_common()
    nombres = [cat for cat, _ in categorias_ordenadas]
    total = sum([count for _, count in categorias_ordenadas])
    
    # Definir niveles de aplicabilidad y sus colores
    suitability_levels = ['High', 'Moderate', 'Low', 'Not applicable']
    suitability_colors = {
        'High': '#2ecc71',           # Verde
        'Moderate': '#f39c12',       # Naranja
        'Low': '#e74c3c',            # Rojo
        'Not applicable': '#95a5a6'  # Gris
    }
    
    # Preparar datos apilados para cada nivel de aplicabilidad
    stacked_data = {}
    for level in suitability_levels:
        stacked_data[level] = []
        for categoria in nombres:
            count = suitability_por_categoria[categoria].get(level, 0)
            stacked_data[level].append(count)
    
    # Crear el gráfico de barras apiladas
    fig = go.Figure()
    
    # Agregar una barra para cada nivel de aplicabilidad
    for level in suitability_levels:
        fig.add_trace(go.Bar(
            name=level,
            x=nombres,
            y=stacked_data[level],
            marker=dict(
                color=suitability_colors[level],
                line=dict(color='#2c3e50', width=1),
                opacity=0.85
            ),
            text=[f"<b>{count}</b>" if count > 0 else "" for count in stacked_data[level]],
            textposition='inside',
            textfont=dict(size=11, color='white', family='Segoe UI, Tahoma, Geneva, Verdana, sans-serif'),
            hovertemplate=f"<b>{level}</b><br>" +
                         "Category: %{x}<br>" +
                         "Count: %{y}<br>" +
                         "<extra></extra>"
        ))
    
    # Agregar texto con el total en la parte superior de cada barra (más visible y destacado)
    valores_totales = [categorias[cat] for cat in nombres]
    porcentajes = [(v / total) * 100 for v in valores_totales]
    max_valor = max(valores_totales)
    
    # Calcular posición Y basada en el valor máximo para que todas las barras tengan la misma altura de texto
    # Esto asegura que las barras más cortas también tengan sus números bien posicionados
    y_positions = [max_valor * 1.25 for _ in valores_totales]  # Posición fija basada en el máximo
    
    fig.add_trace(go.Scatter(
        x=nombres,
        y=y_positions,  # Usar posición fija basada en el valor máximo
        mode='text',
        text=[f"<b>{v}</b><br><b>({p:.1f}%)</b>" for v, p in zip(valores_totales, porcentajes)],
        textfont=dict(size=16, color='#1a252f', family='Segoe UI, Tahoma, Geneva, Verdana, sans-serif'),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Personalizar el layout con estilo moderno
    fig.update_layout(
        title={
            'text': 'Distribution of Studies by Category',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22, 'color': '#2c3e50', 'family': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', 'weight': 'bold'}
        },
        xaxis=dict(
            title=dict(text='Categories', font=dict(size=15, color='#2c3e50', family='Segoe UI, Tahoma, Geneva, Verdana, sans-serif')),
            tickfont=dict(size=12, color='#34495e', family='Segoe UI, Tahoma, Geneva, Verdana, sans-serif'),
            tickangle=-45,
            gridcolor='#ecf0f1',
            gridwidth=1,
            linecolor='#bdc3c7',
            linewidth=1,
            showgrid=True
        ),
        yaxis=dict(
            title=dict(text='Number of Studies', font=dict(size=15, color='#2c3e50', family='Segoe UI, Tahoma, Geneva, Verdana, sans-serif')),
            tickfont=dict(size=12, color='#34495e', family='Segoe UI, Tahoma, Geneva, Verdana, sans-serif'),
            gridcolor='#ecf0f1',
            gridwidth=1,
            linecolor='#bdc3c7',
            linewidth=1,
            showgrid=True,
            range=[0, max_valor * 1.35]  # Aumentar el rango aún más para que el texto quepa completamente
        ),
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        height=650,  # Aumentar altura del gráfico
        margin=dict(b=120, l=80, r=40, t=180, pad=20),  # Aumentar margen superior aún más
        hovermode='closest',
        barmode='stack',  # Modo apilado para las barras
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,  # Mover la leyenda aún más arriba para no interferir con los totales
            xanchor="right",
            x=1,
            font=dict(size=12, family='Segoe UI, Tahoma, Geneva, Verdana, sans-serif')
        ),
        hoverlabel=dict(
            bgcolor='#2c3e50',
            font_size=12,
            font_family='Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
            font_color='white'
        ),
        font=dict(family='Segoe UI, Tahoma, Geneva, Verdana, sans-serif')
    )

    # Preparar datos para JavaScript (información de subcategorías y estudios completos)
    datos_js = {}
    for categoria in nombres:
        subcats = subcategorias_por_categoria[categoria]
        estudios_categoria = estudios_por_categoria[categoria]
        
        # Preparar lista de estudios con información relevante
        estudios_lista = []
        for estudio in estudios_categoria:
            estudios_lista.append({
                'title': normalizar_texto(estudio.get('Title', ''), '[Sin título]'),
                'author': normalizar_texto(estudio.get('Author', ''), '[Sin autor]'),
                'year': normalizar_texto(estudio.get('Year', ''), '[Sin año]'),
                'subcategory': normalizar_texto(estudio.get('Subcategory', ''), '[Sin subcategoría]'),
                'suitability': normalizar_texto(estudio.get('TCIM_suitability_level', ''), 'N/A')
            })
        
        datos_js[categoria] = {
            'subcategorias': [
                {'nombre': subcat, 'count': count}
                for subcat, count in subcats.most_common()
            ],
            'total': categorias[categoria],
            'estudios': estudios_lista
        }

    # Generar el div del gráfico
    html_content = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
    # Crear HTML completo con JavaScript para manejar clicks
    html_completo = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Chart - Studies by Category</title>
    <!-- Cargar Plotly desde CDN (versión 2.27.0 - compatible con plotly Python 6.5.0) -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }}
        .info {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        #detalles {{
            margin-top: 30px;
            padding: 20px;
            background-color: #ecf0f1;
            border-radius: 8px;
            display: none;
        }}
        #detalles h2 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        .subcategoria-item {{
            padding: 8px;
            margin: 5px 0;
            background-color: white;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        .subcategoria-nombre {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .subcategoria-count {{
            color: #7f8c8d;
            margin-left: 10px;
        }}
        .click-instruction {{
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
            color: #2e7d32;
        }}
        #grafico {{
            background-color: #ffffff;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        #grafico .plotly {{
            border-radius: 8px;
        }}
        #tabla-estudios {{
            margin-top: 30px;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            display: none;
        }}
        #tabla-estudios h2 {{
            color: #2c3e50;
            margin-top: 0;
            margin-bottom: 20px;
        }}
        .tabla-container {{
            overflow-x: auto;
            max-height: 600px;
            overflow-y: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        table thead {{
            background-color: #3498db;
            color: white;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        table th {{
            padding: 12px;
            text-align: left;
            font-weight: bold;
            position: relative;
            cursor: pointer;
            user-select: none;
        }}
        table th.sortable {{
            padding-right: 30px;
        }}
        table th.sortable:hover {{
            background-color: #2980b9;
        }}
        table th .sort-icon {{
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 14px;
            opacity: 0.8;
            font-weight: bold;
        }}
        table th .sort-icon::after {{
            content: '⇅';
            opacity: 0.8;
        }}
        table th.sortable:hover .sort-icon::after {{
            opacity: 1;
        }}
        table th.sort-asc .sort-icon::after {{
            content: '▲';
            opacity: 1;
            color: #ffffff;
        }}
        table th.sort-desc .sort-icon::after {{
            content: '▼';
            opacity: 1;
            color: #ffffff;
        }}
        table td {{
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
        }}
        table tbody tr:hover {{
            background-color: #f8f9fa;
        }}
        table tbody tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge-high {{
            background-color: #2ecc71;
            color: white;
        }}
        .badge-moderate {{
            background-color: #f39c12;
            color: white;
        }}
        .badge-low {{
            background-color: #e74c3c;
            color: white;
        }}
        .badge-na {{
            background-color: #95a5a6;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Distribution of Studies by Category</h1>
        <p class="info">Total studies analyzed: {total}</p>
        <div class="click-instruction">
            💡 <strong>Click on any bar</strong> to view subcategory details and the complete table of studies
        </div>
        <div id="grafico">{html_content}</div>
        <div id="detalles">
            <h2 id="detalles-titulo"></h2>
            <div id="detalles-contenido"></div>
        </div>
        <div id="tabla-estudios">
            <h2 id="tabla-titulo"></h2>
            <div class="tabla-container">
                <table id="tabla-estudios-content">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Title</th>
                            <th class="sortable" data-sort="author">Author <span class="sort-icon"></span></th>
                            <th class="sortable" data-sort="year">Year <span class="sort-icon"></span></th>
                            <th class="sortable" data-sort="subcategory">Subcategory <span class="sort-icon"></span></th>
                            <th class="sortable" data-sort="suitability">TCIM Suitability Level <span class="sort-icon"></span></th>
                        </tr>
                    </thead>
                    <tbody id="tabla-estudios-body">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Subcategory data
        const datosSubcategorias = {json.dumps(datos_js, ensure_ascii=False, indent=8)};

        // Function to get CSS class for badge based on suitability level
        function obtenerClaseBadge(suitability) {{
            const nivel = suitability.toLowerCase();
            if (nivel.includes('high')) return 'badge-high';
            if (nivel.includes('moderate')) return 'badge-moderate';
            if (nivel.includes('low')) return 'badge-low';
            return 'badge-na';
        }}

        // Function to display subcategory details
        function mostrarDetalles(categoria, total) {{
            const detallesDiv = document.getElementById('detalles');
            const tituloDiv = document.getElementById('detalles-titulo');
            const contenidoDiv = document.getElementById('detalles-contenido');
            
            if (!datosSubcategorias[categoria]) {{
                contenidoDiv.innerHTML = '<p>No information available for this category.</p>';
                detallesDiv.style.display = 'block';
                return;
            }}
            
            const datos = datosSubcategorias[categoria];
            tituloDiv.textContent = `📁 ${{categoria}} - ${{total}} studies`;
            
            let html = '<div style="margin-top: 15px;">';
            html += '<h3 style="color: #34495e; margin-bottom: 15px;">Subcategories:</h3>';
            
            datos.subcategorias.forEach(function(subcat) {{
                const porcentaje = ((subcat.count / total) * 100).toFixed(1);
                html += `
                    <div class="subcategoria-item">
                        <span class="subcategoria-nombre">${{subcat.nombre}}</span>
                        <span class="subcategoria-count">${{subcat.count}} studies (${{porcentaje}}%)</span>
                    </div>
                `;
            }});
            
            html += '</div>';
            contenidoDiv.innerHTML = html;
            detallesDiv.style.display = 'block';
            
            // Scroll suave hacia el panel de subcategorías
            setTimeout(function() {{
                detallesDiv.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}, 100);
        }}

        // Variable para almacenar los estudios actuales y el orden actual
        let estudiosActuales = [];
        let ordenActual = {{ column: null, direction: 'asc' }};

        // Function to render table rows
        function renderizarFilasTabla(estudios) {{
            const tablaBody = document.getElementById('tabla-estudios-body');
            tablaBody.innerHTML = '';
            
            estudios.forEach(function(estudio, index) {{
                const row = document.createElement('tr');
                const badgeClass = obtenerClaseBadge(estudio.suitability);
                
                row.innerHTML = `
                    <td>${{index + 1}}</td>
                    <td>${{estudio.title}}</td>
                    <td>${{estudio.author}}</td>
                    <td>${{estudio.year}}</td>
                    <td>${{estudio.subcategory}}</td>
                    <td><span class="badge ${{badgeClass}}">${{estudio.suitability}}</span></td>
                `;
                tablaBody.appendChild(row);
            }});
        }}

        // Function to sort table
        function ordenarTabla(column) {{
            if (estudiosActuales.length === 0) return;
            
            // Toggle direction if clicking the same column
            if (ordenActual.column === column) {{
                ordenActual.direction = ordenActual.direction === 'asc' ? 'desc' : 'asc';
            }} else {{
                ordenActual.column = column;
                ordenActual.direction = 'asc';
            }}
            
            // Sort studies
            const estudiosOrdenados = [...estudiosActuales].sort(function(a, b) {{
                let aVal = a[column];
                let bVal = b[column];
                
                // Handle different data types
                if (column === 'year') {{
                    // Sort by year as number
                    aVal = parseInt(aVal) || 0;
                    bVal = parseInt(bVal) || 0;
                }} else {{
                    // Sort as string (case insensitive)
                    aVal = (aVal || '').toString().toLowerCase();
                    bVal = (bVal || '').toString().toLowerCase();
                }}
                
                if (aVal < bVal) return ordenActual.direction === 'asc' ? -1 : 1;
                if (aVal > bVal) return ordenActual.direction === 'asc' ? 1 : -1;
                return 0;
            }});
            
            // Update sort indicators
            document.querySelectorAll('th.sortable').forEach(function(th) {{
                th.classList.remove('sort-asc', 'sort-desc');
                if (th.dataset.sort === column) {{
                    th.classList.add(ordenActual.direction === 'asc' ? 'sort-asc' : 'sort-desc');
                }}
            }});
            
            // Re-render table
            renderizarFilasTabla(estudiosOrdenados);
        }}

        // Function to display studies table
        function mostrarTablaEstudios(categoria, total) {{
            const tablaDiv = document.getElementById('tabla-estudios');
            const tablaTitulo = document.getElementById('tabla-titulo');
            const tablaBody = document.getElementById('tabla-estudios-body');
            
            if (!datosSubcategorias[categoria] || !datosSubcategorias[categoria].estudios) {{
                tablaBody.innerHTML = '<tr><td colspan="6">No studies available for this category.</td></tr>';
                tablaDiv.style.display = 'block';
                return;
            }}
            
            estudiosActuales = datosSubcategorias[categoria].estudios;
            tablaTitulo.textContent = `📋 Studies List: ${{categoria}} (${{total}} studies)`;
            
            // Reset sort
            ordenActual = {{ column: null, direction: 'asc' }};
            document.querySelectorAll('th.sortable').forEach(function(th) {{
                th.classList.remove('sort-asc', 'sort-desc');
            }});
            
            // Render initial table
            renderizarFilasTabla(estudiosActuales);
            
            // Re-configure sort listeners after rendering
            configurarOrdenamientoTabla();
            
            // Show the table
            tablaDiv.style.display = 'block';
            
            // Don't scroll to table, let it stay where subcategories are
        }}

        // Add click event listeners to sortable headers
        function configurarOrdenamientoTabla() {{
            // Remove existing listeners by using a flag
            document.querySelectorAll('th.sortable').forEach(function(th) {{
                // Remove old listener if exists
                if (th._sortHandler) {{
                    th.removeEventListener('click', th._sortHandler);
                }}
                
                // Create new handler
                th._sortHandler = function(e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    ordenarTabla(th.dataset.sort);
                }};
                
                // Add new event listener
                th.addEventListener('click', th._sortHandler);
            }});
        }}

        // Function to configure Plotly event listeners
        function configurarInteractividad() {{
            // Find all Plotly graph elements
            const allPlotDivs = document.querySelectorAll('[id*="plotly"], .plotly-graph-div');
            
            allPlotDivs.forEach(function(plotDiv) {{
                // Check if the graph already has data and doesn't have the handler
                if (plotDiv.data && !plotDiv._clickHandlerAdded) {{
                    plotDiv._clickHandlerAdded = true;
                    
                    // Add event listener for clicks
                    plotDiv.on('plotly_click', function(data) {{
                        if (data.points && data.points.length > 0) {{
                            const punto = data.points[0];
                            const categoria = punto.x;
                            const count = punto.y;
                            
                            // Show subcategory details
                            mostrarDetalles(categoria, count);
                            
                            // Show studies table
                            mostrarTablaEstudios(categoria, count);
                        }}
                    }});
                }}
            }});
            
            // If no graph found, try again after a delay
            if (allPlotDivs.length === 0 || !Array.from(allPlotDivs).some(d => d.data)) {{
                setTimeout(configurarInteractividad, 500);
            }}
        }}

        // Function to wait for Plotly to be available
        function esperarPlotly() {{
            if (window.Plotly) {{
                // Plotly is loaded, wait for DOM to be ready
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', function() {{
                        configurarInteractividad();
                        configurarOrdenamientoTabla();
                    }});
                }} else {{
                    // DOM is already ready, but wait a bit more for Plotly to render
                    setTimeout(function() {{
                        configurarInteractividad();
                        configurarOrdenamientoTabla();
                    }}, 300);
                }}
            }} else {{
                // Plotly is not loaded yet, try again
                setTimeout(esperarPlotly, 100);
            }}
        }}

        // Start waiting when page loads
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', function() {{
                esperarPlotly();
                configurarOrdenamientoTabla();
            }});
        }} else {{
            esperarPlotly();
            configurarOrdenamientoTabla();
        }}
    </script>
</body>
</html>"""

    # Guardar el HTML en la carpeta docs
    os.makedirs('docs', exist_ok=True)  # Crear carpeta docs si no existe
    nombre_archivo = "docs/grafico_interactivo.html"
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(html_completo)
    
    print(f"\n✅ Interactive HTML chart generated: '{nombre_archivo}'")
    print(f"   Open the file in your browser to view the interactive chart.")
    print(f"   Click on the bars to view subcategory details and the studies table.")


def main() -> None:
    filas = leer_csv(CSV_FILE)
    if not filas:
        print("The file contains no data.")
        return

    categorias, subcategorias_por_categoria, estudios_por_categoria, suitability_por_categoria = agrupar_estudios(filas)
    crear_grafico_html_interactivo(categorias, subcategorias_por_categoria, estudios_por_categoria, suitability_por_categoria)


if __name__ == "__main__":
    main()

