import Service
import psycopg2

conn = psycopg2.connect(
    dbname="testDB",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

title = "Cool Book"
authors = ["Best Author"]  # Список авторов
total_quantity = 1

# Service.add_book(title, authors, total_quantity)

#Service.borrow_book(1, "Igor")

print(Service.get_all_books())

cur.close()
conn.close()
