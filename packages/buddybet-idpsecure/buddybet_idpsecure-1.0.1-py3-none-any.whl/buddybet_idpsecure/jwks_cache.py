import requests
import time
from jose import jwk
from .core.environment_config import AppConfig
from buddybet_logmon_common.logger import get_logger


class JWKSCache:
    logger = get_logger()

    def __init__(self, config: AppConfig):
        self.env_var = config.idp_lib_env
        self.keys = {}
        self.last_update = 0

    def get_keys_idp(self):
        now = time.time()
        jwks_url = self.env_var.idp_certificates_url
        if not self.keys or (now - self.env_var.last_updated) > self.env_var.ttl:
            try:
                response = requests.get(jwks_url,  verify=False)
                response.raise_for_status()
                data = response.json()
                self.keys = {k["kid"]: k for k in data["keys"]}
                self.last_update = now
            except Exception:
                self.logger.error("Error Connect IdP", exc_info=True)
        return self.keys
