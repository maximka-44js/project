import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging
from routes.analysis import router as analysis_router
from shared.database import Base, DatabaseManager

SERVICE_NAME = "analysis"
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
    app = FastAPI(title="Analysis Service", version="1.0.0")
    
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
    
    app.include_router(analysis_router, prefix="/analysis")
    
    @app.get("/health")
    def health():
        return {"status": "ok", "service": SERVICE_NAME}
    
    return app

app = create_app()