from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from src.api.flags_router import flags_router
from src.clients.mongo_db_client import MongoDBAsyncClient


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    mongo_client = MongoDBAsyncClient()
    await mongo_client.connect()
    app.state.mongo_client = mongo_client

    yield

    # Shutdown: close MongoDB
    await mongo_client.close()


app = FastAPI(
    title="Feature Flag API",
    version="1.0.0",
    description="API for managing feature flags",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="src/api/templates")
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")
app.include_router(flags_router, tags=["Flags"])


@app.get("/", response_class=HTMLResponse, tags=["Home"], description="Home page")
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("home.html", {"request": request})
