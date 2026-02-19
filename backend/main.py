from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import time
import models
import schemas
import database
import auth
import httpx
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

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

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

# -----------------------------
# Autenticación (MS Graph)
# -----------------------------

@app.get("/auth/login")
def login_flow():
    try:
        flow = auth.init_device_flow()
        return flow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/complete")
async def complete_login(flow: dict):
    try:
        result = auth.complete_device_flow(flow)
        if "access_token" in result:
            # Forzar guardado inmediato
            auth.save_cache()
            print("DEBUG: login complete success - cache saved")
            return {"status": "success", "user": result.get("id_token_claims", {}).get("name", "Usuario")}
        else:
            print(f"DEBUG: login complete failure: {result.get('error')}")
            return {"status": "error", "detail": result.get("error", "Desconocido")}
    except Exception as e:
        print(f"DEBUG: login complete exception: {e}")
        return {"status": "error", "detail": str(e)}

@app.get("/auth/status")
def auth_status():
    token = auth.get_access_token()
    account_name = None
    if token:
        app = auth.get_msal_app()
        accounts = app.get_accounts()
        if accounts:
            account_name = accounts[0].get("username")
    return {"authenticated": token is not None, "user": account_name}

# GraphQL (para demo y consumo desde el minisite)
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

# -----------------------------
# Helper para Graph API
# -----------------------------
async def graph_call(method: str, endpoint: str, data: dict = None):
    token = auth.get_access_token()
    if not token:
        print(f"DEBUG: graph_call {endpoint} failed - No access token")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0{endpoint}"
    async with httpx.AsyncClient() as client:
        print(f"DEBUG: graph_call {method} {url}")
        res = await client.request(method, url, headers=headers, json=data)
        if res.status_code >= 400:
            print(f"Graph Error: {res.status_code} - {res.text}")
            return None
        return res.json() if res.status_code != 204 else {"ok": True}

# -----------------------------
# -----------------------------
# CRUD de Planes
# -----------------------------
@app.get("/plans", response_model=List[schemas.Plan])
async def get_plans(db: Session = Depends(database.get_db)):
    # Intentar obtener de Graph
    graph_data = await graph_call("GET", "/me/planner/plans")
    if graph_data and "value" in graph_data:
        return [{"id": p["id"], "name": p.get("title")} for p in graph_data["value"]]
    
    # Fallback a local
    return [{"id": str(p.id), "name": p.name} for p in db.query(models.Plan).all()]

@app.post("/plans", response_model=schemas.Plan)
async def create_plan(plan: schemas.PlanCreate, db: Session = Depends(database.get_db)):
    db_plan = models.Plan(name=plan.name)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return schemas.Plan(id=str(db_plan.id), name=db_plan.name)

@app.put("/plans/{plan_id}", response_model=schemas.Plan)
async def update_plan(plan_id: str, plan: schemas.PlanCreate, db: Session = Depends(database.get_db)):
    if plan_id.isdigit():
        db_plan = db.query(models.Plan).filter(models.Plan.id == int(plan_id)).first()
        if db_plan:
            db_plan.name = plan.name
            db.commit()
            db.refresh(db_plan)
            return schemas.Plan(id=str(db_plan.id), name=db_plan.name)
    
    # Intento en Graph (PATCH /planner/plans/{id})
    # Requiere eTag, por ahora fallback o error si no se maneja eTag
    res = await graph_call("PATCH", f"/planner/plans/{plan_id}", data={"title": plan.name})
    if res:
        return schemas.Plan(id=plan_id, name=plan.name)
    raise HTTPException(status_code=404, detail="Plan no encontrado")

@app.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str, db: Session = Depends(database.get_db)):
    if plan_id.isdigit():
        db_plan = db.query(models.Plan).filter(models.Plan.id == int(plan_id)).first()
        if db_plan:
            db.delete(db_plan)
            db.commit()
            return {"ok": True}
    
    # Planner no expone un endpoint de DELETE para planes directamente (se borra el grupo)
    # Mostramos error o mensaje informativo
    raise HTTPException(status_code=400, detail="Microsoft Graph no permite eliminar planes directamente. Se debe eliminar el Grupo de O365 asociado.")

# -----------------------------
# CRUD de Buckets
# -----------------------------
@app.get("/buckets", response_model=List[schemas.Bucket])
async def get_buckets(plan_id: str = None, db: Session = Depends(database.get_db)):
    all_buckets = []
    
    if plan_id:
        graph_data = await graph_call("GET", f"/planner/plans/{plan_id}/buckets")
        if graph_data and "value" in graph_data:
            all_buckets = [{"id": b["id"], "name": b["name"], "plan_id": plan_id} for b in graph_data["value"]]
    else:
        # Si no hay plan_id, intentar traer buckets de TODOS los planes del usuario
        plans_data = await graph_call("GET", "/me/planner/plans")
        if plans_data and "value" in plans_data:
            for p in plans_data["value"]:
                p_id = p["id"]
                b_data = await graph_call("GET", f"/planner/plans/{p_id}/buckets")
                if b_data and "value" in b_data:
                    all_buckets.extend([{"id": b["id"], "name": b["name"], "plan_id": p_id} for b in b_data["value"]])

    if all_buckets:
        return all_buckets
    
    # Fallback a local
    query = db.query(models.Bucket)
    if plan_id and plan_id.isdigit():
        query = query.filter(models.Bucket.plan_id == int(plan_id))
    return [{"id": str(b.id), "name": b.name, "plan_id": str(b.plan_id)} for b in query.all()]

