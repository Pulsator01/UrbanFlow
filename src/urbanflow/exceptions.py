"""Custom exception types."""


class UrbanFlowError(Exception):
    """Base error for UrbanFlow."""


class ValidationError(UrbanFlowError):
    """Raised when validation checks fail."""


class OptimizationError(UrbanFlowError):
    """Raised when optimization fails to converge."""
