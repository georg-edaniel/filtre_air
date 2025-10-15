#!/bin/bash

echo "🔧 Lancement du serveur Django pour ESP32..."

# Affiche l'IP WSL visible par l'ESP32
WSL_IP=$(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1)
echo "🌐 IP WSL détectée : $WSL_IP"
echo "👉 Utilise cette IP dans ton ESP32 : http://$WSL_IP:8000"

# Vérifie que le port 8000 est libre
echo "🔍 Vérification du port 8000..."
if lsof -i:8000 | grep LISTEN; then
  echo "⚠️ Le port 8000 est déjà utilisé. Tu dois le libérer ou changer de port."
  exit 1
fi

# Lancer Django sur toutes les interfaces
echo "🚀 Démarrage de Django sur 0.0.0.0:8000..."
python3 manage.py runserver 0.0.0.0:8000
