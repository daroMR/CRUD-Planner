import msal
import os
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Microsoft Graph
CLIENT_ID = os.getenv("MS_GRAPH_CLIENT_ID", "1844799e-1ce4-4d2d-9c40-3beff517f243").strip()
TENANT_ID = os.getenv("MS_GRAPH_TENANT_ID", "common").strip()
CLIENT_SECRET = os.getenv("MS_GRAPH_CLIENT_SECRET", "").strip()
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Tasks.ReadWrite", "User.Read"]

print(f"DEBUG: AUTH_CONFIG -> CLIENT_ID: {CLIENT_ID}")
print(f"DEBUG: AUTH_CONFIG -> TENANT_ID: {TENANT_ID}")
print(f"DEBUG: AUTH_CONFIG -> AUTHORITY: {AUTHORITY}")
print(f"DEBUG: AUTH_CONFIG -> HAS_SECRET: {bool(CLIENT_SECRET)}")

# Ruta absoluta para la caché de tokens
CACHE_PATH = os.path.join(os.path.dirname(__file__), "token_cache.bin")

# Almacén temporal de tokens
token_cache = msal.SerializableTokenCache()
if os.path.exists(CACHE_PATH):
    try:
        token_cache.deserialize(open(CACHE_PATH, "r").read())
        print(f"DEBUG: cache cargada de {CACHE_PATH}")
    except Exception as e:
        print(f"DEBUG: error cargando caché: {e}")

def save_cache():
    print(f"DEBUG: save_cache - state changed: {token_cache.has_state_changed}")
    if token_cache.has_state_changed:
        try:
            with open(CACHE_PATH, "w") as f:
                f.write(token_cache.serialize())
            print(f"DEBUG: save_cache - successfully wrote {CACHE_PATH}")
        except Exception as e:
            print(f"DEBUG: save_cache - ERROR writing file: {e}")

def get_msal_app():
    return msal.PublicClientApplication(
        CLIENT_ID, 
        authority=AUTHORITY,
        token_cache=token_cache
    )

def init_device_flow():
    app = get_msal_app()
    flow = app.initiate_device_flow(scopes=SCOPES)
    print(f"DEBUG: init_device_flow result: {flow}")
    if "user_code" not in flow:
        raise Exception(f"Fallo al iniciar el flujo de dispositivo: {flow.get('error_description', 'Error desconocido')}")
    return flow

def complete_device_flow(flow):
    app = get_msal_app()
    print(f"DEBUG: complete_device_flow calling for: {flow.get('user_code')}")
    result = app.acquire_token_by_device_flow(flow)
    if "error" in result:
        print(f"DEBUG: complete_device_flow ERROR: {result.get('error')} - {result.get('error_description')}")
    else:
        print("DEBUG: complete_device_flow SUCCESS")
    save_cache()
    return result

def get_access_token():
    app = get_msal_app()
    accounts = app.get_accounts()
    print(f"DEBUG: get_access_token accounts found: {len(accounts)}")
    if accounts:
        # Intentar obtener token silenciosamente (usando refresh token si es necesario)
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result:
            print("DEBUG: get_access_token success")
            save_cache()
            return result.get("access_token")
        else:
            print("DEBUG: get_access_token silent acquisition failed")
    return None
