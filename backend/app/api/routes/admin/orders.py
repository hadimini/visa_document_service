import logging

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository
from app.database.repositories.audit import AuditRepository
from app.database.repositories.orders import OrdersRepository
from app.exceptions import NotFoundException
from app.models import LogEntry, Order, User
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.order.admin import (
    AdminOrderFilterSchema,
    AdminOrderPaginatedListSchema,
    AdminOrderDetailSchema,
    AdminOrderCreateSchema,
    AdminOrderUpdateSchema,
)
from app.schemas.order.base import OrderStatusEnum
from app.schemas.pagination import PageParamsSchema

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
        orders_repo: OrdersRepository = Depends(get_repository(OrdersRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
        current_user: User = Depends(get_current_active_user)
):
    try:
        order_data = AdminOrderCreateSchema(
            created_by_id=current_user.id,
            **data.model_dump(exclude={"created_by_id"}),
        )
        order = await orders_repo.create(data=order_data, populate_client=True)

        await audit_repo.create(
            data=LogEntryCreateSchema(
                user_id=current_user.id,
                action=LogEntry.ACTION_CREATE,
                model_type=Order.get_model_type(),
                target_id=order.id
            )
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
        order_id: int = Path(..., gt=0, description="Order ID must be a positive integer"),
        orders_repo: OrdersRepository = Depends(get_repository(OrdersRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
        current_user: User = Depends(get_current_active_user)
):
    try:
        order = await orders_repo.update(order_id=order_id, data=data, populate_client=True)

        if not order:
            raise NotFoundException()

        await audit_repo.create(
            data=LogEntryCreateSchema(
                user_id=current_user.id,
                action=LogEntry.ACTION_UPDATE,
                model_type=Order.get_model_type(),
                target_id=order.id
            )
        )
        return order

    except NotFoundException:
        raise NotFoundException(detail="Order not found")

    except Exception as e:
        logger.error(f"Failed to update order {order_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update order")
