# Guide Développeur IeuOpen - Configuration du Plugin

## 🎯 Objectif

Ce guide vous explique comment configurer le plugin EZVIZ Enhanced avec vos clés de développeur IeuOpen pour récupérer les flux de votre caméra CP2.

## 🔑 Prérequis

- ✅ Compte développeur IeuOpen actif
- ✅ App Key et App Secret générés
- ✅ Caméra EZVIZ CP2 (serial: VOTRE_SERIAL) associée à votre compte
- ✅ Permissions d'accès aux flux configurées

## 📋 Configuration du Plugin

### 1. Récupération de vos Clés

Connectez-vous à votre compte développeur IeuOpen :
1. Allez sur [ieuopen.ezviz.com](https://ieuopen.ezviz.com)
2. Connectez-vous avec votre compte développeur
3. Allez dans "My Applications" ou "Mes Applications"
4. Sélectionnez votre application
5. Copiez votre **App Key** et **App Secret**

### 2. Test de vos Clés

Modifiez le script de test avec vos vraies clés :

```bash
# Éditer le script de test
nano test_ieuopen_developer.py

# Modifier ces lignes :
app_key = "votre_vraie_app_key"
app_secret = "votre_vraie_app_secret"
```

Puis testez :

```bash
python3 test_ieuopen_developer.py
```

### 3. Configuration du Plugin

#### Configuration YAML

```yaml
# configuration.yaml
ezviz_enhanced:
  # Authentification IeuOpen (priorité)
  ieuopen_app_key: "votre_app_key"
  ieuopen_app_secret: "votre_app_secret"
  
  # Authentification EZVIZ Cloud (fallback)
  username: "votre_email@example.com"
  password: "votre_mot_de_passe"
  
  # Configuration des flux
  use_ieuopen: true
  rtsp_port: 8554
  
  # Caméras
  cameras:
    - serial: "VOTRE_SERIAL"
      name: "Caméra Entrée"
      channel: 1
      enabled: true
```

#### Configuration via Interface

1. Allez dans **Paramètres** > **Appareils & Services**
2. Cliquez sur **Ajouter une intégration**
3. Recherchez **EZVIZ Enhanced**
4. Entrez vos clés IeuOpen :
   - **App Key** : Votre clé d'application
   - **App Secret** : Votre secret d'application
5. Ajoutez votre caméra VOTRE_SERIAL

## 🔧 Mise à Jour du Plugin

### Ajout du Support IeuOpen

Modifiez le fichier `custom_components/ezviz_enhanced/const.py` :

```python
# Configuration keys
CONF_IEUOPEN_APP_KEY = "ieuopen_app_key"
CONF_IEUOPEN_APP_SECRET = "ieuopen_app_secret"

# IeuOpen API endpoints
IEUOPEN_API_BASE = "https://ieuopen.ezviz.com/api"
IEUOPEN_AUTH_URL = f"{IEUOPEN_API_BASE}/auth/token"
IEUOPEN_DEVICE_URL = f"{IEUOPEN_API_BASE}/device/list"
IEUOPEN_STREAM_URL = f"{IEUOPEN_API_BASE}/device/stream"
```

### Mise à Jour de l'API

Modifiez le fichier `custom_components/ezviz_enhanced/api.py` :

```python
class IeuOpenApi:
    def __init__(self, app_key: str = None, app_secret: str = None):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = None
    
    async def async_authenticate(self) -> bool:
        """Authenticate with IeuOpen using developer keys."""
        try:
            session = await self.async_get_session()
            
            # Authentification avec clés de développeur
            auth_data = {
                "appKey": self.app_key,
                "appSecret": self.app_secret
            }
            
            async with session.post(IEUOPEN_AUTH_URL, json=auth_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("resultCode") == "0":
                        self.access_token = data.get("accessToken")
                        return True
        except Exception as e:
            _LOGGER.error(f"IeuOpen authentication error: {e}")
        
        return False
    
    async def async_get_stream_info(self, serial: str, channel: int = 1) -> Dict[str, Any]:
        """Get stream information from IeuOpen."""
        if not self.access_token:
            await self.async_authenticate()
        
        if not self.access_token:
            return {}
        
        try:
            session = await self.async_get_session()
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-API-Key": self.access_token
            }
            
            # Récupérer les informations de flux
            stream_url = f"{IEUOPEN_STREAM_URL}/{serial}/{channel}"
            async with session.get(stream_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "serial": serial,
                        "channel": channel,
                        "status": "online",
                        "stream_type": data.get("streamType", "hls"),
                        "hls_url": data.get("hlsUrl"),
                        "rtsp_url": data.get("rtspUrl"),
                        "cloud_url": data.get("cloudUrl")
                    }
        except Exception as e:
            _LOGGER.error(f"Error getting stream info: {e}")
        
        return {}
```

## 🧪 Tests de Validation

### Test 1: Authentification

```bash
python3 test_ieuopen_developer.py
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

## 🔄 Flux de Données

```
Vos Clés IeuOpen → Authentification → API IeuOpen → Flux HLS/RTSP → Conversion FFmpeg → RTSP → Home Assistant
```

### Détail du Processus

1. **Authentification** : Le plugin s'authentifie avec vos clés IeuOpen
2. **Récupération des Flux** : Il récupère les URLs de flux depuis l'API IeuOpen
3. **Conversion** : Il convertit les flux en RTSP via FFmpeg
4. **Exposition** : Il expose les flux RTSP sur le port 8554
5. **Intégration** : Home Assistant accède aux flux RTSP

## 🚨 Dépannage

### Problème d'Authentification

**Symptômes** :
- Erreur "Authentication failed"
- Code de résultat non-0

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

## 📊 URLs Générées

Après configuration réussie :

- **URL IeuOpen** : `https://ieuopen.ezviz.com/console/setnormallive.html?serial=VOTRE_SERIAL&channelNo=1&addressType=1`
- **URL RTSP** : `rtsp://homeassistant.local:8554/ezviz_enhanced_VOTRE_SERIAL`
- **URL HLS** : URL récupérée depuis l'API IeuOpen

## 🎉 Résultat Final

Avec vos clés de développeur IeuOpen :

- ✅ **Accès direct** aux flux via l'API IeuOpen
- ✅ **Authentification sécurisée** avec vos clés
- ✅ **Conversion automatique** en RTSP
- ✅ **Intégration Home Assistant** native
- ✅ **Support Homebridge** via RTSP

**Votre caméra VOTRE_SERIAL sera accessible via l'API IeuOpen avec vos clés de développeur !** 🎯

## 📞 Support

- **Documentation IeuOpen** : [ieuopen.ezviz.com](https://ieuopen.ezviz.com)
- **Support IeuOpen** : [support.ezviz.com](https://support.ezviz.com)
- **Issues GitHub** : [Créer une issue](https://github.com/votre-username/ha-ezviz-enhanced/issues)
