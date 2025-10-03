# Guide d'Authentification IeuOpen - EZVIZ Enhanced

## 🎯 Objectif

Ce guide vous explique comment utiliser la plateforme IeuOpen d'EZVIZ avec authentification pour récupérer les flux de votre caméra CP2 2025, contournant ainsi le problème RTSP local.

## 🔐 Méthodes d'Authentification

### 1️⃣ **Compte Développeur IeuOpen (Recommandé)**

#### Étape 1: Créer un compte développeur
1. Allez sur [ieuopen.ezviz.com](https://ieuopen.ezviz.com)
2. Cliquez sur "Developer" ou "Développeur"
3. Créez un compte développeur
4. Validez votre compte par email

#### Étape 2: Créer une application
1. Connectez-vous à votre compte développeur
2. Allez dans "My Applications" ou "Mes Applications"
3. Créez une nouvelle application
4. Notez votre **App Key** et **App Secret**

#### Étape 3: Obtenir un token d'accès
```python
# Exemple d'authentification avec clé API
import requests

app_key = "votre_app_key"
app_secret = "votre_app_secret"

auth_data = {
    "appKey": app_key,
    "appSecret": app_secret
}

response = requests.post("https://ieuopen.ezviz.com/api/auth/token", json=auth_data)
access_token = response.json()["accessToken"]
```

### 2️⃣ **Compte EZVIZ Personnel (Fallback)**

Si vous n'avez pas de compte développeur, vous pouvez utiliser votre compte EZVIZ personnel :

```python
# Authentification avec compte EZVIZ
auth_data = {
    "account": "votre_email@example.com",
    "password": "votre_mot_de_passe"
}

response = requests.post("https://api.ezvizlife.com/api/login", json=auth_data)
access_token = response.json()["accessToken"]
```

## 🧪 Test d'Authentification

### Script de Test Automatique

```bash
# Exécuter le script de test
python3 test_ieuopen_auth.py
```

Le script vous demandera :
- Nom d'utilisateur EZVIZ
- Mot de passe EZVIZ
- Clé API IeuOpen (optionnel)
- Serial de la caméra (VOTRE_SERIAL)

### Test Manuel

```python
import asyncio
from test_ieuopen_auth import IeuOpenAuthTester

async def test_my_camera():
    async with IeuOpenAuthTester() as tester:
        # Test d'authentification
        success = await tester.test_ezviz_cloud_auth("votre_email", "votre_mot_de_passe")
        
        if success:
            # Test de récupération des flux
            stream_info = await tester.test_get_stream_info("VOTRE_SERIAL")
            print(f"Informations de flux: {stream_info}")

asyncio.run(test_my_camera())
```

## ⚙️ Configuration du Plugin

### Configuration YAML

```yaml
# configuration.yaml
ezviz_enhanced:
  username: "votre_email@example.com"
  password: "votre_mot_de_passe"
  use_ieuopen: true
  ieuopen_api_key: "votre_clé_api"  # Optionnel
  rtsp_port: 8554
  cameras:
    - serial: "VOTRE_SERIAL"
      name: "Caméra Entrée"
      channel: 1
      enabled: true
```

### Configuration via Interface

1. Allez dans **Paramètres** > **Appareils & Services**
2. Cliquez sur **Ajouter une intégration**
3. Recherchez **EZVIZ Enhanced**
4. Entrez vos identifiants EZVIZ
5. Ajoutez votre caméra VOTRE_SERIAL

## 🔄 Flux de Données

```
Vos Identifiants EZVIZ → Authentification IeuOpen → Récupération des Flux → Conversion RTSP → Home Assistant
```

### Détail du Processus

1. **Authentification** : Le plugin s'authentifie avec vos identifiants EZVIZ
2. **Récupération des Flux** : Il récupère les URLs de flux depuis IeuOpen
3. **Conversion** : Il convertit les flux en RTSP via FFmpeg
4. **Exposition** : Il expose les flux RTSP sur le port 8554
5. **Intégration** : Home Assistant accède aux flux RTSP

## 📊 Types de Flux Disponibles

### Flux HLS (HTTP Live Streaming)
- **Format** : `https://ieuopen.ezviz.com/hls/VOTRE_SERIAL/1/index.m3u8`
- **Avantage** : Compatible avec la plupart des lecteurs
- **Conversion** : Converti en RTSP par FFmpeg

### Flux RTSP (Si disponible)
- **Format** : `rtsp://ieuopen.ezviz.com/stream/VOTRE_SERIAL/1`
- **Avantage** : Direct, pas de conversion nécessaire
- **Limitation** : Pas toujours disponible

### Flux Cloud
- **Format** : URL spécifique à EZVIZ
- **Avantage** : Accès cloud fiable
- **Conversion** : Converti en RTSP par FFmpeg

## 🚨 Dépannage

### Problème d'Authentification

**Symptômes** :
- Erreur "Authentication failed"
- Token d'accès invalide

**Solutions** :
1. Vérifiez vos identifiants EZVIZ
2. Testez la connexion sur l'app mobile EZVIZ
3. Créez un compte développeur IeuOpen
4. Utilisez une clé API au lieu des identifiants

### Problème de Récupération des Flux

**Symptômes** :
- Aucun flux trouvé
- Erreur "Stream not available"

**Solutions** :
1. Vérifiez que la caméra est en ligne
2. Vérifiez le serial de la caméra
3. Vérifiez les permissions de votre compte
4. Contactez le support EZVIZ

### Problème de Conversion RTSP

**Symptômes** :
- Flux RTSP non accessible
- Erreur FFmpeg

**Solutions** :
1. Vérifiez que FFmpeg est installé
2. Vérifiez que le port 8554 est ouvert
3. Vérifiez les logs de conversion
4. Redémarrez le service de conversion

## 📋 Checklist de Configuration

- [ ] **Compte EZVIZ** : Identifiants valides
- [ ] **Caméra en ligne** : Caméra accessible via l'app EZVIZ
- [ ] **Serial correct** : VOTRE_SERIAL (ou votre serial)
- [ ] **Plugin installé** : EZVIZ Enhanced dans Home Assistant
- [ ] **FFmpeg installé** : Pour la conversion des flux
- [ ] **Port ouvert** : 8554 pour RTSP
- [ ] **Test réussi** : Script de test fonctionne

## 🎉 Résultat Final

Une fois configuré, vous aurez :

- ✅ **Accès aux flux** via la plateforme IeuOpen
- ✅ **Authentification sécurisée** avec vos identifiants EZVIZ
- ✅ **Conversion automatique** en RTSP
- ✅ **Intégration Home Assistant** native
- ✅ **Support Homebridge** via RTSP

**Votre caméra VOTRE_SERIAL sera accessible via IeuOpen avec authentification !** 🎉

## 🔗 URLs Générées

Après configuration réussie :

- **URL IeuOpen** : `https://ieuopen.ezviz.com/console/setnormallive.html?serial=VOTRE_SERIAL&channelNo=1&addressType=1`
- **URL RTSP** : `rtsp://homeassistant.local:8554/ezviz_enhanced_VOTRE_SERIAL`
- **URL HLS** : `https://ieuopen.ezviz.com/hls/VOTRE_SERIAL/1/index.m3u8` (si disponible)

## 📞 Support

- **Documentation EZVIZ** : [ieuopen.ezviz.com](https://ieuopen.ezviz.com)
- **Support EZVIZ** : [support.ezviz.com](https://support.ezviz.com)
- **Issues GitHub** : [Créer une issue](https://github.com/votre-username/ha-ezviz-enhanced/issues)
