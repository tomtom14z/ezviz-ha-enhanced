# Guide Spécifique pour Votre Caméra EZVIZ CP2

## 🎯 Votre Situation

Vous avez une caméra EZVIZ CP2 2025 avec le serial **VOTRE_SERIAL** qui ne fonctionne qu'avec le cloud. Voici comment récupérer le flux RTSP sans vos identifiants personnels.

## 🔍 Méthodes d'Accès (Sans Vos Identifiants)

### 1️⃣ **Méthode RTSP Local (RECOMMANDÉE)**

Cette méthode utilise les identifiants par défaut de la caméra, pas vos identifiants cloud.

#### Étape 1: Trouver l'IP de votre caméra
```bash
# Scanner votre réseau pour trouver la caméra
nmap -sn 192.168.1.0/24 | grep -B2 -A2 "EZVIZ\|Hikvision"

# Ou utiliser l'app EZVIZ pour voir l'IP
```

#### Étape 2: Trouver le code de vérification
- Regardez l'étiquette de votre caméra
- Cherchez un code à 6 caractères (ex: ABCDEF)
- Ce code est différent de votre mot de passe EZVIZ

#### Étape 3: Activer RTSP sur la caméra
1. Ouvrez l'app EZVIZ
2. Allez dans **Paramètres** > **Vue en direct LAN**
3. Sélectionnez votre caméra
4. Activez **RTSP**

#### Étape 4: Tester l'accès RTSP
```bash
# URL RTSP de votre caméra
rtsp://admin:CODE_VERIFICATION@IP_CAMERA:554/ch1/main

# Exemple avec votre caméra
rtsp://admin:ABCDEF@192.168.1.100:554/ch1/main
```

### 2️⃣ **Méthode IeuOpen (Alternative)**

La plateforme IeuOpen peut fournir des flux, mais nécessite un compte développeur.

#### Accès à la page IeuOpen
```
https://ieuopen.ezviz.com/console/setnormallive.html?serial=VOTRE_SERIAL&channelNo=1&addressType=1
```

#### Limitation
- ✅ La page est accessible
- ❌ Les flux nécessitent un compte développeur EZVIZ
- ❌ Pas d'accès direct aux flux vidéo

## 🛠️ Solution Pratique

### Option A: RTSP Local (Simple)
1. **Activez RTSP** sur votre caméra via l'app EZVIZ
2. **Trouvez l'IP** de votre caméra
3. **Utilisez le code de vérification** (pas vos identifiants cloud)
4. **Configurez directement** dans Home Assistant

```yaml
# configuration.yaml
camera:
  - platform: generic
    name: "EZVIZ CP2"
    stream_source: rtsp://admin:CODE_VERIFICATION@IP_CAMERA:554/ch1/main
    still_image_url: http://IP_CAMERA:80/ISAPI/Streaming/channels/101/picture
```

### Option B: Plugin Amélioré
Utilisez le plugin que nous avons créé avec la méthode RTSP local :

```yaml
# configuration.yaml
ezviz_enhanced:
  access_method: "local_rtsp"
  cameras:
    - serial: "VOTRE_SERIAL"
      name: "Caméra Entrée"
      ip_address: "192.168.1.100"  # IP de votre caméra
      verification_code: "ABCDEF"  # Code sur l'étiquette
      channel: 1
      enabled: true
```

## 🔧 Script de Test pour Votre Caméra

Créez un script de test spécifique :

```python
#!/usr/bin/env python3
import socket

def test_camera_rtsp(ip, verification_code):
    """Teste l'accès RTSP à votre caméra."""
    print(f"🔍 Test de votre caméra EZVIZ CP2")
    print(f"   Serial: VOTRE_SERIAL")
    print(f"   IP: {ip}")
    print(f"   Code: {verification_code}")
    
    # Test de connectivité
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, 554))
        sock.close()
        
        if result == 0:
            print("   ✅ Port RTSP accessible")
            rtsp_url = f"rtsp://admin:{verification_code}@{ip}:554/ch1/main"
            print(f"   🔗 URL RTSP: {rtsp_url}")
            return True
        else:
            print("   ❌ Port RTSP non accessible")
            print("   💡 Vérifiez que RTSP est activé sur la caméra")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

# Testez avec votre IP et code
test_camera_rtsp("192.168.1.100", "ABCDEF")
```

## 📋 Checklist pour Votre Caméra

- [ ] **Trouver l'IP** de la caméra (routeur ou app EZVIZ)
- [ ] **Trouver le code de vérification** (étiquette de la caméra)
- [ ] **Activer RTSP** via l'app EZVIZ
- [ ] **Tester la connectivité** au port 554
- [ ] **Configurer Home Assistant** avec l'URL RTSP
- [ ] **Tester le flux** dans Home Assistant

## 🚨 Problèmes Courants

### RTSP Non Accessible
- Vérifiez que RTSP est activé sur la caméra
- Vérifiez que le port 554 n'est pas bloqué
- Vérifiez l'IP de la caméra

### Code de Vérification Incorrect
- Le code est sur l'étiquette physique de la caméra
- C'est différent de votre mot de passe EZVIZ
- Généralement 6 caractères en majuscules

### Caméra Non Trouvée
- Utilisez un scanner réseau
- Vérifiez que la caméra est sur le même réseau
- Redémarrez la caméra si nécessaire

## 🎉 Résultat Final

Une fois configuré, vous aurez :
- ✅ Accès RTSP direct à votre caméra
- ✅ Intégration dans Home Assistant
- ✅ Pas de dépendance au cloud
- ✅ Performance optimale

**Votre caméra VOTRE_SERIAL sera accessible via RTSP sans vos identifiants cloud !**
