from fastapi import APIRouter, HTTPException, Depends, status, Form, Query
import logging

from shared.database import DatabaseManager
from shared.auth import get_current_user_optional
from utils.compress_resume_agent import agent_summarize_resume


_db_manager = DatabaseManager("analysis")
log = logging.getLogger("analysis-routes")

def get_db():
    db = _db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(tags=["analysis"])

@router.post("/start")
async def start_analysis(
    resume_id: str = Form(...),
    db=Depends(get_db),
    user=Depends(get_current_user_optional),
):
    pass

@router.get("/{id}")
async def get_status_and_result(
    id: str,
    db=Depends(get_db),
    user=Depends(get_current_user_optional),
):
    pass 

@router.post("/webhook")
async def analysis_webhook(

):
    pass