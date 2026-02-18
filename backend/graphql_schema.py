from __future__ import annotations

from typing import List, Optional

import strawberry
from fastapi import Request
from sqlalchemy.orm import Session, joinedload
from strawberry.types import Info

import database
import models


@strawberry.type
class TaskType:
    id: int
    title: str
    percent_complete: int
    bucket_id: int
    plan_id: int


@strawberry.type
class BucketType:
    id: int
    name: str
    plan_id: int
    tasks: List[TaskType]


@strawberry.type
class PlanType:
    id: int
    name: str
    buckets: List[BucketType]


def _to_task(t: models.Task) -> TaskType:
    return TaskType(
        id=t.id,
        title=t.title,
        percent_complete=t.percent_complete,
        bucket_id=t.bucket_id,
        plan_id=t.plan_id,
    )


def _to_bucket(b: models.Bucket) -> BucketType:
    tasks = getattr(b, "tasks", None) or []
    return BucketType(
        id=b.id,
        name=b.name,
        plan_id=b.plan_id,
        tasks=[_to_task(t) for t in tasks],
    )


def _to_plan(p: models.Plan) -> PlanType:
    buckets = getattr(p, "buckets", None) or []
    return PlanType(
        id=p.id,
        name=p.name,
        buckets=[_to_bucket(b) for b in buckets],
    )


@strawberry.type
class Query:
    @strawberry.field
    def plans(self, info: Info) -> List[PlanType]:
        db: Session = info.context["db"]
        plans = (
            db.query(models.Plan)
            .options(joinedload(models.Plan.buckets).joinedload(models.Bucket.tasks))
            .all()
        )
        return [_to_plan(p) for p in plans]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_plan(self, info: Info, name: str) -> PlanType:
        db: Session = info.context["db"]
        if db.query(models.Plan).filter(models.Plan.name == name).first():
            raise ValueError("Ya existe un plan con ese nombre.")
        db_plan = models.Plan(name=name)
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return PlanType(id=db_plan.id, name=db_plan.name, buckets=[])

    @strawberry.mutation
    def create_bucket(self, info: Info, name: str, plan_id: int) -> BucketType:
        db: Session = info.context["db"]
        if not db.query(models.Plan).filter(models.Plan.id == plan_id).first():
            raise ValueError("El plan asociado no existe.")
        db_bucket = models.Bucket(name=name, plan_id=plan_id)
        db.add(db_bucket)
        db.commit()
        db.refresh(db_bucket)
        return BucketType(
            id=db_bucket.id,
            name=db_bucket.name,
            plan_id=db_bucket.plan_id,
            tasks=[],
        )

    @strawberry.mutation
    def create_task(
        self,
        info: Info,
        title: str,
        bucket_id: int,
        plan_id: int,
        percent_complete: int = 0,
    ) -> TaskType:
        db: Session = info.context["db"]
        bucket = db.query(models.Bucket).filter(models.Bucket.id == bucket_id).first()
        if not bucket:
            raise ValueError("El bucket asociado no existe.")
        if not db.query(models.Plan).filter(models.Plan.id == plan_id).first():
            raise ValueError("El plan asociado no existe.")
        if bucket.plan_id != plan_id:
            raise ValueError("El bucket no pertenece al plan indicado.")

        db_task = models.Task(
            title=title,
            percent_complete=percent_complete,
            bucket_id=bucket_id,
            plan_id=plan_id,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return _to_task(db_task)

    @strawberry.mutation
    def update_task(
        self,
        info: Info,
        id: int,
        title: Optional[str] = None,
        percent_complete: Optional[int] = None,
        bucket_id: Optional[int] = None,
        plan_id: Optional[int] = None,
    ) -> TaskType:
        db: Session = info.context["db"]
        db_task = db.query(models.Task).filter(models.Task.id == id).first()
        if not db_task:
            raise ValueError("Task not found")

        new_bucket_id = bucket_id if bucket_id is not None else db_task.bucket_id
        new_plan_id = plan_id if plan_id is not None else db_task.plan_id

        bucket = db.query(models.Bucket).filter(models.Bucket.id == new_bucket_id).first()
        if not bucket:
            raise ValueError("El bucket asociado no existe.")
        if not db.query(models.Plan).filter(models.Plan.id == new_plan_id).first():
            raise ValueError("El plan asociado no existe.")
        if bucket.plan_id != new_plan_id:
            raise ValueError("El bucket no pertenece al plan indicado.")

        if title is not None:
            db_task.title = title
        if percent_complete is not None:
            db_task.percent_complete = percent_complete
        db_task.bucket_id = new_bucket_id
        db_task.plan_id = new_plan_id

        db.commit()
        db.refresh(db_task)
        return _to_task(db_task)

    @strawberry.mutation
    def delete_task(self, info: Info, id: int) -> bool:
        db: Session = info.context["db"]
        db_task = db.query(models.Task).filter(models.Task.id == id).first()
        if not db_task:
            raise ValueError("Task not found")
        db.delete(db_task)
        db.commit()
        return True


schema = strawberry.Schema(query=Query, mutation=Mutation)


async def get_context(request: Request):
    # Crear sesión de base de datos para GraphQL
    db = database.SessionLocal()
    try:
        yield {"request": request, "db": db}
    finally:
        db.close()

