from fastapi import APIRouter

# Import endpoints here
# from app.api.v1.endpoints import users, items

api_router = APIRouter()
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])

@api_router.get("/health")
def health_check():
    return {"status": "ok"}
