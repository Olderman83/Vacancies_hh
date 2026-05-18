"""Модуль для работы с базой данных PostgreSQL."""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from config import DatabaseConfig


class DBManager:
    """Класс для управления базой данных и выполнения запросов."""

    def __init__(self, config: DatabaseConfig):
        """
        Инициализация DBManager.

        Args:
            config: Конфигурация подключения к БД
        """
        self.config = config
        self.connection = None

    def connect(self) -> None:
        """Установить соединение с базой данных."""
        try:
            self.connection = psycopg2.connect(self.config.get_connection_string())
            self.connection.autocommit = False
        except psycopg2.Error as e:
            print(f"Ошибка подключения к БД: {e}")
            raise

    def disconnect(self) -> None:
        """Закрыть соединение с базой данных."""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        """Контекстный менеджер для автоматического подключения."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрыть соединение при выходе из контекста."""
        if exc_type is not None:
            self.connection.rollback()
        self.disconnect()

    def create_database(self) -> None:
        """Создать базу данных если она не существует."""
        # Подключаемся к базе postgres для создания новой БД
        conn = psycopg2.connect(
            dbname="postgres",
            user=self.config.user,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Проверяем существование БД
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.config.dbname}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {self.config.dbname}")
            print(f"База данных {self.config.dbname} создана")

        cursor.close()
        conn.close()

    def create_tables(self) -> None:
        """Создать таблицы employers и vacancies."""
        with self.connection.cursor() as cursor:
            # Таблица employers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employers (
                    id SERIAL PRIMARY KEY,
                    employer_id VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    url VARCHAR(500),
                    trusted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица vacancies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    vacancy_id VARCHAR(50) UNIQUE NOT NULL,
                    employer_id VARCHAR(50) REFERENCES employers(employer_id),
                    name VARCHAR(500) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    avg_salary INTEGER,
                    currency VARCHAR(10),
                    url VARCHAR(500),
                    requirement TEXT,
                    responsibility TEXT,
                    city VARCHAR(100),
                    published_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Индексы для ускорения поиска
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vacancies_employer 
                ON vacancies(employer_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vacancies_name 
                ON vacancies(name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vacancies_avg_salary 
                ON vacancies(avg_salary)
            """)

            self.connection.commit()
            print("Таблицы успешно созданы")

    def insert_employers(self, employers: List[Dict[str, Any]]) -> None:
        """
        Вставить данные о работодателях.

        Args:
            employers: Список работодателей
        """
        with self.connection.cursor() as cursor:
            for employer in employers:
                cursor.execute("""
                    INSERT INTO employers (employer_id, name, url, trusted)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (employer_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        trusted = EXCLUDED.trusted
                """, (
                    employer["employer_id"],
                    employer["name"],
                    employer.get("url"),
                    employer.get("trusted", False)
                ))
            self.connection.commit()
            print(f"Добавлено {len(employers)} работодателей")

    def insert_vacancies(self, vacancies: List[Dict[str, Any]]) -> None:
        """
        Вставить данные о вакансиях.

        Args:
            vacancies: Список вакансий
        """
        with self.connection.cursor() as cursor:
            count = 0
            for vacancy in vacancies:
                try:
                    cursor.execute("""
                        INSERT INTO vacancies (
                            vacancy_id, employer_id, name, salary_from, salary_to,
                            avg_salary, currency, url, requirement, responsibility,
                            city, published_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (vacancy_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            salary_from = EXCLUDED.salary_from,
                            salary_to = EXCLUDED.salary_to,
                            avg_salary = EXCLUDED.avg_salary,
                            url = EXCLUDED.url
                    """, (
                        vacancy["vacancy_id"],
                        vacancy["employer_id"],
                        vacancy["name"],
                        vacancy["salary_from"],
                        vacancy["salary_to"],
                        vacancy["avg_salary"],
                        vacancy["currency"],
                        vacancy["url"],
                        vacancy.get("requirement"),
                        vacancy.get("responsibility"),
                        vacancy.get("city"),
                        vacancy.get("published_at")
                    ))
                    count += 1
                except psycopg2.Error as e:
                    print(f"Ошибка при вставке вакансии {vacancy.get('vacancy_id')}: {e}")
                    continue

            self.connection.commit()
            print(f"Добавлено/обновлено {count} вакансий")

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получить список всех компаний и количество вакансий у каждой.

        Returns:
            Список словарей с названием компании и количеством вакансий
        """
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    e.name AS company_name,
                    COUNT(v.id) AS vacancies_count
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.name, e.employer_id
                ORDER BY vacancies_count DESC
            """)
            return cursor.fetchall()

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получить список всех вакансий с указанием компании, зарплаты и ссылки.

        Returns:
            Список словарей с данными о вакансиях
        """
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    e.name AS company_name,
                    v.name AS vacancy_name,
                    v.salary_from,
                    v.salary_to,
                    v.currency,
                    v.url,
                    v.city
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                ORDER BY v.avg_salary DESC NULLS LAST
            """)
            return cursor.fetchall()

    def get_avg_salary(self) -> float:
        """
        Получить среднюю зарплату по вакансиям.

        Returns:
            Средняя зарплата (целое число)
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(AVG(avg_salary), 0) as avg_salary
                FROM vacancies
                WHERE avg_salary IS NOT NULL
            """)
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получить список вакансий с зарплатой выше средней.

        Returns:
            Список вакансий с зарплатой выше средней
        """
        avg_salary = self.get_avg_salary()

        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    e.name AS company_name,
                    v.name AS vacancy_name,
                    v.salary_from,
                    v.salary_to,
                    v.avg_salary,
                    v.currency,
                    v.url,
                    v.city
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE v.avg_salary > %s
                ORDER BY v.avg_salary DESC
            """, (avg_salary,))
            return cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получить список вакансий, содержащих ключевое слово в названии.

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            Список вакансий, содержащих ключевое слово
        """
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    e.name AS company_name,
                    v.name AS vacancy_name,
                    v.salary_from,
                    v.salary_to,
                    v.currency,
                    v.url,
                    v.city,
                    v.requirement
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE v.name ILIKE %s
                ORDER BY v.avg_salary DESC NULLS LAST
            """, (f"%{keyword}%",))
            return cursor.fetchall()
