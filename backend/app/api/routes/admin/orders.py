import logging

from fastapi import APIRouter, Depends, HTTPException, Path, status, BackgroundTasks

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository
from app.api.dependencies.order import get_order_service
from app.database.repositories.orders import OrdersRepository
from app.exceptions import NotFoundException
from app.models import User
from app.schemas.order.admin import (
    AdminOrderFilterSchema,
    AdminOrderPaginatedListSchema,
    AdminOrderDetailSchema,
    AdminOrderCreateSchema,
    AdminOrderUpdateSchema,
)
from app.schemas.order_service import OrderServicesDataSchema, OrderServicesUpdateSchema
from app.schemas.pagination import PageParamsSchema
from app.services.order import OrderService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    path="",
    response_model=AdminOrderPaginatedListSchema,
    name="admin:order-list",
    status_code=status.HTTP_200_OK,
)
async def order_paginated_list(
        query_filters: AdminOrderFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        orders_repo: OrdersRepository = Depends(get_repository(OrdersRepository)),
):
    """Retrieve a paginated list of orders based on filter criteria.

    This endpoint allows administrators to fetch a list of orders with optional
    filtering and pagination.

    Args:
        query_filters (AdminOrderFilterSchema): The filters to apply to the order list.
        page_params (PageParamsSchema): The pagination parameters (page number and size).
        orders_repo (OrdersRepository): The repository for accessing order data.

    Returns:
        AdminOrderPaginatedListSchema: A paginated list of orders.
    """
    result = await orders_repo.get_paginated_list(query_filters=query_filters, page_params=page_params)
    return result


@router.get(
    path="/{order_id}",
    response_model=AdminOrderDetailSchema,
    name="admin:order-detail",
    status_code=status.HTTP_200_OK,
)
async def order_detail(
        order_id: int = Path(..., gt=0, description="Order ID must be a positive integer"),
        orders_repo: OrdersRepository = Depends(get_repository(OrdersRepository))
):
    """Retrieve the details of a specific order by its ID.

    This endpoint allows administrators to fetch detailed information about a specific
    order.

    Args:
        order_id (int): The ID of the order to retrieve.
        orders_repo (OrdersRepository): The repository for accessing order data.

    Returns:
        AdminOrderDetailSchema: The details of the requested order.

    Raises:
        NotFoundException: If the order with the specified ID does not exist.
    """
    result = await orders_repo.get_by_id(order_id=order_id, populate_client=True)

    if result is None:
        raise NotFoundException(detail="Order not found")

    return result


@router.post(
    path="",
    response_model=AdminOrderDetailSchema,
    name="admin:order-create",
    status_code=status.HTTP_201_CREATED,
)
async def order_create(
        data: AdminOrderCreateSchema,
        order_service: OrderService = Depends(get_order_service),
        current_user: User = Depends(get_current_active_user)
):
    """Create a new order in the system.

    This endpoint allows administrators to create a new order and log the action.

    Args:
        data (AdminOrderCreateSchema): The data schema containing order details.
        orders_repo (OrdersRepository): The repository for accessing order data.
        audit_repo (AuditRepository): The repository for logging actions.
        current_user (User): The currently authenticated user.

    Returns:
        AdminOrderDetailSchema: The details of the created order.

    Raises:
        HTTPException: If the order creation fails.
    """
    try:
        order = await order_service.create_order(
            data=data,
            user_id=current_user.id,
            populate_client=True
        )
        return order

    except Exception as e:
        logger.error(f"Failed to create order: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create order")


