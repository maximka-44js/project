import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging
from routes.resumes import router as resumes_router
from shared.database import Base, DatabaseManager

SERVICE_NAME = "resumes"
AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "1") == "1"

log = logging.getLogger(SERVICE_NAME)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


db_manager = DatabaseManager(SERVICE_NAME)

def get_db():
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

def create_app() -> FastAPI:
    app = FastAPI(title="Resume Service")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    if AUTO_CREATE_TABLES:
        try:
            db_manager.create_tables()
            log.info("Tables ensured")
        except Exception as e:
            log.error(f"Error creating tables: {e}")

    app.include_router(resumes_router, prefix="/api/v1/resumes")
    return app

app = create_app()