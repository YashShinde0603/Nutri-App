# main entry if you prefer to run python -m app.main
from uvicorn import run
from app.api.routes import app
from app.config import settings

if __name__ == "__main__":
    run("app.api.routes:app", host=settings.HOST, port=settings.PORT, reload=True)
