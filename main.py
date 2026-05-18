# main.py
from config import DB_CONFIG
from hh_api import HeadHunterAPI
from db_manager import DBManager


def main():
    print("=" * 60)
    print("ПАРСЕР ВАКАНСИЙ С HEADHUNTER.RU")
    print("=" * 60)

    # 1. Получение данных через API
    print("\n1. Загрузка данных с hh.ru...")
    hh_api = HeadHunterAPI()

    # Получаем данные о работодателях
    employers_data = hh_api.get_all_employers_data()
    print(f"\nЗагружено данных о {len(employers_data)} компаниях")

    # Получаем данные о вакансиях для каждого работодателя
    all_vacancies = []
    for employer in employers_data:
        vacancies = hh_api.get_all_vacancies_data(
            employer['employer_id'],
            employer['employer_name']
        )
        all_vacancies.extend(vacancies)

    print(f"\nВсего загружено вакансий: {len(all_vacancies)}")

    # 2. Создание таблиц и загрузка данных в БД
    print("\n2. Загрузка данных в PostgreSQL...")
    db_manager = DBManager(DB_CONFIG)

    # Создаем таблицы
    db_manager.create_tables()

    # Вставляем данные
    db_manager.insert_employers(employers_data)
    db_manager.insert_vacancies(all_vacancies)

    # 3. Демонстрация работы методов DBManager
    print("\n" + "=" * 60)
    print("3. Анализ данных")
    print("=" * 60)

    # Компании и количество вакансий
    print("\n--- Компании и количество вакансий ---")
    companies_vacancies = db_manager.get_companies_and_vacancies_count()
    for item in companies_vacancies:
        print(f"  {item['employer_name']}: {item['vacancies_count']} вакансий")

    # Все вакансии
    print("\n--- Все вакансии (первые 10) ---")
    all_vacancies_list = db_manager.get_all_vacancies()
    for i, vac in enumerate(all_vacancies_list[:10], 1):
        print(f"  {i}. {vac['employer_name']} - {vac['vacancy_name']}")
        print(f"     Зарплата: {vac['salary_from']} - {vac['salary_to']} {vac['salary_currency']}")
        print(f"     Ссылка: {vac['url']}\n")

    # Средняя зарплата
    print("\n--- Средняя зарплата по всем вакансиям ---")
    avg_salary = db_manager.get_avg_salary()
    print(f"  Средняя зарплата: {avg_salary:.2f} руб.")

    # Вакансии с зарплатой выше средней
    print("\n--- Вакансии с зарплатой выше средней (первые 10) ---")
    high_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
    for i, vac in enumerate(high_salary_vacancies[:10], 1):
        avg_vac_salary = (vac['salary_from'] or 0 + vac['salary_to'] or 0) / 2
        print(f"  {i}. {vac['employer_name']} - {vac['vacancy_name']}")
        print(f"     Зарплата: {vac['salary_from']} - {vac['salary_to']} {vac['salary_currency']} (ср: {avg_vac_salary:.2f})")

    # Поиск по ключевому слову
    print("\n--- Поиск вакансий по ключевому слову 'python' ---")
    keyword_vacancies = db_manager.get_vacancies_with_keyword('python')
    for i, vac in enumerate(keyword_vacancies[:10], 1):
        print(f"  {i}. {vac['employer_name']} - {vac['vacancy_name']}")
        print(f"     Ссылка: {vac['url']}")

    # Закрываем соединение
    db_manager.close()

    print("\n" + "=" * 60)
    print("ГОТОВО!")
    print("=" * 60)


if __name__ == "__main__":
    main()
