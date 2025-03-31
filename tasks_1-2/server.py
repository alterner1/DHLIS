from xmlrpc.server import SimpleXMLRPCServer
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB 
from models import Student, Base  
import threading
import logging

# Подключение к БД
db_user = "postgres"
db_password = "Chi3Kago7"
db_host = "localhost"
db_port = "5432"
db_name = "LCMS_DB"

engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
Session = sessionmaker(bind=engine)
session = Session()

logging.basicConfig(level=logging.INFO)
# XML-RPC сервер

server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True  # Сервер остановится при завершении основного потока
server_thread.start()

print("Сервер запущен в фоновом режиме.")

def search_students(filters, sort_field="id", sort_order="asc", page=1, per_page=10):
    session = Session()
    logging.info(f"Запрос: {filters}")
    try:
        query = session.query(Student)
        
        # Фильтрация
        if "full_name" in filters:
            query = query.filter(
                func.to_tsvector('russian', Student.full_name).op("@@")(
                    func.websearch_to_tsquery('russian', filters["full_name"])
                )
            )
        if "age" in filters:
            query = query.filter(Student.age == filters["age"])
        if "gender" in filters:
            query = query.filter(Student.gender == filters["gender"])
        if "lecture_presence" in filters:
            query = query.filter(
                Student.attendance.has_key(filters["lecture_presence"]["lecture"])
            ).filter(
                Student.attendance[filters["lecture_presence"]["lecture"]].astext == str(filters["lecture_presence"]["is_present"])
            )
        
        # Сортировка
        if sort_order == "desc":
            query = query.order_by(getattr(Student, sort_field).desc())
        else:
            query = query.order_by(getattr(Student, sort_field).asc())
            
        # Пагинация
        total = query.count()
        students = query.offset((page-1)*per_page).limit(per_page).all()
        
        # Результат
        return {
            "data": [
                {
                    "id": s.id,
                    "full_name": s.full_name,
                    "age": s.age,
                    "gender": s.gender,
                    "attendance": s.attendance,
                    "grades": s.grades
                } for s in students
            ],
            "meta": {"page": page, "per_page": per_page, "total": total}
        }
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        raise
       
    finally:
        session.close()

server.register_function(search_students, "search_students")

if __name__ == "__main__":
    server.serve_forever()