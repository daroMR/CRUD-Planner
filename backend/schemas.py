from pydantic import BaseModel, ConfigDict
from typing import Optional

class PlanBase(BaseModel):
    name: str

class PlanCreate(PlanBase):
    pass

class Plan(PlanBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BucketBase(BaseModel):
    name: str
    plan_id: int

class BucketCreate(BucketBase):
    pass

class Bucket(BucketBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TaskBase(BaseModel):
    title: str
    percent_complete: Optional[int] = 0
    bucket_id: int
    plan_id: int

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
