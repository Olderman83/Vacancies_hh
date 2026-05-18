# db_manager.py
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional


class DBManager:
    """Класс для работы с базой данных PostgreSQL"""

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.conn = None
        self._connect()

    def _connect(self):
        """Установка соединения с БД"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
        except psycopg2.Error as e:
            print(f"Ошибка подключения к БД: {e}")
            raise

    def _execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Optional[List[Dict]]:
        """Выполнение SQL запроса"""
        if not self.conn or self.conn.closed:
            self._connect()

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    result = cur.fetchall()
                    return [dict(row) for row in result]
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            return None

    def create_tables(self):
        """Создание таблиц"""
        create_employers = """
        CREATE TABLE IF NOT EXISTS employers (
            employer_id INT PRIMARY KEY,
            employer_name VARCHAR(255) NOT NULL,
            employer_url TEXT,
            alternate_url TEXT,
            vacancies_url TEXT,
            open_vacancies INT
        )
        """

        create_vacancies = """
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id VARCHAR(50) PRIMARY KEY,
            employer_id INT REFERENCES employers(employer_id) ON DELETE CASCADE,
            vacancy_name TEXT NOT NULL,
            salary_from INT,
            salary_to INT,
            salary_currency VARCHAR(10),
            url TEXT,
            requirement TEXT,
            responsibility TEXT,
            published_at TIMESTAMP
        )
        """

        self._execute_query(create_employers)
        self._execute_query(create_vacancies)
        print("Таблицы успешно созданы")

    def insert_employers(self, employers_data: List[Dict]) -> int:
        """Вставка данных о работодателях"""
        query = """
        INSERT INTO employers (employer_id, employer_name, employer_url, alternate_url, vacancies_url, open_vacancies)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (employer_id) DO UPDATE SET
            employer_name = EXCLUDED.employer_name,
            employer_url = EXCLUDED.employer_url,
            alternate_url = EXCLUDED.alternate_url,
            vacancies_url = EXCLUDED.vacancies_url,
            open_vacancies = EXCLUDED.open_vacancies
        """

        count = 0
        for employer in employers_data:
            params = (
                employer['employer_id'],
                employer['employer_name'],
                employer.get('employer_url'),
                employer.get('alternate_url'),
                employer.get('vacancies_url'),
                employer.get('open_vacancies')
            )
            self._execute_query(query, params)
            count += 1

        print(f"Добавлено/обновлено {count} работодателей")
        return count

    def insert_vacancies(self, vacancies_data: List[Dict]) -> int:
        """Вставка данных о вакансиях"""
        query = """
        INSERT INTO vacancies (vacancy_id, employer_id, vacancy_name, salary_from, salary_to, salary_currency, url, requirement, responsibility, published_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (vacancy_id) DO UPDATE SET
            vacancy_name = EXCLUDED.vacancy_name,
            salary_from = EXCLUDED.salary_from,
            salary_to = EXCLUDED.salary_to,
            salary_currency = EXCLUDED.salary_currency,
            url = EXCLUDED.url,
            requirement = EXCLUDED.requirement,
            responsibility = EXCLUDED.responsibility,
            published_at = EXCLUDED.published_at
        """

        count = 0
        for vacancy in vacancies_data:
            params = (
                vacancy['vacancy_id'],
                vacancy['employer_id'],
                vacancy['vacancy_name'],
                vacancy['salary_from'],
                vacancy['salary_to'],
                vacancy['salary_currency'],
                vacancy['url'],
                vacancy.get('requirement'),
                vacancy.get('responsibility'),
                vacancy.get('published_at')
            )
            self._execute_query(query, params)
            count += 1

        print(f"Добавлено/обновлено {count} вакансий")
        return count

    def get_companies_and_vacancies_count(self) -> List[Dict]:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        query = """
        SELECT e.employer_id, e.employer_name, COUNT(v.vacancy_id) as vacancies_count
        FROM employers e
        LEFT JOIN vacancies v ON e.employer_id = v.employer_id
        GROUP BY e.employer_id, e.employer_name
        ORDER BY vacancies_count DESC
        """
        return self._execute_query(query, fetch=True) or []

    def get_all_vacancies(self) -> List[Dict]:
        """Получает список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки"""
        query = """
        SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.employer_id
        ORDER BY e.employer_name, v.vacancy_name
        """
        return self._execute_query(query, fetch=True) or []

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям (усредняя from и to)"""
        query = """
        SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2) as avg_salary
        FROM vacancies
        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        """
        result = self._execute_query(query, fetch=True)
        if result and result[0].get('avg_salary'):
            return float(result[0]['avg_salary'])
        return 0.0

    def get_vacancies_with_higher_salary(self) -> List[Dict]:
        """Получает список всех вакансий, у которых зарплата выше средней"""
        avg_salary = self.get_avg_salary()

        query = """
        SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.employer_id
        WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > %s
        ORDER BY (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 DESC
        """
        return self._execute_query(query, (avg_salary,), fetch=True) or []

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict]:
        """Получает список всех вакансий, в названии которых содержится переданное слово"""
        query = """
        SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.employer_id
        WHERE LOWER(v.vacancy_name) LIKE LOWER(%s)
        ORDER BY e.employer_name, v.vacancy_name
        """
        return self._execute_query(query, (f'%{keyword}%',), fetch=True) or []

    def close(self):
        """Закрытие соединения с БД"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            print("Соединение с БД закрыто")
