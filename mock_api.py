"""Модуль с mock-данными для тестирования без реального API."""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from copy import deepcopy


class MockHeadHunterAPI:
    """
    Mock-класс для имитации работы с API HeadHunter.
    Использует предопределенные данные вместо реальных запросов.
    """

    # Базовые данные о компаниях
    MOCK_COMPANIES = {
        '1001': {
            'id': '1001',
            'name': 'Ozon Tech',
            'alternate_url': 'https://hh.ru/employer/1001',
            'trusted': True,
            'description': 'Технологическая компания Ozon'
        },
        '1002': {
            'id': '1002',
            'name': 'Yandex',
            'alternate_url': 'https://hh.ru/employer/1002',
            'trusted': True,
            'description': 'Яндекс - технологическая компания'
        },
        '1003': {
            'id': '1003',
            'name': 'VK',
            'alternate_url': 'https://hh.ru/employer/1003',
            'trusted': True,
            'description': 'VK - экосистема сервисов'
        },
        '1004': {
            'id': '1004',
            'name': 'Tinkoff',
            'alternate_url': 'https://hh.ru/employer/1004',
            'trusted': True,
            'description': 'Тинькофф - финансовые технологии'
        },
        '1005': {
            'id': '1005',
            'name': 'Sber',
            'alternate_url': 'https://hh.ru/employer/1005',
            'trusted': True,
            'description': 'Сбер - экосистема сервисов'
        },
        '80': {
            'id': '80',
            'name': 'Mail.ru Group',
            'alternate_url': 'https://hh.ru/employer/80',
            'trusted': True,
            'description': 'Mail.ru Group - интернет-компания'
        },
        '15478': {
            'id': '15478',
            'name': 'Avito',
            'alternate_url': 'https://hh.ru/employer/15478',
            'trusted': True,
            'description': 'Avito - платформа объявлений'
        },
        '3529': {
            'id': '3529',
            'name': '2GIS',
            'alternate_url': 'https://hh.ru/employer/3529',
            'trusted': True,
            'description': '2ГИС - картографический сервис'
        },
        '39305': {
            'id': '39305',
            'name': 'Wildberries',
            'alternate_url': 'https://hh.ru/employer/39305',
            'trusted': True,
            'description': 'Wildberries - маркетплейс'
        },
        '87021': {
            'id': '87021',
            'name': 'ЦИАН',
            'alternate_url': 'https://hh.ru/employer/87021',
            'trusted': True,
            'description': 'ЦИАН - платформа недвижимости'
        }
    }

    # Базовые шаблоны вакансий
    VACANCY_TEMPLATES = [
        {
            'name': 'Python разработчик',
            'experience_levels': ['noExperience', 'between1And3', 'between3And6', 'moreThan6'],
            'salary_ranges': {
                'noExperience': (80000, 120000),
                'between1And3': (120000, 180000),
                'between3And6': (180000, 250000),
                'moreThan6': (250000, 400000)
            }
        },
        {
            'name': 'ML инженер',
            'experience_levels': ['between1And3', 'between3And6', 'moreThan6'],
            'salary_ranges': {
                'between1And3': (150000, 220000),
                'between3And6': (220000, 300000),
                'moreThan6': (300000, 500000)
            }
        },
        {
            'name': 'Data Engineer',
            'experience_levels': ['between1And3', 'between3And6', 'moreThan6'],
            'salary_ranges': {
                'between1And3': (130000, 200000),
                'between3And6': (200000, 280000),
                'moreThan6': (280000, 420000)
            }
        },
        {
            'name': 'Backend инженер',
            'experience_levels': ['noExperience', 'between1And3', 'between3And6', 'moreThan6'],
            'salary_ranges': {
                'noExperience': (70000, 110000),
                'between1And3': (110000, 170000),
                'between3And6': (170000, 240000),
                'moreThan6': (240000, 380000)
            }
        },
        {
            'name': 'Frontend разработчик',
            'experience_levels': ['noExperience', 'between1And3', 'between3And6', 'moreThan6'],
            'salary_ranges': {
                'noExperience': (70000, 110000),
                'between1And3': (110000, 160000),
                'between3And6': (160000, 230000),
                'moreThan6': (230000, 350000)
            }
        },
        {
            'name': 'Fullstack разработчик',
            'experience_levels': ['between1And3', 'between3And6', 'moreThan6'],
            'salary_ranges': {
                'between1And3': (120000, 180000),
                'between3And6': (180000, 260000),
                'moreThan6': (260000, 400000)
            }
        },
        {
            'name': 'DevOps инженер',
            'experience_levels': ['between1And3', 'between3And6', 'moreThan6'],
            'salary_ranges': {
                'between1And3': (140000, 200000),
                'between3And6': (200000, 280000),
                'moreThan6': (280000, 450000)
            }
        },
        {
            'name': 'Data Scientist',
            'experience_levels': ['between1And3', 'between3And6', 'moreThan6'],
            'salary_ranges': {
                'between1And3': (130000, 190000),
                'between3And6': (190000, 270000),
                'moreThan6': (270000, 420000)
            }
        }
    ]

    # Города
    CITIES = [
        {'id': '1', 'name': 'Москва'},
        {'id': '2', 'name': 'Санкт-Петербург'},
        {'id': '3', 'name': 'Новосибирск'},
        {'id': '4', 'name': 'Екатеринбург'},
        {'id': '5', 'name': 'Казань'},
        {'id': '6', 'name': 'Нижний Новгород'},
        {'id': '7', 'name': 'Красноярск'},
        {'id': '8', 'name': 'Челябинск'}
    ]

    # Типы занятости
    EMPLOYMENT_TYPES = [
        {'id': 'full', 'name': 'Полная занятость'},
        {'id': 'part', 'name': 'Частичная занятость'},
        {'id': 'project', 'name': 'Проектная работа'}
    ]

    # Графики работы
    SCHEDULE_TYPES = [
        {'id': 'fullDay', 'name': 'Полный день'},
        {'id': 'remote', 'name': 'Удаленная работа'},
        {'id': 'hybrid', 'name': 'Гибридный формат'},
        {'id': 'flexible', 'name': 'Гибкий график'}
    ]

    # Опыт работы
    EXPERIENCE_LEVELS = {
        'noExperience': {'id': 'noExperience', 'name': 'Нет опыта'},
        'between1And3': {'id': 'between1And3', 'name': 'От 1 года до 3 лет'},
        'between3And6': {'id': 'between3And6', 'name': 'От 3 до 6 лет'},
        'moreThan6': {'id': 'moreThan6', 'name': 'Более 6 лет'}
    }

    def __init__(self, use_real_data: bool = False):
        """
        Инициализация Mock API.

        Args:
            use_real_data: Использовать реальные данные из JSON файла
        """
        self.use_real_data = use_real_data
        self.real_data = None

        if use_real_data:
            self._load_real_data()

    def _load_real_data(self):
        """Загрузка реальных данных из предоставленного JSON."""
        # Здесь можно загрузить данные из hh_vacancies.json
        self.real_data = {
            "items": [
                {
                    "id": "10000000",
                    "name": "ML инженер",
                    "area": {"id": "23", "name": "Екатеринбург"},
                    "salary": {"from": 100307, "to": 237024, "currency": "RUR", "gross": False},
                    "employer": {"id": "1002", "name": "Yandex"},
                    "alternate_url": "https://hh.ru/vacancy/10000000",
                    "experience": {"id": "noExperience", "name": "Без опыта"},
                    "employment": {"id": "full", "name": "Полная занятость"},
                    "schedule": {"id": "hybrid", "name": "Гибрид"},
                    "snippet": {"requirement": "Python, SQL", "responsibility": "Разработка ML моделей"},
                    "published_at": "2026-04-20T02:21:46",
                    "created_at": "2026-04-07T02:21:46",
                    "archived": False
                }
                # Добавьте остальные данные из предоставленного JSON
            ]
        }

    def _generate_vacancy_id(self, company_id: str, index: int) -> str:
        """Генерация ID вакансии."""
        return f"{company_id}{index:05d}"

    def _get_random_salary(self, template: Dict, experience_id: str) -> Dict:
        """Генерация случайной зарплаты."""
        salary_range = template['salary_ranges'].get(experience_id, (50000, 100000))
        salary_from = random.randint(salary_range[0], salary_range[1])
        salary_to = salary_from + random.randint(10000, 50000)
        currency = random.choice(['RUR', 'RUR', 'RUR', 'USD'])
        gross = random.choice([True, False])

        return {
            'from': salary_from,
            'to': salary_to,
            'currency': currency if currency == 'RUR' else 'RUR',
            'gross': gross
        }

    def _generate_vacancies_for_company(self, company_id: str, count: int = 15) -> List[Dict]:
        """
        Генерация мок-вакансий для компании.

        Args:
            company_id: ID компании
            count: Количество вакансий для генерации

        Returns:
            List[Dict]: Список сгенерированных вакансий
        """
        vacancies = []
        company = self.MOCK_COMPANIES.get(company_id, {})

        for i in range(count):
            template = random.choice(self.VACANCY_TEMPLATES)
            experience_level = random.choice(template['experience_levels'])
            experience = self.EXPERIENCE_LEVELS[experience_level]
            city = random.choice(self.CITIES)
            employment = random.choice(self.EMPLOYMENT_TYPES)
            schedule = random.choice(self.SCHEDULE_TYPES)
            salary = self._get_random_salary(template, experience_level)

            # Генерация даты публикации (от 1 до 30 дней назад)
            days_ago = random.randint(1, 30)
            published_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
            created_at = (datetime.now() - timedelta(days=days_ago + random.randint(0, 5))).isoformat()

            vacancy = {
                'id': self._generate_vacancy_id(company_id, i),
                'name': template['name'],
                'area': city,
                'salary': salary,
                'type': {'id': 'open', 'name': 'Открытая'},
                'published_at': published_at,
                'created_at': created_at,
                'archived': random.random() < 0.1,  # 10% вакансий в архиве
                'employer': company,
                'snippet': {
                    'requirement': f'Опыт работы с {random.choice(["Python", "Java", "Go", "C++"])}, '
                                   f'{random.choice(["SQL", "NoSQL", "Docker", "K8s"])}, '
                                   f'{random.choice(["API", "REST", "GraphQL"])}',
                    'responsibility': f'Разработка и поддержка {random.choice(["backend", "frontend", "full-stack"])} сервисов'
                },
                'alternate_url': f'https://hh.ru/vacancy/{self._generate_vacancy_id(company_id, i)}',
                'experience': experience,
                'employment': employment,
                'schedule': schedule
            }

            vacancies.append(vacancy)

        return vacancies

    def get_company(self, company_id: str) -> Dict[str, Any]:
        """
        Получение информации о компании (mock).

        Args:
            company_id: ID компании

        Returns:
            Dict: Данные о компании
        """
        if self.use_real_data and self.real_data:
            # Поиск компании в реальных данных
            for item in self.real_data['items']:
                if item['employer']['id'] == company_id:
                    return item['employer']

        # Возвращаем mock-данные
        if company_id in self.MOCK_COMPANIES:
            return self.MOCK_COMPANIES[company_id].copy()
        else:
            return {
                'id': company_id,
                'name': f'Компания {company_id}',
                'alternate_url': f'https://hh.ru/employer/{company_id}',
                'trusted': False
            }

    def get_company_vacancies(self, company_id: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Получение списка вакансий компании (mock).

        Args:
            company_id: ID компании
            per_page: Количество вакансий на странице

        Returns:
            List[Dict]: Список вакансий
        """
        if self.use_real_data and self.real_data:
            # Фильтрация реальных данных по company_id
            real_vacancies = [
                item for item in self.real_data['items']
                if item['employer']['id'] == company_id
            ]
            if real_vacancies:
                return real_vacancies[:per_page]

        # Генерация mock-вакансий
        # Разное количество вакансий для разных компаний
        vacancies_count = {
            '1001': 12,  # Ozon Tech
            '1002': 25,  # Yandex
            '1003': 18,  # VK
            '1004': 15,  # Tinkoff
            '1005': 22,  # Sber
            '80': 10,  # Mail.ru
            '15478': 8,  # Avito
            '3529': 6,  # 2GIS
            '39305': 14,  # Wildberries
            '87021': 5  # CIAN
        }.get(company_id, 10)

        return self._generate_vacancies_for_company(company_id, vacancies_count)

    def get_companies_vacancies(self, company_ids: List[str]) -> Dict[str, Dict]:
        """
        Получение вакансий для списка компаний.

        Args:
            company_ids: Список ID компаний

        Returns:
            Dict: Словарь с данными о компаниях и их вакансиях
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
                print(f'[MOCK] Загружено {len(vacancies)} вакансий для компании {company.get("name", company_id)}')
            except Exception as e:
                print(f'[MOCK] Ошибка при загрузке компании {company_id}: {e}')
                continue

        return result


# Те же самые ID компаний для совместимости
PREDEFINED_COMPANIES = [
    '1001', '1002', '1003', '1004', '1005',
    '80', '15478', '3529', '39305', '87021'
]
