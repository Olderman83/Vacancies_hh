"""Модуль с mock-базой данных для тестирования без PostgreSQL."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class MockDBManager:
    """
    Mock-класс для имитации работы с базой данных.
    Хранит данные в памяти вместо реальной БД.
    """

    def __init__(self):
        """Инициализация mock БД."""
        self.employers = {}  # Словарь для хранения работодателей
        self.vacancies = {}  # Словарь для хранения вакансий
        self.initialized = False

    def connect(self) -> None:
        """Имитация подключения к БД."""
        print("[MOCK] Подключение к базе данных (in-memory)")
        self.initialized = True

    def ensure_connection(self) -> None:
        """Проверка соединения."""
        if not self.initialized:
            self.connect()

    def create_database(self) -> None:
        """Имитация создания базы данных."""
        print("[MOCK] База данных создана (in-memory)")

    def create_tables(self) -> None:
        """Имитация создания таблиц."""
        self.employers.clear()
        self.vacancies.clear()
        print("[MOCK] Таблицы созданы")

    def clear_tables(self) -> None:
        """Очистка таблиц."""
        self.employers.clear()
        self.vacancies.clear()
        print("[MOCK] Таблицы очищены")

    def insert_employer(self, employer_data: Dict[str, Any]) -> None:
        """
        Вставка данных о работодателе.

        Args:
            employer_data: Данные о работодателе
        """
        employer_id = employer_data.get('id')
        if employer_id:
            self.employers[employer_id] = employer_data.copy()
            print(f"[MOCK] Добавлен работодатель: {employer_data.get('name')}")

    def insert_vacancy(self, vacancy_data: Dict[str, Any], employer_id: str) -> None:
        """
        Вставка данных о вакансии.

        Args:
            vacancy_data: Данные о вакансии
            employer_id: ID работодателя
        """
        vacancy_id = vacancy_data.get('id')
        if vacancy_id:
            vacancy_copy = vacancy_data.copy()
            vacancy_copy['employer_id'] = employer_id
            self.vacancies[vacancy_id] = vacancy_copy

    def get_companies_and_vacancies_count(self) -> List[tuple]:
        """
        Получение списка компаний и количества вакансий.

        Returns:
            List[tuple]: Список (название_компании, количество_вакансий)
        """
        result = []
        for employer_id, employer in self.employers.items():
            count = sum(1 for v in self.vacancies.values() if v.get('employer_id') == employer_id)
            result.append((employer.get('name'), count))

        return sorted(result, key=lambda x: x[1], reverse=True)

    def get_all_vacancies(self) -> List[tuple]:
        """
        Получение всех вакансий с информацией о компании.

        Returns:
            List[tuple]: Список вакансий
        """
        result = []
        for vacancy in self.vacancies.values():
            employer = self.employers.get(vacancy.get('employer_id'), {})
            salary = vacancy.get('salary') or {}

            result.append((
                employer.get('name', 'Unknown'),
                vacancy.get('name'),
                salary.get('from'),
                salary.get('to'),
                salary.get('currency', 'RUR'),
                vacancy.get('alternate_url')
            ))

        return result

    def get_avg_salary(self) -> Optional[float]:
        """
        Получение средней зарплаты по вакансиям.

        Returns:
            Optional[float]: Средняя зарплата
        """
        salaries = []
        for vacancy in self.vacancies.values():
            salary = vacancy.get('salary') or {}
            salary_from = salary.get('from')
            salary_to = salary.get('to')

            if salary_from or salary_to:
                avg = (salary_from or 0 + salary_to or 0) / 2
                if salary_from and salary_to:
                    avg = (salary_from + salary_to) / 2
                elif salary_from:
                    avg = salary_from
                elif salary_to:
                    avg = salary_to

                salaries.append(avg)

        if salaries:
            return sum(salaries) / len(salaries)
        return None

    def get_vacancies_with_higher_salary(self) -> List[tuple]:
        """
        Получение вакансий с зарплатой выше средней.

        Returns:
            List[tuple]: Список вакансий с высокой зарплатой
        """
        avg_salary = self.get_avg_salary()
        if not avg_salary:
            return []

        result = []
        for vacancy in self.vacancies.values():
            employer = self.employers.get(vacancy.get('employer_id'), {})
            salary = vacancy.get('salary') or {}

            salary_from = salary.get('from')
            salary_to = salary.get('to')

            if salary_from or salary_to:
                avg = (salary_from or 0 + salary_to or 0) / 2
                if salary_from and salary_to:
                    avg = (salary_from + salary_to) / 2
                elif salary_from:
                    avg = salary_from
                elif salary_to:
                    avg = salary_to

                if avg > avg_salary:
                    result.append((
                        employer.get('name', 'Unknown'),
                        vacancy.get('name'),
                        salary.get('from'),
                        salary.get('to'),
                        salary.get('currency', 'RUR'),
                        vacancy.get('alternate_url')
                    ))

        return sorted(result, key=lambda x: (x[2] or 0 + x[3] or 0), reverse=True)

    def get_vacancies_with_keyword(self, keyword: str) -> List[tuple]:
        """
        Получение вакансий по ключевому слову.

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            List[tuple]: Список найденных вакансий
        """
        result = []
        keyword_lower = keyword.lower()

        for vacancy in self.vacancies.values():
            employer = self.employers.get(vacancy.get('employer_id'), {})
            vacancy_name = vacancy.get('name', '').lower()

            if keyword_lower in vacancy_name:
                salary = vacancy.get('salary') or {}
                result.append((
                    employer.get('name', 'Unknown'),
                    vacancy.get('name'),
                    salary.get('from'),
                    salary.get('to'),
                    salary.get('currency', 'RUR'),
                    vacancy.get('alternate_url')
                ))

        return result

    def close(self) -> None:
        """Закрытие соединения."""
        print("[MOCK] Соединение с БД закрыто")
        self.initialized = False


def create_database_if_not_exists() -> MockDBManager:
    """Создание mock БД."""
    db_manager = MockDBManager()
    db_manager.create_database()
    return db_manager
