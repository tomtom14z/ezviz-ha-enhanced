# Guide Configuration Synology Surveillance Station

## 🎯 Paramètres optimaux pour Synology Surveillance Station

### 1. **Configuration de la caméra dans Surveillance Station**

#### **Onglet "Source"**
- **Protocole** : `RTSP`
- **URL RTSP** : `rtsp://[IP_HA]:8554/ezviz_BE8269237`
  - Remplacez `[IP_HA]` par l'IP de votre Home Assistant
  - Exemple : `rtsp://192.168.1.100:8554/ezviz_BE8269237`
- **Port** : `8554`
- **Nom d'utilisateur** : (laisser vide)
- **Mot de passe** : (laisser vide)

#### **Onglet "Stream"**
- **Stream principal** :
  - **Résolution** : `1920x1080` (ou la résolution native de votre caméra)
  - **FPS** : `15-20` (pas plus pour éviter les sauts)
  - **Bitrate** : `2048-4096 kbps`
  - **Codec** : `H.264`

- **Stream secondaire** (optionnel) :
  - **Résolution** : `640x480`
  - **FPS** : `10-15`
  - **Bitrate** : `512-1024 kbps`

#### **Onglet "Enregistrement"**
- **Qualité d'enregistrement** : `Haute` ou `Moyenne`
- **FPS d'enregistrement** : `15-20`
- **Pré-tampon** : `2-3 secondes`
- **Post-tampon** : `2-3 secondes`

### 2. **Paramètres réseau avancés**

#### **Dans Surveillance Station > Configuration > Réseau**
- **Timeout de connexion** : `30 secondes`
- **Tentatives de reconnexion** : `3`
- **Intervalle de reconnexion** : `5 secondes`
- **Buffer réseau** : `Faible` (pour réduire la latence)

### 3. **Configuration EZVIZ Enhanced optimisée**

#### **Mode "Smooth" (Recommandé pour Synology)**
1. **Allez dans Configuration** → **Intégrations** → **EZVIZ Enhanced**
2. **Cliquez sur "Options système"** (⚙️)
3. **Configurez** :
   - **ID de l'add-on go2rtc** : `a889bffc_go2rtc`
   - **Qualité du stream** : `smooth` (priorité à la fluidité)
   - **Port RTSP** : `8554`

#### **Mode "Quality" (Si vous préférez la qualité)**
- **Qualité du stream** : `quality` (priorité à la qualité, plus de buffer)

### 4. **Paramètres Synology DSM**

#### **Dans DSM > Surveillance Station > Configuration > Enregistrement**
- **Qualité d'image** : `Haute`
- **FPS** : `15-20`
- **Compression** : `H.264`
- **Bitrate** : `Variable` (recommandé)

#### **Dans DSM > Surveillance Station > Configuration > Réseau**
- **Buffer de lecture** : `Faible`
- **Timeout de connexion** : `30s`
- **Tentatives de reconnexion** : `3`

### 5. **Dépannage**

#### **Si vous avez encore des sauts de frame :**
1. **Réduisez les FPS** à 15 dans Surveillance Station
2. **Diminuez le bitrate** à 2048 kbps
3. **Vérifiez la connexion réseau** entre Synology et Home Assistant
4. **Testez avec VLC** : `rtsp://[IP_HA]:8554/ezviz_BE8269237`

#### **Si la connexion se coupe :**
1. **Augmentez le timeout** à 60 secondes
2. **Vérifiez que go2rtc fonctionne** : http://[IP_HA]:1984
3. **Redémarrez l'add-on go2rtc** si nécessaire

### 6. **URLs de test**

- **Interface go2rtc** : http://[IP_HA]:1984
- **Stream RTSP** : rtsp://[IP_HA]:8554/ezviz_BE8269237
- **Test avec VLC** : Ouvrir le flux RTSP dans VLC pour vérifier la qualité

### 7. **Optimisations avancées**

#### **Pour un flux ultra-fluide :**
- **FPS** : 15
- **Bitrate** : 1536 kbps
- **Buffer** : Faible
- **Mode** : Smooth

#### **Pour un flux haute qualité :**
- **FPS** : 20
- **Bitrate** : 4096 kbps
- **Buffer** : Moyen
- **Mode** : Quality

## ⚠️ Notes importantes

- **Testez d'abord avec VLC** avant de configurer Surveillance Station
- **La qualité dépend de votre réseau** : WiFi vs Ethernet
- **Redémarrez Surveillance Station** après modification des paramètres
- **Vérifiez les logs** de go2rtc en cas de problème
