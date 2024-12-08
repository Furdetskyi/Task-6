import time
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

# Конфігурація БД
DATABASE_URL = "postgresql+pg8000://root:Valikf2005@34.79.21.6:5432/test"
engine = create_engine(DATABASE_URL)

# Створення таблиці
metadata = MetaData()
test_table = Table(
    "test_table", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("value", String)
)

# Перевірка підключення до БД
with engine.connect() as connection:
    print("Підключення до бази даних встановлено.")
    metadata.create_all(engine)  # Створення таблиці, якщо вона не існує


def measure_query_time(query_func, *args, **kwargs):
    """Вимірювання часу виконання запиту."""
    try:
        start_time = time.time()
        query_func(*args, **kwargs)
        return time.time() - start_time
    except Exception as e:
        print(f"Помилка при виконанні запиту: {e}")
        return None


def insert_data(connection, count):
    """Вставка даних."""
    print(f"Вставка {count} записів...")
    data = [{"name": f"name_{i}", "value": f"value_{i}"} for i in range(count)]
    connection.execute(test_table.insert(), data)
    print(f"Вставлено {count} записів.")


def select_data(connection):
    """Вибірка всіх даних."""
    print("Вибірка даних...")
    result = connection.execute(test_table.select()).fetchall()
    print(f"Вибрано {len(result)} записів.")
    return result


def update_data(connection):
    """Оновлення всіх записів."""
    print("Оновлення даних...")
    connection.execute(test_table.update().values(value="updated_value"))
    print("Оновлено записи.")


def delete_data(connection):
    """Видалення всіх записів."""
    print("Видалення даних...")
    connection.execute(test_table.delete())
    print("Дані видалено.")


def main():
    results = []
    row_counts = [1000, 10000, 100000, 1000000]

    with engine.connect() as connection:
        for count in row_counts:
            print(f"Обробка {count} записів...")

            # Вставка
            insert_time = measure_query_time(insert_data, connection, count)
            print(f"Час вставки для {count} записів: {insert_time:.4f} секунд")

            # Вибірка
            select_time = measure_query_time(select_data, connection)
            print(f"Час вибірки для {count} записів: {select_time:.4f} секунд")

            # Оновлення
            update_time = measure_query_time(update_data, connection)
            print(f"Час оновлення для {count} записів: {update_time:.4f} секунд")

            # Видалення
            delete_time = measure_query_time(delete_data, connection)
            print(f"Час видалення для {count} записів: {delete_time:.4f} секунд")

            results.append({
                "rows": count,
                "insert_time": insert_time,
                "select_time": select_time,
                "update_time": update_time,
                "delete_time": delete_time,
            })

            print(f"Завершено для {count} записів.\n" + "-" * 40)

    # Виведення результатів
    print("\nРезультати загального тестування:")
    for result in results:
        print(f"Кількість записів: {result['rows']}")
        print(f"Час вставки: {result['insert_time']:.4f} секунд")
        print(f"Час вибірки: {result['select_time']:.4f} секунд")
        print(f"Час оновлення: {result['update_time']:.4f} секунд")
        print(f"Час видалення: {result['delete_time']:.4f} секунд")
        print("-" * 40)


if __name__ == "__main__":
    main()