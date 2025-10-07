# Guide Optimisation Synology Surveillance Station

## 🎯 Problème identifié

Si VLC RTSP fonctionne sans lag mais que Synology Surveillance Station lag, le problème vient de la configuration Synology, pas du flux RTSP.

## 🔧 Solutions pour Synology Surveillance Station

### 1. **Paramètres de caméra dans Surveillance Station**

#### **Onglet "Source"**
- **Protocole** : `RTSP`
- **URL RTSP** : `rtsp://[IP_HA]:8554/ezviz_BE8269237`
- **Port** : `8554`
- **Nom d'utilisateur** : (laisser vide)
- **Mot de passe** : (laisser vide)
- **Timeout de connexion** : `60 secondes` (augmenter)
- **Tentatives de reconnexion** : `5`

#### **Onglet "Stream" - Configuration critique**
- **Stream principal** :
  - **Résolution** : `1280x720` (réduire de 1080p)
  - **FPS** : `10-12` (réduire drastiquement)
  - **Bitrate** : `1024 kbps` (réduire)
  - **Codec** : `H.264`
  - **Profondeur de couleur** : `8 bits`

- **Stream secondaire** :
  - **Résolution** : `640x360`
  - **FPS** : `8`
  - **Bitrate** : `256 kbps`

### 2. **Paramètres réseau Synology**

#### **Dans Surveillance Station > Configuration > Réseau**
- **Buffer de lecture** : `Très faible`
- **Timeout de connexion** : `60 secondes`
- **Tentatives de reconnexion** : `5`
- **Intervalle de reconnexion** : `10 secondes`
- **Buffer réseau** : `Désactivé` (si possible)

### 3. **Paramètres système Synology**

#### **Dans DSM > Surveillance Station > Configuration > Système**
- **Priorité CPU** : `Haute` pour Surveillance Station
- **Mémoire allouée** : Augmenter si possible
- **Désactiver** les autres services non essentiels pendant les tests

### 4. **Configuration EZVIZ Enhanced optimisée**

#### **Mode "CPU Optimized" (Recommandé)**
1. **Allez dans Configuration** → **Intégrations** → **EZVIZ Enhanced**
2. **Cliquez sur "Options système"** (⚙️)
3. **Configurez** :
   - **ID de l'add-on go2rtc** : `a889bffc_go2rtc`
   - **Qualité du stream** : `cpu_optimized` (nouveau mode)
   - **Port RTSP** : `8554`

### 5. **Paramètres avancés Synology**

#### **Dans Surveillance Station > Configuration > Enregistrement**
- **Qualité d'enregistrement** : `Moyenne` (pas Haute)
- **FPS d'enregistrement** : `10`
- **Compression** : `H.264` avec bitrate variable
- **Pré-tampon** : `1 seconde` (réduire)
- **Post-tampon** : `1 seconde` (réduire)

#### **Dans Surveillance Station > Configuration > Affichage**
- **Qualité d'affichage en direct** : `Moyenne`
- **FPS d'affichage** : `8-10`
- **Buffer d'affichage** : `Faible`

### 6. **Optimisations réseau**

#### **Vérifications réseau**
- **Ping** entre Synology et Home Assistant : `< 5ms`
- **Bande passante** : Au moins 2 Mbps disponible
- **Connexion** : Ethernet recommandé (pas WiFi)

#### **Paramètres réseau Synology**
- **MTU** : `1500` (standard)
- **Jumbo frames** : Désactivé
- **Flow control** : Activé

### 7. **Tests de diagnostic**

#### **Test 1 : VLC vs Synology**
```bash
# Test VLC (doit fonctionner)
vlc rtsp://[IP_HA]:8554/ezviz_BE8269237

# Test avec ffmpeg (pour comparer)
ffmpeg -i rtsp://[IP_HA]:8554/ezviz_BE8269237 -t 10 -f null -
```

#### **Test 2 : Monitoring CPU Synology**
- **DSM** → **Moniteur de ressources** → **Performance**
- **Surveillance Station** → **Configuration** → **Système** → **Statistiques**

### 8. **Solutions alternatives**

#### **Option 1 : Stream secondaire uniquement**
- Utiliser seulement le stream secondaire (640x360, 8 FPS)
- Désactiver le stream principal

#### **Option 2 : Délai de démarrage**
- **Délai de démarrage** : `5 secondes`
- **Attendre** que le flux se stabilise

#### **Option 3 : Mode compatibilité**
- **Mode compatibilité** : Activé
- **Décodage matériel** : Désactivé (si disponible)

### 9. **Paramètres de test progressifs**

#### **Test 1 : Configuration minimale**
- **Résolution** : 640x360
- **FPS** : 8
- **Bitrate** : 256 kbps
- **Buffer** : Très faible

#### **Test 2 : Si Test 1 fonctionne**
- **Résolution** : 1280x720
- **FPS** : 10
- **Bitrate** : 512 kbps

#### **Test 3 : Si Test 2 fonctionne**
- **Résolution** : 1920x1080
- **FPS** : 12
- **Bitrate** : 1024 kbps

### 10. **Dépannage avancé**

#### **Si le lag persiste :**
1. **Redémarrer** Surveillance Station
2. **Redémarrer** le service go2rtc
3. **Vérifier** les logs Synology
4. **Tester** avec une autre caméra RTSP

#### **Logs à vérifier :**
- **DSM** → **Centre de journaux** → **Surveillance Station**
- **Home Assistant** → **Logs** → **go2rtc**

## ⚠️ Points importants

- **Commencez toujours par les paramètres les plus bas** (640x360, 8 FPS)
- **Testez progressivement** en augmentant la qualité
- **VLC fonctionne** = le flux RTSP est bon
- **Le problème est dans Synology** = configuration à optimiser
- **Ethernet recommandé** pour la stabilité

## 🎯 Configuration recommandée finale

- **Mode EZVIZ** : `cpu_optimized`
- **Résolution Synology** : `1280x720`
- **FPS Synology** : `10`
- **Bitrate Synology** : `1024 kbps`
- **Buffer Synology** : `Très faible`
- **Timeout Synology** : `60 secondes`
