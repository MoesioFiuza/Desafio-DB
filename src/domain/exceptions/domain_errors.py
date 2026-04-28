class DomainError(Exception):
    """Base exception for domain rule violations."""

    code: str = "domain_error"


class DomainValidationError(DomainError):
    """Raised when an entity or value object is invalid."""

    code = "domain_validation_error"
