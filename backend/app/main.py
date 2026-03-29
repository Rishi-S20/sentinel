from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
import logging
from app.api import auth, agents

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Sentinel API starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("Sentinel API shutting down...")


app = FastAPI(
    title="Sentinel",
    description="Autonomous Market Intelligence Agent API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    schema["components"]["securitySchemes"] = {
        "StackAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "x-stack-access-token",
        }
    }
    schema["security"] = [{"StackAuth": []}]
    app.openapi_schema = schema
    return schema

app.openapi_schema = None
app.openapi = custom_openapi


# ---- Health Check ----
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "sentinel-api", "version": "0.1.0"}


# ---- Register Routers ----
# These will be uncommented as we build each module:
# from app.api import auth, agents, assets, briefings, alerts, billing
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
# app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
# app.include_router(briefings.router, prefix="/api/briefings", tags=["briefings"])
# app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
# app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
