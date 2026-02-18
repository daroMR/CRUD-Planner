from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import time
import models
import schemas
import database
from strawberry.fastapi import GraphQLRouter
from graphql_schema import schema, get_context

app = FastAPI()

# Permitir CORS para pruebas locales
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Inicializar la base de datos después de que el servidor esté listo
    max_retries = 10
    for i in range(max_retries):
        try:
            database.init_db()
            break
        except Exception as e:
            if i == max_retries - 1:
                raise
            time.sleep(2)

# GraphQL (para demo y consumo desde el minisite)
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

# CRUD de Planes
@app.get("/plans", response_model=List[schemas.Plan])
def get_plans(db: Session = Depends(database.get_db)):
    return db.query(models.Plan).all()

@app.post("/plans", response_model=schemas.Plan)
def create_plan(plan: schemas.PlanCreate, db: Session = Depends(database.get_db)):
    # Validar que no exista un plan con el mismo nombre
    if db.query(models.Plan).filter(models.Plan.name == plan.name).first():
        raise HTTPException(status_code=400, detail="Ya existe un plan con ese nombre.")
    db_plan = models.Plan(name=plan.name)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

# CRUD de Buckets
@app.get("/buckets", response_model=List[schemas.Bucket])
def get_buckets(db: Session = Depends(database.get_db)):
    return db.query(models.Bucket).all()

@app.post("/buckets", response_model=schemas.Bucket)
def create_bucket(bucket: schemas.BucketCreate, db: Session = Depends(database.get_db)):
    # Validar que exista el plan asociado
    if not db.query(models.Plan).filter(models.Plan.id == bucket.plan_id).first():
        raise HTTPException(status_code=400, detail="El plan asociado no existe.")
    db_bucket = models.Bucket(name=bucket.name, plan_id=bucket.plan_id)
    db.add(db_bucket)
    db.commit()
    db.refresh(db_bucket)
    return db_bucket

# CRUD de Tareas
@app.get("/tasks", response_model=List[schemas.Task])
def get_tasks(db: Session = Depends(database.get_db)):
    return db.query(models.Task).all()

@app.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    # Validar que existan el bucket y el plan asociados
    if not db.query(models.Bucket).filter(models.Bucket.id == task.bucket_id).first():
        raise HTTPException(status_code=400, detail="El bucket asociado no existe.")
    if not db.query(models.Plan).filter(models.Plan.id == task.plan_id).first():
        raise HTTPException(status_code=400, detail="El plan asociado no existe.")
    db_task = models.Task(
        title=task.title,
        percent_complete=task.percent_complete,
        bucket_id=task.bucket_id,
        plan_id=task.plan_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Validar que existan el bucket y el plan asociados
    if not db.query(models.Bucket).filter(models.Bucket.id == task.bucket_id).first():
        raise HTTPException(status_code=400, detail="El bucket asociado no existe.")
    if not db.query(models.Plan).filter(models.Plan.id == task.plan_id).first():
        raise HTTPException(status_code=400, detail="El plan asociado no existe.")
    db_task.title = task.title
    db_task.percent_complete = task.percent_complete
    db_task.bucket_id = task.bucket_id
    db_task.plan_id = task.plan_id
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"ok": True}
