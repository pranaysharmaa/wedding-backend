from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import get_client

# routers
from .routes import org as org_routes
from .routes import auth as auth_routes

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(org_routes.router, prefix="/org", tags=["org"])
app.include_router(auth_routes.router, prefix="/admin", tags=["admin"])

@app.on_event("startup")
def startup_event():
    client = get_client()
    try:
        client.admin.command("ping")
        print("MongoDB connected.")
    except Exception as e:
        print("Failed to connect to MongoDB:", e)

@app.on_event("shutdown")
def shutdown_event():
    client = get_client()
    client.close()
    print("MongoDB connection closed.")

@app.get("/")
def root():
    return {"status": "ok", "service": settings.APP_NAME}
