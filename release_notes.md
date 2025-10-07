# EZVIZ Enhanced v1.0.7

## 🆕 Nouvelles Fonctionnalités

- **Configuration de l'ID go2rtc** : Possibilité de spécifier l'ID de votre add-on go2rtc
- **Résolution du problème d'actualisation** : Plus de reconnexion manuelle nécessaire toutes les heures
- **Détection automatique améliorée** : Fallback intelligent si l'ID configuré n'est pas trouvé

## 🐛 Corrections

- **Correction de l'actualisation go2rtc** : Le plugin peut maintenant redémarrer correctement l'add-on go2rtc
- **Amélioration des logs** : Messages plus clairs pour le diagnostic des problèmes go2rtc
- **Gestion d'erreur robuste** : Meilleure gestion des cas où go2rtc n'est pas trouvé

## 📋 Changements Techniques

- ✅ Nouveau paramètre `go2rtc_addon_id` dans la configuration
- ✅ ID par défaut `a889bffc_go2rtc` pour votre installation
- ✅ Fallback automatique vers la détection d'add-ons connus
- ✅ Logs informatifs pour le diagnostic go2rtc

## 🚀 Installation

1. Mettez à jour via HACS
2. Allez dans **Configuration** → **Intégrations** → **EZVIZ Enhanced** → **Configurer**
3. Entrez votre ID go2rtc (par défaut : `a889bffc_go2rtc`)
4. Redémarrez Home Assistant

## 🔍 Diagnostic

Après la mise à jour, vérifiez les logs pour :
- `"🔄 Utilisation de l'ID go2rtc configuré : a889bffc_go2rtc"`
- `"✅ Add-on go2rtc redémarré avec succès!"`

## ⚠️ Notes Importantes

- L'ID par défaut est configuré pour votre installation (`a889bffc_go2rtc`)
- Si vous avez un autre ID, modifiez-le dans la configuration
- Redémarrez Home Assistant après la configuration
- Consultez le guide `GUIDE_CONFIGURATION_GO2RTC_ID.md` pour plus de détails

---

# EZVIZ Enhanced v1.0.3

## 🐛 Corrections

- **Correction de l'affichage de l'image** de la caméra (état inactif)
- **Amélioration du stockage des URLs HLS** dans le coordinateur
- **Ajout de logs détaillés** pour diagnostiquer les problèmes de flux
- **Correction de la fonction stream_source** pour une meilleure détection

## 📋 Changements Techniques

- ✅ Stockage séparé de `hls_url` dans le coordinateur
- ✅ Logs informatifs pour les URLs de flux
- ✅ Gestion d'erreur améliorée avec timeouts
- ✅ Priorisation des flux HLS pour Home Assistant

## 🚀 Installation

1. Mettez à jour via HACS
2. Redémarrez Home Assistant
3. Vérifiez les logs pour les URLs de flux

## 🔍 Diagnostic

Après la mise à jour, vérifiez les logs pour :
- `"Using HLS stream for camera [SERIAL]: [URL]"`
- `"Camera [SERIAL] URLs - HLS: [URL], Stream: [URL], RTSP: [URL]"`

## ⚠️ Notes Importantes

- Supprimez l'ancienne intégration `ezviz_cloud` si elle existe
- Redémarrez Home Assistant après la mise à jour
- Vérifiez que vos clés API EZVIZ Open Platform sont correctes
