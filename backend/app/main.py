from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .config import settings
from .db import Base, SessionLocal, engine
from .demo_seed import seed_demo_account
from .deps import get_current_user
from .detail import router as detail_router
from .feed import router as feed_router
from .models import User
from .scheduler import start_scheduler
from .search import router as search_router
from .watchlist import router as watchlist_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # hosted deploys start with an empty disk
    if settings.seed_demo_on_start:
        session = SessionLocal()
        try:
            seed_demo_account(session, "founder@signal.app", create_user=True)
        except Exception as e:
            print(f"[startup seed] skipped: {e}")
        finally:
            session.close()
    scheduler = start_scheduler()
    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(title="Signal API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # The deployed frontend, plus the Vite dev server on any localhost port.
    allow_origins=[settings.frontend_origin] if settings.frontend_origin else [],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(watchlist_router)
app.include_router(feed_router)
app.include_router(search_router)
app.include_router(detail_router)


@app.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}
