import psycopg2
from datetime import datetime

class LibraryDatabase:
    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        # Обновите параметры подключения согласно вашей настройке PostgreSQL
        def safe_str(param):
            if isinstance(param, bytes):
                return param.decode('utf-8')
            return str(param)

        self.conn = psycopg2.connect(
            dbname=safe_str(dbname),
            user=safe_str(user),
            password=safe_str(password),
            host=safe_str(host),
            port=safe_str(port)
        )
        self.cursor = self.conn.cursor()


    def add_user(self, email, password):
        self.cursor.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s) RETURNING id",
            (email, password)
        )
        user_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return user_id

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        return self.cursor.fetchone()

    def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        self.conn.commit()

    def add_book(self, book_data,title, author, pages, genre, year):
        self.cursor.execute(
            "INSERT INTO books (book, author, pages, genre, year,title) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (book_data, author, pages, genre, year,title)
        )
        book_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return book_id

    def edit_book(self, book_id, book_data=None,title=None, author=None, pages=None, genre=None, year=None):
        self.cursor.execute("SELECT book, title, author, pages, genre, year FROM books WHERE id=%s", (book_id,))
        current = self.cursor.fetchone()
        if not current:
            print("Книга с указанным ID не найдена.")
            return

        current_book, current_title, current_author, current_pages, current_genre, current_year = current

        new_book = book_data if book_data is not None else current_book
        new_title = title if title is not None else current_title
        new_author = author if author is not None else current_author
        new_pages = pages if pages is not None else current_pages
        new_genre = genre if genre is not None else current_genre
        new_year = year if year is not None else current_year

        self.cursor.execute("""
            UPDATE books
            SET book = %s, title = %s, author = %s, pages = %s, genre = %s, year = %s
            WHERE id = %s
        """, (new_book,new_title, new_author, new_pages, new_genre, new_year, book_id))
        self.conn.commit()

    def delete_book(self, book_id):
        self.cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        self.conn.commit()

    def get_book(self, book_id):
        self.cursor.execute("SELECT * FROM books WHERE id=%s", (book_id,))
        return self.cursor.fetchone()

    def get_book_by_title(self, title):
        self.cursor.execute("SELECT * FROM books WHERE LOWER(title) = %s", (title.lower(),))
        return self.cursor.fetchone()

    def get_all_books(self):
        self.cursor.execute("SELECT * FROM books")
        return self.cursor.fetchall()

    def get_books_by_filter(self, criterion, value):
        if criterion in ["title", "author", "genre"]:
            query = f"SELECT * FROM books WHERE LOWER({criterion}) = %s"
            self.cursor.execute(query, (value.lower(),))
            return self.cursor.fetchall()
        elif criterion == "year":
            try:
                year_val = int(value)
            except ValueError:
                return []  # Если значение не число, возвращаем пустой список
            self.cursor.execute("SELECT * FROM books WHERE year = %s", (year_val,))
            return self.cursor.fetchall()
        else:
            return []

    def add_favorite(self, user_id, book_id):
        self.cursor.execute("""
            INSERT INTO favorites (user_id, book_id) VALUES (%s, %s) RETURNING id
        """, (user_id, book_id))
        favorite_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return favorite_id

    def remove_favorite(self, user_id, book_id):
        self.cursor.execute("""
            DELETE FROM favorites WHERE user_id = %s AND book_id = %s
        """, (user_id, book_id))
        self.conn.commit()

    def get_user_favorites(self, user_id):
        self.cursor.execute("""
            SELECT b.* FROM books b
            JOIN favorites f ON b.id = f.book_id
            WHERE f.user_id = %s
        """, (user_id,))
        return self.cursor.fetchall()

    def add_history(self, user_id, book_id):
        view_date = datetime.now().isoformat()
        self.cursor.execute("""
            INSERT INTO history (user_id, book_id, view_date) VALUES (%s, %s, %s) RETURNING id
        """, (user_id, book_id, view_date))
        history_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return history_id

    def get_user_history(self, user_id):
        self.cursor.execute("""
            SELECT b.*, h.view_date FROM books b
            JOIN history h ON b.id = h.book_id
            WHERE h.user_id = %s
            ORDER BY h.view_date DESC
        """, (user_id,))
        return self.cursor.fetchall()

    def add_comment(self, user_id, book_id, comment_text):
        comment_date = datetime.now().isoformat()
        self.cursor.execute("""
            INSERT INTO comments (user_id, book_id, comment, comment_date) VALUES (%s, %s, %s, %s) RETURNING id
        """, (user_id, book_id, comment_text, comment_date))
        comment_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return comment_id

    def get_book_comments(self, book_id):
        self.cursor.execute("""
            SELECT u.email, c.comment, c.comment_date FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.book_id = %s
            ORDER BY c.comment_date DESC
        """, (book_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
