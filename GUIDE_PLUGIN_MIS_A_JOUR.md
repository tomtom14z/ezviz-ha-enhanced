# 🎯 Guide Plugin Home Assistant Mis à Jour

## ✅ Plugin EZVIZ Enhanced avec Support IeuOpen

Le plugin a été mis à jour pour utiliser automatiquement l'API EZVIZ Open Platform (IeuOpen) avec vos clés de développeur !

## 🔧 Installation

### 1. Copier le Plugin

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

## 🎥 Fonctionnalités du Plugin Mis à Jour

### ✅ **Récupération Automatique des Flux**

Le plugin essaie automatiquement différents protocoles et qualités :

1. **HLS Fluent** (sub-bitrate) - ⭐ **PRIORITÉ**
2. **HLS HD** (main bitrate)
3. **FLV Fluent** (sub-bitrate)
4. **FLV HD** (main bitrate)

### ✅ **Support Direct HLS**

- **URLs HLS** utilisées directement par Home Assistant
- **Pas de conversion** RTSP nécessaire pour HLS
- **Meilleure performance** et stabilité

### ✅ **Régénération Automatique**

- **URLs expirées** détectées automatiquement
- **Nouvelles URLs** générées toutes les heures
- **Fallback** vers d'autres protocoles si nécessaire

## 🔄 Flux de Données

```
Vos Clés IeuOpen → API EZVIZ Open → HLS Fluent → Home Assistant (direct)
```

### Détail du Processus

1. **Authentification** : Plugin s'authentifie avec vos clés IeuOpen
2. **Test des Protocoles** : Essaie HLS Fluent en premier
3. **Récupération des URLs** : URLs HLS récupérées depuis l'API
4. **Utilisation Directe** : Home Assistant utilise l'URL HLS directement
5. **Régénération** : Nouvelles URLs générées automatiquement

## 📊 URLs Générées

Après configuration réussie :

- **URL HLS Fluent** : `https://ieuopen.ezvizlife.com/v3/openlive/VOTRE_SERIAL_1_2.m3u8?...`
- **URL IeuOpen** : `https://ieuopen.ezviz.com/console/setnormallive.html?serial=VOTRE_SERIAL&channelNo=1&addressType=1`
- **URL RTSP** : Générée si nécessaire (fallback)

## 🧪 Tests de Validation

### Test 1: Authentification API
```bash
python3 get_live_broadcast_urls.py
```

**Résultat attendu** :
- ✅ Authentification réussie
- ✅ URLs HLS Fluent récupérées
- ✅ URLs accessibles

### Test 2: Intégration Home Assistant
**Résultat attendu** :
- ✅ Caméra détectée dans Home Assistant
- ✅ Flux HLS visible
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

### Problème d'Affichage

**Symptômes** :
- Caméra détectée mais pas de flux
- Erreur de lecture

**Solutions** :
1. Vérifiez les logs Home Assistant
2. Testez l'URL HLS manuellement
3. Régénérez les URLs avec le script

## 📱 Configuration Homebridge

### Plugin Homebridge Camera FFmpeg

```json
{
  "platform": "Camera-ffmpeg",
  "cameras": [
    {
      "name": "EZVIZ Caméra",
      "videoConfig": {
        "source": "-i https://ieuopen.ezvizlife.com/v3/openlive/VOTRE_SERIAL_1_2.m3u8?expire=...",
        "stillImageSource": "-i https://ieuopen.ezvizlife.com/v3/openlive/VOTRE_SERIAL_1_2.m3u8?expire=... -vframes 1 -y %s",
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
- ✅ **URLs HLS** utilisées directement par Home Assistant
- ✅ **Régénération automatique** des URLs expirées
- ✅ **Support Homebridge** via URLs HLS
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

**🎊 Félicitations ! Votre caméra EZVIZ CP2 est maintenant intégrée avec succès via IeuOpen !** 🎊
