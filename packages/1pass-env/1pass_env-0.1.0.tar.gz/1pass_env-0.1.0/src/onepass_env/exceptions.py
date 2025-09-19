"""Custom exceptions for 1pass-env."""


class OnePassEnvError(Exception):
    """Base exception for 1pass-env errors."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AuthenticationError(OnePassEnvError):
    """Raised when authentication with 1Password fails."""
    pass


class VaultError(OnePassEnvError):
    """Raised when there's an issue with the 1Password vault."""
    pass


class ConfigurationError(OnePassEnvError):
    """Raised when there's a configuration issue."""
    pass


class ValidationError(OnePassEnvError):
    """Raised when input validation fails."""
    pass
