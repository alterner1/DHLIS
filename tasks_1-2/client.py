import xmlrpc.client
import os

# Адрес XML-RPC сервера
proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

# Настройки запроса
filters = {
   # "gender": "мужской",
     "lecture_presence": {"lecture": "Лекция 1", "is_present": True}
}
sort_field = "age"
sort_order = "desc"
per_page = 5


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def print_students(response):
    clear_terminal()
    data = response["data"]
    meta = response["meta"]
    total_pages = ((meta["total"] - 1) // meta["per_page"]) + 1

    print(f"\nСтраница: {meta['page']} из {total_pages} | Всего записей: {meta['total']}\n")

    if not data:
        print("Нет данных на этой странице.")
        return

    start_index = (meta['page'] - 1) * meta['per_page'] + 1
    for i, student in enumerate(data, start=start_index):
        print(f"  Студент {i}:")
        print(f"  ID: {student['id']}")
        print(f"  ФИО: {student['full_name']}")
        print(f"  Возраст: {student['age']}")
        print(f"  Пол: {student['gender']}")
        print("  Посещаемость:")
        for lecture, present in student["attendance"].items():
            print(f"    - {lecture}: {'Присутствовал' if present else 'Отсутствовал'}")
        print("  Оценки:")
        for subject, grade in student["grades"].items():
            print(f"    - {subject}: {grade}")
        print("-" * 40)


def main():
    page = 1
    while True:
        try:
            response = proxy.search_students(filters, sort_field, sort_order, page, per_page)
            print_students(response)
        except xmlrpc.client.Fault as e:
            print(f"Ошибка сервера: {e}")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            break

        cmd = input("\n[n] — следующая | [p] — предыдущая | [q] — выход: ").strip().lower()
        if cmd == "n":
            if page * per_page < response["meta"]["total"]:
                page += 1
            else:
                print("Это последняя страница.")
        elif cmd == "p":
            if page > 1:
                page -= 1
            else:
                print("Это первая страница.")
        elif cmd == "q":
            print("Выход.")
            break
        else:
            print("Неверная команда.")


if __name__ == "__main__":
    main()
