# Guide : Flux RTSP Local via go2rtc

## 🎯 Fonctionnalité

Le plugin EZVIZ Enhanced intègre **go2rtc** pour créer automatiquement des flux RTSP locaux à partir des flux HLS d'EZVIZ.

### **Avantages**
- ✅ **Usage CPU minimal** : go2rtc fait du "stream copy" (pas de réencodage)
- ✅ **Automatique** : Les flux sont créés et mis à jour automatiquement
- ✅ **Compatible** : Fonctionne avec Scrypted, Homebridge, Frigate, etc.
- ✅ **Local** : Pas besoin de cloud, tout reste sur votre réseau

---

## 📋 Prérequis

### **go2rtc doit être installé et actif**

go2rtc est inclus dans Home Assistant depuis la version 2023.3 via l'intégration WebRTC.

#### **Vérifier si go2rtc est actif** :

1. **Ouvrez** : `http://IP_HOME_ASSISTANT:1984/`
2. Si vous voyez l'interface go2rtc, c'est bon !
3. Sinon, ajoutez dans `configuration.yaml` :

```yaml
go2rtc:
```

4. **Redémarrez Home Assistant**

---

## 🚀 Utilisation

### **1. Récupérer l'URL RTSP Locale**

Une fois le plugin EZVIZ Enhanced installé :

1. **Allez dans** : **Outils de Développement** → **États**
2. **Cherchez** : `camera.oeilcp2` (ou le nom de votre caméra)
3. **Attribut** : `rtsp_local_url`

Vous verrez quelque chose comme :
```
rtsp://localhost:8554/ezviz_BE8269237
```

### **2. Utiliser dans d'Autres Applications**

#### **Pour Scrypted** :
1. **Ajoutez une caméra RTSP**
2. **URL** : `rtsp://IP_HOME_ASSISTANT:8554/ezviz_SERIAL`
3. Remplacez `IP_HOME_ASSISTANT` par l'IP de votre Home Assistant
4. Remplacez `SERIAL` par le numéro de série de votre caméra

#### **Pour Homebridge** :
```json
{
  "platform": "Camera-ffmpeg",
  "cameras": [
    {
      "name": "EZVIZ Camera",
      "videoConfig": {
        "source": "-rtsp_transport tcp -i rtsp://IP_HOME_ASSISTANT:8554/ezviz_BE8269237"
      }
    }
  ]
}
```

#### **Pour Frigate** :
```yaml
cameras:
  ezviz_camera:
    ffmpeg:
      inputs:
        - path: rtsp://IP_HOME_ASSISTANT:8554/ezviz_BE8269237
          roles:
            - detect
            - record
```

---

## 🔧 Configuration Avancée

### **go2rtc personnalisé**

Si vous voulez personnaliser go2rtc, ajoutez dans `configuration.yaml` :

```yaml
go2rtc:
  streams:
    # Les streams EZVIZ sont créés automatiquement par le plugin
    # Vous pouvez ajouter d'autres streams ici
```

### **Accès via Internet**

⚠️ **Attention** : Pour des raisons de sécurité, il est recommandé de ne PAS exposer go2rtc sur Internet.

Si vous en avez vraiment besoin :
1. Utilisez un VPN (WireGuard, Tailscale)
2. Ou configurez un reverse proxy avec authentification

---

## 📊 Performance

### **Usage CPU**

go2rtc utilise le **stream copy** (pas de réencodage), donc :
- **CPU** : ~1-2% par stream
- **RAM** : ~50-100 MB par stream
- **Réseau** : Dépend du bitrate du flux HLS d'EZVIZ

### **Comparaison avec FFmpeg**

| Méthode | CPU | Qualité | Latence |
|---------|-----|---------|---------|
| **go2rtc** | 1-2% | Identique | Faible |
| **FFmpeg réencodage** | 30-50% | Variable | Moyenne |

---

## 🐛 Dépannage

### **go2rtc non détecté**

**Logs** :
```
🔴 EZVIZ Enhanced: go2rtc non disponible
```

**Solution** :
1. Vérifiez que go2rtc est actif : `http://IP_HOME_ASSISTANT:1984/`
2. Ajoutez `go2rtc:` dans `configuration.yaml`
3. Redémarrez Home Assistant

### **Flux RTSP ne fonctionne pas**

**Vérifications** :
1. Testez l'URL dans VLC : `Média` → `Ouvrir un flux réseau`
2. Vérifiez les logs de go2rtc : `http://IP_HOME_ASSISTANT:1984/`
3. Vérifiez que l'URL HLS source fonctionne

### **Vérifier les logs**

Cherchez dans les logs Home Assistant :
```
🔴 EZVIZ Enhanced: go2rtc détecté et disponible
🔴 EZVIZ Enhanced: Stream RTSP créé pour SERIAL: rtsp://...
🔴 EZVIZ Enhanced: URL RTSP locale exposée dans les attributs
```

---

## 🎉 Exemple Complet

### **Home Assistant**
Le flux HLS est automatiquement converti en RTSP local.

### **Scrypted (pour HomeKit Secure Video)**
```
rtsp://192.168.1.100:8554/ezviz_BE8269237
```

### **Frigate (pour détection IA)**
```yaml
cameras:
  entree:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.1.100:8554/ezviz_BE8269237
          roles:
            - detect
            - record
    detect:
      width: 1920
      height: 1080
```

### **Blue Iris**
1. **Ajoutez une caméra**
2. **Type** : RTSP
3. **URL** : `rtsp://192.168.1.100:8554/ezviz_BE8269237`

---

## ℹ️ Informations Techniques

### **Mise à Jour Automatique des URLs**

Le plugin met à jour automatiquement les URLs HLS toutes les 30 secondes. go2rtc détecte automatiquement les changements d'URL et continue le streaming sans interruption.

### **Formats Supportés**

- **Entrée** : HLS (flux EZVIZ)
- **Sortie** : RTSP, WebRTC, MSE, MP4, MJPEG

### **Ports Utilisés**

- **go2rtc API** : 1984
- **RTSP** : 8554
- **WebRTC** : 8555 (UDP)

---

🎉 **Profitez de vos caméras EZVIZ avec un flux RTSP local performant !**

