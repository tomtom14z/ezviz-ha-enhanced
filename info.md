# EZVIZ Enhanced - Changelog

## Version 1.0.1 (2024-10-03)

### 🐛 Corrections
- **Ajout des modules manquants** : binary_sensor, sensor, switch
- **Correction de l'erreur** ModuleNotFoundError lors de l'installation
- **Amélioration de la compatibilité** HACS

### 📋 Changements
- ✅ Ajout de `binary_sensor.py` - Capteurs binaires (statut en ligne)
- ✅ Ajout de `sensor.py` - Capteurs d'informations (type de flux)
- ✅ Ajout de `switch.py` - Interrupteurs (activer/désactiver flux)
- ✅ Mise à jour du `manifest.json` vers la version 1.0.1

### 🚀 Installation
1. Mettez à jour via HACS
2. Redémarrez Home Assistant
3. Reconfigurez l'intégration si nécessaire

---

## Version 1.0.0 (2024-10-03)

### 🎉 Version Initiale
- Support de l'API EZVIZ Open Platform (IeuOpen)
- Récupération automatique des flux HLS
- Support des clés de développeur
- Intégration avec Home Assistant
- Support Homebridge
