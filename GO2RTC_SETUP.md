# Configuration go2rtc pour EZVIZ Enhanced

Ce guide vous aide à configurer go2rtc pour convertir les flux HLS en RTSP.

## 📋 Prérequis

go2rtc doit être installé dans Home Assistant pour utiliser les streams RTSP.

## 🔧 Installation de go2rtc

### Option 1 : Via HACS (Recommandé)

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur "Intégrations"
3. Recherchez "go2rtc"
4. Installez l'intégration **"WebRTC Camera"** (qui inclut go2rtc)
5. Redémarrez Home Assistant

### Option 2 : Add-on Home Assistant OS

1. Allez dans **Paramètres** > **Modules complémentaires** > **Boutique des modules**
2. Recherchez "go2rtc"
3. Installez et démarrez le module
4. Activez "Démarrer au boot"

## ✅ Vérifier l'installation

### 1. Vérifier que go2rtc fonctionne

Accédez à l'interface go2rtc :
```
http://[IP_HOME_ASSISTANT]:1984/
```

Vous devriez voir l'interface web de go2rtc.

### 2. Vérifier le fichier de configuration

Le fichier `go2rtc.yaml` doit être créé automatiquement dans votre dossier de configuration Home Assistant.

Via SSH ou File Editor :
```bash
cat /config/go2rtc.yaml
```

Vous devriez voir quelque chose comme :
```yaml
streams:
  ezviz_BE8269237:
  - https://api.ezvizlife.com/v3/...votre_url_hls...
```

## 🎥 Tester le stream

### Dans l'interface go2rtc

1. Ouvrez http://[IP_HOME_ASSISTANT]:1984/
2. Vous devriez voir votre stream `ezviz_XXXXXXX` dans la liste
3. Cliquez dessus pour le tester

### Avec VLC

1. Ouvrez VLC
2. **Fichier** > **Ouvrir un flux réseau**
3. Entrez l'URL : `rtsp://[IP_HOME_ASSISTANT]:8554/ezviz_BE8269237`
4. Cliquez sur **Lire**

### Avec Homebridge

Ajoutez le stream RTSP dans votre configuration Homebridge :
```json
{
  "source": "-rtsp_transport tcp -i rtsp://[IP_HOME_ASSISTANT]:8554/ezviz_BE8269237",
  "name": "Caméra EZVIZ"
}
```

## 🐛 Dépannage

### Le stream n'apparaît pas dans go2rtc

1. **Vérifier que go2rtc est bien installé et démarré**
   ```bash
   curl http://localhost:1984/api/streams
   ```

2. **Vérifier le fichier go2rtc.yaml**
   ```bash
   cat /config/go2rtc.yaml
   ```

3. **Vérifier les logs de EZVIZ Enhanced**
   - Allez dans **Paramètres** > **Système** > **Journaux**
   - Filtrez par `ezviz_enhanced`
   - Cherchez le message "✅ EZVIZ Enhanced: Stream go2rtc configuré"

4. **Redémarrer go2rtc**
   - Si c'est un add-on : redémarrez-le dans **Modules complémentaires**
   - Si c'est via HACS : redémarrez Home Assistant

### Le stream est dans go2rtc mais ne fonctionne pas

1. **Vérifier l'URL HLS**
   - Dans Home Assistant, vérifiez les attributs de votre caméra
   - L'attribut `hls_url` doit contenir une URL valide
   - Testez l'URL directement dans VLC

2. **Problème d'expiration**
   - Les URLs HLS EZVIZ expirent après quelques heures
   - EZVIZ Enhanced les renouvelle automatiquement
   - Attendez la prochaine mise à jour (toutes les 1 minute)

3. **Vérifier les logs go2rtc**
   - Interface go2rtc : http://localhost:1984/
   - Onglet "Logs"
   - Cherchez les erreurs liées à votre stream

## 📝 Configuration manuelle (optionnel)

Si vous voulez configurer manuellement, éditez `/config/go2rtc.yaml` :

```yaml
streams:
  ezviz_BE8269237:
    - https://api.ezvizlife.com/v3/...votre_url_hls...
  
  # Vous pouvez ajouter des options go2rtc
  ezviz_autre_camera:
    - https://...
    - "ffmpeg:ezviz_autre_camera#video=h264#audio=aac"
```

Puis redémarrez go2rtc pour appliquer les changements.

## 🔗 Liens utiles

- [Documentation go2rtc](https://github.com/AlexxIT/go2rtc)
- [WebRTC Camera (HACS)](https://github.com/AlexxIT/WebRTC)
- [Formats de streams supportés](https://github.com/AlexxIT/go2rtc#source-types)

## 💡 Astuces

### Voir l'URL RTSP dans Home Assistant

L'URL RTSP est disponible comme attribut de votre entité caméra :
1. Allez dans **Outils de développement** > **États**
2. Cherchez `camera.ezviz_[votre_numero]`
3. L'attribut `rtsp_local_url` contient l'URL RTSP

### go2rtc recharge automatiquement

go2rtc détecte automatiquement les modifications du fichier `go2rtc.yaml`. Pas besoin de redémarrer Home Assistant quand EZVIZ Enhanced met à jour les URLs.

## ❓ Questions fréquentes

**Q : Pourquoi utiliser go2rtc au lieu du flux HLS direct ?**  
R : Certaines applications (Homebridge, NVR, etc.) ne supportent que RTSP. go2rtc fait la conversion automatiquement.

**Q : Les URLs expirent-elles ?**  
R : Oui, les URLs HLS EZVIZ expirent. EZVIZ Enhanced les renouvelle automatiquement et met à jour go2rtc.

**Q : Puis-je utiliser plusieurs caméras ?**  
R : Oui, EZVIZ Enhanced crée automatiquement un stream go2rtc pour chaque caméra.

**Q : Y a-t-il un délai ?**  
R : Le délai dépend de go2rtc et de votre réseau, généralement 1-3 secondes.

