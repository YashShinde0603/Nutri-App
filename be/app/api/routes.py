from fastapi import FastAPI
from app.api.users import router as users_router
from app.api.usda import router as usda_router
from app.api.pantry import router as pantry_router
from app.api.auth import router as auth_router
from app.db.session import init_db

app = FastAPI(title="Nutrition Backend")

# init DB (create tables)
init_db()

app.include_router(users_router)
app.include_router(usda_router)
app.include_router(pantry_router)
app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok"}