@app.post("/buckets", response_model=schemas.Bucket)
async def create_bucket(bucket: schemas.BucketCreate, db: Session = Depends(database.get_db)):
    db_bucket = models.Bucket(name=bucket.name, plan_id=int(bucket.plan_id) if bucket.plan_id.isdigit() else 0)
    db.add(db_bucket)
    db.commit()
    db.refresh(db_bucket)
    return schemas.Bucket(id=str(db_bucket.id), name=db_bucket.name, plan_id=str(db_bucket.plan_id))

@app.put("/buckets/{bucket_id}", response_model=schemas.Bucket)
async def update_bucket(bucket_id: str, bucket: schemas.BucketCreate, db: Session = Depends(database.get_db)):
    if bucket_id.isdigit():
        db_bucket = db.query(models.Bucket).filter(models.Bucket.id == int(bucket_id)).first()
        if db_bucket:
            db_bucket.name = bucket.name
            db_bucket.plan_id = int(bucket.plan_id) if bucket.plan_id.isdigit() else db_bucket.plan_id
            db.commit()
            db.refresh(db_bucket)
            return schemas.Bucket(id=str(db_bucket.id), name=db_bucket.name, plan_id=str(db_bucket.plan_id))
    
    # Graph PATCH /planner/buckets/{id}
    res = await graph_call("PATCH", f"/planner/buckets/{bucket_id}", data={"name": bucket.name})
    if res:
        return schemas.Bucket(id=bucket_id, name=bucket.name, plan_id=bucket.plan_id)
    raise HTTPException(status_code=404, detail="Bucket no encontrado")

@app.delete("/buckets/{bucket_id}")
async def delete_bucket(bucket_id: str, db: Session = Depends(database.get_db)):
    if bucket_id.isdigit():
        db_bucket = db.query(models.Bucket).filter(models.Bucket.id == int(bucket_id)).first()
        if db_bucket:
            db.delete(db_bucket)
            db.commit()
            return {"ok": True}
    
    res = await graph_call("DELETE", f"/planner/buckets/{bucket_id}")
    if res is not None:
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Bucket no encontrado")

# -----------------------------
# CRUD de Tareas
# -----------------------------
@app.get("/tasks", response_model=List[schemas.Task])
async def get_tasks(bucket_id: str = None, plan_id: str = None, db: Session = Depends(database.get_db)):
    if bucket_id:
        graph_data = await graph_call("GET", f"/planner/buckets/{bucket_id}/tasks")
        if graph_data and "value" in graph_data:
            return [{
                "id": t["id"],
                "title": t["title"],
                "percent_complete": t.get("percentComplete", 0),
                "bucket_id": bucket_id,
                "plan_id": t.get("planId", "")
            } for t in graph_data["value"]]
    
    # Intentar obtener todas las tareas del usuario de Graph
    graph_all = await graph_call("GET", "/me/planner/tasks")
    if graph_all and "value" in graph_all:
         return [{
                "id": t["id"],
                "title": t["title"],
                "percent_complete": t.get("percentComplete", 0),
                "bucket_id": t.get("bucketId", ""),
                "plan_id": t.get("planId", "")
            } for t in graph_all["value"]]

    # Fallback a local
    query = db.query(models.Task)
    if bucket_id and bucket_id.isdigit():
        query = query.filter(models.Task.bucket_id == int(bucket_id))
    return [{
        "id": str(t.id),
        "title": t.title,
        "percent_complete": t.percent_complete,
        "bucket_id": str(t.bucket_id),
        "plan_id": str(t.plan_id)
    } for t in query.all()]

@app.post("/tasks", response_model=schemas.Task)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    db_task = models.Task(
        title=task.title,
        percent_complete=task.percent_complete,
        bucket_id=int(task.bucket_id) if task.bucket_id.isdigit() else 0,
        plan_id=int(task.plan_id) if task.plan_id.isdigit() else 0
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return schemas.Task(
        id=str(db_task.id),
        title=db_task.title,
        percent_complete=db_task.percent_complete,
        bucket_id=str(db_task.bucket_id),
        plan_id=str(db_task.plan_id)
    )

@app.put("/tasks/{task_id}", response_model=schemas.Task)
async def update_task(task_id: str, task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    # Primero intentar local
    if task_id.isdigit():
        db_task = db.query(models.Task).filter(models.Task.id == int(task_id)).first()
        if db_task:
            db_task.title = task.title
            db_task.percent_complete = task.percent_complete
            db_task.bucket_id = int(task.bucket_id) if task.bucket_id.isdigit() else db_task.bucket_id
            db_task.plan_id = int(task.plan_id) if task.plan_id.isdigit() else db_task.plan_id
            db.commit()
            db.refresh(db_task)
            return schemas.Task(
                id=str(db_task.id),
                title=db_task.title,
                percent_complete=db_task.percent_complete,
                bucket_id=str(db_task.bucket_id),
                plan_id=str(db_task.plan_id)
            )
    
    # Si no es local, intentar Graph
    # Implementar PATCH a Graph si es necesario
    raise HTTPException(status_code=404, detail="Tarea no encontrada localmente y edición en Graph no implementada.")

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(database.get_db)):
    if task_id.isdigit():
        db_task = db.query(models.Task).filter(models.Task.id == int(task_id)).first()
        if db_task:
            db.delete(db_task)
            db.commit()
            return {"ok": True}
    
    # Intentar DELETE en Graph si el ID coincide
    res = await graph_call("DELETE", f"/planner/tasks/{task_id}")
    if res is not None:
        return {"ok": True}
        
    raise HTTPException(status_code=404, detail="Task not found")
