import socket
import json
import threading
import logging


from dataBaseLibrary import LibraryDatabase

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [SERVER] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Создаем единый экземпляр БД на сервер
db = LibraryDatabase(
    dbname="library",
    user="postgres",
    password="45682",
    host="localhost",
    port="5432"
)

def handle_client(client_socket, client_address):
    logger.info(f"Обработка клиента: {client_address}")
    try:
        buffer = b''
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            buffer += data
            if b'<END>' in buffer:
                request_data = buffer.split(b'<END>')[0]
                buffer = b''  # очищаем буфер
                request = json.loads(request_data.decode())
                response = process_request(request)
                client_socket.sendall(json.dumps(response).encode() + b'<END>')
    except Exception as e:
        logger.error(f"Ошибка при работе с клиентом {client_address}: {e}")
    finally:
        client_socket.close()
        logger.info(f"Соединение с клиентом {client_address} закрыто")

def process_request(request):
    action = request.get("action")

    if action == "get_books":
        books = db.get_all_books()
        formatted = [
            {
                "id": row[0],
                "title": row[6],
                "author": row[2],
                "pages": row[3],
                "genre": row[4],
                "year": row[5]
            }
            for row in books
        ]
        logger.info("get_books выполнено успешно")
        return {"status": "ok", "books": formatted}

    elif action == "register_user":
        email = request.get("email")
        password = request.get("password")
        db.cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if db.cursor.fetchone():
            return {"status": "error", "message": "Пользователь уже существует"}
        new_id = db.add_user(email, password)
        logger.info(f"Пользователь {email} зарегистрирован с id={new_id}")
        return {"status": "ok", "message": "Регистрация успешна", "user_id": new_id}

    elif action == "login_user":
        email = request.get("email")
        password = request.get("password")
        db.cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = db.cursor.fetchone()
        if not user:
            return {"status": "error", "message": "Пользователь не найден"}
        if user[2] != password:
            return {"status": "error", "message": "Неверный пароль"}
        return {"status": "ok", "message": "Авторизация успешна", "user_id": user[0]}

    elif action == "login_admin":
        if request.get("email") == "admin@library.com" and request.get("password") == "admin123":
            return {"status": "ok", "message": "Авторизация админа успешна", "account_type": "Администратор"}
        return {"status": "error", "message": "Неверные данные администратора"}

    elif action == "get_user_profile":
        user_id = request.get("user_id")
        if not user_id:
            return {"status": "error", "message": "Не указан user_id"}
        row = db.get_user(int(user_id))
        if not row:
            return {"status": "error", "message": "Пользователь не найден"}
        return {
            "status": "ok",
            "profile": {
                "email": row[1],
                "password": row[2]
            }
        }

    elif action == "edit_user":
        user_id = request.get("user_id")
        email = request.get("email", "").strip()
        password = request.get("password", "").strip()
        if not all([user_id, email, password]):
            return {"status": "error", "message": "Нужно user_id, email и password"}
        try:
            db.edit_user(int(user_id), email, password)
            return {"status": "ok", "message": "Профиль успешно сохранён"}
        except Exception as e:
            logger.error("edit_user failed: %s", e)
            return {"status": "error", "message": "Ошибка при сохранении профиля"}

    elif action == "find_book_by_title":
        title = request.get("title", "")
        row = db.get_book_by_title(title)
        if row:
            return {
                "status": "ok",
                "book": {
                    "id": row[0],
                "title": row[6],
                "author": row[2],
                "pages": row[3],
                "genre": row[4],
                "year": row[5]
                }
            }
        return {"status": "error", "message": "Книга не найдена"}

    elif action == "find_books_by_filter":
        criterion = request.get("criterion", "").lower()
        value = request.get("value", "")
        rows = db.get_books_by_filter(criterion, value)
        if rows:
            formatted = [
                {
                    "id": row[0],
                "title": row[6],
                "author": row[2],
                "pages": row[3],
                "genre": row[4],
                "year": row[5]
                }
                for row in rows
            ]
            logger.info(f"Команда 'find_books_by_filter' выполнена успешно для критерия '{criterion}' = '{value}'")
            return {"status": "ok", "books": formatted}
        else:
            logger.info(f"Команда 'find_books_by_filter': книги не найдены для критерия '{criterion}' = '{value}'")
            return {"status": "error", "message": "Книги не найдены по заданному критерию"}

    elif action == "get_users":
        db.cursor.execute("SELECT id, email FROM users")
        rows = db.cursor.fetchall()
        users = [{"id": row[0], "email": row[1]} for row in rows]
        return {"status": "ok", "users": users}

    elif action == "delete_book":
        book_id = request.get("book_id")
        try:
            # Преобразуем, если необходимо
            db.delete_book(int(book_id))
            logger.info(f"Команда 'delete_book' выполнена успешно для книги id {book_id}")
            return {"status": "ok", "message": "Книга удалена"}
        except Exception as e:
            logger.error(f"Ошибка при удалении книги id {book_id}: {e}")
            return {"status": "error", "message": "Ошибка удаления книги"}

    elif action == "delete_user":
        user_id = request.get("user_id")
        try:
            # Преобразуем, если необходимо
            db.delete_user(int(user_id))
            logger.info(f"Команда 'delete_user' выполнена успешно для пользователя id {user_id}")
            return {"status": "ok", "message": "Пользователь удален"}
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя id {user_id}: {e}")
            return {"status": "error", "message": "Ошибка удаления пользователя"}

    elif action == "edit_book":
        book_id = request.get("book_id")
        title = request.get("title")
        author = request.get("author")
        genre = request.get("genre")
        year = request.get("year")
        pages = request.get("pages")
        try:
            db.edit_book(int(book_id), title=title, author=author, pages=pages, genre=genre, year=year)
            logger.info(f"Команда 'edit_book' выполнена успешно для книги id {book_id}")
            return {"status": "ok", "message": "Изменения сохранены"}
        except Exception as e:
            logger.error(f"Ошибка редактирования книги id {book_id}: {e}")
            return {"status": "error", "message": "Ошибка сохранения изменений"}

    elif action == "add_book":
        book_data = request.get("book_data", "")  # можно оставить пустой строкой, если не используется
        title = request.get("title")
        author = request.get("author")
        pages = request.get("pages")
        genre = request.get("genre")
        year = request.get("year")
        if not all([title, author, pages, genre, year]):
            return {"status": "error", "message": "Не заполнены обязательные поля"}
        try:
            db.add_book(book_data, title, author, pages, genre, year)
            logger.info("Команда 'add_book' выполнена успешно")
            return {"status": "ok", "message": "Книга добавлена"}
        except Exception as e:
            logger.error(f"Ошибка при добавлении книги: {e}")
            return {"status": "error", "message": "Ошибка добавления книги"}

    elif action == "add_history":
        user_id = request.get("user_id")
        book_id = request.get("book_id")
        if not user_id or not book_id:
            return {"status": "error", "message": "Не указан user_id или book_id"}
        try:
            db.add_history(int(user_id), int(book_id))
            logger.info(f"История: пользователь {user_id} открыл книгу {book_id}")
            return {"status": "ok"}
        except Exception as e:
            logger.error(f"Ошибка добавления истории: {e}")
            return {"status": "error", "message": "Ошибка записи истории"}

    elif action == "get_book_details":
        book_id = request.get("book_id")
        user_id = request.get("user_id")
        if book_id:
            book = db.get_book(book_id)
            if book:
                if user_id:
                    db.add_history(int(user_id),int(book_id))
                keys = ["id", "book","author", "pages","genre","year", "title"]
                return {"status": "ok", "book": dict(zip(keys, book))}
            else:
                return {"status": "error", "message": "Книга не найдена"}
        return {"status": "error", "message": "Не указан ID книги"}

    elif action == "get_history":
        user_id = request.get("user_id")
        if not user_id:
            return {"status": "error", "message": "Не указан user_id"}
        rows = db.get_user_history(int(user_id))
        formatted = [
            {
                "id": row[0],
                "title": row[6],
                "author": row[2],
                "pages": row[3],
                "genre": row[4],
                "year": row[5],
                "view_date": row[7]
            }
            for row in rows
        ]
        return {"status": "ok", "history": formatted}

    elif action == "add_favorite":
        user_id = request.get("user_id")
        book_id = request.get("book_id")
        if not all([user_id, book_id]):
            return {"status": "error", "message": "Неполные данные для избранного"}
        try:
            db.add_favorite(int(user_id), int(book_id))
            return {"status": "ok", "message": "Книга добавлена в избранное"}
        except Exception as e:
            logger.error(f"add_favorite error: {e}")
            return {"status": "error", "message": "Не удалось добавить в избранное"}

    elif action == "remove_favorite":
        user_id = request.get("user_id")
        book_id = request.get("book_id")
        if not all([user_id, book_id]):
            return {"status": "error", "message": "Неполные данные для удаления"}
        try:
            db.remove_favorite(int(user_id), int(book_id))
            return {"status": "ok", "message": "Книга удалена из избранного"}
        except Exception as e:
            logger.error(f"remove_favorite error: {e}")
            return {"status": "error", "message": "Не удалось удалить из избранного"}

    elif action == "get_favorites":
        user_id = request.get("user_id")
        if not user_id:
            return {"status": "error", "message": "Не указан user_id"}
        rows = db.get_user_favorites(int(user_id))
        formatted = [
            {
                "id": row[0],
                "title": row[6],
                "author": row[2],
                "pages": row[3],
                "genre": row[4],
                "year": row[5]
            }
            for row in rows
        ]
        return {"status": "ok", "books": formatted}

    elif action == "add_comment":
        user_id   = request.get("user_id")
        book_id   = request.get("book_id")
        comment   = request.get("comment", "").strip()
        if not all([user_id, book_id, comment]):
            return {"status": "error", "message": "Нужно user_id, book_id и текст комментария"}
        try:
            db.add_comment(int(user_id), int(book_id), comment)
            logger.info(f"Комментарий добавлен: user={user_id}, book={book_id}")
            return {"status": "ok", "message": "Комментарий отправлен"}
        except Exception as e:
            logger.error(f"Ошибка add_comment: {e}")
            return {"status": "error", "message": "Не удалось добавить комментарий"}

    elif action == "get_comments":
        book_id = request.get("book_id")
        if not book_id:
            return {"status": "error", "message": "Не указан book_id"}
        try:
            rows = db.get_book_comments(int(book_id))
            # rows — список кортежей (email, comment, comment_date)
            formatted = [
                {"email": email, "comment": txt, "date": date}
                for email, txt, date in rows
            ]
            return {"status": "ok", "comments": formatted}
        except Exception as e:
            logger.error(f"Ошибка get_comments: {e}")
            return {"status": "error", "message": "Не удалось загрузить комментарии"}

    return {"status": "error", "message": "Неизвестное действие"}

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9000))
    server_socket.listen(5)
    print("Сервер запущен на порту 9000")
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            logger.info(f"Подключен клиент: {client_address}")
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        logger.info("Сервер остановлен пользователем")
    finally:
        db.close()
        server_socket.close()

if __name__ == '__main__':
    start_server()
