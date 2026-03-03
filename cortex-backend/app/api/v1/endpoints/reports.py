from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import Project, Task, User
from app.schemas.report import CountItem, OverviewReport

router = APIRouter()

STATUS_ORDER = ["TODO", "IN_PROGRESS", "REVIEW", "DONE"]
PRIORITY_ORDER = ["LOW", "MEDIUM", "HIGH"]


def _build_overview_report(total_projects: int, tasks: List[Task]) -> OverviewReport:
    status_counts = {status: 0 for status in STATUS_ORDER}
    priority_counts = {priority: 0 for priority in PRIORITY_ORDER}

    for task in tasks:
        normalized_status = str(task.status).strip().upper()
        if normalized_status in status_counts:
            status_counts[normalized_status] += 1
        else:
            status_counts[normalized_status] = status_counts.get(normalized_status, 0) + 1

        normalized_priority = str(task.priority).strip().upper()
        if normalized_priority in priority_counts:
            priority_counts[normalized_priority] += 1
        else:
            priority_counts[normalized_priority] = priority_counts.get(normalized_priority, 0) + 1

    total_tasks = len(tasks)
    completed_tasks = status_counts.get("DONE", 0)
    completion_rate = round((completed_tasks / total_tasks) * 100, 2) if total_tasks else 0.0

    status_distribution = [CountItem(key=key, count=value) for key, value in status_counts.items()]
    priority_distribution = [CountItem(key=key, count=value) for key, value in priority_counts.items()]

    return OverviewReport(
        total_projects=total_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        completion_rate=completion_rate,
        status_distribution=status_distribution,
        priority_distribution=priority_distribution,
    )


@router.get("/overview", response_model=OverviewReport)
async def get_overview_report(current_user: User = Depends(get_current_user)):
    projects = await Project.filter(
        members__id=current_user.id,
        deleted_at__isnull=True,
    ).all()
    total_projects = len(projects)

    if total_projects == 0:
        return _build_overview_report(total_projects=0, tasks=[])

    project_ids = [project.id for project in projects]
    tasks = await Task.filter(
        project_id__in=project_ids,
        deleted_at__isnull=True,
    ).all()

    return _build_overview_report(total_projects=total_projects, tasks=tasks)
