from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
from datetime import datetime

app = FastAPI()

DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    priority: int = Field(default=1, ge=1, le=5)

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: int
    completed: bool
    priority: int = Field(default=1,ge=1, le=5)

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority : Optional[int] = Field(default=None, ge=1, le=5)

SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/tasks")
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task(title=task.title, description=task.description, priority=task.priority)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@app.get("/tasks")
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    completed: bool = None,
    session: Session = Depends(get_session)
):
    query = select(Task)
    
    if completed is not None:
        query = query.where(Task.completed == completed)
    
    tasks = session.exec(query.offset(skip).limit(limit)).all()
    return tasks

@app.get("/tasks/{task_id}")
def read_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(404, "Task not found")
    
    if task_update.title:
        db_task.title = task_update.title
    if task_update.description is not None:
        db_task.description = task_update.description
    if task_update.completed is not None:
        db_task.completed = task_update.completed
    if task_update.priority:
        db_task.priority = task_update.priority

    session.commit()
    return {
        "message": "Task updated successfully",
        "task": db_task
    }

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    
    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}

@app.get("/stats")
def get_stats(session: Session = Depends(get_session)):
    total_tasks = session.exec(select(Task)).all()
    completed_tasks = session.exec(select(Task).where(Task.completed == True)).all()
    
    return {
        "total_tasks": len(total_tasks),
        "completed_tasks": len(completed_tasks),
        "pending_tasks": len(total_tasks) - len(completed_tasks),
        "completion_rate": len(completed_tasks) / len(total_tasks) if total_tasks else 0
    }