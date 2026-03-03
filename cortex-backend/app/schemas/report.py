from pydantic import BaseModel
from typing import List


class CountItem(BaseModel):
    key: str
    count: int


class OverviewReport(BaseModel):
    total_projects: int
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    status_distribution: List[CountItem]
    priority_distribution: List[CountItem]
