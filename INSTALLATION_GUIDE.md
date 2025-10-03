# Guide d'Installation - EZVIZ Enhanced Integration

## 🎯 Objectif

Ce plugin résout le problème des caméras EZVIZ CP2 2025 qui ne fonctionnent qu'avec le cloud en :
1. Récupérant les flux via la plateforme ouverte EZVIZ (ieuopen.ezviz.com)
2. Convertissant automatiquement ces flux en RTSP
3. Les rendant accessibles dans Home Assistant et Homebridge

## 📋 Prérequis

- Home Assistant installé et fonctionnel
- Caméra EZVIZ CP2 2025 avec serial connu
- FFmpeg installé sur le système
- Accès internet pour la plateforme IeuOpen

## 🚀 Installation Rapide

### Étape 1: Télécharger le Plugin

```bash
# Cloner le dépôt
git clone https://github.com/votre-username/ha-ezviz-enhanced.git
cd ha-ezviz-enhanced

# Ou télécharger le ZIP et l'extraire
```

### Étape 2: Installation Automatique

```bash
# Exécuter le script d'installation
./install.sh
```

### Étape 3: Installation Manuelle (Alternative)

```bash
# Copier le plugin dans Home Assistant
cp -r custom_components/ezviz_enhanced /config/custom_components/

# Redémarrer Home Assistant
```

## ⚙️ Configuration

### Étape 1: Configuration dans Home Assistant

1. Redémarrez Home Assistant
2. Allez dans **Paramètres** > **Appareils & Services**
3. Cliquez sur **Ajouter une intégration**
4. Recherchez **EZVIZ Enhanced**
5. Suivez l'assistant de configuration

### Étape 2: Informations Requises

- **Nom d'utilisateur EZVIZ** : Votre email de compte EZVIZ
- **Mot de passe EZVIZ** : Votre mot de passe de compte EZVIZ
- **Serial de la caméra** : VOTRE_SERIAL (remplacez par votre serial)
- **Canal** : 1 (généralement)
- **Port RTSP** : 8554 (par défaut)

### Étape 3: Configuration YAML (Optionnelle)

```yaml
# configuration.yaml
ezviz_enhanced:
  username: "votre_email@example.com"
  password: "votre_mot_de_passe"
  use_ieuopen: true
  rtsp_port: 8554
  cameras:
    - serial: "VOTRE_SERIAL"
      name: "Caméra Entrée"
      channel: 1
      enabled: true
```

## 🔧 Test de la Configuration

### Tester la Plateforme IeuOpen

```bash
# Exécuter le script de test
python3 test_ieuopen.py VOTRE_SERIAL

# Remplacer VOTRE_SERIAL par votre serial de caméra
```

### Vérifier les Logs

```yaml
# configuration.yaml
logger:
  logs:
    custom_components.ezviz_enhanced: debug
```

## 🏠 Intégration Homebridge

### Configuration Homebridge

```json
{
  "platform": "Camera-ffmpeg",
  "cameras": [
    {
      "name": "EZVIZ CP2",
      "videoConfig": {
        "source": "-i rtsp://homeassistant.local:8554/ezviz_enhanced_VOTRE_SERIAL",
        "maxStreams": 2,
        "maxWidth": 1280,
        "maxHeight": 720,
        "maxFPS": 30,
        "vcodec": "libx264",
        "audio": false
      }
    }
  ]
}
```

## 🔍 URLs Générées

Après configuration, le plugin génère automatiquement :

- **URL IeuOpen** : `https://ieuopen.ezviz.com/console/setnormallive.html?serial=VOTRE_SERIAL&channelNo=1&addressType=1`
- **URL RTSP** : `rtsp://homeassistant.local:8554/ezviz_enhanced_VOTRE_SERIAL`

## 🚨 Dépannage

### Problèmes Courants

1. **Caméra non détectée**
   - Vérifiez le serial de la caméra
   - Testez l'URL IeuOpen manuellement

2. **Flux RTSP non accessible**
   - Vérifiez que FFmpeg est installé
   - Vérifiez que le port 8554 est ouvert

3. **Erreur d'authentification**
   - Vérifiez vos identifiants EZVIZ
   - Testez la connexion sur l'app mobile

### Logs de Débogage

```bash
# Vérifier les logs Home Assistant
tail -f /config/home-assistant.log | grep ezviz_enhanced

# Vérifier les processus FFmpeg
ps aux | grep ffmpeg
```

## 📊 Fonctionnalités

### ✅ Fonctionnalités Implémentées

- Intégration avec l'API cloud EZVIZ
- Support de la plateforme IeuOpen
- Conversion automatique en RTSP
- Interface de configuration dans Home Assistant
- Support multi-caméras
- Logs de débogage détaillés

### 🔄 Flux de Données

1. **Récupération** : Le plugin récupère les flux depuis ieuopen.ezviz.com
2. **Conversion** : FFmpeg convertit les flux en RTSP
3. **Exposition** : Les flux RTSP sont exposés sur le port configuré
4. **Intégration** : Home Assistant et Homebridge accèdent aux flux RTSP

## 🆘 Support

### Ressources

- **Documentation** : README.md
- **Dépannage** : TROUBLESHOOTING.md
- **Issues** : [GitHub Issues](https://github.com/votre-username/ha-ezviz-enhanced/issues)

### Informations de Diagnostic

En cas de problème, fournissez :
1. Version Home Assistant
2. Serial de la caméra
3. Logs d'erreur complets
4. Résultat du script de test

## 🎉 Résultat Final

Après installation et configuration, vous aurez :

- ✅ Accès aux flux vidéo de votre caméra CP2 2025
- ✅ Intégration native dans Home Assistant
- ✅ Support Homebridge via RTSP
- ✅ Conversion automatique des flux
- ✅ Interface de configuration intuitive

Votre caméra EZVIZ CP2 2025 sera maintenant pleinement intégrée dans votre écosystème domotique !
