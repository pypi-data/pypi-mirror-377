class InvalidSignature(Exception):
    pass


class ExpiredToken(Exception):
    pass


class InvalidAudience(Exception):
    pass


class InvalidIssuer(Exception):
    pass


class InvalidNotBefore(Exception):
    pass


class InvalidClaims(Exception):
    pass


class InvalidToken(Exception):
    pass


class JWTValidationError(Exception):
    pass
    """Base class for JWT validation errors"""
