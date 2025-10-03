#!/bin/bash

# Script d'installation pour EZVIZ Enhanced Integration
# Ce script aide à installer et configurer le plugin dans Home Assistant

set -e

echo "🚀 Installation d'EZVIZ Enhanced Integration pour Home Assistant"
echo "================================================================"

# Vérifier si Home Assistant est installé
if [ ! -d "/config" ] && [ ! -d "$HOME/.homeassistant" ]; then
    echo "❌ Home Assistant n'est pas détecté. Veuillez installer Home Assistant d'abord."
    exit 1
fi

# Déterminer le répertoire de configuration Home Assistant
if [ -d "/config" ]; then
    HA_CONFIG_DIR="/config"
elif [ -d "$HOME/.homeassistant" ]; then
    HA_CONFIG_DIR="$HOME/.homeassistant"
else
    echo "❌ Répertoire de configuration Home Assistant non trouvé."
    exit 1
fi

echo "📁 Répertoire de configuration Home Assistant: $HA_CONFIG_DIR"

# Créer le répertoire custom_components s'il n'existe pas
CUSTOM_COMPONENTS_DIR="$HA_CONFIG_DIR/custom_components"
if [ ! -d "$CUSTOM_COMPONENTS_DIR" ]; then
    echo "📁 Création du répertoire custom_components..."
    mkdir -p "$CUSTOM_COMPONENTS_DIR"
fi

# Copier le plugin
echo "📦 Installation du plugin EZVIZ Enhanced..."
cp -r custom_components/ezviz_enhanced "$CUSTOM_COMPONENTS_DIR/"

echo "✅ Plugin installé avec succès!"

# Vérifier si FFmpeg est installé
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg n'est pas installé. Il est requis pour la conversion RTSP."
    echo "   Veuillez installer FFmpeg:"
    echo "   - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Windows: Téléchargez depuis https://ffmpeg.org/"
fi

# Créer un exemple de configuration
echo "📝 Création d'un exemple de configuration..."

cat > "$HA_CONFIG_DIR/ezviz_enhanced_example.yaml" << EOF
# Exemple de configuration pour EZVIZ Enhanced
# Copiez cette configuration dans votre configuration.yaml

ezviz_enhanced:
  username: "votre_email@example.com"
  password: "votre_mot_de_passe"
  use_ieuopen: true
  rtsp_port: 8554
  cameras:
    - serial: "VOTRE_SERIAL"  # Remplacez par le serial de votre caméra
      name: "Caméra Entrée"
      channel: 1
      enabled: true

# Configuration pour les logs de débogage (optionnel)
logger:
  logs:
    custom_components.ezviz_enhanced: debug
EOF

echo "📄 Exemple de configuration créé: $HA_CONFIG_DIR/ezviz_enhanced_example.yaml"

# Instructions finales
echo ""
echo "🎉 Installation terminée!"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Redémarrez Home Assistant"
echo "2. Allez dans Paramètres > Appareils & Services"
echo "3. Cliquez sur 'Ajouter une intégration'"
echo "4. Recherchez 'EZVIZ Enhanced'"
echo "5. Suivez les instructions de configuration"
echo ""
echo "📖 Pour plus d'informations, consultez le README.md"
echo ""
echo "🔧 Configuration de votre caméra CP2:"
echo "   - Serial: VOTRE_SERIAL (remplacez par votre serial)"
echo "   - URL IeuOpen: https://ieuopen.ezviz.com/console/setnormallive.html?serial=VOTRE_SERIAL&channelNo=1&addressType=1"
echo ""
echo "💡 Le plugin générera automatiquement une URL RTSP pour Homebridge:"
echo "   rtsp://homeassistant.local:8554/ezviz_enhanced_VOTRE_SERIAL"
