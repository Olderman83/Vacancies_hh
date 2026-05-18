"""Модуль для работы с API hh.ru."""
import requests
from typing import Dict, List, Optional, Any
from config import EMPLOYERS


class HHAPI:
    """Класс для взаимодействия с API hh.ru."""

    BASE_URL = "https://api.hh.ru"

    def __init__(self, employers: Optional[List[Dict[str, str]]] = None):
        """
        Инициализация API.

        Args:
            employers: Список словарей с id и name компаний
        """
        self.employers = employers or EMPLOYERS
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "HH-Parser/1.0 (contact@example.com)"
        })

    def get_employer_vacancies(self, employer_id: str) -> List[Dict[str, Any]]:
        """
        Получить вакансии конкретного работодателя.

        Args:
            employer_id: ID работодателя

        Returns:
            Список вакансий
        """
        vacancies = []
        page = 0
        per_page = 100

        while True:
            params = {
                "employer_id": employer_id,
                "page": page,
                "per_page": per_page,
                "only_with_salary": True
            }

            try:
                response = self.session.get(
                    f"{self.BASE_URL}/vacancies",
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()

                vacancies.extend(data.get("items", []))

                if page >= data.get("pages", 0) - 1:
                    break

                page += 1

            except requests.RequestException as e:
                print(f"Ошибка при получении вакансий для {employer_id}: {e}")
                break

        return vacancies

    def get_all_vacancies(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Получить вакансии для всех компаний из списка.

        Returns:
            Словарь {название_компании: список_вакансий}
        """
        all_vacancies = {}

        for employer in self.employers:
            print(f"Получение вакансий для {employer['name']}...")
            vacancies = self.get_employer_vacancies(employer["id"])
            all_vacancies[employer["name"]] = vacancies
            print(f"Получено {len(vacancies)} вакансий")

        return all_vacancies

    @staticmethod
    def parse_vacancy(vacancy: Dict[str, Any], employer_name: str) -> Dict[str, Any]:
        """
        Парсинг данных вакансии для сохранения в БД.

        Args:
            vacancy: Данные вакансии из API
            employer_name: Название компании-работодателя

        Returns:
            Словарь с подготовленными данными
        """
        salary_data = vacancy.get("salary")

        # Обработка зарплаты
        salary_from = None
        salary_to = None

        if salary_data:
            salary_from = salary_data.get("from")
            salary_to = salary_data.get("to")

        # Средняя зарплата для сортировки
        avg_salary = None
        if salary_from and salary_to:
            avg_salary = (salary_from + salary_to) // 2
        elif salary_from:
            avg_salary = salary_from
        elif salary_to:
            avg_salary = salary_to

        return {
            "vacancy_id": vacancy.get("id"),
            "name": vacancy.get("name"),
            "salary_from": salary_from,
            "salary_to": salary_to,
            "avg_salary": avg_salary,
            "currency": salary_data.get("currency") if salary_data else None,
            "url": vacancy.get("alternate_url"),
            "requirement": vacancy.get("snippet", {}).get("requirement"),
            "responsibility": vacancy.get("snippet", {}).get("responsibility"),
            "employer_name": employer_name,
            "city": vacancy.get("area", {}).get("name"),
            "published_at": vacancy.get("published_at"),
        }


# Данные для тестирования (если API блокируется)
MOCK_VACANCIES = {
    "Yandex": [],
    "Ozon Tech": [],
    "Sber": [],
    "Tinkoff": [],
    "VK": [],
}
