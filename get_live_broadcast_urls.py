#!/usr/bin/env python3
"""
Script pour récupérer les adresses de broadcast live depuis l'API IeuOpen
Ces adresses correspondent à celles affichées dans l'interface développeur
"""

import urllib.request
import urllib.parse
import json
import ssl
import time
from datetime import datetime

# Configuration
EZVIZ_OPEN_BASE_URL = "https://open.ezvizlife.com"
EZVIZ_OPEN_API_BASE = f"{EZVIZ_OPEN_BASE_URL}/api/lapp"
EZVIZ_OPEN_AUTH_URL = f"{EZVIZ_OPEN_API_BASE}/token/get"
EZVIZ_OPEN_DEVICE_URL = f"{EZVIZ_OPEN_API_BASE}/device/list"
EZVIZ_OPEN_LIVE_URL = f"{EZVIZ_OPEN_API_BASE}/live/address/get"

# Configuration file path
CONFIG_FILE = "ezviz_config.json"

def load_config():
    """Load configuration from file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_credentials():
    """Get credentials from config file."""
    config = load_config()
    
    if not config:
        print(f"❌ Fichier de configuration {CONFIG_FILE} non trouvé!")
        print(f"📝 Créez le fichier {CONFIG_FILE} avec vos informations :")
        print(f"""
{{
  "app_key": "votre_app_key_ieuopen",
  "app_secret": "votre_app_secret_ieuopen", 
  "camera_serial": "VOTRE_SERIAL",
  "camera_channel": 1
}}
""")
        return None, None, None, None
    
    if 'app_key' not in config or 'app_secret' not in config:
        print(f"❌ Clés manquantes dans {CONFIG_FILE}")
        print(f"📝 Ajoutez 'app_key' et 'app_secret' dans le fichier")
        return None, None, None, None
    
    print(f"📁 Configuration chargée depuis {CONFIG_FILE}")
    return config['app_key'], config['app_secret'], config.get('camera_serial', 'VOTRE_SERIAL'), config.get('camera_channel', 1)

def create_ssl_context():
    """Create SSL context that ignores certificate verification."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context

