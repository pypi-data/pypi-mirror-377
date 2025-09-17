"""
Operation mixins for DRF ViewSets.

Provides a unified mixin that enhances standard ViewSet endpoints with efficient
synchronous bulk operations using query parameters.
"""

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

# Optional OpenAPI schema support
try:
    from drf_spectacular.types import OpenApiTypes
    from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema

    SPECTACULAR_AVAILABLE = True
except ImportError:
    SPECTACULAR_AVAILABLE = False

    # Create dummy decorator if drf-spectacular is not available
    def extend_schema(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    # Create dummy classes for OpenAPI types
    class OpenApiParameter:
        QUERY = "query"

        def __init__(self, name, type, location, description, examples=None):
            pass

    class OpenApiExample:
        def __init__(self, name, value, description=None):
            pass

    class OpenApiTypes:
        STR = "string"
        INT = "integer"


import logging

from django_bulk_drf.processing import (
    async_create_task,
    async_get_task,
    async_upsert_task,
)


class BulkOperationsMixin:
    """
    Unified mixin providing synchronous bulk operations with intelligent routing.

    Simple routing strategy:
    - Single instances (dict): Direct database operations (no Celery overhead)
    - Arrays (list): Celery workers for heavy lifting (triggers fire in workers)

    Enhanced endpoints:
    - GET    /api/model/?ids=1                    # Direct single get
    - GET    /api/model/?ids=1,2,3               # Celery multi-get
    - POST   /api/model/?unique_fields=...       # Smart upsert routing
    - PATCH  /api/model/?unique_fields=...      # Smart upsert routing
    - PUT    /api/model/?unique_fields=...      # Smart upsert routing

    Relies on DRF's built-in payload size limits for request validation.
    Maintains synchronous API behavior while optimizing performance and resource usage.
    Database triggers fire in the appropriate execution context based on payload type.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('django_bulk_drf.mixins')

    def get_serializer(self, *args, **kwargs):
        """Handle array data for serializers with upsert context."""
        try:
            data = kwargs.get("data", None)
            if data is not None and isinstance(data, list):
                kwargs["many"] = True

            serializer = super().get_serializer(*args, **kwargs)

            # Note: Upsert validation bypass is now handled directly in _handle_array_upsert_direct()
            # for individual serializers to ensure proper handling of uniqueness constraints

            return serializer
        except Exception:
            raise

    # =============================================================================
    # Enhanced Standard ViewSet Methods (Sync Operations)
    # =============================================================================

    def list(self, request, *args, **kwargs):
        """
        Enhanced list endpoint that supports multi-get via ?ids= parameter.

        - GET /api/model/                    # Standard list
        - GET /api/model/?ids=1,2,3          # Sync multi-get (small datasets)
        """
        ids_param = request.query_params.get("ids")
        if ids_param:
            return self._sync_multi_get(request, ids_param)

        # Standard list behavior
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Enhanced create endpoint that supports bulk operations.

        - POST /api/model/                                    # Standard single create (dict data)
        - POST /api/model/                                    # Bulk create (array data, uses Celery)
        - POST /api/model/?unique_fields=field1,field2       # Bulk upsert (array data, uses Celery)
        """
        unique_fields_param = request.query_params.get("unique_fields")
        self.logger.debug(
            f"BulkOperationsMixin.create() - unique_fields_param: {unique_fields_param}, data_type: {type(request.data)}, is_list: {isinstance(request.data, list)}"
        )

        if isinstance(request.data, list):
            # Array data - route based on unique_fields presence
            if unique_fields_param:
                self.logger.debug(
                    f"BulkOperationsMixin.create() - Routing to bulk upsert with unique_fields: {unique_fields_param}"
                )
                return self._sync_upsert(request, unique_fields_param)
            else:
                self.logger.debug(
                    "BulkOperationsMixin.create() - Routing to bulk create (no unique_fields)"
                )
                return self._handle_bulk_create(request)

        self.logger.debug(
            "BulkOperationsMixin.create() - Using standard single create behavior"
        )
        # Standard single create behavior
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Enhanced update endpoint that supports sync upsert via query params.

        - PUT /api/model/{id}/                               # Standard single update
        - PUT /api/model/?unique_fields=field1,field2       # Sync upsert (array data)
        """
        unique_fields_param = request.query_params.get("unique_fields")
        if unique_fields_param and isinstance(request.data, list):
            return self._sync_upsert(request, unique_fields_param)

        # Standard single update behavior
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Enhanced partial update endpoint that supports sync upsert via query params.

        - PATCH /api/model/{id}/                             # Standard single partial update
        - PATCH /api/model/?unique_fields=field1,field2     # Sync upsert (array data)
        """
        unique_fields_param = request.query_params.get("unique_fields")
        if unique_fields_param and isinstance(request.data, list):
            return self._sync_upsert(request, unique_fields_param)

        # Standard single partial update behavior
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="unique_fields",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated unique field names for upsert mode",
                examples=[OpenApiExample("Fields", value="account_number,email")],
            ),
            OpenApiParameter(
                name="update_fields",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated field names to update (optional, auto-inferred if not provided)",
                examples=[OpenApiExample("Fields", value="business,status")],
            ),
            OpenApiParameter(
                name="max_items",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Maximum items for sync processing (default: 50)",
                examples=[OpenApiExample("Max Items", value=50)],
            ),
            OpenApiParameter(
                name="partial_success",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Allow partial success (default: false). Set to 'true' to allow some records to succeed while others fail.",
                examples=[OpenApiExample("Partial Success", value="true")],
            ),
            OpenApiParameter(
                name="include_results",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="If 'false', skips serializing response results to improve performance (default: true)",
                examples=[OpenApiExample("Include Results", value="false")],
            ),
            OpenApiParameter(
                name="db_batch_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Optional database batch_size for bulk_create (default: ORM default)",
                examples=[OpenApiExample("DB Batch Size", value=2000)],
            ),
        ],
        request={
            "application/json": {
                "type": "array",
                "description": "Array of objects to upsert",
            }
        },
        responses={
            200: {
                "description": "Upsert completed successfully - returns updated/created objects",
                "oneOf": [
                    {"type": "object", "description": "Single object response"},
                    {"type": "array", "description": "Multiple objects response"},
                ],
            },
            207: {
                "description": "Partial success - some records succeeded, others failed",
                "type": "object",
                "properties": {
                    "success": {
                        "type": "array",
                        "description": "Successfully processed records",
                    },
                    "errors": {
                        "type": "array",
                        "description": "Failed records with error details",
                    },
                    "summary": {"type": "object", "description": "Operation summary"},
                },
            },
            400: {"description": "Bad request - missing parameters or invalid data"},
        },
        description="Upsert multiple instances synchronously. Creates new records or updates existing ones based on unique fields. Defaults to all-or-nothing behavior unless partial_success=true.",
        summary="Sync upsert (PATCH)",
    )
    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH requests on list endpoint for sync upsert.

        DRF doesn't handle PATCH on list endpoints by default, so we add this method
        to support: PATCH /api/model/?unique_fields=field1,field2
        """
        unique_fields_param = request.query_params.get("unique_fields")
        preparsed_list = request.data

        if unique_fields_param and isinstance(preparsed_list, list):
            return self._sync_upsert(
                request, unique_fields_param, preparsed_data=preparsed_list
            )

        # If no unique_fields or not array data, this is invalid
        return Response(
            {
                "error": "PATCH on list endpoint requires 'unique_fields' parameter and array data"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="unique_fields",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated unique field names for upsert mode",
                examples=[OpenApiExample("Fields", value="account_number,email")],
            ),
            OpenApiParameter(
                name="update_fields",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated field names to update (optional, auto-inferred if not provided)",
                examples=[OpenApiExample("Fields", value="business,status")],
            ),
            OpenApiParameter(
                name="max_items",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Maximum items for sync processing (default: 50)",
                examples=[OpenApiExample("Max Items", value=50)],
            ),
            OpenApiParameter(
                name="partial_success",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Allow partial success (default: false). Set to 'true' to allow some records to succeed while others fail.",
                examples=[OpenApiExample("Partial Success", value="true")],
            ),
            OpenApiParameter(
                name="include_results",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="If 'false', skips serializing response results to improve performance (default: true)",
                examples=[OpenApiExample("Include Results", value="false")],
            ),
            OpenApiParameter(
                name="db_batch_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Optional database batch_size for bulk_create (default: ORM default)",
                examples=[OpenApiExample("DB Batch Size", value=2000)],
            ),
        ],
        request={
            "application/json": {
                "type": "array",
                "description": "Array of objects to upsert",
            }
        },
        responses={
            200: {
                "description": "Upsert completed successfully - returns updated/created objects",
                "oneOf": [
                    {"type": "object", "description": "Single object response"},
                    {"type": "array", "description": "Multiple objects response"},
                ],
            },
            207: {
                "description": "Partial success - some records succeeded, others failed",
                "type": "object",
                "properties": {
                    "success": {
                        "type": "array",
                        "description": "Successfully processed records",
                    },
                    "errors": {
                        "type": "array",
                        "description": "Failed records with error details",
                    },
                    "summary": {"type": "object", "description": "Operation summary"},
                },
            },
            400: {"description": "Bad request - missing parameters or invalid data"},
        },
        description="Upsert multiple instances synchronously. Creates new records or updates existing ones based on unique fields. Defaults to all-or-nothing behavior unless partial_success=true.",
        summary="Sync upsert (PUT)",
    )
    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests on list endpoint for sync upsert.

        DRF doesn't handle PUT on list endpoints by default, so we add this method
        to support: PUT /api/model/?unique_fields=field1,field2
        """
        unique_fields_param = request.query_params.get("unique_fields")
        if unique_fields_param and isinstance(request.data, list):
            return self._sync_upsert(request, unique_fields_param)

        # If no unique_fields or not array data, this is invalid
        return Response(
            {
                "error": "PUT on list endpoint requires 'unique_fields' parameter and array data"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # =============================================================================
    # Sync Operation Implementations
    # =============================================================================

    def _sync_multi_get(self, request, ids_param):
        """Handle sync multi-get - direct for single items, Celery for arrays."""
        try:
            ids_list = [int(id_str.strip()) for id_str in ids_param.split(",")]
        except ValueError:
            return Response(
                {"error": "Invalid ID format. Use comma-separated integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Simple routing: single item direct, arrays via Celery
        if len(ids_list) == 1:
            # Single item - direct database call
            return self._handle_single_get(ids_list[0])
        else:
            # Multiple items - use Celery workers
            return self._handle_array_get(request, ids_list)

    def _handle_single_get(self, item_id):
        """Handle single item retrieval directly without Celery overhead."""
        try:
            queryset = self.get_queryset().filter(id=item_id)
            instance = queryset.first()

            if instance:
                serializer = self.get_serializer(instance)
                return Response(
                    {
                        "count": 1,
                        "results": [serializer.data],
                        "is_sync": True,
                        "operation_type": "direct_get",
                    }
                )
            else:
                return Response(
                    {"error": f"Item with id {item_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response(
                {"error": f"Direct get failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_array_get(self, request, ids_list):
        """Handle array retrieval using Celery workers."""
        # Use Celery worker for multiple items
        model_class = self.get_queryset().model
        model_class_path = f"{model_class.__module__}.{model_class.__name__}"
        serializer_class = self.get_serializer_class()
        serializer_class_path = (
            f"{serializer_class.__module__}.{serializer_class.__name__}"
        )

        query_data = {"ids": ids_list}
        user_id = request.user.id if request.user.is_authenticated else None

        # Start Celery task with optimized settings
        task = async_get_task.delay(
            model_class_path, serializer_class_path, query_data, user_id
        )

        # Wait for task completion with fixed timeout
        try:
            # Wait for the task to complete (synchronous behavior)
            task_result = task.get(timeout=180)  # 3 minute timeout for get operations

            if task_result.get("success", False):
                return Response(
                    {
                        "count": task_result.get("count", 0),
                        "results": task_result.get("results", []),
                        "is_sync": True,
                        "task_id": task.id,
                        "operation_type": "sync_get_via_worker",
                    }
                )
            else:
                return Response(
                    {"error": f"Worker task failed: {task_result.get('error')}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:
            return Response(
                {"error": f"Task execution failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _sync_upsert(self, request, unique_fields_param, preparsed_data=None):
        """Handle sync upsert operations - direct for single items, Celery for arrays."""
        self.logger.debug(
            f"BulkOperationsMixin._sync_upsert() - Called with unique_fields_param: {unique_fields_param}"
        )

        # Parse parameters
        unique_fields = [f.strip() for f in unique_fields_param.split(",") if f.strip()]
        self.logger.debug(
            f"BulkOperationsMixin._sync_upsert() - Parsed unique_fields: {unique_fields}"
        )

        update_fields_param = request.query_params.get("update_fields")
        update_fields = None
        if update_fields_param:
            update_fields = [
                f.strip() for f in update_fields_param.split(",") if f.strip()
            ]
        self.logger.debug(
            f"BulkOperationsMixin._sync_upsert() - Parsed update_fields: {update_fields}"
        )

        # Use pre-parsed data from caller if available
        data_payload = preparsed_data if preparsed_data is not None else request.data
        self.logger.debug(
            f"BulkOperationsMixin._sync_upsert() - Data payload type: {type(data_payload)}, is_list: {isinstance(data_payload, list)}"
        )

        if isinstance(data_payload, list):
            self.logger.debug(
                f"BulkOperationsMixin._sync_upsert() - Array with {len(data_payload)} items"
            )

        # Simple routing: dict direct, list via Celery
        if isinstance(data_payload, dict):
            self.logger.debug(
                "BulkOperationsMixin._sync_upsert() - Routing to single upsert"
            )
            # Single instance - direct database operations
            return self._handle_single_upsert(
                request, unique_fields, update_fields, data_payload
            )
        elif isinstance(data_payload, list):
            self.logger.debug(
                "BulkOperationsMixin._sync_upsert() - Routing to array upsert (Celery)"
            )
            # Array - use Celery workers for heavy operations
            return self._handle_array_upsert(
                request, unique_fields, update_fields, data_payload
            )
        else:
            self.logger.debug(
                f"BulkOperationsMixin._sync_upsert() - Invalid data type: {type(data_payload)}"
            )
            return Response(
                {"error": "Expected dict or array data for upsert operations."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _handle_single_upsert(self, request, unique_fields, update_fields, data_dict):
        """Handle single instance upsert directly without Celery overhead."""
        self.logger.debug(
            f"BulkOperationsMixin._handle_single_upsert() - Processing single item: {data_dict}"
        )

        if not unique_fields:
            self.logger.error(
                "BulkOperationsMixin._handle_single_upsert() - ERROR: No unique_fields provided"
            )
            return Response(
                {"error": "unique_fields parameter is required for upsert operations"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Auto-infer update_fields if not provided
        if not update_fields:
            update_fields = self._infer_update_fields([data_dict], unique_fields)
            self.logger.debug(
                f"BulkOperationsMixin._handle_single_upsert() - Auto-inferred update_fields: {update_fields}"
            )

        # Use direct database operations for single instance
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model
        self.logger.debug(
            f"BulkOperationsMixin._handle_single_upsert() - Using model: {model_class.__name__}"
        )

        try:
            # Try to find existing instance
            unique_filter = {}
            for field in unique_fields:
                if field in data_dict:
                    unique_filter[field] = data_dict[field]

            self.logger.debug(
                f"BulkOperationsMixin._handle_single_upsert() - Unique filter: {unique_filter}"
            )

            existing_instance = None
            if unique_filter:
                existing_instance = model_class.objects.filter(**unique_filter).first()
                self.logger.debug(
                    f"BulkOperationsMixin._handle_single_upsert() - Existing instance found: {existing_instance is not None}"
                )

            if existing_instance:
                self.logger.debug(
                    f"BulkOperationsMixin._handle_single_upsert() - Updating existing instance ID: {existing_instance.id}"
                )
                # Update existing instance
                if update_fields:
                    update_data = {
                        k: v for k, v in data_dict.items() if k in update_fields
                    }
                else:
                    update_data = {
                        k: v for k, v in data_dict.items() if k not in unique_fields
                    }

                self.logger.debug(
                    f"BulkOperationsMixin._handle_single_upsert() - Update data: {update_data}"
                )

                for field, value in update_data.items():
                    setattr(existing_instance, field, value)
                existing_instance.save()

                serializer = serializer_class(existing_instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                self.logger.debug(
                    "BulkOperationsMixin._handle_single_upsert() - Creating new instance"
                )
                # Create new instance
                serializer = serializer_class(data=data_dict)
                if serializer.is_valid():
                    instance = serializer.save()
                    self.logger.debug(
                        f"BulkOperationsMixin._handle_single_upsert() - Created instance ID: {instance.id}"
                    )
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    self.logger.error(
                        f"BulkOperationsMixin._handle_single_upsert() - Validation failed: {serializer.errors}"
                    )
                    return Response(
                        {
                            "error": "Validation failed",
                            "errors": [
                                {
                                    "index": 0,
                                    "error": str(serializer.errors),
                                    "data": data_dict,
                                }
                            ],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Exception as e:
            self.logger.error(
                f"BulkOperationsMixin._handle_single_upsert() - ERROR: {str(e)}"
            )
            return Response(
                {"error": f"Direct upsert failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_bulk_create(self, request):
        """Handle bulk create operations using Celery workers."""
        data_list = request.data
        self.logger.debug(
            f"BulkOperationsMixin._handle_bulk_create() - Processing bulk create with {len(data_list)} items"
        )

        # Use Celery worker for bulk create
        serializer_class = self.get_serializer_class()
        serializer_class_path = (
            f"{serializer_class.__module__}.{serializer_class.__name__}"
        )
        user_id = request.user.id if request.user.is_authenticated else None

        # Start Celery bulk create task
        self.logger.debug(
            "BulkOperationsMixin._handle_bulk_create() - Dispatching bulk create to Celery"
        )
        task = async_create_task.delay(serializer_class_path, data_list, user_id)
        self.logger.debug(
            f"BulkOperationsMixin._handle_bulk_create() - Task dispatched with ID: {task.id}"
        )

        # Wait for task completion
        try:
            self.logger.debug(
                "BulkOperationsMixin._handle_bulk_create() - Waiting for task completion (300s timeout)..."
            )
            # Wait for the task to complete (synchronous behavior)
            task_result = task.get(
                timeout=300
            )  # 5 minute timeout for bulk create operations
            self.logger.debug(
                "BulkOperationsMixin._handle_bulk_create() - Task completed successfully"
            )
            self.logger.debug(
                f"BulkOperationsMixin._handle_bulk_create() - Result: success_count={task_result.get('success_count', 0)}, error_count={task_result.get('error_count', 0)}"
            )

            # Check for errors first
            errors = task_result.get("errors", [])
            if errors:
                self.logger.error(
                    f"BulkOperationsMixin._handle_bulk_create() - Returning errors: {errors}"
                )
                return Response(
                    {
                        "errors": errors,
                        "error_count": task_result.get("error_count", 0),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Return successful result in standard DRF format
            serializer_class = self.get_serializer_class()
            model_class = serializer_class.Meta.model

            # Get the created instances
            created_ids = task_result.get("created_ids", [])
            if created_ids:
                created_instances = list(model_class.objects.filter(id__in=created_ids))
                serializer = serializer_class(created_instances, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # No instances were created successfully
                self.logger.debug(
                    "BulkOperationsMixin._handle_bulk_create() - No instances created and no errors"
                )
                return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            self.logger.error(
                f"BulkOperationsMixin._handle_bulk_create() - ERROR: Task execution failed: {str(e)}"
            )
            return Response(
                {"error": f"Bulk create task execution failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_array_upsert(self, request, unique_fields, update_fields, data_list):
        """Handle array upsert using Celery workers."""
        self.logger.debug(
            f"BulkOperationsMixin._handle_array_upsert() - Processing array with {len(data_list)} items"
        )

        # TEMPORARY DEBUGGING: Bypass Celery for direct debugging
        # Set to True to debug validation issues without Celery overhead
        DEBUG_BYPASS_CELERY = True  # Set to False to use Celery again

        if DEBUG_BYPASS_CELERY:
            self.logger.debug(
                "BulkOperationsMixin._handle_array_upsert() - DEBUG MODE: Bypassing Celery for direct execution"
            )
            return self._handle_array_upsert_direct(
                request, unique_fields, update_fields, data_list
            )

        if not unique_fields:
            self.logger.error(
                "BulkOperationsMixin._handle_array_upsert() - ERROR: No unique_fields provided"
            )
            return Response(
                {"error": "unique_fields parameter is required for upsert operations"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Auto-infer update_fields if not provided
        if not update_fields:
            update_fields = self._infer_update_fields(data_list, unique_fields)
            self.logger.debug(
                f"BulkOperationsMixin._handle_array_upsert() - Auto-inferred update_fields: {update_fields}"
            )

        # Use Celery worker for array operations
        serializer_class = self.get_serializer_class()
        serializer_class_path = (
            f"{serializer_class.__module__}.{serializer_class.__name__}"
        )
        self.logger.debug(
            f"BulkOperationsMixin._handle_array_upsert() - Using serializer: {serializer_class_path}"
        )

        user_id = request.user.id if request.user.is_authenticated else None
        self.logger.debug(
            f"BulkOperationsMixin._handle_array_upsert() - User ID: {user_id}"
        )

        # Start Celery upsert task with optimized settings
        self.logger.debug(
            "BulkOperationsMixin._handle_array_upsert() - Dispatching Celery task..."
        )

        # Pass upsert context to skip uniqueness validation
        upsert_context = {
            "skip_uniqueness_validation": True,
            "unique_fields": unique_fields,
        }

        task = async_upsert_task.delay(
            serializer_class_path,
            data_list,
            unique_fields,
            update_fields,
            user_id,
            upsert_context,
        )
        self.logger.debug(
            f"BulkOperationsMixin._handle_array_upsert() - Task dispatched with ID: {task.id}"
        )

        # Wait for task completion with fixed timeout
        try:
            self.logger.debug(
                "BulkOperationsMixin._handle_array_upsert() - Waiting for task completion (300s timeout)..."
            )
            # Wait for the task to complete (synchronous behavior)
            task_result = task.get(
                timeout=300
            )  # 5 minute timeout for upsert operations
            self.logger.debug(
                "BulkOperationsMixin._handle_array_upsert() - Task completed successfully"
            )
            self.logger.debug(
                f"BulkOperationsMixin._handle_array_upsert() - Result: success_count={task_result.get('success_count', 0)}, error_count={task_result.get('error_count', 0)}"
            )

            # Check for errors first
            errors = task_result.get("errors", [])
            if errors:
                self.logger.error(
                    f"BulkOperationsMixin._handle_array_upsert() - Returning errors: {errors}"
                )
                return Response(
                    {
                        "errors": errors,
                        "error_count": task_result.get("error_count", 0),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Return successful result in standard DRF format
            serializer_class = self.get_serializer_class()
            model_class = serializer_class.Meta.model

            # Get all affected instances (created and updated)
            created_ids = task_result.get("created_ids", [])
            updated_ids = task_result.get("updated_ids", [])
            all_ids = created_ids + updated_ids

            if all_ids:
                affected_instances = list(model_class.objects.filter(id__in=all_ids))
                serializer = serializer_class(affected_instances, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # No instances were affected and no errors
                self.logger.debug(
                    "BulkOperationsMixin._handle_array_upsert() - No instances affected and no errors"
                )
                return Response([], status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(
                f"BulkOperationsMixin._handle_array_upsert() - ERROR: Task execution failed: {str(e)}"
            )
            return Response(
                {"error": f"Upsert task execution failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_array_upsert_direct(
        self, request, unique_fields, update_fields, data_list
    ):
        """
        Simplified bulk upsert that leverages DRF's internal field conversion.

        Instead of manually converting fields, we use DRF's save() method to handle
        all the complex field conversion, then extract the model data for bulk operations.
        """
        import time
        start_time = time.time()
        
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model

        self.logger.debug(
            f"BulkOperationsMixin._handle_array_upsert_direct() - Processing {len(data_list)} items"
        )
        
        # Log timing for initialization
        init_time = time.time() - start_time
        self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Initialization took {init_time:.4f}s")

        instances_to_upsert = []
        errors = []

        # Start timing for data processing
        data_processing_start = time.time()
        
        for index, item_data in enumerate(data_list):
            try:
                self.logger.debug(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Processing item {index}: {item_data}"
                )

                # For upsert operations, we bypass DRF's uniqueness validation completely
                # and handle uniqueness at the database level during bulk_create with update_conflicts
                serializer = serializer_class(
                    data=item_data, context={"upsert_mode": True}
                )

                # Manually convert field values without running uniqueness validation
                validated_data = {}
                for field_name, field_value in item_data.items():
                    if (
                        hasattr(serializer, "fields")
                        and field_name in serializer.fields
                    ):
                        field = serializer.fields[field_name]
                        try:
                            # Use the field's to_internal_value method directly to convert data types
                            # This bypasses uniqueness validation while still doing field conversion
                            validated_data[field_name] = field.to_internal_value(
                                field_value
                            )
                        except Exception as field_error:
                            self.logger.warning(
                                f"BulkOperationsMixin._handle_array_upsert_direct() - Field conversion failed for {field_name}: {field_error}, using original value"
                            )
                            # If field conversion fails, use the original value
                            validated_data[field_name] = field_value
                    else:
                        # If field is not in serializer, use original value
                        validated_data[field_name] = field_value

                self.logger.debug(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Converted data {index}: {validated_data}"
                )

                # Create a new instance with the validated data for bulk operations
                new_instance = model_class(**validated_data)
                instances_to_upsert.append(new_instance)

            except Exception as e:
                self.logger.error(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Error processing item {index}: {e}"
                )
                errors.append(
                    {
                        "index": index,
                        "error": f"Processing error: {str(e)}",
                        "data": item_data,
                    }
                )

        # Log timing for data processing
        data_processing_time = time.time() - data_processing_start
        self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Data processing took {data_processing_time:.4f}s for {len(data_list)} items")

        # Return errors if any
        if errors:
            self.logger.error(
                f"BulkOperationsMixin._handle_array_upsert_direct() - Returning {len(errors)} errors"
            )
            return Response(
                {"errors": errors, "error_count": len(errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Now perform the bulk upsert with the properly converted instances
        if instances_to_upsert:
            try:
                bulk_operation_start = time.time()
                
                self.logger.debug(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Performing bulk upsert with {len(instances_to_upsert)} instances"
                )
                self.logger.debug(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Instance data preview: {[{'id': getattr(inst, 'id', None), **{k: getattr(inst, k) for k in unique_fields if hasattr(inst, k)}} for inst in instances_to_upsert[:3]]}"
                )

                # Auto-infer update_fields if not provided
                field_inference_start = time.time()
                if not update_fields:
                    update_fields = self._infer_update_fields(data_list, unique_fields)
                    self.logger.debug(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Auto-inferred update_fields: {update_fields}"
                    )

                    # If no update_fields were inferred, provide a default set
                    # This ensures we have fields to update when conflicts occur
                    if not update_fields:
                        # Get all model fields except unique_fields and auto fields
                        model_fields = [f.name for f in model_class._meta.fields]
                        auto_fields = ["id", "created_at", "updated_at"]
                        unique_fields_set = set(unique_fields)

                        update_fields = [
                            field
                            for field in model_fields
                            if field not in unique_fields_set
                            and field not in auto_fields
                        ]
                        self.logger.debug(
                            f"BulkOperationsMixin._handle_array_upsert_direct() - Using default update_fields: {update_fields}"
                        )
                
                field_inference_time = time.time() - field_inference_start
                self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Field inference took {field_inference_time:.4f}s")

                # Implement proper upsert logic: check existing records and handle create vs update separately
                self.logger.debug(
                    "BulkOperationsMixin._handle_array_upsert_direct() - Implementing proper upsert logic"
                )
                self.logger.debug(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - unique_fields: {unique_fields}, update_fields: {update_fields}"
                )

                # Step 1: Extract unique field values from all instances to check for existing records
                unique_extraction_start = time.time()
                unique_values_list = []
                for instance in instances_to_upsert:
                    unique_values = {}
                    for field in unique_fields:
                        if hasattr(instance, field):
                            unique_values[field] = getattr(instance, field)
                    if unique_values:
                        unique_values_list.append(unique_values)

                unique_extraction_time = time.time() - unique_extraction_start
                self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Unique value extraction took {unique_extraction_time:.4f}s")
                self.logger.debug(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Checking for {len(unique_values_list)} existing records"
                )

                # Step 2: Find existing records based on unique fields
                db_query_start = time.time()
                existing_records = {}
                if unique_values_list:
                    # Build a query to find all existing records in one query
                    query_conditions = []
                    for unique_values in unique_values_list:
                        condition = {}
                        for field, value in unique_values.items():
                            condition[f"{field}"] = value
                        query_conditions.append(condition)

                    # Use Q objects to build OR conditions for finding existing records
                    combined_query = Q()
                    for condition in query_conditions:
                        combined_query |= Q(**condition)

                    existing_queryset = model_class.objects.filter(combined_query)
                    existing_records = {
                        tuple(getattr(obj, field) for field in unique_fields): obj
                        for obj in existing_queryset
                    }

                db_query_time = time.time() - db_query_start
                self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Database query for existing records took {db_query_time:.4f}s")
                self.logger.debug(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Found {len(existing_records)} existing records"
                )

                # Step 3: Separate instances into create vs update lists
                separation_start = time.time()
                instances_to_create = []
                instances_to_update = []

                for instance in instances_to_upsert:
                    unique_key = tuple(
                        getattr(instance, field) for field in unique_fields
                    )
                    if unique_key in existing_records:
                        # This is an update operation
                        existing_instance = existing_records[unique_key]
                        self.logger.debug(
                            f"BulkOperationsMixin._handle_array_upsert_direct() - Will update existing record ID {existing_instance.id}"
                        )
                        instances_to_update.append((instance, existing_instance))
                    else:
                        # This is a create operation
                        instances_to_create.append(instance)

                separation_time = time.time() - separation_start
                self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Instance separation took {separation_time:.4f}s")

                # Step 4: Perform bulk create for new records
                bulk_create_start = time.time()
                created_instances = []
                if instances_to_create:
                    self.logger.debug(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Bulk creating {len(instances_to_create)} new records"
                    )
                    created_instances = model_class.objects.bulk_create(
                        instances_to_create, batch_size=1000
                    )
                
                bulk_create_time = time.time() - bulk_create_start
                self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Bulk create took {bulk_create_time:.4f}s")

                # Step 5: Perform bulk updates for existing records (no DML in loops!)
                bulk_update_start = time.time()
                updated_instances = []
                update_preparation_time = 0.0  # Initialize to avoid UnboundLocalError
                
                if instances_to_update:
                    self.logger.debug(
                        f"BulkOperationsMixin._handle_array_upsert_direct() - Bulk updating {len(instances_to_update)} existing records"
                    )

                    # Prepare data for bulk update - map existing instances to new data
                    update_preparation_start = time.time()
                    instances_to_bulk_update = []
                    fields_to_bulk_update = set()

                    for new_data_instance, existing_instance in instances_to_update:
                        # Update the existing instance with new data
                        if update_fields:
                            for field in update_fields:
                                if hasattr(new_data_instance, field):
                                    setattr(
                                        existing_instance,
                                        field,
                                        getattr(new_data_instance, field),
                                    )
                                    fields_to_bulk_update.add(field)
                        else:
                            # Update all non-unique fields
                            for field in model_class._meta.fields:
                                if (
                                    field.name not in unique_fields
                                    and not field.primary_key
                                    and not getattr(field, "auto_now", False)
                                ):
                                    if hasattr(new_data_instance, field.name):
                                        setattr(
                                            existing_instance,
                                            field.name,
                                            getattr(new_data_instance, field.name),
                                        )
                                        fields_to_bulk_update.add(field.name)

                        instances_to_bulk_update.append(existing_instance)

                    update_preparation_time = time.time() - update_preparation_start
                    self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Update preparation took {update_preparation_time:.4f}s")

                    # Perform bulk update (single query, no loop!)
                    if instances_to_bulk_update and fields_to_bulk_update:
                        self.logger.debug(
                            f"BulkOperationsMixin._handle_array_upsert_direct() - Bulk updating fields: {list(fields_to_bulk_update)}"
                        )
                        model_class.objects.bulk_update(
                            instances_to_bulk_update,
                            list(fields_to_bulk_update),
                            batch_size=1000,
                        )

                    updated_instances = instances_to_bulk_update
                
                bulk_update_time = time.time() - bulk_update_start
                self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Bulk update took {bulk_update_time:.4f}s")

                # Step 6: Collect all affected instances and serialize response
                serialization_start = time.time()
                all_instances = list(created_instances) + updated_instances

                self.logger.debug(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Successfully processed {len(all_instances)} instances ({len(created_instances)} created, {len(updated_instances)} updated)"
                )

                if all_instances:
                    serializer = serializer_class(all_instances, many=True)
                    response_data = serializer.data
                else:
                    response_data = []
                
                serialization_time = time.time() - serialization_start
                self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Serialization took {serialization_time:.4f}s")
                
                # Log total timing
                total_time = time.time() - bulk_operation_start
                self.logger.debug(f"BulkOperationsMixin._handle_array_upsert_direct() - Total bulk operation took {total_time:.4f}s")
                
                # Log detailed timing breakdown
                self.logger.info("BulkOperationsMixin._handle_array_upsert_direct() - TIMING BREAKDOWN:")
                self.logger.info(f"  - Initialization: {init_time:.4f}s")
                self.logger.info(f"  - Data processing: {data_processing_time:.4f}s")
                self.logger.info(f"  - Field inference: {field_inference_time:.4f}s")
                self.logger.info(f"  - Unique extraction: {unique_extraction_time:.4f}s")
                self.logger.info(f"  - DB query: {db_query_time:.4f}s")
                self.logger.info(f"  - Instance separation: {separation_time:.4f}s")
                self.logger.info(f"  - Bulk create: {bulk_create_time:.4f}s")
                self.logger.info(f"  - Update preparation: {update_preparation_time:.4f}s")
                self.logger.info(f"  - Bulk update: {bulk_update_time:.4f}s")
                self.logger.info(f"  - Serialization: {serialization_time:.4f}s")
                self.logger.info(f"  - TOTAL: {total_time:.4f}s")

                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                self.logger.error(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Bulk upsert failed: {e}"
                )

                # Provide more specific error messages for common issues
                error_message = str(e).lower()
                if (
                    "unique constraint" in error_message
                    or "unique_fields" in error_message
                ):
                    detailed_error = (
                        "Unique constraint error during upsert. "
                        f"Ensure that fields {unique_fields} form a unique constraint in your database. "
                        "If you're using a multi-column unique constraint, make sure it's properly defined."
                    )
                elif (
                    "cannot force an update" in error_message
                    or "no primary key" in error_message
                ):
                    detailed_error = (
                        "Upsert operation failed due to primary key conflicts. "
                        "This usually occurs when trying to update existing records without proper primary key handling."
                    )
                else:
                    detailed_error = f"Bulk upsert failed: {str(e)}"

                return Response(
                    {
                        "error": "Bulk upsert failed",
                        "details": detailed_error,
                        "unique_fields": unique_fields,
                        "update_fields": update_fields,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            self.logger.debug(
                "BulkOperationsMixin._handle_array_upsert_direct() - No instances to upsert"
            )
            return Response([], status=status.HTTP_200_OK)

    def _infer_update_fields(self, data_list, unique_fields):
        """Auto-infer update fields from data payload."""
        if not data_list:
            return []

        all_fields = set()
        for item in data_list:
            if isinstance(item, dict):
                all_fields.update(item.keys())

        unique_fields_set = set(unique_fields)
        return list(all_fields - unique_fields_set)


# Legacy aliases for backwards compatibility
OperationsMixin = BulkOperationsMixin  # Backward compatibility alias
