import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers.auth       import router as auth_router
from .routers.table      import router as table_router
from .routers.menu       import router as menu_router
from .routers.order      import router as order_router
from .routers.payment    import router as payment_router
from .routers.admin      import router as admin_router
from .routers.admin_menu import router as admin_menu_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="QR Ordering API")

# CORS
origins = os.getenv("CORS_ORIGINS", "*")
if origins != "*":
    origins = [o.strip() for o in origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth_router)
app.include_router(table_router)
app.include_router(menu_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(admin_router)
app.include_router(admin_menu_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT",8000)), reload=True)