def make_request(url, data=None, method="GET"):
    """Make HTTP request with proper headers and SSL context."""
    ssl_context = create_ssl_context()
    
    if data:
        # Convert dict to form data
        if isinstance(data, dict):
            data = urllib.parse.urlencode(data).encode('utf-8')
        
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    else:
        request = urllib.request.Request(url, method=method)
    
    request.add_header('User-Agent', 'EZVIZ-Enhanced-Test/1.0')
    
    try:
        with urllib.request.urlopen(request, context=ssl_context, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            return {
                'status': response.status,
                'data': json.loads(response_data) if response_data else {},
                'headers': dict(response.headers)
            }
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8') if e.fp else 'No error details'
        return {
            'status': e.code,
            'error': error_data,
            'headers': dict(e.headers) if hasattr(e, 'headers') else {}
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def authenticate():
    """Authenticate with EZVIZ Open Platform."""
    print("🔐 Authentification avec EZVIZ Open Platform")
    print(f"URL: {EZVIZ_OPEN_AUTH_URL}")
    print("-" * 50)
    
    auth_data = {
        "appKey": app_key,
        "appSecret": app_secret
    }
    
    result = make_request(EZVIZ_OPEN_AUTH_URL, auth_data, "POST")
    
    print(f"Status: {result.get('status')}")
    if 'data' in result:
        if result['data'].get('code') == '200':
            access_token = result['data'].get('data', {}).get('accessToken')
            if access_token:
                print(f"✅ Authentification réussie!")
                print(f"Access Token: {access_token[:20]}...")
                return access_token
            else:
                print("❌ Pas de token d'accès dans la réponse")
        else:
            print(f"❌ Échec de l'authentification: {result['data'].get('msg', 'Erreur inconnue')}")
    else:
        print(f"❌ Erreur de requête: {result.get('error', 'Erreur inconnue')}")
    
    return None

def get_live_broadcast_addresses(access_token):
    """Récupérer les adresses de broadcast live avec différents protocoles."""
    print("\n📺 Récupération des adresses de broadcast live")
    print(f"URL: {EZVIZ_OPEN_LIVE_URL}")
    print(f"Caméra: {camera_serial}")
    print(f"Canal: {camera_channel}")
    print("-" * 50)
    
    # Protocoles disponibles selon la documentation
    protocols = {
        1: "ezopen",
        2: "hls", 
        3: "rtmp",
        4: "flv"
    }
    
    broadcast_urls = {}
    
    # Récupérer les URLs pour chaque protocole avec différentes qualités
    qualities = {
        1: "HD (main bitrate)",
        2: "Fluent (sub-bitrate)"
    }
    
    for protocol_id, protocol_name in protocols.items():
        for quality_id, quality_name in qualities.items():
            print(f"\n🔍 Récupération du protocole {protocol_name} (ID: {protocol_id}) - Qualité {quality_name}")
            
            stream_data = {
                "accessToken": access_token,
                "deviceSerial": camera_serial,
                "channelNo": str(camera_channel),
                "protocol": str(protocol_id),
                "quality": str(quality_id),
                "expireTime": "3600"  # 1 heure de validité
            }
            
            # Ajouter le code de chiffrement si disponible (essayer sans d'abord)
            # stream_data["code"] = "votre_code_chiffrement"  # À décommenter si nécessaire
            
            result = make_request(EZVIZ_OPEN_LIVE_URL, stream_data, "POST")
            
            print(f"Status: {result.get('status')}")
            if 'data' in result:
                if result['data'].get('code') == '200':
                    stream_info = result['data'].get('data', {})
                    url = stream_info.get('url')
                    expire_time = stream_info.get('expireTime')
                    
                    if url:
                        key = f"{protocol_name}_{quality_name.lower().replace(' ', '_')}"
                        broadcast_urls[key] = {
                            'url': url,
                            'expire_time': expire_time,
                            'protocol_id': protocol_id,
                            'quality_id': quality_id,
                            'quality_name': quality_name
                        }
                        print(f"  ✅ {protocol_name.upper()} {quality_name}: {url}")
                        if expire_time:
                            print(f"  ⏰ Expiration: {expire_time}")
                    else:
                        print(f"  ❌ Pas d'URL pour {protocol_name} {quality_name}")
                else:
                    print(f"  ❌ Erreur {protocol_name} {quality_name}: {result['data'].get('msg', 'Erreur inconnue')}")
            else:
                print(f"  ❌ Erreur de requête {protocol_name} {quality_name}: {result.get('error', 'Erreur inconnue')}")
    
    if broadcast_urls:
        print(f"\n✅ {len(broadcast_urls)} protocoles récupérés avec succès!")
        return broadcast_urls
    else:
        print(f"\n❌ Aucun protocole récupéré")
        return None

def test_broadcast_urls(broadcast_urls):
    """Tester l'accessibilité des URLs de broadcast."""
    print("\n🧪 Test d'accessibilité des URLs")
    print("-" * 50)
    
    ssl_context = create_ssl_context()
    
    for protocol_name, protocol_data in broadcast_urls.items():
        url = protocol_data['url']
        print(f"\n🔍 Test de {protocol_name.upper()}: {url}")
        
        try:
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'EZVIZ-Enhanced-Test/1.0')
            
            with urllib.request.urlopen(request, context=ssl_context, timeout=10) as response:
                if response.status == 200:
                    print(f"  ✅ Accessible (Status: {response.status})")
                else:
                    print(f"  ⚠️  Status: {response.status}")
        except Exception as e:
            print(f"  ❌ Erreur: {e}")

def save_broadcast_urls(broadcast_urls):
    """Sauvegarder les URLs de broadcast dans un fichier."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"broadcast_urls_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(broadcast_urls, f, indent=2)
    
    print(f"\n💾 URLs sauvegardées dans: {filename}")
    return filename

def main():
    """Fonction principale."""
    global app_key, app_secret, camera_serial, camera_channel
    
    print("🚀 Récupération des adresses de broadcast live EZVIZ")
    print("=" * 60)
    print(f"Base URL: {EZVIZ_OPEN_BASE_URL}")
    print(f"API Base: {EZVIZ_OPEN_API_BASE}")
    print("=" * 60)
    
    # Charger les identifiants
    app_key, app_secret, camera_serial, camera_channel = get_credentials()
    
    if not app_key or not app_secret:
        print("\n❌ Impossible de continuer sans les clés de configuration.")
        return
    
    # Authentification
    access_token = authenticate()
    if not access_token:
        print("\n❌ Échec de l'authentification. Impossible de continuer.")
        return
    
    # Récupérer les adresses de broadcast live
    broadcast_urls = get_live_broadcast_addresses(access_token)
    if not broadcast_urls:
        print("\n❌ Impossible de récupérer les adresses de broadcast live.")
        return
    
    # Tester l'accessibilité
    test_broadcast_urls(broadcast_urls)
    
    # Sauvegarder les URLs
    filename = save_broadcast_urls(broadcast_urls)
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print(f"✅ Authentification: RÉUSSIE")
    print(f"✅ Adresses de broadcast: RÉCUPÉRÉES")
    print(f"✅ Fichier de sauvegarde: {filename}")
    
    print(f"\n🎯 URLs recommandées pour Home Assistant:")
    
    # Prioriser HLS Fluent (sub-bitrate) car plus stable
    if 'hls_fluent_(sub-bitrate)' in broadcast_urls:
        print(f"   HLS Fluent (recommandé): {broadcast_urls['hls_fluent_(sub-bitrate)']['url']}")
    elif 'hls_hd_(main_bitrate)' in broadcast_urls:
        print(f"   HLS HD: {broadcast_urls['hls_hd_(main_bitrate)']['url']}")
    
    # Afficher toutes les URLs disponibles
    print(f"\n📋 Toutes les URLs disponibles:")
    for key, data in broadcast_urls.items():
        print(f"   {key}: {data['url']}")
    
    print(f"\n⚠️  Note: Ces URLs ont une durée de validité limitée.")
    print(f"   Utilisez ce script pour les régénérer régulièrement.")

if __name__ == "__main__":
    main()
