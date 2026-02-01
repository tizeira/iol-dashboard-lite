"""Custom exceptions for IOL API interactions."""


class IOLError(Exception):
    """Base exception for all IOL-related errors."""

    pass


class IOLAuthError(IOLError):
    """Authentication-related errors."""

    pass


class InvalidCredentialsError(IOLAuthError):
    """Wrong username/password."""

    def __init__(self):
        super().__init__("Credenciales inválidas. Verificá usuario y contraseña.")


class TokenExpiredError(IOLAuthError):
    """Token expired, needs refresh."""

    def __init__(self):
        super().__init__("Sesión expirada. Volvé a iniciar sesión.")


class IOLAPIError(IOLError):
    """Generic API error."""

    pass


class RateLimitError(IOLAPIError):
    """Hit rate limit."""

    def __init__(self, retry_after: int = 60):
        super().__init__(f"Límite de requests alcanzado. Reintentá en {retry_after}s.")
        self.retry_after = retry_after


class NetworkError(IOLAPIError):
    """Network/timeout issues."""

    def __init__(self, original_error: Exception):
        super().__init__(f"Error de conexión: {original_error}")
        self.original_error = original_error
