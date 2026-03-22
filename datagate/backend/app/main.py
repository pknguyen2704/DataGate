from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import profiling

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Cấu hình CORS (Cho phép Frontend gọi API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép tất cả các nguồn để tránh lỗi CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure routers
app.include_router(profiling.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to DataGate API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