@router.put(
    path="/{order_id}",
    response_model=AdminOrderDetailSchema,
    name="admin:order-update",
    status_code=status.HTTP_200_OK,
)
async def order_update(
        data: AdminOrderUpdateSchema,
        bg_tasks: BackgroundTasks,
        order_id: int = Path(..., gt=0, description="Order ID must be a positive integer"),
        order_service: OrderService = Depends(get_order_service),
        current_user: User = Depends(get_current_active_user),

):
    """Update an existing order in the system.

    This endpoint allows administrators to modify the details of an existing order.
    It also supports background tasks for additional processing if needed.

    Args:
        data (AdminOrderUpdateSchema): The data schema containing updated order details.
        bg_tasks (BackgroundTasks): Background tasks to be executed after the response is sent.
        order_id (int): The ID of the order to update.
        order_service (OrderService): The service for handling order-related operations.
        current_user (User): The currently authenticated user.

    Returns:
        AdminOrderDetailSchema: The details of the updated order.

    Raises:
        NotFoundException: If the order with the specified ID does not exist.
        HTTPException: If the order update fails for any reason.
    """
    try:
        order = await order_service.update_order(
            order_id=order_id,
            data=data,
            user_id=current_user.id,
            bg_tasks=bg_tasks,
            populate_client=True
        )
        return order

    except NotFoundException:
        raise NotFoundException(detail="Order not found")

    except Exception as e:
        logger.error(f"Failed to update order {order_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update order")


@router.get(
    path="/{order_id}/services",
    name="admin:order-services-list",
    response_model=OrderServicesDataSchema,
    status_code=status.HTTP_200_OK,
)
async def order_service_list(
        order_id: int = Path(..., gt=0, description="Order ID must be a positive integer"),
        orders_repo: OrdersRepository = Depends(get_repository(OrdersRepository)),
        order_service: OrderService = Depends(get_order_service),
):
    """Get services related to an order.

    Retrieves the services attached and available for a specified order ID.
    Returns HTTP 200 with a JSON object containing two lists:
     - **"attached"**: services currently attached to the order.
     - **"available"**: services that can be attached.

    Parameters:
        order_id : int
            Path parameter. ** Must be a positive integer.**
        order_service : OrderService
            Dependency-injected service used to retrieve attached and available services.

    Returns
    -------
    dict
        JSON object with keys "attatched" and "available", each mapping to a list of service objects.

    Raises:
    _______
        HTTPException 404: If the specified order does not exist.
        HTTPException 400: If there is an error updating the order services.
    """
    try:
        if await orders_repo.get_by_id(order_id=order_id) is None:
            raise NotFoundException()

        result = await order_service.get_order_services(order_id=order_id)
        return result
    except NotFoundException:
        raise NotFoundException(detail="Order not found")

    except Exception as e:
        logger.error(f"Failed to get services for order {order_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update order services")


@router.put(
    path="/{order_id}/services",
    name="admin:order-services-update",
    response_model=OrderServicesDataSchema,
    status_code=status.HTTP_200_OK,
)
async def order_service_update(
        data: OrderServicesUpdateSchema,
        order_id: int = Path(..., gt=0, description="Order ID must be a positive integer"),
        orders_repo: OrdersRepository = Depends(get_repository(OrdersRepository)),
        order_service: OrderService = Depends(get_order_service),
):
    """
    Update services for an existing order.

    Replaces all currently attached services with the specified tariff services.
    Returns the updated list of both attached and available services for the order.

    Args:
        order_id: ID of the order to update services for (path parameter, must be positive integer).
        data: Request body containing tariff services IDs to attach to the order.

    Returns:
        OrderServicesDataSchema: Object containing:
            - attached: list of services currently attached to the order.
            - available: list of services available for attachment based on order criteria.

    Raises:
    ______
        HTTPException 404: If the specified order does not exist.
        HTTPException 400: If there is an error updating the order services.

    Example:
        PUT /admin/orders/123/services
        {
            "tariff_services_ids": [1, 2, 3]
        }
    """
    try:
        if await orders_repo.get_by_id(order_id=order_id) is None:
            raise NotFoundException()

        result = await order_service.update_order_services(order_id=order_id, data=data)
        return result

    except NotFoundException:
        raise NotFoundException(detail="Order not found")

    except Exception as e:
        logger.error(f"Failed to update services for order {order_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update order services")
