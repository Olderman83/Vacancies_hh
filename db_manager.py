"""Модуль для управления базой данных."""
import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any, Optional
from config import Config


class DBManager:
    """
    Класс для работы с базой данных PostgreSQL.

    Предоставляет методы для создания таблиц, заполнения данных
    и выполнения запросов к БД.
    """

    def __init__(self) -> None:
        """Инициализация DBManager с подключением к БД."""
        self.connection = None
        self.connect()

    def connect(self) -> None:
        """Установка соединения с базой данных."""
        try:
            params = Config.get_db_params()
            self.connection = psycopg2.connect(**params)
            self.connection.autocommit = False
        except Exception as e:
            print(f'Ошибка подключения к БД: {e}')
            raise

    def ensure_connection(self) -> None:
        """Проверка и восстановление соединения при необходимости."""
        if self.connection is None or self.connection.closed:
            self.connect()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[List[tuple]]:
        """
        Выполнение SQL-запроса.

        Args:
            query: SQL-запрос
            params: Параметры запроса

        Returns:
            Optional[List[tuple]]: Результат запроса для SELECT, None для других операций
        """
        self.ensure_connection()
        result = None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)

                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            print(f'Ошибка выполнения запроса: {e}')
            raise

        return result

    def create_database(self) -> None:
        """Создание базы данных."""
        db_name = Config.DB_NAME
        params = Config.get_db_params()
        params.pop('dbname')

        try:
            conn = psycopg2.connect(**params)
            conn.autocommit = True

            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [db_name])
                if not cursor.fetchone():
                    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                    print(f'База данных {db_name} успешно создана')
                else:
                    print(f'База данных {db_name} уже существует')

            conn.close()

        except Exception as e:
            print(f'Ошибка создания базы данных: {e}')
            raise

    def create_tables(self) -> None:
        """Создание таблиц employers и vacancies."""

        create_employers_table = """
        CREATE TABLE IF NOT EXISTS employers (
            employer_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            alternate_url VARCHAR(500),
            trusted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        create_vacancies_table = """
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id VARCHAR(50) PRIMARY KEY,
            employer_id VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            salary_from INTEGER,
            salary_to INTEGER,
            salary_currency VARCHAR(10),
            salary_gross BOOLEAN,
            area_name VARCHAR(100),
            experience_name VARCHAR(100),
            employment_name VARCHAR(100),
            schedule_name VARCHAR(100),
            requirement TEXT,
            responsibility TEXT,
            alternate_url VARCHAR(500),
            published_at TIMESTAMP,
            created_at TIMESTAMP,
            archived BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (employer_id) REFERENCES employers(employer_id) ON DELETE CASCADE
        )
        """

        # Создание индексов для оптимизации
        create_indexes = """
        CREATE INDEX IF NOT EXISTS idx_vacancies_employer_id ON vacancies(employer_id);
        CREATE INDEX IF NOT EXISTS idx_vacancies_salary_from ON vacancies(salary_from);
        CREATE INDEX IF NOT EXISTS idx_vacancies_salary_to ON vacancies(salary_to);
        CREATE INDEX IF NOT EXISTS idx_vacancies_name ON vacancies(name);
        CREATE INDEX IF NOT EXISTS idx_employers_name ON employers(name);
        """

        self.execute_query(create_employers_table)
        self.execute_query(create_vacancies_table)
        self.execute_query(create_indexes)
        print('Таблицы успешно созданы')

    def insert_employer(self, employer_data: Dict[str, Any]) -> None:
        """
        Вставка данных о работодателе.

        Args:
            employer_data: Словарь с данными о работодателе
        """
        query = """
        INSERT INTO employers (employer_id, name, alternate_url, trusted)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (employer_id) DO UPDATE SET
            name = EXCLUDED.name,
            alternate_url = EXCLUDED.alternate_url,
            trusted = EXCLUDED.trusted
        """

        params = (
            employer_data.get('id'),
            employer_data.get('name'),
            employer_data.get('alternate_url'),
            employer_data.get('trusted', False)
        )

        self.execute_query(query, params)

    def insert_vacancy(self, vacancy_data: Dict[str, Any], employer_id: str) -> None:
        """
        Вставка данных о вакансии.

        Args:
            vacancy_data: Словарь с данными о вакансии
            employer_id: ID работодателя
        """
        salary = vacancy_data.get('salary') or {}

        query = """
        INSERT INTO vacancies (
            vacancy_id, employer_id, name, salary_from, salary_to,
            salary_currency, salary_gross, area_name, experience_name,
            employment_name, schedule_name, requirement, responsibility,
            alternate_url, published_at, created_at, archived
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (vacancy_id) DO UPDATE SET
            name = EXCLUDED.name,
            salary_from = EXCLUDED.salary_from,
            salary_to = EXCLUDED.salary_to,
            archived = EXCLUDED.archived
        """

        params = (
            vacancy_data.get('id'),
            employer_id,
            vacancy_data.get('name'),
            salary.get('from'),
            salary.get('to'),
            salary.get('currency'),
            salary.get('gross'),
            vacancy_data.get('area', {}).get('name'),
            vacancy_data.get('experience', {}).get('name'),
            vacancy_data.get('employment', {}).get('name'),
            vacancy_data.get('schedule', {}).get('name'),
            vacancy_data.get('snippet', {}).get('requirement'),
            vacancy_data.get('snippet', {}).get('responsibility'),
            vacancy_data.get('alternate_url'),
            vacancy_data.get('published_at'),
            vacancy_data.get('created_at'),
            vacancy_data.get('archived', False)
        )

        self.execute_query(query, params)

    def get_companies_and_vacancies_count(self) -> List[tuple]:
        """
        Получение списка всех компаний и количества вакансий у каждой.

        Returns:
            List[tuple]: Список кортежей (название_компании, количество_вакансий)
        """
        query = """
        SELECT e.name, COUNT(v.vacancy_id) as vacancies_count
        FROM employers e
        LEFT JOIN vacancies v ON e.employer_id = v.employer_id
        GROUP BY e.name, e.employer_id
        ORDER BY vacancies_count DESC
        """

        return self.execute_query(query) or []

    def get_all_vacancies(self) -> List[tuple]:
        """
        Получение списка всех вакансий с информацией о компании.

        Returns:
            List[tuple]: Список кортежей (название_компании, название_вакансии, зарплата_от, зарплата_до, ссылка)
        """
        query = """
        SELECT 
            e.name as company_name,
            v.name as vacancy_name,
            v.salary_from,
            v.salary_to,
            v.salary_currency,
            v.alternate_url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.employer_id
        ORDER BY e.name, v.name
        """

        return self.execute_query(query) or []

    def get_avg_salary(self) -> Optional[float]:
        """
        Получение средней зарплаты по вакансиям.
        Использует среднее между salary_from и salary_to.

        Returns:
            Optional[float]: Средняя зарплата или None
        """
        query = """
        SELECT AVG((COALESCE(salary_from, salary_to, 0) + COALESCE(salary_to, salary_from, 0)) / 2.0)
        FROM vacancies
        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        """

        result = self.execute_query(query)
        return result[0][0] if result and result[0][0] else None

    def get_vacancies_with_higher_salary(self) -> List[tuple]:
        """
        Получение списка вакансий с зарплатой выше средней.

        Returns:
            List[tuple]: Список вакансий с зарплатой выше средней
        """
        avg_salary = self.get_avg_salary()

        if not avg_salary:
            return []

        query = """
        SELECT 
            e.name as company_name,
            v.name as vacancy_name,
            v.salary_from,
            v.salary_to,
            v.salary_currency,
            v.alternate_url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.employer_id
        WHERE (COALESCE(v.salary_from, v.salary_to, 0) + COALESCE(v.salary_to, v.salary_from, 0)) / 2.0 > %s
        ORDER BY (COALESCE(v.salary_from, v.salary_to, 0) + COALESCE(v.salary_to, v.salary_from, 0)) / 2.0 DESC
        """

        return self.execute_query(query, (avg_salary,)) or []

    def get_vacancies_with_keyword(self, keyword: str) -> List[tuple]:
        """
        Получение списка вакансий, содержащих ключевое слово в названии.

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            List[tuple]: Список вакансий, содержащих ключевое слово
        """
        query = """
        SELECT 
            e.name as company_name,
            v.name as vacancy_name,
            v.salary_from,
            v.salary_to,
            v.salary_currency,
            v.alternate_url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.employer_id
        WHERE v.name ILIKE %s
        ORDER BY e.name, v.name
        """

        return self.execute_query(query, (f'%{keyword}%',)) or []

    def close(self) -> None:
        """Закрытие соединения с БД."""
        if self.connection:
            self.connection.close()
            print('Соединение с БД закрыто')


def create_database_if_not_exists() -> None:
    """Создание базы данных, если она не существует."""
    db_manager = None
    try:
        db_manager = DBManager()
        db_manager.create_database()
    finally:
        if db_manager:
            db_manager.close()
