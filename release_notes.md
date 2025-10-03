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
