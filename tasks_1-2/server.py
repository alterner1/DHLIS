from xmlrpc.server import SimpleXMLRPCServer
from sqlalchemy import create_engine, func, text, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB 
from models import Student, Base  
from dotenv import load_dotenv
import os
import threading
import logging


# Загрузка переменных окружения
load_dotenv()

# Получение значений из .env файла
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

# Подключение к БД
engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
Session = sessionmaker(bind=engine)
session = Session()

# Логи в терминале (DEBUG, INFO, WARNING, ERROR)
#logging.basicConfig(level=logging.INFO) x
# XML-RPC сервер
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True  # Сервер остановится при завершении основного потока
server_thread.start()

print("Сервер запущен в фоновом режиме на порту 8000.")

def search_students(filters, sort_field="id", sort_order="asc", page=1, per_page=10):
    # Логика метода - для документирования
    """
    Поиск студентов по фильтру.
    Параметры:
    - filter: dict (например, {"gender": "мужской"}),
    - sort_field: str (поле сортировки),
    - sort_order: str ("asc" или "desc"),
    - page: int (номер страницы),
    - per_page: int (количество на странице).
    """
    return []
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
                Student.attendance[filters["lecture_presence"]["lecture"]].astext.cast(Boolean) == 
                filters["lecture_presence"]["is_present"]
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
server.register_introspection_functions() # обязательно для документирования сервиса
if __name__ == "__main__":
    server.serve_forever()