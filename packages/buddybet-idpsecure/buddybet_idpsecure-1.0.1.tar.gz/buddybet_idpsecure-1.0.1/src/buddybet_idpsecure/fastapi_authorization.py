from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .user_claims import UserClaims
from .validator import TokenValidator
from .exceptions import JWTValidationError
from .core.environment_config import AppConfig
from .core.settings_config import load_config


class FastAPIAuthorization:
    def __init__(self):
        self.bearer = HTTPBearer()

    async def __call__(self,
                       credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
                       config: AppConfig = Depends(load_config)) -> UserClaims:
        try:
            validator = TokenValidator(config)
            return validator.validate_token(credentials.credentials)
        except JWTValidationError as e:
            raise HTTPException(status_code=401, detail=str(e))
