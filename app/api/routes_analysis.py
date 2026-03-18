"""Analysis results retrieval endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..storage.file_store import list_sessions, load_results

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/results/{session_id}")
async def get_results(session_id: str):
    """Get analysis results for a specific session."""
    results = load_results(session_id)
    if results is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return results


@router.get("/sessions")
async def get_sessions():
    """List all available analysis sessions."""
    sessions = list_sessions()
    return {"sessions": sessions}
