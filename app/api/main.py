from fastapi.routing import APIRouter

from app.api.routes.auth_routes import router as auth_router
from app.api.routes.generation_routes import router as generation_router
from app.api.routes.payment_routes import router as payment_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(generation_router)
api_router.include_router(payment_router)
