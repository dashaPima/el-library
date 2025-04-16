from dataBaseLibrary import LibraryDatabase

if __name__ == "__main__":
    # Передаём параметры подключения для PostgreSQL
    db = LibraryDatabase(
        dbname="library",
        user="postgres",
        password="45682",
        host="localhost",
        port="5432"
    )
    print("База данных успешно подключена.")
    db.close()
