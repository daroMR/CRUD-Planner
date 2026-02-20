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
    id: strawberry.ID
    title: str
    percent_complete: int
    bucket_id: strawberry.ID
    plan_id: strawberry.ID


@strawberry.type
class BucketType:
    id: strawberry.ID
    name: str
    plan_id: strawberry.ID
    tasks: List[TaskType]


@strawberry.type
class PlanType:
    id: strawberry.ID
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
    async def plans(self, info: Info) -> List[PlanType]:
        from main import graph_call
        
        # 1. Intentar obtener de Microsoft Graph
        graph_data = await graph_call("GET", "/me/planner/plans")
        if graph_data and "value" in graph_data:
            result_plans = []
            for p in graph_data["value"]:
                plan_id = p["id"]
                # Obtener buckets para este plan
                buckets_data = await graph_call("GET", f"/planner/plans/{plan_id}/buckets")
                plan_buckets = []
                if buckets_data and "value" in buckets_data:
                    for b in buckets_data["value"]:
                        bucket_id = b["id"]
                        # Obtener tareas para este bucket
                        tasks_data = await graph_call("GET", f"/planner/buckets/{bucket_id}/tasks")
                        bucket_tasks = []
                        if tasks_data and "value" in tasks_data:
                            for t in tasks_data["value"]:
                                bucket_tasks.append(TaskType(
                                    id=strawberry.ID(t["id"]),
                                    title=t["title"],
                                    percent_complete=t.get("percentComplete", 0),
                                    bucket_id=strawberry.ID(bucket_id),
                                    plan_id=strawberry.ID(plan_id)
                                ))
                        
                        plan_buckets.append(BucketType(
                            id=strawberry.ID(bucket_id),
                            name=b["name"],
                            plan_id=strawberry.ID(plan_id),
                            tasks=bucket_tasks
                        ))
                
                result_plans.append(PlanType(
                    id=strawberry.ID(plan_id),
                    name=p["title"],
                    buckets=plan_buckets
                ))
            return result_plans

        # 2. Fallback a Base de Datos Local
        db: Session = info.context["db"]
        plans = (
            db.query(models.Plan)
            .options(joinedload(models.Plan.buckets).joinedload(models.Bucket.tasks))
            .all()
        )
        return [PlanType(
            id=strawberry.ID(str(p.id)),
            name=p.name,
            buckets=[BucketType(
                id=strawberry.ID(str(b.id)),
                name=b.name,
                plan_id=strawberry.ID(str(p.id)),
                tasks=[TaskType(
                    id=strawberry.ID(str(t.id)),
                    title=t.title,
                    percent_complete=t.percent_complete,
                    bucket_id=strawberry.ID(str(b.id)),
                    plan_id=strawberry.ID(str(p.id))
                ) for t in b.tasks]
            ) for b in p.buckets]
        ) for p in plans]


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
    async def update_plan(self, info: Info, id: strawberry.ID, name: str) -> PlanType:
        from main import graph_call
        # Graph attempt
        res = await graph_call("PATCH", f"/planner/plans/{id}", data={"title": name})
        if res:
            return PlanType(id=id, name=name, buckets=[])
        
        # Local fallback
        db: Session = info.context["db"]
        db_plan = db.query(models.Plan).filter(models.Plan.id == int(id) if str(id).isdigit() else 0).first()
        if not db_plan:
            raise ValueError("Plan not found")
        db_plan.name = name
        db.commit()
        db.refresh(db_plan)
        return PlanType(id=strawberry.ID(str(db_plan.id)), name=db_plan.name, buckets=[])

    @strawberry.mutation
    async def delete_plan(self, info: Info, id: strawberry.ID) -> bool:
        db: Session = info.context["db"]
        if str(id).isdigit():
            db_plan = db.query(models.Plan).filter(models.Plan.id == int(id)).first()
            if db_plan:
                db.delete(db_plan)
                db.commit()
                return True
        raise ValueError("Microsoft Graph no permite eliminar planes directamente. Se debe eliminar el Grupo de O365 asociado.")

    @strawberry.mutation
    async def update_bucket(self, info: Info, id: strawberry.ID, name: str) -> BucketType:
        from main import graph_call
        # Graph attempt
        res = await graph_call("PATCH", f"/planner/buckets/{id}", data={"name": name})
        if res:
            return BucketType(id=id, name=name, plan_id=strawberry.ID(""), tasks=[])
            
        # Local fallback
        db: Session = info.context["db"]
        db_bucket = db.query(models.Bucket).filter(models.Bucket.id == int(id) if str(id).isdigit() else 0).first()
        if not db_bucket:
            raise ValueError("Bucket not found")
        db_bucket.name = name
        db.commit()
        db.refresh(db_bucket)
        return BucketType(id=strawberry.ID(str(db_bucket.id)), name=db_bucket.name, plan_id=strawberry.ID(str(db_bucket.plan_id)), tasks=[])

    @strawberry.mutation
    async def delete_bucket(self, info: Info, id: strawberry.ID) -> bool:
        from main import graph_call
        res = await graph_call("DELETE", f"/planner/buckets/{id}")
        if res is not None:
            return True
            
        db: Session = info.context["db"]
        if str(id).isdigit():
            db_bucket = db.query(models.Bucket).filter(models.Bucket.id == int(id)).first()
            if db_bucket:
                db.delete(db_bucket)
                db.commit()
                return True
        return False

    @strawberry.mutation
    async def delete_task(self, info: Info, id: strawberry.ID) -> bool:
        from main import graph_call

        # Intentar DELETE en Graph si el ID es un UUID (no numérico)
        if not str(id).isdigit():
            res = await graph_call("DELETE", f"/planner/tasks/{id}")
            if res is not None:
                return True

        # Fallback: buscar en DB local por ID entero
        db: Session = info.context["db"]
        if str(id).isdigit():
            db_task = db.query(models.Task).filter(models.Task.id == int(id)).first()
            if db_task:
                db.delete(db_task)
                db.commit()
                return True

        raise ValueError(f"Tarea {id} no encontrada ni en Graph ni en la base de datos local.")


schema = strawberry.Schema(query=Query, mutation=Mutation)


async def get_context(request: Request):
    # Crear sesión de base de datos para GraphQL
    db = database.SessionLocal()
    try:
        yield {"request": request, "db": db}
    finally:
        db.close()

