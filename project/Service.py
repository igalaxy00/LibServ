import psycopg2
from psycopg2 import sql
import Service

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="testDB",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

cur = conn.cursor()
#def pass():


# Добавление книги с указанием авторов
def add_book(title, authors, total_quantity):
    cur.execute(
        "INSERT INTO Books (title, available_quantity, total_quantity) VALUES (%s, %s, %s) RETURNING book_id",
        (title, total_quantity, total_quantity))
    book_id = cur.fetchone()[0]
    for author in authors:
        cur.execute("SELECT author_id FROM Authors WHERE author_name = %s", (author,))
        author_id = cur.fetchone()
        if author_id is None:
            cur.execute("INSERT INTO Authors (author_name) VALUES (%s) RETURNING author_id", (author,))
            author_id = cur.fetchone()[0]
        else:
            author_id = author_id[0]
        cur.execute("INSERT INTO Book_Authors (book_id, author_id) VALUES (%s, %s)", (book_id, author_id))
    conn.commit()


# Получение всех книг
def get_all_books():
    cur.execute("SELECT * FROM Books")
    return cur.fetchall()


#  читатель берет книгу  из библиотеки
def borrow_book(book_id, borrower_name):
    # Проверяем доступность книги
    cur.execute("SELECT available_quantity FROM Books WHERE book_id = %s", (book_id,))
    available_quantity = cur.fetchone()[0]
    if available_quantity > 0:
        # Получаем ID читателя
        cur.execute("SELECT borrower_id FROM Borrowers WHERE borrower_name = %s", (borrower_name,))
        borrower_id = cur.fetchone()
        if borrower_id is None:
            # Если читатель не существует, создаем новую запись
            cur.execute("INSERT INTO Borrowers (borrower_name) VALUES (%s) RETURNING borrower_id", (borrower_name,))
            borrower_id = cur.fetchone()[0]
        else:
            borrower_id = borrower_id[0]

        # Выдаем книгу читателю
        cur.execute("INSERT INTO Borrowed_Books (book_id, borrower_id, borrowed_date) VALUES (%s, %s, CURRENT_DATE)",
                    (book_id, borrower_id))
        cur.execute("UPDATE Books SET available_quantity = available_quantity - 1 WHERE book_id = %s", (book_id,))
        conn.commit()
        print("Книга выдана читателю.")
    else:
        print("Извините, данная книга временно недоступна.")


# Списание книги
def return_book(book_id):
    cur.execute("UPDATE Books SET available_quantity = available_quantity + 1 WHERE book_id = %s", (book_id,))
    cur.execute(
        "UPDATE Borrowed_Books SET returned_date = CURRENT_DATE WHERE book_id = %s AND returned_date IS NULL",
        (book_id,))
    conn.commit()
    print("Книга возвращена.")


# Функция для удаления книг из доступа и из базы данных
def remove_books(book_id, quantity):
    # Получаем доступное количество указанной книги
    cur.execute("SELECT available_quantity FROM Books WHERE book_id = %s", (book_id,))
    available_quantity = cur.fetchone()[0]

    # Проверяем, достаточно ли книг для удаления
    if available_quantity >= quantity:
        cur.execute("UPDATE Books SET available_quantity = available_quantity - %s WHERE book_id = %s",
                    (quantity, book_id))


        cur.execute("SELECT available_quantity FROM Books WHERE book_id = %s", (book_id,))
        updated_available_quantity = cur.fetchone()[0]
        if updated_available_quantity == 0:
            cur.execute("DELETE FROM Books WHERE book_id = %s", (book_id,))

        conn.commit()
        print(f"{quantity} книг(и) удалено из доступа и из базы данных.")
    else:
        print("Недостаточно книг для удаления.")