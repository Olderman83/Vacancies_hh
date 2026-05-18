# hh_api.py
import requests
import time
from typing import List, Dict, Any


class HeadHunterAPI:
    """Класс для работы с API HeadHunter"""

    BASE_URL = 'https://api.hh.ru'

    # 10 интересных компаний (ID компаний с hh.ru)
    EMPLOYERS = [
        {'id': 1740, 'name': 'Яндекс'},           # Яндекс
        {'id': 3529, 'name': 'Сбер'},              # Сбер
        {'id': 2180, 'name': 'Ozon'},              # Ozon
        {'id': 80, 'name': 'Альфа-Банк'},          # Альфа-Банк
        {'id': 15478, 'name': 'VK'},               # VK
        {'id': 78638, 'name': 'Т-Банк'},           # Т-Банк (Тинькофф)
        {'id': 2381, 'name': 'Wildberries'},       # Wildberries
        {'id': 1057, 'name': 'Mail.ru Group'},     # Mail.ru Group
        {'id': 3776, 'name': 'МТС'},               # МТС
        {'id': 2748, 'name': 'EPAM Systems'},      # EPAM Systems
    ]

    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Выполнение запроса с обработкой ошибок"""
        time.sleep(self.delay)  # Задержка для соблюдения лимитов API
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return {}

    def get_employer_info(self, employer_id: int) -> Dict:
        """Получение информации о работодателе"""
        url = f'{self.BASE_URL}/employers/{employer_id}'
        return self._make_request(url)

    def get_vacancies_by_employer(self, employer_id: int, per_page: int = 100) -> List[Dict]:
        """Получение вакансий работодателя"""
        vacancies = []
        page = 0

        while True:
            params = {
                'employer_id': employer_id,
                'per_page': per_page,
                'page': page,
                'only_with_salary': False
            }

            url = f'{self.BASE_URL}/vacancies'
            data = self._make_request(url, params)

            if not data or 'items' not in data:
                break

            vacancies.extend(data['items'])

            # Проверяем, есть ли еще страницы
            if page >= (data.get('pages', 0) - 1):
                break

            page += 1

        return vacancies

    def get_all_employers_data(self) -> List[Dict]:
        """Получение данных по всем выбранным работодателям"""
        employers_data = []

        for employer in self.EMPLOYERS:
            print(f"Загрузка данных о компании: {employer['name']}")

            # Получаем информацию о работодателе
            employer_info = self.get_employer_info(employer['id'])
            if employer_info:
                employers_data.append({
                    'employer_id': employer_info.get('id'),
                    'employer_name': employer_info.get('name'),
                    'employer_url': employer_info.get('site_url'),
                    'alternate_url': employer_info.get('alternate_url'),
                    'vacancies_url': employer_info.get('vacancies_url'),
                    'open_vacancies': employer_info.get('open_vacancies', 0)
                })

        return employers_data

    def get_all_vacancies_data(self, employer_id: int, employer_name: str) -> List[Dict]:
        """Получение всех вакансий для конкретного работодателя"""
        print(f"Загрузка вакансий для компании: {employer_name}")
        vacancies = self.get_vacancies_by_employer(employer_id)

        vacancies_data = []
        for vacancy in vacancies:
            # Обработка зарплаты
            salary = vacancy.get('salary')
            salary_from = None
            salary_to = None
            salary_currency = None

            if salary:
                salary_from = salary.get('from')
                salary_to = salary.get('to')
                salary_currency = salary.get('currency')

            vacancies_data.append({
                'vacancy_id': vacancy.get('id'),
                'employer_id': employer_id,
                'vacancy_name': vacancy.get('name'),
                'salary_from': salary_from,
                'salary_to': salary_to,
                'salary_currency': salary_currency,
                'url': vacancy.get('alternate_url'),
                'requirement': vacancy.get('snippet', {}).get('requirement'),
                'responsibility': vacancy.get('snippet', {}).get('responsibility'),
                'published_at': vacancy.get('published_at')
            })

        print(f"  Загружено {len(vacancies_data)} вакансий")
        return vacancies_data
