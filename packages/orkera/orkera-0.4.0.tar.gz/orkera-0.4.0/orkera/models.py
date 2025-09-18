"""
Pydantic models for Taskflow SDK.
"""

from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


class Task(BaseModel):
    task_id: str
    task_name: str
    task_args: List[Any] = []
    task_kwargs: Dict[str, Any] = {}
    schedule_time: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    callback_url: Optional[str] = None
    result: Optional[Any] = None
    timestamp: Optional[str] = None 