from pydantic import BaseModel


class AppConfigEnvironment(BaseModel):
    idp_certificates_url: str
    ttl: int
    expected_audience: str
    issuer: str


class AppConfig(BaseModel):
    idp_lib_env: AppConfigEnvironment
