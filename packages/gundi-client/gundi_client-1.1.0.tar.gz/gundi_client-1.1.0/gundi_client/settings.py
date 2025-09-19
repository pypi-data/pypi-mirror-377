import os
from environs import Env

envfile = os.environ.get("GUNDI_CLIENT_ENVFILE", None)

env = Env()

if envfile:
    env.read_env(envfile)
else:
    # Default behavior
    env.read_env()

KEYCLOAK_ISSUER = env.str("KEYCLOAK_ISSUER", None)
KEYCLOAK_CLIENT_ID = env.str("KEYCLOAK_CLIENT_ID", None)
KEYCLOAK_CLIENT_SECRET = env.str("KEYCLOAK_CLIENT_SECRET", None)
KEYCLOAK_AUDIENCE = env.str("KEYCLOAK_AUDIENCE", None)

CDIP_API_ENDPOINT = env.str("CDIP_API_ENDPOINT", None)
CDIP_ADMIN_ENDPOINT = env.str("CDIP_ADMIN_ENDPOINT", None)

CDIP_API_SSL_VERIFY = env.bool("CDIP_API_SSL_VERIFY", True)
CDIP_ADMIN_SSL_VERIFY = env.bool("CDIP_ADMIN_SSL_VERIFY", True)

LOG_LEVEL = env.log_level("LOG_LEVEL", "INFO")

RUNNING_IN_K8S = bool("KUBERNETES_PORT" in os.environ)

OAUTH_TOKEN_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/token"
PORTAL_API_ENDPOINT = f"{CDIP_ADMIN_ENDPOINT}/api/v1.0"
