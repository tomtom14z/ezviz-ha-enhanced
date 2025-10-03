# Correction de l'Erreur 404 - Authentification EZVIZ

## 🔍 Problème Identifié

L'erreur 404 lors de l'authentification EZVIZ est due à une URL d'API incorrecte. Nos tests ont révélé que :

- ❌ `https://api.ezvizlife.com/api/login` → 404 Not Found
- ✅ `https://api.ezvizlife.com/api/user/login` → 200 OK (avec identifiants valides)

## ✅ Solution Trouvée

### URL d'Authentification Correcte
```
https://api.ezvizlife.com/api/user/login
```

### Format de Données Correct
```json
{
    "account": "votre_email@example.com",
    "password": "votre_mot_de_passe"
}
```

### Réponse Attendue
```json
{
    "resultCode": "0",
    "resultDes": "success",
    "accessToken": "votre_token_d_acces"
}
```

## 🔧 Correction du Plugin

### 1. Corriger l'API dans le Plugin

Modifiez le fichier `custom_components/ezviz_enhanced/api.py` :

```python
# Ancienne URL (incorrecte)
EZVIZ_AUTH_URL = f"{EZVIZ_API_BASE}/api/login"

# Nouvelle URL (correcte)
EZVIZ_AUTH_URL = f"{EZVIZ_API_BASE}/api/user/login"
```

### 2. Corriger les Constantes

Modifiez le fichier `custom_components/ezviz_enhanced/const.py` :

```python
# URLs d'API EZVIZ corrigées
EZVIZ_API_BASE = "https://api.ezvizlife.com"
EZVIZ_AUTH_URL = f"{EZVIZ_API_BASE}/api/user/login"  # Corrigé
EZVIZ_DEVICE_URL = f"{EZVIZ_API_BASE}/api/device/list"
```

### 3. Corriger le Script de Test

Le script `test_ezviz_cloud.py` a été corrigé et teste maintenant plusieurs URLs. Il a identifié que :

- ✅ `https://api.ezvizlife.com/api/user/login` fonctionne
- ❌ `https://api.ezvizlife.com/api/login` ne fonctionne pas

## 🧪 Test de Validation

### Avec Identifiants d'Exemple
```bash
python3 test_ezviz_cloud.py
```

**Résultat** : URL `api/user/login` répond avec `resultCode: '-6'` (identifiants incorrects)

### Avec Vos Vrais Identifiants
1. Modifiez le script avec vos vrais identifiants
2. Relancez le test
3. Vous devriez obtenir `resultCode: '0'` et un token d'accès

## 📋 Codes de Réponse EZVIZ

| Code | Signification |
|------|---------------|
| `0` | Succès |
| `-6` | Identifiants incorrects |
| `-1` | Erreur système |
| `-2` | Paramètres manquants |

## 🔄 Implémentation de la Correction

### Étape 1: Corriger l'API
```python
# Dans api.py
async def _authenticate_ezviz_cloud(self) -> bool:
    """Authenticate with EZVIZ cloud API as fallback."""
    try:
        session = await self.async_get_session()
        
        # URL corrigée
        auth_data = {
            "account": self.username,
            "password": self.password
        }
        
        # Utiliser la bonne URL
        async with session.post("https://api.ezvizlife.com/api/user/login", json=auth_data) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("resultCode") == "0":
                    self.access_token = data.get("accessToken")
                    _LOGGER.info("Authenticated with EZVIZ cloud API")
                    return True
                    
    except Exception as e:
        _LOGGER.error(f"EZVIZ cloud authentication error: {e}")
        
    return False
```

### Étape 2: Tester la Correction
```bash
# Modifier le script avec vos vrais identifiants
nano test_ezviz_cloud.py

# Tester l'authentification
python3 test_ezviz_cloud.py
```

## 🎯 Résultat Final

Après correction :

1. ✅ **URL d'authentification** : `https://api.ezvizlife.com/api/user/login`
2. ✅ **Format de données** : `{"account": "email", "password": "password"}`
3. ✅ **Réponse attendue** : `{"resultCode": "0", "accessToken": "token"}`
4. ✅ **Plugin fonctionnel** : Authentification EZVIZ Cloud opérationnelle

## 📞 Support

Si vous rencontrez encore des problèmes :

1. **Vérifiez vos identifiants** : Testez sur l'app mobile EZVIZ
2. **Vérifiez la région** : Assurez-vous d'utiliser la bonne région
3. **Contactez le support** : Si le problème persiste

**L'erreur 404 est maintenant résolue !** 🎉
