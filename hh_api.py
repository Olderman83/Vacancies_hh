"""Модуль для взаимодействия с API hh.ru."""
import requests
from typing import List, Dict, Any


class HeadHunterAPI:
    """
    Класс для работы с API HeadHunter.

    Позволяет получать информацию о компаниях и их вакансиях.
    """

    BASE_URL: str = 'https://api.hh.ru'

    def __init__(self) -> None:
        """Инициализация класса HeadHunterAPI."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HH-Vacancy-Parser/1.0'
        })

    def get_company(self, company_id: str) -> Dict[str, Any]:
        """
        Получение информации о компании по ID.

        Args:
            company_id: ID компании на hh.ru

        Returns:
            Dict: Данные о компании
        """
        url = f'{self.BASE_URL}/employers/{company_id}'
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_company_vacancies(self, company_id: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Получение списка вакансий компании.

        Args:
            company_id: ID компании на hh.ru
            per_page: Количество вакансий на странице

        Returns:
            List[Dict]: Список вакансий компании
        """
        vacancies = []
        page = 0

        while True:
            params = {
                'employer_id': company_id,
                'per_page': per_page,
                'page': page,
                'only_with_salary': False
            }

            url = f'{self.BASE_URL}/vacancies'
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            vacancies.extend(data.get('items', []))

            if page >= data.get('pages', 1) - 1:
                break

            page += 1

        return vacancies

    def get_companies_vacancies(self, company_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Получение вакансий для списка компаний.

        Args:
            company_ids: Список ID компаний

        Returns:
            Dict: Словарь с вакансиями по компаниям
        """
        result = {}

        for company_id in company_ids:
            try:
                company = self.get_company(company_id)
                vacancies = self.get_company_vacancies(company_id)
                result[company_id] = {
                    'company_info': company,
                    'vacancies': vacancies
                }
                print(f'Загружено {len(vacancies)} вакансий для компании {company.get("name", company_id)}')
            except Exception as e:
                print(f'Ошибка при загрузке компании {company_id}: {e}')
                continue

        return result


# Предустановленные компании для загрузки (10 компаний)
PREDEFINED_COMPANIES = [
    '1001',  # Ozon Tech
    '1002',  # Yandex
    '1003',  # VK
    '1004',  # Tinkoff
    '1005',  # Sber
    '80',  # Mail.ru Group
    '15478',  # Avito
    '3529',  # 2GIS
    '39305',  # Wildberries
    '87021'  # ЦИАН
]
