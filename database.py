from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import FastAPI, HTTPException

app = FastAPI()


class Student(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    group: str
    average_score: float


class Teacher(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    subject: str
    experience: float = Field(ge=0)


engine = create_engine("sqlite:///students.db")

SQLModel.metadata.create_all(engine)

@app.get("/students")
def get_students():
    with Session(engine) as session:
        return session.exec(select(Student)).all()
    
@app.post("/students")
def add_student(student : Student):
    with Session(engine) as session:
        session.add(student)
        session.commit()
        session.refresh(student)
        return {"message": f"студент {student.name} добавлен"}
    
@app.get("/students/{student_id}")
def get_student(studend_id :int):
    with Session(engine) as session:
        student = session.get(Student, studend_id)
        if not student:
            raise HTTPException(status_code=404, detail="студент не найден")
        return student

@app.put("/students/{student_id}")
def update_student(student_id : int, update : Student):
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="студент не найден")
        student.name = update.name
        student.group = update.group
        student.average_score = update.average_score
        session.add(student)
        session.commit()
        session.refresh(student)
        return {"message": "данные студента обновлены"}
    
@app.delete("/students/{student_id}")
def delete_student(student_id : int):
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="студент не найден")
        session.delete(student)
        session.commit()
        return {"message": "студент удалён"}
    
@app.get("/teachers")
def get_teachers():
    with Session(engine) as session:
        return session.exec(select(Session)).all()
    
@app.post("/teacher")
def add_teacher(teacher : Teacher):
    with Session(engine) as session:
        session.add(teacher)
        session.commit()
        session.refresh(teacher)
        return {"message": f"учитель {teacher.name} добавлен"}
    
@app.get("/teacher/{teacher_id}")
def get_teacher(teacher_id : int):
    with Session(engine) as session:
        teacher = session.get(Teacher, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="учитель не найден")
        return teacher
    
@app.put("/teacher/{teacher_id}")
def update_teacher(teacher_id : int, update : Teacher):
    with Session(engine) as session:
        teacher = session.get(Teacher, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="студент не найден")
        session.name = update.name
        session.subject = update.subject
        session.experience = update.experience
        session.add(teacher)
        session.commit()
        session.refresh(teacher)
        return {"message": "данные учителя обновлены"}
    
@app.delete("/teacher/{teacher_id}")
def delete_teacher(teacher_id : int):
    with Session(engine) as session:
        teacher = session.get(Teacher, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="учитель не найден")
        session.delete(teacher)
        session.commit()
        return {"message": "учитель удалён"}