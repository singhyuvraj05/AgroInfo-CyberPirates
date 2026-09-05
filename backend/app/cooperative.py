from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CooperativeInsight


def create_insight(
    db: Session,
    *,
    publisher_state: str,
    crop: str,
    insight_type: str,
    title: str,
    description: str,
    version: str,
    metric_label: str | None = None,
    metric_value: float | None = None,
) -> CooperativeInsight:
    insight = CooperativeInsight(
        publisher_state=publisher_state,
        crop=crop,
        insight_type=insight_type,
        title=title,
        description=description,
        version=version,
        metric_label=metric_label,
        metric_value=metric_value,
        status="published",
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


def list_insights(
    db: Session,
    *,
    state: str | None = None,
    crop: str | None = None,
    insight_type: str | None = None,
) -> list[CooperativeInsight]:
    statement = select(CooperativeInsight).order_by(CooperativeInsight.id)
    if state:
        statement = statement.where(CooperativeInsight.publisher_state == state)
    if crop:
        statement = statement.where(CooperativeInsight.crop == crop)
    if insight_type:
        statement = statement.where(CooperativeInsight.insight_type == insight_type)
    return list(db.scalars(statement).all())


def reuse_insight(
    db: Session,
    source: CooperativeInsight,
    *,
    target_state: str,
    adaptation_note: str,
) -> CooperativeInsight:
    adapted = CooperativeInsight(
        publisher_state=target_state,
        crop=source.crop,
        insight_type=source.insight_type,
        title=source.title,
        description=source.description,
        version=source.version,
        metric_label=source.metric_label,
        metric_value=source.metric_value,
        status="adapted",
        source_insight_id=source.id,
        adaptation_note=adaptation_note,
    )
    db.add(adapted)
    db.commit()
    db.refresh(adapted)
    return adapted
