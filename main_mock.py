"""Главный модуль для тестирования с mock-данными."""
import sys
from mock_api import MockHeadHunterAPI, PREDEFINED_COMPANIES
from mock_db import MockDBManager, create_database_if_not_exists


def load_vacancies_to_db(use_mock_api: bool = True) -> None:
    """
    Загрузка данных о вакансиях с использованием mock API.

    Args:
        use_mock_api: Использовать mock API (True) или реальный API (False)
    """
    print("=" * 60)
    print("ЗАГРУЗКА ДАННЫХ (MOCK РЕЖИМ)")
    print("=" * 60)

    # Создание mock БД
    print("\n1. Подготовка базы данных...")
    db_manager = create_database_if_not_exists()

    try:
        print("\n2. Создание таблиц...")
        db_manager.create_tables()

        # Получение данных через mock API
        print("\n3. Загрузка данных через Mock API...")
        hh_api = MockHeadHunterAPI(use_real_data=False)
        companies_data = hh_api.get_companies_vacancies(PREDEFINED_COMPANIES)

        # Заполнение таблиц
        print("\n4. Заполнение таблиц данными...")
        employers_count = 0
        vacancies_count = 0

        for company_id, data in companies_data.items():
            company_info = data.get('company_info')
            vacancies = data.get('vacancies', [])

            if company_info:
                db_manager.insert_employer(company_info)
                employers_count += 1

                for vacancy in vacancies:
                    db_manager.insert_vacancy(vacancy, company_id)
                    vacancies_count += 1

        print(f"\n✓ Загрузка завершена!")
        print(f"  - Загружено компаний: {employers_count}")
        print(f"  - Загружено вакансий: {vacancies_count}")

        return db_manager

    except Exception as e:
        print(f"\nОшибка при загрузке: {e}")
        db_manager.close()
        raise


def display_vacancies(vacancies: list, title: str, limit: int = 20) -> None:
    """Отображение списка вакансий."""
    print(f"\n{title}")
    print("-" * 80)

    if not vacancies:
        print("Нет данных для отображения")
        return

    for i, vac in enumerate(vacancies[:limit], 1):
        company = vac[0]
        name = vac[1]
        salary_from = vac[2] if len(vac) > 2 else None
        salary_to = vac[3] if len(vac) > 3 else None
        currency = vac[4] if len(vac) > 4 else "RUR"
        url = vac[5] if len(vac) > 5 else ""

        salary_str = f"от {salary_from}" if salary_from else ""
        if salary_to:
            salary_str += f" до {salary_to}" if salary_str else f"до {salary_to}"
        salary_str = salary_str or "не указана"

        print(f"{i}. {company} - {name}")
        print(f"   Зарплата: {salary_str} {currency}")
        print(f"   Ссылка: {url[:80]}..." if len(url) > 80 else f"   Ссылка: {url}")
        print()

    if len(vacancies) > limit:
        print(f"... и еще {len(vacancies) - limit} вакансий")


def interactive_mode(db_manager: MockDBManager) -> None:
    """Интерактивный режим работы с mock БД."""
    while True:
        print("\n" + "=" * 60)
        print("СИСТЕМА АНАЛИЗА ВАКАНСИЙ (MOCK РЕЖИМ)")
        print("=" * 60)
        print("\nВыберите действие:")
        print("1. Список компаний и количество их вакансий")
        print("2. Список всех вакансий")
        print("3. Средняя зарплата по всем вакансиям")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("\nВаш выбор: ").strip()

        if choice == "0":
            print("До свидания!")
            break

        elif choice == "1":
            result = db_manager.get_companies_and_vacancies_count()
            print("\nКОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ")
            print("-" * 50)
            if not result:
                print("Нет данных")
            for company, count in result:
                print(f"• {company}: {count} вакансий")

        elif choice == "2":
            result = db_manager.get_all_vacancies()
            display_vacancies(result, f"ВСЕ ВАКАНСИИ (всего: {len(result)})")

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"\nСРЕДНЯЯ ЗАРПЛАТА")
            print("-" * 50)
            if avg_salary:
                print(f"Средняя зарплата по всем вакансиям: {avg_salary:.2f} RUR")
            else:
                print("Недостаточно данных для расчета средней зарплаты")

        elif choice == "4":
            result = db_manager.get_vacancies_with_higher_salary()
            avg_salary = db_manager.get_avg_salary()
            if avg_salary:
                print(f"\nВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ ({avg_salary:.2f} RUR)")
                display_vacancies(result, f"Найдено: {len(result)} вакансий")
            else:
                print("Недостаточно данных для сравнения")

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if keyword:
                result = db_manager.get_vacancies_with_keyword(keyword)
                display_vacancies(result, f"ВАКАНСИИ, СОДЕРЖАЩИЕ '{keyword}' (найдено: {len(result)})")
            else:
                print("Ключевое слово не может быть пустым")

        else:
            print("Неверный выбор. Пожалуйста, выберите от 0 до 5.")


def main():
    """Главная функция для тестирования с mock-данными."""
    print("\n" + "=" * 60)
    print("ЗАПУСК В MOCK РЕЖИМЕ (БЕЗ РЕАЛЬНОЙ БД И API)")
    print("=" * 60)
    print("\nВ этом режиме используются сгенерированные данные")
    print("и in-memory хранилище вместо реальной БД.\n")

    try:
        # Загрузка mock-данных
        db_manager = load_vacancies_to_db(use_mock_api=True)

        # Интерактивный режим
        interactive_mode(db_manager)

        # Закрытие соединения
        db_manager.close()

    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
