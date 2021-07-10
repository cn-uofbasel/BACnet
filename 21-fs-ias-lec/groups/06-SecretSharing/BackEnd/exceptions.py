"""Exceptions for the Secret Sharing Project."""


class SecretSharingError(Exception):
    """Signals that an error occurred in Secret Sharing."""
    def __init__(self, message: str):
        self.message = message
        super().__init__()

    def msg(self):
        return self.message


class PasswordError(SecretSharingError):
    """Signals that a password was not accepted or didn't fulfill specifications."""
    def __init__(self, message: str, password: str):
        self.message = message
        self.password = password
        super().__init__(message)

    def password(self) -> str:
        return self.password


class MappingError(SecretSharingError):
    """Signals that a Secret-to-Number mapping failed."""
    def __init__(self, message: str, mapping: tuple):
        self.message = message
        self.mapping = mapping
        super().__init__(message)

    def mapping(self) -> tuple:
        return self.mapping


class SecretPackagingError(SecretSharingError):
    def __init__(self, message: str, secret: bytes):
        self.message = message
        self._secret = secret
        super().__init__(message)

    def secret(self) -> bytes:
        return self._secret
