# EZVIZ Enhanced - Home Assistant Integration

## 🎯 Description

Plugin Home Assistant pour les caméras EZVIZ avec support de l'API EZVIZ Open Platform (IeuOpen).

> **Fork amélioré** du plugin [ha-ezviz](https://github.com/RenierM26/ha-ezviz) de [RenierM26](https://github.com/RenierM26) avec ajout du support de l'API EZVIZ Open Platform (IeuOpen) pour les caméras qui ne supportent que le cloud.

## ✨ Fonctionnalités

- ✅ Support de l'API EZVIZ Open Platform (IeuOpen)
- ✅ Récupération automatique des flux HLS
- ✅ Support des clés de développeur
- ✅ Régénération automatique des URLs expirées
- ✅ Support multi-protocoles (HLS, FLV, RTMP)
- ✅ Intégration directe avec Home Assistant
- ✅ Support Homebridge

## 🔧 Installation

### Via HACS (Recommandé)

1. Ouvrez HACS dans Home Assistant
2. Allez dans "Intégrations"
3. Cliquez sur "..." → "Intégrations personnalisées"
4. Ajoutez l'URL : `https://github.com/tomtom14z/ezviz-ha-enhanced`
5. Installez le plugin

### Via Git

```bash
cd /config/custom_components
git clone https://github.com/tomtom14z/ezviz-ha-enhanced.git ezviz_enhanced
```

## 📋 Configuration

1. Redémarrez Home Assistant
2. Allez dans Paramètres → Appareils & Services
3. Ajoutez l'intégration "EZVIZ Enhanced"
4. Configurez avec vos clés IeuOpen

## 🎥 Caméras Supportées

- EZVIZ CP2 (2025)
- Toutes les caméras EZVIZ compatibles avec IeuOpen

## 📞 Support

- Issues : [GitHub Issues](https://github.com/tomtom14z/ezviz-ha-enhanced/issues)
- Documentation : Voir les guides dans le repository

## 🙏 Crédits

- **Plugin original** : [RenierM26/ha-ezviz](https://github.com/RenierM26/ha-ezviz) par [RenierM26](https://github.com/RenierM26)
- **API EZVIZ Open Platform** : Documentation officielle [EZVIZ Open Platform](https://open.ezvizlife.com)
- **Améliorations** : Support IeuOpen, flux HLS, authentification développeur

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.
