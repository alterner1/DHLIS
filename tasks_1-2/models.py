from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, DateTime, Text 
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

Base = declarative_base()

# class Student(Base):
#     __tablename__ = "students"
#     __table_args__ = {"schema": "public"} 
#     id = Column(Integer, primary_key=True)
#     info = Column(JSONB, nullable=False, server_default=text("'{}'"))
#     questions = relationship("StudentQuestion", back_populates="student")  

class Student(Base):  # обновленная схема для задания 2
    __tablename__ = "students"
    __table_args__ = {"schema": "public"} 
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)      # Обязательное поле
    age = Column(Integer, nullable=False)           # Обязательное поле
    gender = Column(String, nullable=False)         # Обязательное поле
    attendance = Column(JSONB, server_default=text("'{}'"))  # JSON-данные посещений
    grades = Column(JSONB, server_default=text("'{}'"))      # JSON-данные оценок
    info = Column(JSONB, server_default=text("'{}'"))        # Дополнительные данные
   # questions = relationship("StudentQuestion", back_populates="student")

class Teacher(Base):
    __tablename__ = "teachers"
    __table_args__ = {"schema": "public"} 
    id = Column(Integer, primary_key=True)
    info = Column(JSONB, nullable=False, server_default=text("'{}'"))

class Discipline(Base):
    __tablename__ = "disciplines"
    __table_args__ = {"schema": "public"} 
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    extra_data = Column(JSONB, nullable=True, server_default=text("'{}'"))
    video_records = relationship("VideoRecord", back_populates="discipline")
    presentations = relationship("Presentation", back_populates="discipline")

class Schedule(Base):
    __tablename__ = "schedule"
    __table_args__ = {"schema": "public"} 
    id = Column(Integer, primary_key=True)
    discipline_id = Column(Integer, ForeignKey("public.disciplines.id"))  
    teacher_id = Column(Integer, ForeignKey("public.teachers.id"))  
    type = Column(String(50), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    extra_data = Column(JSONB, nullable=True, server_default=text("'{}'"))

class VideoRecord(Base):
    __tablename__ = "video_records"
    __table_args__ = {"schema": "public"} 
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    discipline_id = Column(Integer, ForeignKey("public.disciplines.id"), nullable=False)  
    extra_data = Column(JSONB, server_default=text("'{}'"))  
    discipline = relationship("Discipline", back_populates="video_records")
    questions = relationship("StudentQuestion", back_populates="video_record")  

class Presentation(Base):
    __tablename__ = "presentations"
    __table_args__ = {"schema": "public"} 
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    discipline_id = Column(Integer, ForeignKey("public.disciplines.id"), nullable=False)  
    extra_data = Column(JSONB, server_default=text("'{}'"))  
    discipline = relationship("Discipline", back_populates="presentations")

class StudentQuestion(Base):
    __tablename__ = "student_questions"
    __table_args__ = {"schema": "public"} 
    id = Column(Integer, primary_key=True)
    # text = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    student_id = Column(Integer, ForeignKey("public.students.id"), nullable=False)  
    video_id = Column(Integer, ForeignKey("public.video_records.id"), nullable=False)  
    extra_data = Column(JSONB, server_default=text("'{}'")) 
   # student = relationship("Student", back_populates="questions")
    video_record = relationship("VideoRecord", back_populates="questions")