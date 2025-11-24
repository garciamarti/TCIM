#!/bin/bash
# Script para verificar Homebrew e instalar Python

echo "Verificando instalación de Homebrew..."

# Verificar si Homebrew está instalado
if command -v brew &> /dev/null; then
    echo "✓ Homebrew está instalado"
    
    # Verificar si Python ya está instalado via Homebrew
    if brew list python@3.12 &> /dev/null || brew list python@3.11 &> /dev/null || brew list python@3.10 &> /dev/null; then
        echo "✓ Python ya está instalado via Homebrew"
        python3 --version
    else
        echo "Instalando Python via Homebrew..."
        brew install python
        echo "✓ Python instalado correctamente"
        python3 --version
    fi
else
    echo "✗ Homebrew no está instalado"
    echo ""
    echo "Por favor, instala Homebrew primero ejecutando:"
    echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo ""
echo "Verificando que Python funciona correctamente..."
python3 contar_lineas.py

