from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .deps import get_current_user
from .models import User

app = FastAPI(title="Signal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # the Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}
