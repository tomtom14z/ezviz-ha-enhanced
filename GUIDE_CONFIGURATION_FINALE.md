# 🎯 Guide de Configuration Finale - EZVIZ Enhanced

## ✅ Solution Complète Implémentée

Votre plugin EZVIZ Enhanced est maintenant configuré pour utiliser l'API EZVIZ Open Platform (IeuOpen) avec vos clés de développeur !

## 🔧 Configuration du Plugin

### 1. Installation

```bash
# Copier le plugin dans Home Assistant
cp -r custom_components/ezviz_enhanced /config/custom_components/

# Redémarrer Home Assistant
```

### 2. Configuration via Interface

1. Allez dans **Paramètres** > **Appareils & Services**
2. Cliquez sur **Ajouter une intégration**
3. Recherchez **EZVIZ Enhanced**
4. Configurez avec vos informations :

```
Username: votre_email@example.com
Password: votre_mot_de_passe
Use IeuOpen: ✅ Activé
App Key: votre_app_key_ieuopen
App Secret: votre_app_secret_ieuopen
RTSP Port: 8554
```

### 3. Configuration YAML (Alternative)

```yaml
# configuration.yaml
ezviz_enhanced:
  username: "votre_email@example.com"
  password: "votre_mot_de_passe"
  use_ieuopen: true
  app_key: "votre_app_key_ieuopen"
  app_secret: "votre_app_secret_ieuopen"
  rtsp_port: 8554
  cameras:
    - serial: "VOTRE_SERIAL"
      name: "Caméra Entrée"
      channel: 1
      enabled: true
```

## 🎥 Fonctionnalités Disponibles

### ✅ **Accès aux Flux via IeuOpen**
- Authentification avec vos clés de développeur
- Récupération automatique des URLs de flux HLS
- Support des flux en direct et enregistrés

### ✅ **Conversion RTSP**
- Conversion automatique HLS → RTSP via FFmpeg
- Exposition sur le port 8554
- Compatible avec Home Assistant et Homebridge

### ✅ **Intégration Home Assistant**
- Entité caméra native
- Contrôles de lecture/pause
- Historique des événements
- Notifications de mouvement

### ✅ **Support Homebridge**
- Flux RTSP accessible depuis Homebridge
- Intégration Apple HomeKit
- Contrôles iOS/macOS

## 🔄 Flux de Données

```
Vos Clés IeuOpen → API EZVIZ Open → Flux HLS → FFmpeg → RTSP → Home Assistant/Homebridge
```

### Détail du Processus

1. **Authentification** : Plugin s'authentifie avec vos clés IeuOpen
2. **Récupération des Flux** : URLs HLS récupérées depuis l'API
3. **Conversion** : FFmpeg convertit HLS en RTSP
4. **Exposition** : Flux RTSP disponible sur port 8554
5. **Intégration** : Home Assistant accède aux flux

## 📊 URLs Générées

Après configuration réussie :

- **URL IeuOpen** : `https://ieuopen.ezviz.com/console/setnormallive.html?serial=VOTRE_SERIAL&channelNo=1&addressType=1`
- **URL RTSP** : `rtsp://homeassistant.local:8554/ezviz_enhanced_VOTRE_SERIAL`
- **URL HLS** : URL récupérée depuis l'API IeuOpen

## 🧪 Tests de Validation

### Test 1: Authentification API
```bash
python3 test_ezviz_open_api.py
```

**Résultat attendu** :
- ✅ Authentification réussie
- ✅ Token d'accès récupéré
- ✅ Liste des appareils accessible

### Test 2: Flux de la Caméra
**Résultat attendu** :
- ✅ Informations de flux récupérées
- ✅ URLs HLS/RTSP disponibles
- ✅ Flux accessible

### Test 3: Intégration Home Assistant
**Résultat attendu** :
- ✅ Caméra détectée dans Home Assistant
- ✅ Flux vidéo visible
- ✅ Contrôles fonctionnels

## 🚨 Dépannage

### Problème d'Authentification

**Symptômes** :
- Erreur "Authentication failed"
- Code de résultat non-200

**Solutions** :
1. Vérifiez vos clés App Key et App Secret
2. Vérifiez que votre compte développeur est actif
3. Vérifiez les permissions de votre application

### Problème de Flux

**Symptômes** :
- Aucun flux trouvé
- Erreur "Stream not available"

**Solutions** :
1. Vérifiez que la caméra est associée à votre compte
2. Vérifiez les permissions d'accès aux flux
3. Vérifiez que la caméra est en ligne

### Problème de Conversion RTSP

**Symptômes** :
- Flux RTSP non accessible
- Erreur FFmpeg

**Solutions** :
1. Vérifiez que FFmpeg est installé
2. Vérifiez que le port 8554 est ouvert
3. Vérifiez les logs de conversion

## 📱 Configuration Homebridge

### Plugin Homebridge Camera FFmpeg

```json
{
  "platform": "Camera-ffmpeg",
  "cameras": [
    {
      "name": "EZVIZ Caméra",
      "videoConfig": {
        "source": "-i rtsp://homeassistant.local:8554/ezviz_enhanced_VOTRE_SERIAL",
        "stillImageSource": "-i rtsp://homeassistant.local:8554/ezviz_enhanced_VOTRE_SERIAL -vframes 1 -y %s",
        "maxStreams": 2,
        "maxWidth": 1280,
        "maxHeight": 720,
        "maxFPS": 30
      }
    }
  ]
}
```

## 🎉 Résultat Final

Avec cette configuration :

- ✅ **Accès direct** aux flux via l'API IeuOpen
- ✅ **Authentification sécurisée** avec vos clés de développeur
- ✅ **Conversion automatique** en RTSP
- ✅ **Intégration Home Assistant** native
- ✅ **Support Homebridge** via RTSP
- ✅ **Compatibilité Apple HomeKit**

**Votre caméra VOTRE_SERIAL est maintenant accessible via l'API IeuOpen avec vos clés de développeur !** 🎯

## 📞 Support

- **Documentation IeuOpen** : [ieuopen.ezviz.com](https://ieuopen.ezviz.com)
- **Support EZVIZ** : [support.ezviz.com](https://support.ezviz.com)
- **Issues GitHub** : [Créer une issue](https://github.com/votre-username/ha-ezviz-enhanced/issues)

## 🔄 Mise à Jour

Pour mettre à jour le plugin :

```bash
# Sauvegarder la configuration
cp /config/custom_components/ezviz_enhanced/config.json /tmp/

# Mettre à jour le plugin
git pull origin main

# Restaurer la configuration
cp /tmp/config.json /config/custom_components/ezviz_enhanced/

# Redémarrer Home Assistant
```

---

**🎊 Félicitations ! Votre caméra EZVIZ CP2 est maintenant intégrée avec succès !** 🎊
