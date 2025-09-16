from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository


from app.database.repositories.audit import AuditRepository
from app.database.repositories.services import ServicesRepository
from app.exceptions import NotFoundException
from app.models import LogEntry, Service, User
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.pagination import PageParamsSchema
from app.schemas.service import ServiceResponseSchema, ServiceFilterSchema, ServiceCreateSchema, \
    ServiceListResponseSchema, ServiceUpdateSchema

router = APIRouter()


@router.get(
    path="",
    response_model=ServiceListResponseSchema,
    name="admin:service-list"
)
async def service_list(
        query_filters: ServiceFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository))
):
    """Retrieve a paginated list of services based on filter criteria.

    This endpoint allows administrators to fetch a list of services with optional
    filtering and pagination.

    Args:
        query_filters (ServiceFilterSchema): The filters to apply to the service list.
        page_params (PageParamsSchema): The pagination parameters (page number and size).
        services_repo (ServicesRepository): The repository for accessing service data.

    Returns:
        ServiceListResponseSchema: A paginated list of services.
    """
    result = await services_repo.get_paginated_list(query_filters=query_filters, page_params=page_params)
    return result


@router.get(
    path="/{service_id}",
    response_model=ServiceResponseSchema,
    name="admin:service-detail"
)
async def service_detail(
        service_id: int,
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository))
):
    """Retrieve the details of a specific service by its ID.

    This endpoint allows administrators to fetch detailed information about a specific
    service.

    Args:
        service_id (int): The ID of the service to retrieve.
        services_repo (ServicesRepository): The repository for accessing service data.

    Returns:
        ServiceResponseSchema: The details of the requested service.

    Raises:
        NotFoundException: If the service with the specified ID does not exist.
    """
    service = await services_repo.get_by_id(service_id=service_id)

    if not service:
        raise NotFoundException(detail="Service not found")

    return service


@router.post(
    path="",
    response_model=ServiceResponseSchema,
    name="admin:service-create",
    status_code=status.HTTP_201_CREATED
)
async def service_create(
        data: ServiceCreateSchema,
        current_user: User = Depends(get_current_active_user),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository))
):

    """Create a new service in the system.

    This endpoint allows administrators to create a new service and log the action.

    Args:
        data (ServiceCreateSchema): The data schema containing service details.
        current_user (User): The currently authenticated user.
        services_repo (ServicesRepository): The repository for accessing service data.
        audit_repo (AuditRepository): The repository for logging actions.

    Returns:
        ServiceResponseSchema: The details of the created service.
    """
    service = await services_repo.create(data=data)
    await audit_repo.create(
        data=LogEntryCreateSchema(
            user_id=current_user.id,
            action=LogEntry.ACTION_CREATE,
            model_type=Service.get_model_type(),
            target_id=service.id
        )
    )
    return service


@router.put(
    path="/{service_id}",
    response_model=ServiceResponseSchema,
    name="admin:service-update",
)
async def service_update(
        service_id: int,
        data: ServiceUpdateSchema,
        current_user: User = Depends(get_current_active_user),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository))
):
    """Update an existing service in the system.

    This endpoint allows administrators to modify the details of an existing service
    and log the action.

    Args:
        service_id (int): The ID of the service to update.
        data (ServiceUpdateSchema): The data schema containing updated service details.
        current_user (User): The currently authenticated user.
        services_repo (ServicesRepository): The repository for accessing service data.
        audit_repo (AuditRepository): The repository for logging actions.

    Returns:
        ServiceResponseSchema: The details of the updated service.

    Raises:
        NotFoundException: If the service with the specified ID does not exist.
    """
    service = await services_repo.update(service_id=service_id, data=data)

    if not service:
        raise NotFoundException(detail="Service not found")

    await audit_repo.create(
        data=LogEntryCreateSchema(
            user_id=current_user.id,
            action=LogEntry.ACTION_UPDATE,
            model_type=Service.get_model_type(),
            target_id=service.id
        )
    )
    return service
