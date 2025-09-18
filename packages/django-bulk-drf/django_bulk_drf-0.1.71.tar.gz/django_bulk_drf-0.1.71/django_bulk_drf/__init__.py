"""
Django Bulk DRF - Enhanced operations for Django REST Framework

Provides a unified mixin that enhances standard ViewSet endpoints with synchronous
bulk operations that execute heavy database work (including triggers) in Celery workers
while maintaining synchronous API behavior for clients.
"""

__version__ = "0.1.19"
__author__ = "Konrad Beck"
__email__ = "konrad.beck@merchantcapital.co.za"

# Make common imports available at package level
from .mixins import BulkModelViewSet, BulkOperationsMixin, OperationsMixin
from .config import validate_bulk_drf_config, get_bulk_drf_settings

__all__ = [
    "BulkModelViewSet",      # Primary class name
    "BulkOperationsMixin",   # Backward compatibility alias
    "OperationsMixin",       # Legacy alias
    "validate_bulk_drf_config",
    "get_bulk_drf_settings",
]