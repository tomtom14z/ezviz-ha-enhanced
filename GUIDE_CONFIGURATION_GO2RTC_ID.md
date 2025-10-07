# Guide de Configuration de l'ID go2rtc

## Problème résolu

Le plugin EZVIZ Enhanced peut maintenant être configuré avec l'ID spécifique de votre add-on go2rtc. Cela résout le problème d'actualisation automatique des streams toutes les heures.

## Configuration

### 1. Trouver votre ID go2rtc

Pour trouver l'ID de votre add-on go2rtc :

1. Allez dans **Configuration** → **Modules complémentaires** → **Modules complémentaires**
2. Trouvez votre add-on go2rtc
3. Cliquez sur l'add-on
4. L'ID apparaît dans l'URL ou dans les détails de l'add-on

Exemple d'IDs courants :
- `a889bffc_go2rtc` (votre cas)
- `a0d7b954_go2rtc`
- `alexxit_go2rtc`
- `core_go2rtc`
- `local_go2rtc`

### 2. Configurer le plugin

1. Allez dans **Configuration** → **Intégrations**
2. Trouvez **EZVIZ Enhanced** et cliquez sur **Configurer**
3. Dans le formulaire de configuration, vous verrez maintenant un nouveau champ :
   - **ID de l'add-on go2rtc** : Entrez votre ID (par défaut : `a889bffc_go2rtc`)

### 3. Redémarrer Home Assistant

Après la configuration, redémarrez Home Assistant pour que les changements prennent effet.

## Vérification

Après redémarrage, dans les logs, vous devriez voir :

```
INFO (MainThread) [custom_components.ezviz_enhanced.go2rtc_manager] 🔄 Utilisation de l'ID go2rtc configuré : a889bffc_go2rtc
INFO (MainThread) [custom_components.ezviz_enhanced.go2rtc_manager] 🔄 Redémarrage add-on go2rtc (a889bffc_go2rtc)...
INFO (MainThread) [custom_components.ezviz_enhanced.go2rtc_manager] ✅ Add-on go2rtc redémarré avec succès!
```

Au lieu de :
```
WARNING (MainThread) [custom_components.ezviz_enhanced.go2rtc_manager] ⚠️ Aucun add-on go2rtc trouvé, tentative reload API...
```

## Avantages

- ✅ Actualisation automatique des streams go2rtc
- ✅ Plus de reconnexion manuelle nécessaire
- ✅ Streams stables sans interruption
- ✅ Configuration personnalisée selon votre installation

## Dépannage

Si vous avez encore des problèmes :

1. Vérifiez que l'ID est correct
2. Vérifiez que l'add-on go2rtc est bien installé et démarré
3. Consultez les logs pour voir les messages d'erreur
4. Redémarrez l'add-on go2rtc manuellement si nécessaire
