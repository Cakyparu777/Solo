# app/main.py

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers.auth    import router as auth_router
from app.routers.table   import router as table_router
from app.routers.menu    import router as menu_router
from app.routers.order   import router as order_router
from app.routers.payment import router as payment_router
from app.routers.admin   import router as admin_router

# Create tables if they don't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="QR Ordering API")

#
# CORS
#
# You can lock this down to your dev-server’s origin
# or use ["*"] to allow everything while you debug.
#
# Common dev-server origins:
#   • Expo iOS/macOS/web   → http://localhost:19006 or http://127.0.0.1:19006
#   • Android emulator     → http://10.0.2.2:19006
#
origins = os.getenv("CORS_ORIGINS", "*")
if origins != "*":
    # if you supply a comma-separated list in .env, e.g.
    # CORS_ORIGINS=http://localhost:19006,http://10.0.2.2:19006
    origins = [o.strip() for o in origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # can be ["*"] or list of strings
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

#
# Routers
#
app.include_router(auth_router)    # /api/auth
app.include_router(table_router)   # /api/table
app.include_router(menu_router)    # /api/restaurants
app.include_router(order_router)   # /api/orders
app.include_router(payment_router) # /api/payments
app.include_router(admin_router)   # /api/admin

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )