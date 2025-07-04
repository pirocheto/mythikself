from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.config import get_settings
from app.core.products import Units, get_product_by_name, get_product_by_units
from app.db.models import UserORM
from app.schemas.lemonsqueezy import OrderResponse
from app.schemas.shared import MessageResponse

settings = get_settings()

router = APIRouter()


@router.get("/credits/{units}")
async def credit_user_account(
    current_user: Annotated[UserORM, Depends(get_current_user)],
    units: Annotated[Units, Depends()],
) -> RedirectResponse:
    """Redirect user to LemonSqueeze payment provider to credit their account."""

    product = get_product_by_units(units)

    if not product["url"]:
        return RedirectResponse(
            url=product["url"],
            status_code=400,
            headers={"X-Error": "Invalid units specified"},
        )

    return RedirectResponse(url=product["url"])


@router.post("/lemonsqueeze/callback", response_model=MessageResponse)
async def lemonsqueezy_callback(
    data: Annotated[OrderResponse, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Handle callback from LemonSqueeze payment provider."""

    user_email = data.data.attributes.user_email
    status = data.data.attributes.status
    product_name = data.data.attributes.first_order_item.product_name

    product = get_product_by_name(product_name)

    if not user_email:
        return {
            "message": "Invalid callback data",
            "error": "User email not found in callback data",
        }

    if status != "paid":
        return {
            "message": "Payment not successful",
            "error": f"Payment status is {status}, expected 'paid'",
        }

    async with session.begin():
        statement = select(UserORM).where(UserORM.email == user_email)
        result = await session.execute(statement)
        user_orm = result.scalars().one_or_none()

        if not user_orm:
            return {
                "message": "User not found",
                "error": f"No user found with email: {user_email}",
            }

        user_orm.credits += product["units"]

    return {"message": "Payment processed successfully"}
