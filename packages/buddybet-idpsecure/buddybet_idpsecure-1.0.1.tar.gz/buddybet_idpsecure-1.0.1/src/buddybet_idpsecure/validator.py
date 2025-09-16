from jose import jwt, jwk, ExpiredSignatureError
from jose.exceptions import JWTClaimsError, JWTError
from datetime import datetime, timezone
from .core.environment_config import AppConfig
from .jwks_cache import JWKSCache
from .exceptions import *
from .core.idp_constants import IdpConstants
from buddybet_logmon_common.logger import get_logger

from .user_claims import UserClaims


class TokenValidator:
    logger = get_logger()

    def __init__(self, config: AppConfig):
        self.env_var = config.idp_lib_env
        self.jwksCacheObj = JWKSCache(config)

    def validate_token(self, token: str):
        print("validate_token ")
        if not self.jwksCacheObj:
            self.logger.error("Validator not initialized. Call init_validator()", exc_info=True)
            raise RuntimeError("Validator not initialized. Call init_validator()")

        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")
        keys = self.jwksCacheObj.get_keys_idp()

        if kid not in keys:
            self.logger.error("Invalid KID in token header.", exc_info=True)
            raise InvalidSignature("Invalid KID in token header.")

        key = keys[kid]
        try:
            claims_dict = jwt.decode(
                token,
                key,
                algorithms=[IdpConstants.ALGORITHM],
                audience=self.env_var.expected_audience,
                issuer=self.env_var.issuer
            )
        except ExpiredSignatureError:
            self.logger.error("Token expired.", exc_info=True)
            raise ExpiredToken("Token expired.")
        except JWTClaimsError as e:
            self.logger.error(f"Invalid claims:", exc_info=True)
            raise InvalidClaims(f"Invalid claims: {str(e)}")
        except JWTError as e:
            self.logger.error(f"Invalid token:", exc_info=True)
            raise InvalidToken(f"Invalid token: {str(e)}")

        now = datetime.now(timezone.utc).timestamp()
        if "exp" in claims_dict and claims_dict["exp"] < now:
            self.logger.error(f"Token expired", exc_info=True)
            raise ExpiredToken("Token expired.")
        if "nbf" in claims_dict and claims_dict["nbf"] > now:
            self.logger.error(f"Token not valid yet", exc_info=True)
            raise InvalidNotBefore("Token not valid yet.")

        claims_dict["token"] = token
        return UserClaims(**claims_dict)
