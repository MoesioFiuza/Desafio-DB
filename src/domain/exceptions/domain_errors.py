class DomainError(Exception):
    code: str = "domain_error"


class DomainValidationError(DomainError):
    code = "domain_validation_error"
