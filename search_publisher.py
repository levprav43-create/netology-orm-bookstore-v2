# search_publisher.py
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Publisher, Book, Shop, Stock, Sale

# === НАСТРОЙКИ ПОДКЛЮЧЕНИЯ ===
DB_USER = "postgres"
DB_PASSWORD = "makinTosh1122"  
DB_NAME = "bookstore"
DB_HOST = "localhost"

DSN = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
engine = create_engine(DSN, connect_args={'client_encoding': 'UTF8'})
Session = sessionmaker(bind=engine)
session = Session()


def create_tables():
    Base.metadata.create_all(engine)


def find_sales_by_publisher(publisher_input):
    try:
        publisher_id = int(publisher_input)
        publisher = session.query(Publisher).filter(Publisher.id == publisher_id).first()
    except ValueError:
        publisher = session.query(Publisher).filter(Publisher.name == publisher_input).first()

    if not publisher:
        print("Издатель не найден.")
        return

    results = (
        session.query(Book.title, Shop.name, Sale.price, Sale.date_sale)
        .join(Stock, Sale.id_stock == Stock.id)
        .join(Book, Stock.id_book == Book.id)
        .join(Publisher, Book.id_publisher == Publisher.id)
        .join(Shop, Stock.id_shop == Shop.id)
        .filter(Publisher.id == publisher.id)
        .order_by(Sale.date_sale.desc())
        .all()
    )

    if not results:
        print(f"Нет продаж для издателя '{publisher.name}'.")
        return

    for title, shop_name, price, date_sale in results:
        print(f"{title} | {shop_name} | {price} | {date_sale.strftime('%d-%m-%Y')}")


if __name__ == "__main__":
    create_tables()

    # === ТЕСТОВЫЕ ДАННЫЕ (автоматически добавляются при запуске) ===
    pub = Publisher(name="Пушкин")
    book1 = Book(title="Евгений Онегин", publisher=pub)
    book2 = Book(title="Капитанская дочка", publisher=pub)
    shop1 = Shop(name="Буквоед")
    shop2 = Shop(name="Лабиринт")

    stock1 = Stock(book=book1, shop=shop1, count=10)
    stock2 = Stock(book=book2, shop=shop1, count=5)
    stock3 = Stock(book=book2, shop=shop2, count=3)

    sale1 = Sale(price=490, date_sale=datetime(2022, 11, 2), stock=stock1, count=1)
    sale2 = Sale(price=600, date_sale=datetime(2022, 11, 9), stock=stock2, count=2)
    sale3 = Sale(price=580, date_sale=datetime(2022, 11, 5), stock=stock3, count=1)

    session.add_all([pub, book1, book2, shop1, shop2, stock1, stock2, stock3, sale1, sale2, sale3])
    session.commit()

    # === ЗАПРОС ОТ ПОЛЬЗОВАТЕЛЯ ===
    find_sales_by_publisher("Пушкин")

    session.close()
