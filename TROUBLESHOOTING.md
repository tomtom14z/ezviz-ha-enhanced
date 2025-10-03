# Guide de Dépannage - EZVIZ Enhanced

Ce guide vous aide à résoudre les problèmes courants avec l'intégration EZVIZ Enhanced.

## 🔍 Diagnostic Initial

### 1. Vérifier l'installation

```bash
# Vérifier que le plugin est installé
ls -la /config/custom_components/ezviz_enhanced/

# Vérifier les logs Home Assistant
tail -f /config/home-assistant.log | grep ezviz_enhanced
```

### 2. Tester la plateforme IeuOpen

```bash
# Exécuter le script de test
python3 test_ieuopen.py VOTRE_SERIAL
```

## 🚨 Problèmes Courants

### Problème 1: Caméra non détectée

**Symptômes:**
- La caméra n'apparaît pas dans Home Assistant
- Erreur "Device not found" dans les logs

**Solutions:**
1. Vérifiez le serial de la caméra
2. Vérifiez que la caméra est en ligne
3. Testez l'URL IeuOpen manuellement

```bash
# Test manuel de l'URL
curl "https://ieuopen.ezviz.com/console/setnormallive.html?serial=VOTRE_SERIAL&channelNo=1&addressType=1"
```

### Problème 2: Flux RTSP non accessible

**Symptômes:**
- Erreur "Stream not available"
- Flux vidéo ne se charge pas

**Solutions:**
1. Vérifiez que FFmpeg est installé
2. Vérifiez que le port 8554 est ouvert
3. Vérifiez les logs de conversion

```bash
# Vérifier FFmpeg
ffmpeg -version

# Vérifier le port
netstat -tulpn | grep 8554
```

### Problème 3: Erreur d'authentification

**Symptômes:**
- Erreur "Invalid credentials"
- Impossible de se connecter à l'API EZVIZ

**Solutions:**
1. Vérifiez vos identifiants EZVIZ
2. Testez la connexion sur l'app mobile EZVIZ
3. Réinitialisez le mot de passe si nécessaire

### Problème 4: Conversion RTSP échoue

**Symptômes:**
- Erreur FFmpeg dans les logs
- Flux RTSP non généré

**Solutions:**
1. Vérifiez les permissions FFmpeg
2. Vérifiez l'espace disque disponible
3. Redémarrez le service de conversion

```bash
# Vérifier les processus FFmpeg
ps aux | grep ffmpeg

# Tuer les processus FFmpeg bloqués
pkill -f ffmpeg
```

## 🔧 Configuration Avancée

### Configuration YAML Complète

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
    - serial: "BE8269238"  # Caméra supplémentaire
      name: "Caméra Jardin"
      channel: 1
      enabled: true

# Logs de débogage
logger:
  logs:
    custom_components.ezviz_enhanced: debug
    homeassistant.components.camera: debug
```

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

## 📊 Monitoring et Logs

### Activer les Logs Détaillés

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.ezviz_enhanced: debug
    homeassistant.components.camera: debug
    homeassistant.components.ffmpeg: debug
```

### Vérifier les Logs

```bash
# Logs Home Assistant
tail -f /config/home-assistant.log

# Logs spécifiques EZVIZ
grep "ezviz_enhanced" /config/home-assistant.log

# Logs FFmpeg
grep "ffmpeg" /config/home-assistant.log
```

## 🔄 Redémarrage et Réinitialisation

### Redémarrage Complet

1. Arrêter Home Assistant
2. Nettoyer les processus FFmpeg
3. Redémarrer Home Assistant

```bash
# Arrêter Home Assistant
sudo systemctl stop home-assistant@homeassistant

# Nettoyer FFmpeg
pkill -f ffmpeg

# Redémarrer
sudo systemctl start home-assistant@homeassistant
```

### Réinitialisation du Plugin

1. Supprimer l'intégration dans Home Assistant
2. Supprimer le dossier du plugin
3. Réinstaller le plugin
4. Reconfigurer l'intégration

## 🆘 Support et Aide

### Informations de Diagnostic

En cas de problème, collectez ces informations :

1. **Version Home Assistant:** `homeassistant --version`
2. **Logs d'erreur:** Copiez les logs d'erreur complets
3. **Configuration:** Votre configuration YAML (sans mots de passe)
4. **Serial caméra:** Le serial de votre caméra
5. **Résultat du test:** Sortie du script `test_ieuopen.py`

### Ressources Utiles

- [Documentation EZVIZ](https://support.ezviz.com/)
- [Forum Home Assistant](https://community.home-assistant.io/)
- [Documentation FFmpeg](https://ffmpeg.org/documentation.html)

### Contact

- **Issues GitHub:** [Créer une issue](https://github.com/votre-username/ha-ezviz-enhanced/issues)
- **Email:** support@example.com

## 📝 Changelog

### Version 1.0.0
- Support initial de la plateforme IeuOpen
- Conversion automatique en RTSP
- Intégration Home Assistant
- Support Homebridge
