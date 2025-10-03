# Instructions de Debug pour l'Affichage de la Caméra

## 🔍 Étape 1 : Vérifier la Configuration FFmpeg

### Dans configuration.yaml, vérifiez que vous avez :

```yaml
ffmpeg:

stream:
```

**IMPORTANT** : Ajoutez aussi la ligne `stream:` si elle n'y est pas !

## 🔍 Étape 2 : Vérifier les Logs FFmpeg

1. **Allez dans Paramètres → Système → Logs**
2. **Cherchez** "ffmpeg" ou "stream"
3. **Envoyez-moi les erreurs** qui mentionnent FFmpeg

## 🔍 Étape 3 : Tester avec une Configuration Simplifiée

### Ajoutez cette configuration dans configuration.yaml :

```yaml
camera:
  - platform: ffmpeg
    name: "Test EZVIZ Direct"
    input: "VOTRE_URL_HLS_COMPLETE_ICI"
```

Remplacez `VOTRE_URL_HLS_COMPLETE_ICI` par l'URL HLS complète que vous voyez dans les attributs de `camera.oeilcp2`.

## 🔍 Étape 4 : Vérifier l'URL Utilisée

1. **Outils de Développement** → **États**
2. **Cherchez** `camera.oeilcp2`
3. **Vérifiez l'attribut** `hls_url`
4. **Copiez cette URL** et testez-la dans VLC

## 🔍 Étape 5 : Logs à Fournir

Si rien ne fonctionne, envoyez-moi :
1. Les logs avec 🔴 (EZVIZ Enhanced)
2. Les logs FFmpeg
3. Les logs "stream"
4. Le contenu de votre configuration.yaml (sans les infos sensibles)

## ⚠️ Points à Vérifier

- [ ] FFmpeg est installé (devrait être pré-installé avec Home Assistant OS)
- [ ] La ligne `stream:` est présente dans configuration.yaml
- [ ] L'URL HLS fonctionne dans le navigateur
- [ ] La carte caméra est bien ajoutée avec `camera.oeilcp2`
- [ ] Home Assistant a bien été redémarré après les modifications

