#!/bin/bash
# Escanea la carpeta actual y agrupa coincidencias por archivo

# Palabras clave a buscar
KEYWORDS="interactive button url call reply"

# Recorre todos los archivos de texto en la carpeta
for file in $(find . -type f -name "*.py" -o -name "*.json" -o -name "*.env"); do
  matches=$(grep -nE "$(echo $KEYWORDS | sed 's/ /|/g')" "$file")
  if [ -n "$matches" ]; then
    echo "=== Archivo: $file ==="
    echo "$matches"
    echo
  fi
done
