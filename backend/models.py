from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Plan(Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    buckets = relationship('Bucket', back_populates='plan', cascade="all, delete-orphan")

class Bucket(Base):
    __tablename__ = 'buckets'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    plan = relationship('Plan', back_populates='buckets')
    tasks = relationship('Task', back_populates='bucket', cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    percent_complete = Column(Integer, default=0)
    bucket_id = Column(Integer, ForeignKey('buckets.id'), nullable=False)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    bucket = relationship('Bucket', back_populates='tasks')
