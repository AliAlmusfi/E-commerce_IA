

class AppBaseException(Exception):
    """Base exception for all business logic errors."""
    def __init__(self, message, code="BAD_REQUEST", status_code=400, details=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

# Specific exceptions for your modules
class InventoryServiceError(AppBaseException):
    def __init__(self, message="Inventory service unavailable."):
        super().__init__(message, code="INVENTORY_UNAVAILABLE", status_code=503)

class BusinessRuleViolation(AppBaseException):
    def __init__(self, message, details=None):
        super().__init__(message, code="BUSINESS_RULE_VIOLATION", status_code=400, details=details)