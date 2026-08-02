"""Cliente não oficial para a API web da Evemex."""

from .client import EvemexClient
from .exceptions import AuthenticationError, EvemexAPIError, RequestError
from .models import Account, Candle, OperationResult, PatternStats, Signal

__all__ = [
    "Account",
    "AuthenticationError",
    "Candle",
    "EvemexAPIError",
    "EvemexClient",
    "OperationResult",
    "PatternStats",
    "RequestError",
    "Signal",
]
