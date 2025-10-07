# Guide HLS Direct pour Synology Surveillance Station

## 🎯 Avantage du HLS Direct

Le **HLS (HTTP Live Streaming)** est beaucoup plus efficace que RTSP car :
- ✅ **Pas de conversion FFmpeg** = CPU économisé
- ✅ **Stream natif** = moins de latence
- ✅ **Moins énergivore** = meilleure performance
- ✅ **Plus stable** = moins de déconnexions

## 🔧 Configuration Synology pour HLS

### 1. **Paramètres de caméra dans Surveillance Station**

#### **Onglet "Source"**
- **Protocole** : `HTTP` (pas RTSP !)
- **URL** : `http://[IP_HA]:8555/ezviz_BE8269237/index.m3u8`
  - Remplacez `[IP_HA]` par l'IP de votre Home Assistant
  - Exemple : `http://192.168.1.100:8555/ezviz_BE8269237/index.m3u8`
- **Port** : `8555` (port HLS de go2rtc)
- **Nom d'utilisateur** : (laisser vide)
- **Mot de passe** : (laisser vide)

#### **Onglet "Stream"**
- **Stream principal** :
  - **Résolution** : `1920x1080` (peut être plus élevée avec HLS)
  - **FPS** : `15-20` (plus stable avec HLS)
  - **Bitrate** : `2048-4096 kbps`
  - **Codec** : `H.264`

### 2. **Configuration EZVIZ Enhanced**

#### **Mode "CPU Optimized" (Recommandé)**
1. **Allez dans Configuration** → **Intégrations** → **EZVIZ Enhanced**
2. **Cliquez sur "Options système"** (⚙️)
3. **Configurez** :
   - **ID de l'add-on go2rtc** : `a889bffc_go2rtc`
   - **Qualité du stream** : `cpu_optimized` (HLS direct uniquement)
   - **Port RTSP** : `8554` (pour compatibilité)

### 3. **URLs disponibles**

#### **HLS (Recommandé pour Synology)**
- **URL HLS** : `http://[IP_HA]:8555/ezviz_BE8269237/index.m3u8`
- **Interface go2rtc** : http://[IP_HA]:1984
- **Test HLS** : Ouvrir l'URL dans VLC ou navigateur

#### **RTSP (Fallback)**
- **URL RTSP** : `rtsp://[IP_HA]:8554/ezviz_BE8269237`
- **Port** : `8554`

### 4. **Test de configuration**

#### **Test 1 : Vérifier HLS**
```bash
# Test avec curl
curl -I http://[IP_HA]:8555/ezviz_BE8269237/index.m3u8

# Test avec VLC
vlc http://[IP_HA]:8555/ezviz_BE8269237/index.m3u8
```

#### **Test 2 : Comparer performances**
- **HLS** : Moins de CPU, plus stable
- **RTSP** : Plus de CPU, plus de lag

### 5. **Paramètres Synology optimisés pour HLS**

#### **Dans Surveillance Station > Configuration > Réseau**
- **Buffer de lecture** : `Faible`
- **Timeout de connexion** : `30 secondes`
- **Tentatives de reconnexion** : `3`
- **Intervalle de reconnexion** : `5 secondes`

#### **Dans Surveillance Station > Configuration > Enregistrement**
- **Qualité d'enregistrement** : `Haute` (possible avec HLS)
- **FPS d'enregistrement** : `20`
- **Compression** : `H.264`
- **Pré-tampon** : `2 secondes`
- **Post-tampon** : `2 secondes`

### 6. **Avantages du mode CPU optimisé**

#### **Configuration automatique**
- **HLS direct uniquement** : Pas de conversion FFmpeg
- **CPU économisé** : Moins de charge sur Home Assistant
- **Plus stable** : Moins de déconnexions
- **Meilleure qualité** : Stream natif sans conversion

#### **Logs à vérifier**
```
🔋 Mode CPU optimisé : HLS direct uniquement pour BE8269237
🎬 Sources: HLS direct uniquement (mode CPU optimisé)
```

### 7. **Dépannage HLS**

#### **Si HLS ne fonctionne pas :**
1. **Vérifiez l'URL** : `http://[IP_HA]:8555/ezviz_BE8269237/index.m3u8`
2. **Testez dans le navigateur** : L'URL doit afficher un fichier .m3u8
3. **Vérifiez go2rtc** : http://[IP_HA]:1984
4. **Redémarrez go2rtc** si nécessaire

#### **Si Synology ne reconnaît pas HLS :**
1. **Vérifiez la version** de Surveillance Station (doit supporter HLS)
2. **Essayez HTTP** au lieu de RTSP
3. **Testez avec VLC** d'abord

### 8. **Configuration alternative**

#### **Si HLS ne fonctionne pas sur Synology :**
- **Revenez à RTSP** : `rtsp://[IP_HA]:8554/ezviz_BE8269237`
- **Mode smooth** : Au lieu de cpu_optimized
- **Paramètres Synology** : Réduire FPS et bitrate

### 9. **Monitoring des performances**

#### **Home Assistant**
- **CPU usage** : Doit être plus faible avec HLS
- **Mémoire** : Moins d'utilisation
- **Logs go2rtc** : Pas d'erreurs FFmpeg

#### **Synology**
- **CPU usage** : Plus stable
- **Réseau** : Moins de latence
- **Qualité** : Plus constante

## ⚠️ Notes importantes

- **HLS est plus efficace** que RTSP pour Synology
- **Mode cpu_optimized** = HLS direct uniquement
- **Testez d'abord** avec VLC avant de configurer Synology
- **URL HLS** : `http://[IP_HA]:8555/ezviz_BE8269237/index.m3u8`
- **Port HLS** : `8555` (pas 8554)

## 🎯 Configuration recommandée finale

- **Mode EZVIZ** : `cpu_optimized`
- **Protocole Synology** : `HTTP`
- **URL Synology** : `http://[IP_HA]:8555/ezviz_BE8269237/index.m3u8`
- **Résolution Synology** : `1920x1080`
- **FPS Synology** : `20`
- **Bitrate Synology** : `4096 kbps`
