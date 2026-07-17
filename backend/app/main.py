from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, tags, bookmarks, favorites, click_history
from app.models.init_db import init_db

app = FastAPI(title="LinkNest API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tags.router)
app.include_router(favorites.router)
app.include_router(click_history.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
