"""Главный модуль для запуска парсера hh.ru и взаимодействия с БД."""
import sys
from typing import Dict, List, Any

from config import DatabaseConfig, EMPLOYERS
from hh_api import HHAPI
from db_manager import DBManager


def format_salary(salary_from: int, salary_to: int, currency: str) -> str:
    """
    Форматировать вывод зарплаты.

    Args:
        salary_from: Нижняя граница
        salary_to: Верхняя граница
        currency: Валюта

    Returns:
        Отформатированная строка зарплаты
    """
    if salary_from and salary_to:
        return f"{salary_from:,} - {salary_to:,} {currency}".replace(",", " ")
    elif salary_from:
        return f"от {salary_from:,} {currency}".replace(",", " ")
    elif salary_to:
        return f"до {salary_to:,} {currency}".replace(",", " ")
    return "Не указана"


def display_companies_and_vacancies(db_manager: DBManager) -> None:
    """Отобразить компании и количество вакансий."""
    print("\n" + "=" * 60)
    print("КОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ")
    print("=" * 60)

    results = db_manager.get_companies_and_vacancies_count()
    for item in results:
        print(f"📢 {item['company_name']}: {item['vacancies_count']} вакансий")


def display_all_vacancies(db_manager: DBManager) -> None:
    """Отобразить все вакансии."""
    print("\n" + "=" * 60)
    print("ВСЕ ВАКАНСИИ")
    print("=" * 60)

    vacancies = db_manager.get_all_vacancies()
    for vac in vacancies:
        salary = format_salary(vac['salary_from'], vac['salary_to'], vac['currency'] or 'RUR')
        print(f"\n🏢 {vac['company_name']}")
        print(f"📌 {vac['vacancy_name']}")
        print(f"💰 {salary}")
        print(f"📍 {vac['city']}")
        print(f"🔗 {vac['url']}")
        print("-" * 40)


def display_avg_salary(db_manager: DBManager) -> None:
    """Отобразить среднюю зарплату."""
    print("\n" + "=" * 60)
    print("СРЕДНЯЯ ЗАРПЛАТА ПО ВСЕМ ВАКАНСИЯМ")
    print("=" * 60)

    avg_salary = db_manager.get_avg_salary()
    print(f"💰 Средняя зарплата: {avg_salary:,.0f} RUR".replace(",", " "))


def display_higher_salary_vacancies(db_manager: DBManager) -> None:
    """Отобразить вакансии с зарплатой выше средней."""
    print("\n" + "=" * 60)
    print("ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ")
    print("=" * 60)

    vacancies = db_manager.get_vacancies_with_higher_salary()
    avg_salary = db_manager.get_avg_salary()

    print(f"Средняя зарплата: {avg_salary:,.0f} RUR".replace(",", " "))
    print("-" * 40)

    for vac in vacancies:
        salary = format_salary(vac['salary_from'], vac['salary_to'], vac['currency'] or 'RUR')
        print(f"\n🏢 {vac['company_name']}")
        print(f"📌 {vac['vacancy_name']}")
        print(f"💰 {salary} (средняя: {vac['avg_salary']:,} RUR)".replace(",", " "))
        print(f"🔗 {vac['url']}")
        print("-" * 40)


def display_vacancies_by_keyword(db_manager: DBManager) -> None:
    """Отобразить вакансии по ключевому слову."""
    keyword = input("\nВведите ключевое слово для поиска: ").strip()

    if not keyword:
        print("Ключевое слово не может быть пустым!")
        return

    print("\n" + "=" * 60)
    print(f"ВАКАНСИИ, СОДЕРЖАЩИЕ '{keyword}'")
    print("=" * 60)

    vacancies = db_manager.get_vacancies_with_keyword(keyword)

    if not vacancies:
        print(f"Вакансии, содержащие '{keyword}', не найдены")
        return

    for vac in vacancies:
        salary = format_salary(vac['salary_from'], vac['salary_to'], vac['currency'] or 'RUR')
        print(f"\n🏢 {vac['company_name']}")
        print(f"📌 {vac['vacancy_name']}")
        print(f"💰 {salary}")
        print(f"📝 Требования: {vac['requirement'][:150] if vac['requirement'] else 'Не указаны'}...")
        print(f"🔗 {vac['url']}")
        print("-" * 40)


def load_data_from_api() -> None:
    """Загрузить данные из API hh.ru и сохранить в БД."""
    print("Начало загрузки данных с hh.ru...")

    # Получаем данные через API
    api = HHAPI()
    all_vacancies = api.get_all_vacancies()

    # Подготовка данных для БД
    employers_data = []
    vacancies_data = []

    for employer in EMPLOYERS:
        employers_data.append({
            "employer_id": employer["id"],
            "name": employer["name"],
            "url": f"https://hh.ru/employer/{employer['id']}",
            "trusted": True
        })

    for employer_name, vacancies in all_vacancies.items():
        employer_id = next(
            (e["id"] for e in EMPLOYERS if e["name"] == employer_name),
            None
        )
        if employer_id:
            for vacancy in vacancies:
                parsed = api.parse_vacancy(vacancy, employer_name)
                parsed["employer_id"] = employer_id
                vacancies_data.append(parsed)

    # Сохраняем в БД
    config = DatabaseConfig()
    with DBManager(config) as db:
        db.create_database()
        db.connect()
        db.create_tables()
        db.insert_employers(employers_data)
        db.insert_vacancies(vacancies_data)

    print(f"\nЗагрузка завершена. Получено {len(vacancies_data)} вакансий")


def interactive_menu() -> None:
    """Интерактивное меню для работы с БД."""
    config = DatabaseConfig()

    with DBManager(config) as db:
        db.create_database()
        db.connect()
        db.create_tables()

        while True:
            print("\n" + "=" * 60)
            print("СИСТЕМА УПРАВЛЕНИЯ ВАКАНСИЯМИ")
            print("=" * 60)
            print("1. Показать компании и количество вакансий")
            print("2. Показать все вакансии")
            print("3. Показать среднюю зарплату")
            print("4. Показать вакансии с зарплатой выше средней")
            print("5. Поиск вакансий по ключевому слову")
            print("0. Выход")
            print("=" * 60)

            choice = input("\nВыберите действие: ").strip()

            if choice == "1":
                display_companies_and_vacancies(db)
            elif choice == "2":
                display_all_vacancies(db)
            elif choice == "3":
                display_avg_salary(db)
            elif choice == "4":
                display_higher_salary_vacancies(db)
            elif choice == "5":
                display_vacancies_by_keyword(db)
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неверный выбор. Пожалуйста, попробуйте снова.")


def main() -> None:
    """Главная функция."""
    print("Добро пожаловать в парсер вакансий hh.ru!")
    print("\nВыберите режим работы:")
    print("1. Загрузить данные с hh.ru (требуется интернет)")
    print("2. Работать с существующей базой данных")
    print("3. Использовать тестовые данные (без API)")

    choice = input("\nВаш выбор (1/2/3): ").strip()

    if choice == "1":
        try:
            load_data_from_api()
            interactive_menu()
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            print("Попробуйте использовать режим с тестовыми данными или проверьте подключение")
    elif choice == "2":
        interactive_menu()
    elif choice == "3":
        print("Использование тестовых данных...")
        # Здесь можно добавить загрузку mock-данных из предоставленного JSON
        interactive_menu()
    else:
        print("Неверный выбор. Завершение программы.")
        sys.exit(1)


if __name__ == "__main__":
    main()
