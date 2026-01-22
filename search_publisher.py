# search_publisher.py
import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Publisher, Book, Shop, Stock, Sale

# === НАСТРОЙКИ ПОДКЛЮЧЕНИЯ ===
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'makinTosh1122')  # ← Замени на свой пароль, если нужно
DB_NAME = os.getenv('DB_NAME', 'bookstore')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

DSN = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)


def find_purchases_by_publisher(publisher_input):
    """
    Выводит покупки книг заданного издателя.
    :param publisher_input: Имя издателя (строка) или его идентификатор (число)
    """
    with Session() as session:
        # Определяем, число это или строка
        if publisher_input.isdigit():
            publisher_id = int(publisher_input)
            publisher = session.query(Publisher).filter(Publisher.id == publisher_id).one_or_none()
        else:
            publisher = session.query(Publisher).filter(Publisher.name == publisher_input).one_or_none()

        if not publisher:
            print(f"Издатель '{publisher_input}' не найден.")
            return

        # Выполняем JOIN-запрос
        results = (
            session.query(Book.title, Shop.name, Sale.price, Sale.date_sale)
            .join(Stock, Stock.id_book == Book.id)
            .join(Sale, Sale.id_stock == Stock.id)
            .join(Shop, Stock.id_shop == Shop.id)
            .filter(Book.id_publisher == publisher.id)
            .order_by(Sale.date_sale)  # без .desc() — как в эталоне
            .all()
        )

        if not results:
            print(f"Нет продаж для издателя '{publisher.name}'.")
            return

        for title, shop_name, price, date_sale in results:
            print(f"{title} | {shop_name} | {price} | {date_sale.strftime('%d-%m-%Y')}")


if __name__ == "__main__":
    # Создаём таблицы (если ещё не созданы)
    Base.metadata.create_all(engine)

    # Запрашиваем у пользователя
    publisher_input = input("Введите имя или ID издателя: ").strip()
    find_purchases_by_publisher(publisher_input)
