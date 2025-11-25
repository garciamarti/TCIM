#!/bin/bash
# Script para publicar archivos HTML a GitHub Pages

echo "🚀 Publicando archivos HTML a GitHub Pages..."
echo ""

# Crear carpeta docs si no existe
mkdir -p docs

# Copiar todos los archivos HTML al directorio docs
echo "📋 Copiando archivos HTML a docs/..."
find . -maxdepth 1 -name "*.html" -type f -exec cp {} docs/ \;

# Contar archivos copiados
html_count=$(ls -1 docs/*.html 2>/dev/null | wc -l | tr -d ' ')

if [ "$html_count" -eq 0 ]; then
    echo "⚠️  No se encontraron archivos HTML para publicar"
    exit 1
fi

echo "✅ $html_count archivo(s) HTML copiado(s) a docs/"
ls -1 docs/*.html

# Agregar cambios a git
echo ""
echo "📦 Agregando cambios a git..."
git add docs/

# Verificar si hay cambios
if git diff --staged --quiet; then
    echo "ℹ️  No hay cambios para commitear"
else
    echo "💾 Creando commit..."
    git commit -m "Update GitHub Pages: publish HTML files"
    
    echo "📤 Subiendo a GitHub..."
    git push origin main
    
    echo ""
    echo "✅ ¡Archivos HTML publicados exitosamente!"
    echo "   Tu sitio estará disponible en:"
    echo "   https://garciamarti.github.io/TCIM/"
    echo ""
    echo "   Nota: Puede tardar unos minutos en actualizarse."
else
    echo "ℹ️  No hay cambios para commitear"
fi


