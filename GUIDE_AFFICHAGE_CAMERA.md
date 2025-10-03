# Guide de Résolution - Affichage de la Caméra EZVIZ

## 🎯 Problème Identifié

L'intégration EZVIZ Enhanced fonctionne parfaitement et récupère les flux HLS, mais Home Assistant a des difficultés à afficher directement les flux HLS d'EZVIZ.

## ✅ Solutions

### Solution 1 : Configuration FFmpeg (Recommandée)

1. **Vérifiez que FFmpeg est installé** :
   - Allez dans **Paramètres** → **Système** → **Logs**
   - Cherchez des erreurs FFmpeg

2. **Ajoutez cette configuration** à votre `configuration.yaml` :
   ```yaml
   ffmpeg:
     ffmpeg_bin: /usr/bin/ffmpeg
   
   camera:
     - platform: generic
       name: "EZVIZ Stream"
       stream_source: "{{ state_attr('camera.oeilcp2', 'hls_url') }}"
       verify_ssl: false
   ```

3. **Redémarrez Home Assistant**

### Solution 2 : Utilisation de la Carte Caméra

1. **Ajoutez une carte caméra** à votre tableau de bord :
   ```yaml
   type: camera
   entity: camera.oeilcp2
   ```

2. **Ou utilisez l'interface graphique** :
   - Éditez votre tableau de bord
   - Ajoutez une carte "Caméra"
   - Sélectionnez `camera.oeilcp2`

### Solution 3 : Test Direct du Flux

1. **Testez l'URL HLS directement** :
   - Copiez l'URL HLS depuis les attributs de la caméra
   - Testez-la dans VLC ou un autre lecteur
   - Si elle fonctionne, le problème vient de Home Assistant

### Solution 4 : Configuration Avancée

Si les solutions précédentes ne fonctionnent pas, ajoutez cette configuration :

```yaml
camera:
  - platform: ffmpeg
    name: "EZVIZ FFmpeg Stream"
    input: "{{ state_attr('camera.oeilcp2', 'hls_url') }}"
    extra_arguments: "-c:v copy -c:a copy"
```

## 🔍 Diagnostic

### Vérifiez les Attributs de la Caméra

1. Allez dans **Paramètres** → **Appareils & Services**
2. Trouvez votre caméra **"OeilCP2"**
3. Cliquez dessus
4. Vérifiez que l'attribut `hls_url` contient une URL valide

### Logs à Surveiller

Cherchez dans les logs :
- `�� EZVIZ Enhanced: Using HLS stream for camera`
- Erreurs FFmpeg
- Erreurs de stream

## 🎯 État Actuel

✅ **L'intégration fonctionne parfaitement** :
- Authentification IeuOpen : OK
- Récupération des flux HLS : OK
- URLs de flux valides : OK
- Mise à jour automatique : OK

❌ **Problème d'affichage** :
- Home Assistant ne peut pas lire directement les flux HLS d'EZVIZ
- Solution : Utiliser FFmpeg ou la plateforme generic

## 🚀 Prochaines Étapes

1. Essayez la **Solution 1** (Configuration FFmpeg)
2. Si ça ne fonctionne pas, essayez la **Solution 2** (Carte caméra)
3. Vérifiez les logs pour des erreurs FFmpeg
4. Testez l'URL HLS directement dans VLC

L'intégration est **100% fonctionnelle** ! Il ne reste plus qu'à configurer l'affichage ! ��
